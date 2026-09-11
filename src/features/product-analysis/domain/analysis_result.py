"""
Product Analysis — Structured output result models.

Framework-independent. No HTTP, no LLM calls. No fabricated data.

All fields are populated strictly from retrieved evidence and deterministic
logic. No legal conclusions are stated here — only structured containers
for evidence-backed assessments labelled as preliminary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Sub-result models
# ---------------------------------------------------------------------------


@dataclass
class ClassificationAssessment:
    """
    Preliminary product classification assessment.

    user_selected: the classification submitted by the user (not legally verified).
    preliminary_assessment: AYUSHYA's evidence-based preliminary note.
    evidence_strength: strength of retrieved evidence supporting this assessment.
    requires_verification: always True — this is never an official determination.
    supporting_citation_ids: citation_ids from retrieved evidence that informed this.
    """

    user_selected: str
    preliminary_assessment: str
    evidence_strength: str
    requires_verification: bool = True
    supporting_citation_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_selected": self.user_selected,
            "preliminary_assessment": self.preliminary_assessment,
            "evidence_strength": self.evidence_strength,
            "requires_verification": self.requires_verification,
            "supporting_citation_ids": self.supporting_citation_ids,
        }


@dataclass
class IPAssessmentItem:
    """
    Preliminary IP protection assessment for one IP type.

    ip_type: Patent / Trademark / GI / Copyright / Design / Trade Secret
    relevance: 'potentially_relevant' | 'low_relevance' | 'insufficient_evidence'
    preliminary_assessment: brief text labelled as preliminary
    reasoning: evidence-based reasoning (not legal conclusions)
    evidence_strength: strong / moderate / weak / insufficient
    requires_verification: always True — this is never a legal determination.
    supporting_citation_ids: validated citation IDs from selected evidence
    """

    ip_type: str
    relevance: str
    preliminary_assessment: str
    reasoning: str
    evidence_strength: str
    requires_verification: bool = True
    supporting_citation_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip_type": self.ip_type,
            "relevance": self.relevance,
            "preliminary_assessment": self.preliminary_assessment,
            "reasoning": self.reasoning,
            "evidence_strength": self.evidence_strength,
            "requires_verification": self.requires_verification,
            "supporting_citation_ids": self.supporting_citation_ids,
        }


@dataclass
class RegulatoryAssessmentItem:
    """
    Preliminary regulatory framework assessment for one framework.

    framework: name of regulatory framework (e.g. "Drugs and Cosmetics Act, 1940")
    why_applicable: reason this framework may apply (based on product attributes)
    relevant_provisions: brief list of potentially relevant provisions from evidence
    evidence_strength: strong / moderate / weak / insufficient
    requires_verification: always True — this is never a regulatory determination.
    supporting_citation_ids: validated citation IDs
    """

    framework: str
    why_applicable: str
    relevant_provisions: List[str]
    evidence_strength: str
    requires_verification: bool = True
    supporting_citation_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework": self.framework,
            "why_applicable": self.why_applicable,
            "relevant_provisions": self.relevant_provisions,
            "evidence_strength": self.evidence_strength,
            "requires_verification": self.requires_verification,
            "supporting_citation_ids": self.supporting_citation_ids,
        }


@dataclass
class TKBiodiversityAssessment:
    """
    Traditional knowledge and biodiversity/ABS preliminary assessment.

    All fields are derived from retrieved evidence, never fabricated.
    """

    tk_considerations: str          # preliminary TK considerations from evidence
    biodiversity_considerations: str # preliminary biodiversity/ABS considerations
    abs_note: str                   # ABS note from evidence
    evidence_strength: str
    requires_verification: bool = True
    supporting_citation_ids: List[str] = field(default_factory=list)
    insufficient: bool = False      # True if evidence was insufficient for this dimension

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tk_considerations": self.tk_considerations,
            "biodiversity_considerations": self.biodiversity_considerations,
            "abs_note": self.abs_note,
            "evidence_strength": self.evidence_strength,
            "requires_verification": self.requires_verification,
            "supporting_citation_ids": self.supporting_citation_ids,
            "insufficient": self.insufficient,
        }


@dataclass
class ComplianceItem:
    """
    A single actionable compliance checklist item derived from retrieved evidence.

    All items must be traceable to evidence — never fabricated.
    """

    action: str
    reason: str
    legal_area: str
    priority: str   # 'high' | 'medium' | 'low'
    requires_verification: bool = True
    supporting_citation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "action": self.action,
            "reason": self.reason,
            "legal_area": self.legal_area,
            "priority": self.priority,
            "requires_verification": self.requires_verification,
        }
        if self.supporting_citation_id:
            result["supporting_citation_id"] = self.supporting_citation_id
        return result


# ---------------------------------------------------------------------------
# Top-level result
# ---------------------------------------------------------------------------


@dataclass
class ProductAnalysisResult:
    """
    Complete structured product formulation analysis result.

    Produced by ProductAnalysisUseCase after:
      multi-query retrieval → evidence evaluation → evidence selection
      → grounded LLM synthesis → citation validation.

    No field is fabricated. All assessments are explicitly preliminary.
    """

    analysis_id: str
    product_name: str
    jurisdiction: str
    user_selected_classification: str

    # Overall evidence quality
    evidence_strength: str
    abstained: bool
    abstention_reason: Optional[str]
    requires_human_review: bool

    # Grounded LLM narrative (one synthesis call)
    grounded_summary: Optional[str]

    # Validated citation IDs referenced in the LLM summary
    citations: List[str]

    # All selected evidence items (full set for Sources tab)
    evidence: Dict[str, Any]   # {selected: [...], count: int}

    # Evidence assessment from evaluator
    evidence_assessment: Dict[str, Any]

    # Structured assessments (populated from LLM output + evidence)
    classification: Optional[ClassificationAssessment] = None
    ip_assessment: List[IPAssessmentItem] = field(default_factory=list)
    regulatory_assessment: List[RegulatoryAssessmentItem] = field(default_factory=list)
    tk_biodiversity: Optional[TKBiodiversityAssessment] = None
    compliance_checklist: List[ComplianceItem] = field(default_factory=list)

    # Domains that were queried
    domains_queried: List[str] = field(default_factory=list)

    # Number of targeted queries run
    query_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "analysis_id": self.analysis_id,
            "product_name": self.product_name,
            "jurisdiction": self.jurisdiction,
            "user_selected_classification": self.user_selected_classification,
            "evidence_strength": self.evidence_strength,
            "abstained": self.abstained,
            "abstention_reason": self.abstention_reason,
            "requires_human_review": self.requires_human_review,
            "grounded_summary": self.grounded_summary,
            "citations": self.citations,
            "evidence": self.evidence,
            "evidence_assessment": self.evidence_assessment,
            "domains_queried": self.domains_queried,
            "query_count": self.query_count,
        }
        if self.classification is not None:
            result["classification"] = self.classification.to_dict()
        if self.ip_assessment:
            result["ip_assessment"] = [i.to_dict() for i in self.ip_assessment]
        if self.regulatory_assessment:
            result["regulatory_assessment"] = [r.to_dict() for r in self.regulatory_assessment]
        if self.tk_biodiversity is not None:
            result["tk_biodiversity"] = self.tk_biodiversity.to_dict()
        if self.compliance_checklist:
            result["compliance_checklist"] = [c.to_dict() for c in self.compliance_checklist]
        return result


@dataclass
class ProductAnalysisAbstention:
    """Returned when overall evidence is insufficient to run synthesis."""

    analysis_id: str
    product_name: str
    jurisdiction: str
    abstention_reason: str
    evidence_strength: str
    domains_queried: List[str]
    query_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "product_name": self.product_name,
            "jurisdiction": self.jurisdiction,
            "abstained": True,
            "abstention_reason": self.abstention_reason,
            "evidence_strength": self.evidence_strength,
            "grounded_summary": None,
            "citations": [],
            "evidence": {"selected": [], "count": 0},
            "evidence_assessment": {
                "strength": self.evidence_strength,
                "abstention_recommended": True,
                "requires_human_review": True,
                "reasons": [self.abstention_reason],
            },
            "requires_human_review": True,
            "domains_queried": self.domains_queried,
            "query_count": self.query_count,
        }
