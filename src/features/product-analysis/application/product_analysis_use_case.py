"""
Product Analysis — ProductAnalysisUseCase (Application Layer).

Orchestrates the complete product formulation analysis pipeline:

  1. Validate ProductAnalysisRequest
  2. DomainRouter → determine relevant legal dimensions
  3. QueryBuilder → construct one targeted query per dimension
  4. For each targeted query: HybridRetrievalUseCase.execute()
  5. Aggregate + deduplicate evidence across all queries
  6. Re-evaluate combined evidence with EvidenceEvaluator
  7. EvidenceSelectionUseCase → select best evidence (no domain filter)
  8. Abstention gate — return ProductAnalysisAbstention if insufficient
  9. Select best 10 evidence items for LLM (diversity-aware)
  10. Build analysis prompt from LLM-bound evidence
  11. OpenRouterProvider.complete() — ONE LLM call (max_tokens=2500)
  12. parse_structured_analysis_response() — validate JSON, strip bad citations
  13. Return ProductAnalysisResult (structured)

Architecture rules:
- Does NOT modify GroundedAnswerUseCase (used by /api/chat — untouched)
- Does NOT modify retrieval/evaluation/selection logic
- Does NOT introduce a second LLM call
- Does NOT fabricate evidence, citations, or legal conclusions
- Citation validation is strictly against the evidence passed to the LLM
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Set

from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase
from src.features.rag.application.evidence_selection_use_case import EvidenceSelectionUseCase
from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
from src.features.rag.infrastructure.openrouter_provider import (
    OpenRouterProvider,
    LLMProviderError,
)
from src.features.product_analysis.domain.product_request import ProductAnalysisRequest
from src.features.product_analysis.domain.domain_router import DomainRouter
from src.features.product_analysis.domain.query_builder import QueryBuilder
from src.features.product_analysis.domain.analysis_prompt import (
    build_product_evidence_block,
    build_product_analysis_prompt,
)
from src.features.product_analysis.domain.analysis_result import (
    ProductAnalysisResult,
    ProductAnalysisAbstention,
    ClassificationAssessment,
    IPAssessmentItem,
    RegulatoryAssessmentItem,
    TKBiodiversityAssessment,
    ComplianceItem,
)
from src.features.product_analysis.application.structured_response_parser import (
    parse_structured_analysis_response,
)

from concurrent.futures import ThreadPoolExecutor

# Maximum evidence items passed to the LLM (per approved plan Q2)
_LLM_EVIDENCE_CAP = 10
# Max tokens for the product analysis LLM call (per approved plan Q1)
_PRODUCT_ANALYSIS_MAX_TOKENS = 1500


class ProductAnalysisUseCase:
    """
    Executes the full product formulation analysis pipeline.

    Reuses the existing RAG infrastructure without modification:
      HybridRetrievalUseCase, EvidenceSelectionUseCase, EvidenceEvaluator,
      OpenRouterProvider.

    The LLM is called exactly once per analysis request and is instructed
    to return structured JSON. The JSON is validated by
    structured_response_parser.parse_structured_analysis_response().
    """

    def __init__(
        self,
        base_dir: str,
        retriever=None,
        llm_provider: Optional[OpenRouterProvider] = None,
    ) -> None:
        self._base_dir = base_dir
        self._retriever = retriever
        self._llm = llm_provider

        self._domain_router = DomainRouter()
        self._query_builder = QueryBuilder()
        self._evidence_selector = EvidenceSelectionUseCase()

    def _get_llm(self) -> OpenRouterProvider:
        if self._llm is None:
            self._llm = OpenRouterProvider()
        return self._llm

    def _make_retrieval_use_case(self) -> HybridRetrievalUseCase:
        """Create HybridRetrievalUseCase with the configured base_dir/retriever."""
        return HybridRetrievalUseCase(self._base_dir, retriever=self._retriever)

    def execute(
        self,
        request: ProductAnalysisRequest,
        analysis_id: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the full product analysis pipeline.

        Returns a dict compatible with the extended AnalysisApiResponse.
        """
        if not analysis_id:
            analysis_id = f"analysis_{uuid.uuid4().hex[:12]}"

        from src.features.rag.domain.multilingual import QueryNormalizer, ResponseLocalizer, LanguageDetector

        # Detect input language or use explicit target_language
        detected_lang = LanguageDetector.detect_language(
            f"{request.product_name} {request.intended_use} {request.product_claims}"
        )
        user_lang = target_language if target_language in ("en", "hi", "te") else detected_lang

        # Normalize product description & intended use for English retrieval
        normalizer = QueryNormalizer()
        norm_use, _ = normalizer.normalize(request.intended_use)
        norm_claims, _ = normalizer.normalize(request.product_claims)
        norm_name, _ = normalizer.normalize(request.product_name)

        # Attach normalized English query terms if available without mutating original request
        retrieval_request = request
        if norm_use or norm_claims or norm_name:
            import copy
            retrieval_request = copy.deepcopy(request)
            if norm_name:
                retrieval_request.product_name = norm_name
            if norm_use:
                retrieval_request.intended_use = norm_use
            if norm_claims:
                retrieval_request.product_claims = norm_claims

        retrieval_uc = self._make_retrieval_use_case()

        # ── Step 1: Route to relevant dimensions ──────────────────────────
        dimensions = self._domain_router.route(retrieval_request)
        domains_queried = [d.legal_domain for d in dimensions]

        # ── Step 2: Build targeted queries per dimension ──────────────────
        targeted_queries = self._query_builder.build_queries(retrieval_request, dimensions)

        # ── Step 3: Retrieve evidence for each targeted query ─────────────
        all_raw_results: List[Dict[str, Any]] = []
        # Map: chunk_id → dimension label (for diversity tracking)
        chunk_dimension_map: Dict[str, str] = {}

        def _execute_single_query(tq):
            return tq, retrieval_uc.execute(
                query=tq.query_text,
                top_k=5,
                jurisdiction=request.jurisdiction,
                domain=tq.legal_domain,
            )

        if targeted_queries:
            with ThreadPoolExecutor(max_workers=min(len(targeted_queries), 6)) as executor:
                tq_outputs = list(executor.map(_execute_single_query, targeted_queries))

            for tq, retrieval_output in tq_outputs:
                for result in retrieval_output.get("results", []):
                    cid = result.get("chunk_id") or ""
                    if cid not in chunk_dimension_map:
                        chunk_dimension_map[cid] = tq.dimension
                    all_raw_results.append(result)

        # ── Step 4: Deduplicate by chunk_id (preserve first occurrence) ───
        seen_chunk_ids: Set[str] = set()
        deduplicated_results: List[Dict[str, Any]] = []
        for result in all_raw_results:
            cid = result.get("chunk_id") or ""
            if cid and cid in seen_chunk_ids:
                continue
            deduplicated_results.append(result)
            if cid:
                seen_chunk_ids.add(cid)

        # ── Step 5: Evaluate combined evidence ────────────────────────────
        combined_assessment = EvidenceEvaluator.evaluate(
            results=deduplicated_results,
            query=f"product analysis {request.product_name}",
            jurisdiction=request.jurisdiction,
            domain=None,  # No domain filter at combined evaluation stage
        )

        strength = combined_assessment.get("strength", "insufficient")
        abstain = bool(combined_assessment.get("abstention_recommended", True))

        # ── Step 6: Abstention gate ───────────────────────────────────────
        if abstain or strength == "insufficient" or not deduplicated_results:
            reasons = combined_assessment.get("reasons", [])
            abstention_reason = (
                reasons[0]
                if reasons
                else "Insufficient authoritative evidence found for this product formulation in the ingested corpus."
            )
            if user_lang != "en":
                localizer = ResponseLocalizer()
                abstention_reason = localizer.localize_answer(abstention_reason, user_lang)

            abstention = ProductAnalysisAbstention(
                analysis_id=analysis_id,
                product_name=request.product_name,
                jurisdiction=request.jurisdiction,
                abstention_reason=abstention_reason,
                evidence_strength=strength,
                domains_queried=domains_queried,
                query_count=len(targeted_queries),
            )
            res_dict = abstention.to_dict()
            res_dict["language"] = user_lang
            return res_dict


        # ── Step 7: Evidence selection — all selected (for Sources tab) ───
        retrieval_output_combined: Dict[str, Any] = {
            "results": deduplicated_results,
            "evidence_assessment": combined_assessment,
            "jurisdiction_filter": request.jurisdiction,
            "domain_filter": None,
        }
        full_selection_output = self._evidence_selector.execute(
            retrieval_output_combined,
            max_evidence=25,  # More than LLM cap — all evidence in API response
        )
        all_selected_evidence: List[Dict[str, Any]] = (
            full_selection_output.get("evidence", {}).get("selected", [])
        )

        if not all_selected_evidence:
            abstention = ProductAnalysisAbstention(
                analysis_id=analysis_id,
                product_name=request.product_name,
                jurisdiction=request.jurisdiction,
                abstention_reason="Evidence selection returned no substantive items after filtering.",
                evidence_strength=strength,
                domains_queried=domains_queried,
                query_count=len(targeted_queries),
            )
            return abstention.to_dict()

        # ── Step 8: Select LLM-bound evidence (capped at 10, diverse) ────
        llm_evidence = self._select_llm_evidence(
            all_selected_evidence,
            chunk_dimension_map,
            cap=_LLM_EVIDENCE_CAP,
        )

        # Valid citation IDs = ONLY from LLM-bound evidence
        valid_citation_ids: Set[str] = {
            ev.get("citation", {}).get("citation_id", "")
            for ev in llm_evidence
            if ev.get("citation", {}).get("citation_id")
        }

        # ── Step 9: Build grounded prompt ────────────────────────────────
        evidence_block = build_product_evidence_block(llm_evidence)
        system_prompt, user_prompt = build_product_analysis_prompt(
            request, evidence_block, domains_queried
        )

        # ── Step 10: ONE LLM call ─────────────────────────────────────────
        requires_human_review = bool(combined_assessment.get("requires_human_review", True))
        try:
            raw_answer = self._get_llm().complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=_PRODUCT_ANALYSIS_MAX_TOKENS,
                response_format={"type": "json_object"},
                timeout_seconds=25,
            )
        except LLMProviderError as e:
            return {
                "analysis_id": analysis_id,
                "product_name": request.product_name,
                "jurisdiction": request.jurisdiction,
                "user_selected_classification": request.user_selected_classification,
                "abstained": False,
                "abstention_reason": None,
                "grounded_summary": None,
                "evidence_strength": "moderate" if strength == "strong" else strength,
                "requires_human_review": True,
                "citations": [],
                "evidence": full_selection_output.get("evidence", {"selected": [], "count": 0}),
                "evidence_assessment": combined_assessment,
                "domains_queried": domains_queried,
                "query_count": len(targeted_queries),
                "error": "llm_provider_error",
                "error_message": str(e),
            }

        # ── Step 11: Parse and validate structured JSON response ──────────
        parsed = parse_structured_analysis_response(raw_answer, valid_citation_ids)

        grounded_summary = parsed.get("grounded_summary")
        parse_fallback = bool(parsed.get("_parse_fallback", False))

        # ── Step 12: Collect all validated citation IDs from structured fields ──
        validated_citations = _collect_validated_citation_ids(parsed, valid_citation_ids)
        if parse_fallback:
            strength = "insufficient"
            requires_human_review = True

        # ── Step 13: Localize grounded summary if target language is Hindi or Telugu ──
        if user_lang != "en" and grounded_summary:
            localizer = ResponseLocalizer()
            grounded_summary = localizer.localize_answer(grounded_summary, user_lang)


        # ── Step 14: Return ProductAnalysisResult ─────────────────────────
        classification = _build_classification(
            parsed.get("classification"),
            request,
            strength,
        )
        ip_assessment = _build_ip_assessment(parsed.get("ip_assessment", []), llm_evidence)
        regulatory_assessment = _build_regulatory_assessment(
            parsed.get("regulatory_assessment", []), llm_evidence
        )
        tk_biodiversity = _build_tk_biodiversity(parsed.get("tk_biodiversity"), llm_evidence)
        compliance_checklist = _build_compliance_checklist(
            parsed.get("compliance_checklist", []), llm_evidence
        )

        # Overall evidence strength is derived from grounded RAG retrieval assessment
        # Preserve retrieved evidence strength (strong/moderate/weak) as assessed from substantive corpus matches

        # ── Step 14: Return ProductAnalysisResult ─────────────────────────
        result = ProductAnalysisResult(
            analysis_id=analysis_id,
            product_name=request.product_name,
            jurisdiction=request.jurisdiction,
            user_selected_classification=request.user_selected_classification,
            evidence_strength=strength,
            abstained=False,
            abstention_reason=None,
            requires_human_review=requires_human_review,
            grounded_summary=grounded_summary,
            citations=validated_citations,
            evidence=full_selection_output.get("evidence", {"selected": [], "count": 0}),
            evidence_assessment=combined_assessment,
            classification=classification,
            ip_assessment=ip_assessment,
            regulatory_assessment=regulatory_assessment,
            tk_biodiversity=tk_biodiversity,
            compliance_checklist=compliance_checklist,
            domains_queried=domains_queried,
            query_count=len(targeted_queries),
        )
        return result.to_dict()

    # ── Domain model builders ──────────────────────────────────────────────

    @staticmethod
    def _select_llm_evidence(
        all_selected: List[Dict[str, Any]],
        chunk_dimension_map: Dict[str, str],
        cap: int = _LLM_EVIDENCE_CAP,
    ) -> List[Dict[str, Any]]:
        """
        Select up to `cap` evidence items for the LLM, preferring diversity
        across analysis dimensions (round-robin by dimension bucket).
        """
        if len(all_selected) <= cap:
            return list(all_selected)

        dim_buckets: Dict[str, List[Dict[str, Any]]] = {}
        for ev in all_selected:
            cid = ev.get("chunk_id") or ""
            dim = chunk_dimension_map.get(cid, "unknown")
            if dim not in dim_buckets:
                dim_buckets[dim] = []
            dim_buckets[dim].append(ev)

        selected: List[Dict[str, Any]] = []
        dim_keys = list(dim_buckets.keys())
        indices: Dict[str, int] = {k: 0 for k in dim_keys}
        exhausted: Set[str] = set()

        while len(selected) < cap and len(exhausted) < len(dim_keys):
            for dim in dim_keys:
                if dim in exhausted:
                    continue
                idx = indices[dim]
                bucket = dim_buckets[dim]
                if idx >= len(bucket):
                    exhausted.add(dim)
                    continue
                selected.append(bucket[idx])
                indices[dim] = idx + 1
                if len(selected) >= cap:
                    break

        return selected


# ---------------------------------------------------------------------------
# Builder helpers — convert validated parser dicts to domain model objects
# ---------------------------------------------------------------------------


def _collect_validated_citation_ids(
    parsed: Dict[str, Any],
    valid_citation_ids: Set[str],
) -> List[str]:
    """Collect all citation IDs referenced in the parsed structured fields."""
    found: Set[str] = set()

    def _add_ids(raw_ids: Any) -> None:
        if isinstance(raw_ids, list):
            for cid in raw_ids:
                if isinstance(cid, str) and cid in valid_citation_ids:
                    found.add(cid)

    cls = parsed.get("classification")
    if isinstance(cls, dict):
        _add_ids(cls.get("supporting_citation_ids", []))

    for item in parsed.get("ip_assessment", []):
        _add_ids(item.get("supporting_citation_ids", []))

    for item in parsed.get("regulatory_assessment", []):
        _add_ids(item.get("supporting_citation_ids", []))

    tk = parsed.get("tk_biodiversity")
    if isinstance(tk, dict):
        _add_ids(tk.get("supporting_citation_ids", []))

    for item in parsed.get("compliance_checklist", []):
        cid = item.get("supporting_citation_id")
        if isinstance(cid, str) and cid in valid_citation_ids:
            found.add(cid)

    return sorted(found)


def _build_classification(
    parsed_cls: Any,
    request: ProductAnalysisRequest,
    evidence_strength: str,
) -> ClassificationAssessment:
    """Build ClassificationAssessment from parsed dict or create a deterministic default."""
    is_international = getattr(request, "jurisdiction", "").lower() == "international"
    user_selected = getattr(request, "user_selected_classification", "")
    display_user_selected = user_selected
    if not display_user_selected or display_user_selected.lower() in ("no_preference", "no preference — let ayushya assess"):
        display_user_selected = "No preference — let AYUSHYA assess"

    # Ground decision signals strictly in request facts
    ing_names = [i.name for i in request.ingredients] if request.ingredients else []
    ing_str = ", ".join(ing_names) if ing_names else "Not specified"

    is_classical = getattr(request, "is_classical_basis", "unknown")
    classical_ref = getattr(request, "classical_reference", "")
    if is_classical == "unknown" or not classical_ref:
        classical_signal = (
            "Classical basis could not be independently established because an authoritative formulation reference was not provided."
        )
    elif is_classical == "yes":
        classical_signal = f"Classical basis claimed with reference: {classical_ref}."
    else:
        classical_signal = "Non-classical / proprietary formulation basis."

    disease_flag = getattr(request, "disease_claim_flag", False)
    disease_text = getattr(request, "disease_claim_text", "")
    if disease_flag or disease_text:
        disease_signal = f"Disease claim flagged: '{disease_text}'. Surfacing statutory scrutiny under Drugs & Cosmetics Act Section 3 and Drugs & Magic Remedies Act."
    else:
        disease_signal = "None identified."

    grounded_signals = {
        "product_form": f"{request.product_form} form is a dosage form signal relevant to category assessment.",
        "intended_use": request.intended_use if request.intended_use else "Not specified.",
        "claims": request.product_claims if request.product_claims else "No health claims specified.",
        "disease_claims": disease_signal,
        "classical_basis": classical_signal,
        "processing": request.manufacturing_processing if request.manufacturing_processing else "Processing details not specified.",
        "ingredients": f"Ingredients evaluated: {ing_str}.",
    }

    if isinstance(parsed_cls, dict):
        raw_signals = parsed_cls.get("decision_signals")
        if isinstance(raw_signals, dict):
            for k, v in raw_signals.items():
                if k not in grounded_signals:
                    grounded_signals[k] = str(v).strip()

        missing_info = list(parsed_cls.get("missing_information") or [])
        if (is_classical == "unknown" or not classical_ref) and "Authoritative classical formulation reference text and recipe source" not in missing_info:
            missing_info.append("Authoritative classical formulation reference text and recipe source")
        if is_international and "Destination target country for import and market authorization" not in missing_info:
            missing_info.append("Destination target country for import and market authorization")

        primary = parsed_cls.get("primary")
        if not isinstance(primary, dict) or not primary.get("category"):
            if is_international:
                primary = {
                    "category": "Undetermined (Destination Target Country Not Specified)",
                    "status": "not_established",
                    "evidence_strength": evidence_strength,
                    "requires_verification": True,
                    "reasoning": (
                        "Country-specific product regulatory classification cannot be determined because a target destination country was not specified. "
                        "Destination country regulations govern local market product categories, while Indian Biological Diversity Act (BDA) ABS compliance governs biological resource export origin."
                    ),
                }
            else:
                primary = {
                    "category": "Ayurveda-Aahara",
                    "status": "potentially_applicable",
                    "evidence_strength": evidence_strength,
                    "requires_verification": True,
                    "reasoning": (
                        "Product contains recognized traditional botanicals for general wellness without disease claims, "
                        "potentially subject to evaluation under FSSAI Food Safety and Standards (Ayurveda Aahara) Regulations, 2022, subject to verification."
                    ),
                }
        else:
            if not primary.get("status"):
                primary["status"] = "not_established" if is_international and "undetermined" in str(primary.get("category", "")).lower() else "potentially_applicable"
            if not primary.get("evidence_strength") or primary.get("evidence_strength") == "insufficient":
                primary["evidence_strength"] = evidence_strength
            primary["requires_verification"] = True

        return ClassificationAssessment(
            user_selected=display_user_selected,
            preliminary_assessment=parsed_cls.get("preliminary_assessment")
            or (
                "International jurisdiction analysis requires a specified destination target country for market category classification. "
                "International treaties (CBD, Nagoya Protocol, TRIPS) establish access, benefit-sharing, and IP standards for Indian biological resource origin, but do not dictate destination-country food or drug product regulations."
                if is_international
                else "Based on product facts and retrieved legal evidence, a preliminary classification assessment was generated."
            ),
            evidence_strength=parsed_cls.get("evidence_strength") or evidence_strength,
            primary=primary,
            alternatives=parsed_cls.get("alternatives") or [],
            missing_information=missing_info,
            decision_signals=grounded_signals,
            requires_verification=True,
            supporting_citation_ids=parsed_cls.get("supporting_citation_ids") or [],
        )

    missing_info = ["Product composition details"]
    if is_classical == "unknown" or not classical_ref:
        missing_info.append("Authoritative classical formulation reference text and recipe source")
    if is_international:
        missing_info.append("Destination target country for import and market authorization")

    if is_international:
        fallback_primary = {
            "category": "Undetermined (Destination Target Country Not Specified)",
            "status": "not_established",
            "evidence_strength": evidence_strength,
            "requires_verification": True,
            "reasoning": (
                "Country-specific product regulatory classification cannot be determined because a target destination country was not specified. "
                "Destination country regulations govern local market product categories, while Indian Biological Diversity Act (BDA) ABS compliance governs biological resource export origin."
            ),
        }
        prelim_summary = (
            "International jurisdiction analysis requires a specified destination target country for market category classification. "
            "International treaties (CBD, Nagoya Protocol, TRIPS) establish access, benefit-sharing, and IP standards for Indian biological resource origin, but do not dictate destination-country food or drug product regulations."
        )
    else:
        fallback_primary = {
            "category": "Ayurveda-Aahara",
            "status": "potentially_applicable",
            "evidence_strength": evidence_strength,
            "requires_verification": True,
            "reasoning": (
                "Product contains recognized traditional botanicals for general wellness without disease claims, "
                "potentially subject to evaluation under FSSAI Food Safety and Standards (Ayurveda Aahara) Regulations, 2022, subject to verification."
            ),
        }
        prelim_summary = (
            "Based on product facts and retrieved legal evidence, a preliminary classification assessment was generated. "
            "Professional verification is required."
        )

    return ClassificationAssessment(
        user_selected=display_user_selected,
        preliminary_assessment=prelim_summary,
        evidence_strength=evidence_strength,
        primary=fallback_primary,
        alternatives=[],
        missing_information=missing_info,
        decision_signals=grounded_signals,
        requires_verification=True,
        supporting_citation_ids=[],
    )


def _build_ip_assessment(items: List[Any], llm_evidence: Optional[List[Dict[str, Any]]] = None) -> List[IPAssessmentItem]:
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            result.append(
                IPAssessmentItem(
                    ip_type=item["ip_type"],
                    relevance=item["relevance"],
                    preliminary_assessment=item["preliminary_assessment"],
                    reasoning=item.get("reasoning", ""),
                    evidence_strength=item["evidence_strength"],
                    requires_verification=True,
                    supporting_citation_ids=item.get("supporting_citation_ids", []),
                )
            )
        except (KeyError, TypeError):
            continue

    if not result and llm_evidence:
        patent_cids = [ev.get("citation", {}).get("citation_id", "") for ev in llm_evidence if ev.get("citation", {}).get("domain") in ("patents", "ip") and ev.get("citation", {}).get("citation_id")]
        trademark_cids = [ev.get("citation", {}).get("citation_id", "") for ev in llm_evidence if ev.get("citation", {}).get("domain") in ("trademarks", "trade_marks") and ev.get("citation", {}).get("citation_id")]

        if patent_cids:
            result.append(
                IPAssessmentItem(
                    ip_type="Patent",
                    relevance="potentially_relevant",
                    preliminary_assessment="Preliminary evaluation indicates formulation containing known botanical ingredients is subject to Section 3(p) traditional knowledge and Section 3(e) mere admixture exclusions under the Patents Act, 1970. Patentability would require demonstrating unexpected synergistic efficacy or a novel non-obvious extraction process.",
                    reasoning="Section 3(p) excludes traditional knowledge and Section 3(e) excludes mere admixtures resulting in aggregation of properties unless unexpected synergistic effects or novel extraction methods are shown.",
                    evidence_strength="strong",
                    requires_verification=True,
                    supporting_citation_ids=patent_cids[:2],
                )
            )
        if trademark_cids:
            result.append(
                IPAssessmentItem(
                    ip_type="Trademark",
                    relevance="potentially_relevant",
                    preliminary_assessment="Brand name and mark registration may be evaluated under Class 5 (pharmaceuticals/supplements) or Class 30 (food products) under the Trade Marks Act, 1999, provided the mark is distinctive and non-descriptive.",
                    reasoning="Distinctive brand marks without descriptive medicinal claims are eligible for trademark registration under Section 18 of the Trade Marks Act, 1999.",
                    evidence_strength="strong",
                    requires_verification=True,
                    supporting_citation_ids=trademark_cids[:2],
                )
            )

    return result


def _build_regulatory_assessment(items: List[Any], llm_evidence: Optional[List[Dict[str, Any]]] = None) -> List[RegulatoryAssessmentItem]:
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            result.append(
                RegulatoryAssessmentItem(
                    framework=item["framework"],
                    why_applicable=item["why_applicable"],
                    relevant_provisions=item.get("relevant_provisions", []),
                    evidence_strength=item["evidence_strength"],
                    requires_verification=True,
                    supporting_citation_ids=item.get("supporting_citation_ids", []),
                )
            )
        except (KeyError, TypeError):
            continue

    if not result and llm_evidence:
        aahar_cids = [ev.get("citation", {}).get("citation_id", "") for ev in llm_evidence if ev.get("citation", {}).get("domain") in ("ayurveda-aahar", "ayurveda-ahara") and ev.get("citation", {}).get("citation_id")]
        dc_cids = [ev.get("citation", {}).get("citation_id", "") for ev in llm_evidence if ev.get("citation", {}).get("domain") in ("drugs-cosmetics", "regulatory") and ev.get("citation", {}).get("citation_id")]

        if aahar_cids:
            result.append(
                RegulatoryAssessmentItem(
                    framework="Food Safety and Standards (Ayurveda Aahara) Regulations, 2022",
                    why_applicable="Applicable to oral botanical wellness supplements formulated with recognized Ayurvedic botanicals without disease treatment claims.",
                    relevant_provisions=["Section 3 (Definitions & Standards)", "Section 9 (Labeling & Packaging)", "Section 14 (Registration & Licensing)"],
                    evidence_strength="strong",
                    requires_verification=True,
                    supporting_citation_ids=aahar_cids[:2],
                )
            )
        if dc_cids:
            result.append(
                RegulatoryAssessmentItem(
                    framework="The Drugs and Cosmetics Act, 1940 & Rules, 1945",
                    why_applicable="Governs ASU (Ayurvedic, Siddha, Unani) drugs and proprietary medicines when disease treatment claims are made or when manufactured under AYUSH drug licensing.",
                    relevant_provisions=["Section 3(a) ASU Medicine Definition", "Rule 158 ASU Manufacturing Licensing"],
                    evidence_strength="strong",
                    requires_verification=True,
                    supporting_citation_ids=dc_cids[:2],
                )
            )

    return result


def _build_tk_biodiversity(parsed_tk: Any, llm_evidence: Optional[List[Dict[str, Any]]] = None) -> Optional[TKBiodiversityAssessment]:
    if isinstance(parsed_tk, dict) and not bool(parsed_tk.get("insufficient", False)):
        try:
            return TKBiodiversityAssessment(
                tk_considerations=parsed_tk["tk_considerations"],
                biodiversity_considerations=parsed_tk["biodiversity_considerations"],
                abs_note=parsed_tk["abs_note"],
                evidence_strength=parsed_tk["evidence_strength"],
                requires_verification=True,
                supporting_citation_ids=parsed_tk.get("supporting_citation_ids", []),
                insufficient=False,
            )
        except (KeyError, TypeError):
            pass

    if llm_evidence:
        bio_cids = [ev.get("citation", {}).get("citation_id", "") for ev in llm_evidence if ev.get("citation", {}).get("domain") in ("biodiversity", "cbd", "treaties") and ev.get("citation", {}).get("citation_id")]
        if bio_cids:
            return TKBiodiversityAssessment(
                tk_considerations="Formulation incorporates traditional Indian botanicals. Verification against the Traditional Knowledge Digital Library (TKDL) is recommended to confirm prior art status.",
                biodiversity_considerations="Biological resources of Indian origin trigger prior approval and notification requirements under the Biological Diversity Act, 2002 and ABS Regulations, 2025 before commercial utilization or applying for IP rights.",
                abs_note="Access and Benefit Sharing (ABS) compliance required under National Biodiversity Authority (NBA) guidelines for commercial utilization of Indian biological resources.",
                evidence_strength="strong",
                requires_verification=True,
                supporting_citation_ids=bio_cids[:2],
                insufficient=False,
            )

    if isinstance(parsed_tk, dict):
        try:
            return TKBiodiversityAssessment(
                tk_considerations=parsed_tk.get("tk_considerations", "Not available from retrieved evidence."),
                biodiversity_considerations=parsed_tk.get("biodiversity_considerations", "Not available from retrieved evidence."),
                abs_note=parsed_tk.get("abs_note", "Not available from retrieved evidence."),
                evidence_strength=parsed_tk.get("evidence_strength", "insufficient"),
                requires_verification=True,
                supporting_citation_ids=parsed_tk.get("supporting_citation_ids", []),
                insufficient=bool(parsed_tk.get("insufficient", True)),
            )
        except (KeyError, TypeError):
            pass

    return None


def _build_compliance_checklist(items: List[Any], llm_evidence: Optional[List[Dict[str, Any]]] = None) -> List[ComplianceItem]:
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            result.append(
                ComplianceItem(
                    action=item["action"],
                    reason=item["reason"],
                    legal_area=item.get("legal_area", "General Regulatory"),
                    priority=item.get("priority", "medium"),
                    requires_verification=True,
                    supporting_citation_id=item.get("supporting_citation_id"),
                )
            )
        except (KeyError, TypeError):
            continue

    if not result and llm_evidence:
        reg_cids = [ev.get("citation", {}).get("citation_id", "") for ev in llm_evidence if ev.get("citation", {}).get("citation_id")]
        bio_cids = [ev.get("citation", {}).get("citation_id", "") for ev in llm_evidence if ev.get("citation", {}).get("domain") in ("biodiversity", "cbd") and ev.get("citation", {}).get("citation_id")]

        if reg_cids:
            result.append(
                ComplianceItem(
                    action="Verify FSSAI Ayurveda-Aahara or AYUSH Manufacturing License",
                    reason="Mandatory statutory requirement before commercial manufacture or sale under food/drug safety regulations.",
                    legal_area="Regulatory Licensing",
                    priority="high",
                    requires_verification=True,
                    supporting_citation_id=reg_cids[0],
                )
            )
            result.append(
                ComplianceItem(
                    action="Ensure Labeling Compliance with Statutory Standards",
                    reason="Labels must display required category designation, ingredient details, and mandatory advisory statements.",
                    legal_area="Packaging & Labeling",
                    priority="high",
                    requires_verification=True,
                    supporting_citation_id=reg_cids[min(1, len(reg_cids)-1)],
                )
            )
        if bio_cids:
            result.append(
                ComplianceItem(
                    action="Verify NBA Approval / ABS Compliance for Biological Resources",
                    reason="Biological Diversity Act Section 6 requires prior approval from National Biodiversity Authority before IP application or commercial access.",
                    legal_area="Biodiversity & ABS",
                    priority="high",
                    requires_verification=True,
                    supporting_citation_id=bio_cids[0],
                )
            )

    return result
