"""
Phase 7 — Evidence Selection Use Case (Application Layer).

Orchestrates: HybridRetrievalUseCase output → EvidenceEvaluator → EvidenceSelector.
No LLM. No new retrieval algorithm. No new embedding model.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.features.rag.domain.evidence_selector import select_evidence


class EvidenceSelectionUseCase:
    """
    Takes the output of HybridRetrievalUseCase (already containing evidence_assessment)
    and appends a structured 'evidence' section with selected chunks and citations.

    Usage:
        retrieval_output = HybridRetrievalUseCase(base_dir).execute(...)
        final = EvidenceSelectionUseCase().execute(retrieval_output)
    """

    def execute(
        self,
        retrieval_output: Dict[str, Any],
        max_evidence: int = 5,
    ) -> Dict[str, Any]:
        """
        Extends retrieval_output with an 'evidence' key.

        Args:
            retrieval_output: The dict returned by HybridRetrievalUseCase.execute().
            max_evidence:     Maximum number of evidence items to select.

        Returns:
            Same dict extended with 'evidence' section (mutated copy).
        """
        results: list = retrieval_output.get("results", [])
        assessment: Dict[str, Any] = retrieval_output.get("evidence_assessment", {
            "strength": "insufficient",
            "abstention_recommended": True,
            "requires_human_review": True,
            "reasons": [],
        })

        jurisdiction: Optional[str] = retrieval_output.get("jurisdiction_filter")
        domain: Optional[str] = retrieval_output.get("domain_filter")

        evidence = select_evidence(
            results=results,
            assessment=assessment,
            jurisdiction=jurisdiction,
            domain=domain,
            max_evidence=max_evidence,
        )

        output = dict(retrieval_output)
        output["evidence"] = evidence
        return output
