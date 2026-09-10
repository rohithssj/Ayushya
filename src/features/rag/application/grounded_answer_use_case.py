"""
Phase 8 — Grounded Answer Use Case (Application Layer).

Orchestrates:
  HybridRetrievalUseCase
  → EvidenceEvaluator (already embedded in HybridRetrievalUseCase output)
  → EvidenceSelectionUseCase
  → Abstention gate (DO NOT call LLM if abstain=True or evidence insufficient)
  → OpenRouterProvider (infrastructure)
  → Citation validation
  → GroundedAnswer / AbstentionResponse

No retrieval logic, no HTTP, no domain models live here.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Set

from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase
from src.features.rag.application.evidence_selection_use_case import EvidenceSelectionUseCase
from src.features.rag.domain.grounded_answer import (
    GroundedAnswer,
    AbstentionResponse,
    build_evidence_block,
    build_grounding_prompt,
    extract_citation_ids,
)
from src.features.rag.infrastructure.openrouter_provider import (
    OpenRouterProvider,
    LLMProviderError,
)


class GroundedAnswerUseCase:
    """
    Executes the full grounded answer pipeline:

    1. Hybrid retrieval + evidence evaluation (HybridRetrievalUseCase)
    2. Evidence selection + citation construction (EvidenceSelectionUseCase)
    3. Abstention gate — if abstain=True or strength=insufficient → return AbstentionResponse
    4. Build grounding prompt from selected evidence only
    5. Call LLM via OpenRouterProvider
    6. Validate citation IDs in response against actual selected evidence
    7. Return GroundedAnswer

    The LLM never replaces retrieval, evidence evaluation, or citation construction.
    """

    def __init__(
        self,
        base_dir: str,
        retriever=None,
        llm_provider: Optional[OpenRouterProvider] = None,
    ) -> None:
        self._retrieval = HybridRetrievalUseCase(base_dir, retriever=retriever)
        self._evidence_selector = EvidenceSelectionUseCase()
        self._llm = llm_provider  # Injected for testing; created lazily for production

    def _get_llm(self) -> OpenRouterProvider:
        if self._llm is None:
            self._llm = OpenRouterProvider()
        return self._llm

    def execute(
        self,
        query: str,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
        top_k: int = 5,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full pipeline: retrieval → evidence → LLM gate → grounded answer.

        Returns a dict compatible with the /api/chat route.
        """
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:12]}"

        # ── Step 1: Retrieve + evaluate evidence ──
        retrieval_output = self._retrieval.execute(
            query=query,
            top_k=top_k,
            jurisdiction=jurisdiction,
            domain=domain,
        )

        # ── Step 2: Evidence selection + citation construction ──
        retrieval_output = self._evidence_selector.execute(retrieval_output)

        assessment: Dict[str, Any] = retrieval_output.get("evidence_assessment", {})
        strength: str = assessment.get("strength", "insufficient")
        abstain: bool = bool(assessment.get("abstention_recommended", True))
        requires_human_review: bool = bool(assessment.get("requires_human_review", True))
        selected_evidence: List[Dict[str, Any]] = retrieval_output.get("evidence", {}).get("selected", [])

        # ── Step 3: Abstention gate ──
        if abstain or strength == "insufficient" or not selected_evidence:
            reasons = assessment.get("reasons", [])
            abstention_reason = (
                reasons[0] if reasons
                else "Insufficient authoritative evidence found for this query."
            )
            resp = AbstentionResponse(
                request_id=request_id,
                query=query,
                evidence_strength=strength,
                requires_human_review=True,
                abstention_reason=abstention_reason,
            )
            result = resp.to_dict()
            result["evidence"] = retrieval_output.get("evidence", {"selected": [], "count": 0})
            result["evidence_assessment"] = assessment
            return result

        # ── Step 4: Build prompt from selected evidence only ──
        evidence_block = build_evidence_block(selected_evidence)
        system_prompt, user_prompt = build_grounding_prompt(query, evidence_block)

        # ── Step 5: Call LLM ──
        try:
            raw_answer = self._get_llm().complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except LLMProviderError as e:
            # Return a stable application-level error; never leak provider details
            return {
                "request_id": request_id,
                "query": query,
                "answer": None,
                "abstained": False,
                "abstention_reason": None,
                "evidence_strength": strength,
                "requires_human_review": True,
                "citations": [],
                "evidence": retrieval_output.get("evidence", {"selected": [], "count": 0}),
                "evidence_assessment": assessment,
                "error": "llm_provider_error",
                "error_message": str(e),
            }

        # ── Step 6: Citation validation ──
        valid_citation_ids: Set[str] = {
            ev.get("citation", {}).get("citation_id", "")
            for ev in selected_evidence
            if ev.get("citation", {}).get("citation_id")
        }
        validated_citations = extract_citation_ids(raw_answer, valid_citation_ids)

        # ── Step 7: Return GroundedAnswer ──
        grounded = GroundedAnswer(
            request_id=request_id,
            query=query,
            answer=raw_answer,
            abstained=False,
            abstention_reason=None,
            evidence_strength=strength,
            requires_human_review=requires_human_review,
            citations=validated_citations,
        )
        result = grounded.to_dict()
        result["evidence"] = retrieval_output.get("evidence", {"selected": [], "count": 0})
        result["evidence_assessment"] = assessment
        return result
