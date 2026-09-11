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

# Maximum evidence items passed to the LLM (per approved plan Q2)
_LLM_EVIDENCE_CAP = 10
# Max tokens for the product analysis LLM call (per approved plan Q1)
_PRODUCT_ANALYSIS_MAX_TOKENS = 4000


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
    ) -> Dict[str, Any]:
        """
        Run the full product analysis pipeline.

        Returns a dict compatible with the extended AnalysisApiResponse.
        """
        if not analysis_id:
            analysis_id = f"analysis_{uuid.uuid4().hex[:12]}"

        retrieval_uc = self._make_retrieval_use_case()

        # ── Step 1: Route to relevant dimensions ──────────────────────────
        dimensions = self._domain_router.route(request)
        domains_queried = [d.legal_domain for d in dimensions]

        # ── Step 2: Build targeted queries per dimension ──────────────────
        targeted_queries = self._query_builder.build_queries(request, dimensions)

        # ── Step 3: Retrieve evidence for each targeted query ─────────────
        all_raw_results: List[Dict[str, Any]] = []
        # Map: chunk_id → dimension label (for diversity tracking)
        chunk_dimension_map: Dict[str, str] = {}

        for tq in targeted_queries:
            retrieval_output = retrieval_uc.execute(
                query=tq.query_text,
                top_k=5,
                jurisdiction=request.jurisdiction,
                domain=tq.legal_domain,
            )
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
            abstention = ProductAnalysisAbstention(
                analysis_id=analysis_id,
                product_name=request.product_name,
                jurisdiction=request.jurisdiction,
                abstention_reason=abstention_reason,
                evidence_strength=strength,
                domains_queried=domains_queried,
                query_count=len(targeted_queries),
            )
            return abstention.to_dict()

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
                timeout_seconds=45,
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
                "evidence_strength": strength,
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

        # ── Step 13: Build domain model objects from parsed data ───────────
        classification = _build_classification(
            parsed.get("classification"),
            request.user_selected_classification,
            strength,
        )
        ip_assessment = _build_ip_assessment(parsed.get("ip_assessment", []))
        regulatory_assessment = _build_regulatory_assessment(
            parsed.get("regulatory_assessment", [])
        )
        tk_biodiversity = _build_tk_biodiversity(parsed.get("tk_biodiversity"))
        compliance_checklist = _build_compliance_checklist(
            parsed.get("compliance_checklist", [])
        )

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
    user_selected: str,
    evidence_strength: str,
) -> ClassificationAssessment:
    """Build ClassificationAssessment from parsed dict or create a deterministic default."""
    if isinstance(parsed_cls, dict):
        return ClassificationAssessment(
            user_selected=user_selected,
            preliminary_assessment=parsed_cls.get("preliminary_assessment")
            or (
                "Insufficient evidence for a preliminary classification assessment. "
                "Professional verification is required."
            ),
            evidence_strength=parsed_cls.get("evidence_strength") or "insufficient",
            requires_verification=True,
            supporting_citation_ids=parsed_cls.get("supporting_citation_ids") or [],
        )

    # Fallback when classification field is missing or invalid
    return ClassificationAssessment(
        user_selected=user_selected,
        preliminary_assessment=(
            "Insufficient evidence for a preliminary classification assessment. "
            "Professional verification is required."
        ),
        evidence_strength="insufficient",
        requires_verification=True,
        supporting_citation_ids=[],
    )


def _build_ip_assessment(items: List[Any]) -> List[IPAssessmentItem]:
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
    return result


def _build_regulatory_assessment(items: List[Any]) -> List[RegulatoryAssessmentItem]:
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
    return result


def _build_tk_biodiversity(parsed_tk: Any) -> Optional[TKBiodiversityAssessment]:
    if not isinstance(parsed_tk, dict):
        return None
    try:
        return TKBiodiversityAssessment(
            tk_considerations=parsed_tk["tk_considerations"],
            biodiversity_considerations=parsed_tk["biodiversity_considerations"],
            abs_note=parsed_tk["abs_note"],
            evidence_strength=parsed_tk["evidence_strength"],
            requires_verification=True,
            supporting_citation_ids=parsed_tk.get("supporting_citation_ids", []),
            insufficient=bool(parsed_tk.get("insufficient", False)),
        )
    except (KeyError, TypeError):
        return None


def _build_compliance_checklist(items: List[Any]) -> List[ComplianceItem]:
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
    return result
