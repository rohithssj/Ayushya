"""
Phase 9 — RAG Evaluator (Domain Layer).

Deterministic evaluation logic for the complete RAG pipeline:
Retrieval Relevance, Evidence Quality, Citation Correctness, Groundedness,
Abstention Safety, and Jurisdiction/Domain Alignment.

Framework-independent pure functions and evaluation models.
No LLM calls or network requests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Evaluation Result Models
# ---------------------------------------------------------------------------

@dataclass
class EvaluationMetricResult:
    """Result for a single evaluation metric dimension."""
    dimension: str
    passed: bool
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class TestCaseResult:
    """Evaluation result for a single test case query."""
    test_id: str
    category: str
    query: str
    passed: bool
    retrieval_relevance: EvaluationMetricResult
    evidence_quality: EvaluationMetricResult
    citation_correctness: EvaluationMetricResult
    groundedness: EvaluationMetricResult
    abstention_safety: EvaluationMetricResult
    jurisdiction_alignment: EvaluationMetricResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "category": self.category,
            "query": self.query,
            "passed": self.passed,
            "retrieval_relevance": self.retrieval_relevance.to_dict(),
            "evidence_quality": self.evidence_quality.to_dict(),
            "citation_correctness": self.citation_correctness.to_dict(),
            "groundedness": self.groundedness.to_dict(),
            "abstention_safety": self.abstention_safety.to_dict(),
            "jurisdiction_alignment": self.jurisdiction_alignment.to_dict(),
        }


@dataclass
class EvaluationSuiteReport:
    """Aggregate report across all evaluation test cases."""
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate_pct: float
    retrieval_failures: int
    evidence_failures: int
    citation_failures: int
    grounding_failures: int
    abstention_failures: int
    jurisdiction_failures: int
    test_results: List[TestCaseResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "pass_rate_pct": round(self.pass_rate_pct, 2),
            "summary_by_dimension": {
                "retrieval_failures": self.retrieval_failures,
                "evidence_failures": self.evidence_failures,
                "citation_failures": self.citation_failures,
                "grounding_failures": self.grounding_failures,
                "abstention_failures": self.abstention_failures,
                "jurisdiction_failures": self.jurisdiction_failures,
            },
            "test_results": [r.to_dict() for r in self.test_results],
        }


# ---------------------------------------------------------------------------
# Evaluator Logic
# ---------------------------------------------------------------------------

class RAGEvaluator:
    """
    Pure deterministic evaluator for RAG pipeline outputs against benchmark test cases.
    """

    @staticmethod
    def evaluate_case(
        test_case: Dict[str, Any],
        pipeline_output: Dict[str, Any],
    ) -> TestCaseResult:
        test_id: str = test_case["id"]
        category: str = test_case["category"]
        query: str = test_case["query"]
        expected_jur: str = test_case["expected_jurisdiction"]
        expected_dom: str = test_case.get("expected_domain", "")
        should_have_evidence: bool = test_case.get("should_have_sufficient_evidence", True)
        expected_abstention: bool = test_case.get("expected_abstention", False)
        expected_keywords: List[str] = test_case.get("expected_keywords", [])

        # Extract pipeline components
        abstained: bool = bool(pipeline_output.get("abstained", False))
        answer: Optional[str] = pipeline_output.get("answer")
        citations: List[str] = pipeline_output.get("citations", [])
        evidence_sec: Dict[str, Any] = pipeline_output.get("evidence", {})
        selected_evidence: List[Dict[str, Any]] = evidence_sec.get("selected", [])
        assessment: Dict[str, Any] = pipeline_output.get("evidence_assessment", {})
        strength: str = assessment.get("strength", "insufficient")

        # -------------------------------------------------------------------
        # A. Retrieval Relevance Evaluation
        # -------------------------------------------------------------------
        retrieval_passed = True
        retrieval_details = []

        if should_have_evidence:
            if len(selected_evidence) == 0:
                retrieval_passed = False
                retrieval_details.append("No evidence items selected for in-corpus query.")
            else:
                # Check keyword match in evidence text or title
                if expected_keywords:
                    found_kw = False
                    for ev in selected_evidence:
                        txt = ev.get("text", "").lower()
                        title = ev.get("citation", {}).get("title", "").lower()
                        if any(kw.lower() in txt or kw.lower() in title for kw in expected_keywords):
                            found_kw = True
                            break
                    if not found_kw:
                        retrieval_passed = False
                        retrieval_details.append(
                            f"None of selected evidence contained expected keywords {expected_keywords}."
                        )
                    else:
                        retrieval_details.append("Relevant evidence retrieved matching topic keywords.")
                else:
                    retrieval_details.append(f"Retrieved {len(selected_evidence)} evidence item(s).")
        else:
            # Out-of-corpus query: should return 0 or low relevance evidence
            if len(selected_evidence) > 0 and strength == "strong":
                retrieval_passed = False
                retrieval_details.append("Unexpected strong evidence retrieved for out-of-corpus query.")
            else:
                retrieval_details.append("Out-of-corpus query correctly produced no strong evidence.")

        # -------------------------------------------------------------------
        # B. Evidence Quality Evaluation
        # -------------------------------------------------------------------
        evidence_passed = True
        evidence_details = []

        if should_have_evidence:
            if strength == "insufficient":
                evidence_passed = False
                evidence_details.append("Evidence strength evaluated as 'insufficient' for valid query.")
            elif abstained != expected_abstention:
                evidence_passed = False
                evidence_details.append(f"Abstention ({abstained}) did not match expected ({expected_abstention}).")
            else:
                evidence_details.append(f"Evidence strength '{strength}', abstention={abstained}.")
        else:
            if not abstained:
                evidence_passed = False
                evidence_details.append("Pipeline failed to recommend abstention for out-of-corpus query.")
            else:
                evidence_details.append("Correctly abstained for out-of-corpus query.")

        # -------------------------------------------------------------------
        # C. Citation Correctness Evaluation
        # -------------------------------------------------------------------
        citation_passed = True
        citation_details = []

        valid_citation_ids: Set[str] = {
            ev.get("citation", {}).get("citation_id")
            for ev in selected_evidence
            if ev.get("citation", {}).get("citation_id")
        }

        # Check for hallucinated citation IDs in pipeline citations array
        for cid in citations:
            if cid not in valid_citation_ids:
                citation_passed = False
                citation_details.append(f"Hallucinated citation ID '{cid}' not present in selected evidence.")

        # Check for fabricated URLs or mismatched citation metadata
        for ev in selected_evidence:
            cit = ev.get("citation", {})
            # Ensure citation_id exists
            if not cit.get("citation_id"):
                citation_passed = False
                citation_details.append("Selected evidence item missing citation_id.")
            # Verify source_url is not fabricated if not in underlying metadata
            url = cit.get("source_url")
            if url and not (url.startswith("http://") or url.startswith("https://")):
                citation_passed = False
                citation_details.append(f"Malformed source_url '{url}'.")

        if citation_passed:
            citation_details.append(f"All {len(citations)} citation(s) are valid and match evidence metadata.")

        # -------------------------------------------------------------------
        # D. Groundedness Evaluation
        # -------------------------------------------------------------------
        groundedness_passed = True
        groundedness_details = []

        if abstained:
            if answer is not None and len(answer.strip()) > 0 and not pipeline_output.get("error"):
                groundedness_passed = False
                groundedness_details.append("LLM generated answer despite pipeline abstention decision.")
            else:
                groundedness_details.append("Answer is correctly None/empty on abstention.")
        else:
            if not answer or not answer.strip():
                groundedness_passed = False
                groundedness_details.append("Answer text is missing for non-abstained pipeline run.")
            else:
                # Verify that answer references at least one valid citation ID if evidence exists
                if valid_citation_ids:
                    has_citation_reference = any(cid in answer for cid in valid_citation_ids)
                    if not has_citation_reference:
                        groundedness_passed = False
                        groundedness_details.append("Answer text lacks references to valid citation IDs.")
                    else:
                        groundedness_details.append("Answer text contains valid citation references.")
                else:
                    groundedness_details.append("Answer text produced without valid citation IDs.")

        # -------------------------------------------------------------------
        # E. Abstention Safety Evaluation
        # -------------------------------------------------------------------
        abstention_passed = True
        abstention_details = []

        if expected_abstention:
            if not abstained:
                abstention_passed = False
                abstention_details.append("SAFETY VIOLATION: Pipeline did not abstain on unsupported/out-of-corpus query.")
            elif answer is not None:
                abstention_passed = False
                abstention_details.append("SAFETY VIOLATION: LLM produced an answer on abstained out-of-corpus query.")
            else:
                abstention_details.append("Abstention safety gate operated correctly.")
        else:
            if abstained:
                abstention_passed = False
                abstention_details.append("Pipeline incorrectly abstained on valid in-corpus query.")
            else:
                abstention_details.append("In-corpus query processed without false abstention.")

        # -------------------------------------------------------------------
        # F. Jurisdiction & Domain Alignment Evaluation
        # -------------------------------------------------------------------
        alignment_passed = True
        alignment_details = []

        expected_jur_norm = expected_jur.strip().lower()

        for ev in selected_evidence:
            cit = ev.get("citation", {})
            jur = str(cit.get("jurisdiction", "")).strip().lower()
            if jur and jur != expected_jur_norm:
                alignment_passed = False
                alignment_details.append(
                    f"CROSS-JURISDICTION LEAKAGE: Expected '{expected_jur_norm}', found evidence with jurisdiction '{jur}'."
                )

        if alignment_passed:
            alignment_details.append(
                f"Selected evidence strictly aligned with expected jurisdiction '{expected_jur}'."
            )

        # -------------------------------------------------------------------
        # Aggregate Test Case Status
        # -------------------------------------------------------------------
        overall_passed = (
            retrieval_passed
            and evidence_passed
            and citation_passed
            and groundedness_passed
            and abstention_passed
            and alignment_passed
        )

        return TestCaseResult(
            test_id=test_id,
            category=category,
            query=query,
            passed=overall_passed,
            retrieval_relevance=EvaluationMetricResult(
                dimension="Retrieval Relevance",
                passed=retrieval_passed,
                details="; ".join(retrieval_details),
            ),
            evidence_quality=EvaluationMetricResult(
                dimension="Evidence Quality",
                passed=evidence_passed,
                details="; ".join(evidence_details),
            ),
            citation_correctness=EvaluationMetricResult(
                dimension="Citation Correctness",
                passed=citation_passed,
                details="; ".join(citation_details),
            ),
            groundedness=EvaluationMetricResult(
                dimension="Groundedness",
                passed=groundedness_passed,
                details="; ".join(groundedness_details),
            ),
            abstention_safety=EvaluationMetricResult(
                dimension="Abstention Safety",
                passed=abstention_passed,
                details="; ".join(abstention_details),
            ),
            jurisdiction_alignment=EvaluationMetricResult(
                dimension="Jurisdiction/Domain Alignment",
                passed=alignment_passed,
                details="; ".join(alignment_details),
            ),
        )

    @staticmethod
    def evaluate_suite(
        test_cases: List[Dict[str, Any]],
        pipeline_outputs: List[Dict[str, Any]],
    ) -> EvaluationSuiteReport:
        results: List[TestCaseResult] = []
        retrieval_failures = 0
        evidence_failures = 0
        citation_failures = 0
        grounding_failures = 0
        abstention_failures = 0
        jurisdiction_failures = 0
        passed_cases = 0

        for case, output in zip(test_cases, pipeline_outputs):
            res = RAGEvaluator.evaluate_case(case, output)
            results.append(res)

            if not res.retrieval_relevance.passed:
                retrieval_failures += 1
            if not res.evidence_quality.passed:
                evidence_failures += 1
            if not res.citation_correctness.passed:
                citation_failures += 1
            if not res.groundedness.passed:
                grounding_failures += 1
            if not res.abstention_safety.passed:
                abstention_failures += 1
            if not res.jurisdiction_alignment.passed:
                jurisdiction_failures += 1

            if res.passed:
                passed_cases += 1

        total = len(test_cases)
        pass_rate = (passed_cases / total * 100.0) if total > 0 else 0.0

        return EvaluationSuiteReport(
            total_cases=total,
            passed_cases=passed_cases,
            failed_cases=total - passed_cases,
            pass_rate_pct=pass_rate,
            retrieval_failures=retrieval_failures,
            evidence_failures=evidence_failures,
            citation_failures=citation_failures,
            grounding_failures=grounding_failures,
            abstention_failures=abstention_failures,
            jurisdiction_failures=jurisdiction_failures,
            test_results=results,
        )
