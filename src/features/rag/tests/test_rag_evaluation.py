"""
Phase 9 — RAG Evaluation Suite Unit Tests (Deterministic).

Tests RAGEvaluator metrics and runs full evaluation across the 18 dataset cases
using a deterministic mocked LLM provider.
"""

import os
import unittest
from unittest.mock import MagicMock
from typing import Any, Dict, List

from src.features.rag.domain.rag_evaluator import RAGEvaluator, TestCaseResult
from src.features.rag.application.run_rag_evaluation_use_case import RunRAGEvaluationUseCase


class MockLLMProvider:
    """Deterministic mock LLM provider for evaluation suite tests."""
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # Extract citation ID from user prompt if available
        import re
        cids = re.findall(r"citation_id:\s*(cit_[a-f0-9]+)", user_prompt)
        if cids:
            return (
                f"Based on the authoritative legal evidence ({cids[0]}), "
                "the relevant statutory requirements and provisions are clearly outlined. "
                "Note: Please consult a qualified legal professional for binding advice."
            )
        return (
            "Based on the provided evidence, the legal requirements are clearly established. "
            "Note: Please consult a qualified legal professional for binding advice."
        )


class TestRAGEvaluatorMetrics(unittest.TestCase):

    def test_evaluator_passes_valid_case(self):
        case = {
            "id": "TEST_001",
            "category": "Patents",
            "query": "Can simple mixtures be patented?",
            "expected_jurisdiction": "India",
            "expected_domain": "patents",
            "should_have_sufficient_evidence": True,
            "expected_abstention": False,
            "expected_keywords": ["mixture", "patent"],
        }
        output = {
            "request_id": "req_001",
            "query": case["query"],
            "answer": "Simple mixtures are not patentable (cit_123). Note: consult counsel.",
            "abstained": False,
            "abstention_reason": None,
            "evidence_strength": "strong",
            "requires_human_review": False,
            "citations": ["cit_123"],
            "evidence": {
                "selected": [
                    {
                        "text": "A substance obtained by mere mixture is non-patentable.",
                        "citation": {
                            "citation_id": "cit_123",
                            "title": "The Patents Act, 1970",
                            "jurisdiction": "india",
                            "source_url": None,
                        },
                    }
                ],
                "count": 1,
            },
            "evidence_assessment": {
                "strength": "strong",
                "abstention_recommended": False,
                "requires_human_review": False,
            },
        }

        res = RAGEvaluator.evaluate_case(case, output)
        self.assertTrue(res.passed)
        self.assertTrue(res.retrieval_relevance.passed)
        self.assertTrue(res.evidence_quality.passed)
        self.assertTrue(res.citation_correctness.passed)
        self.assertTrue(res.groundedness.passed)
        self.assertTrue(res.abstention_safety.passed)
        self.assertTrue(res.jurisdiction_alignment.passed)

    def test_evaluator_detects_cross_jurisdiction_leakage(self):
        case = {
            "id": "TEST_002",
            "category": "Patents",
            "query": "Indian patent inquiry",
            "expected_jurisdiction": "India",
            "should_have_sufficient_evidence": True,
            "expected_abstention": False,
            "expected_keywords": [],
        }
        output = {
            "request_id": "req_002",
            "query": case["query"],
            "answer": "TRIPS provisions apply (cit_international).",
            "abstained": False,
            "citations": ["cit_international"],
            "evidence": {
                "selected": [
                    {
                        "text": "International treaty provision.",
                        "citation": {
                            "citation_id": "cit_international",
                            "title": "TRIPS Agreement",
                            "jurisdiction": "international",  # Leaked!
                        },
                    }
                ],
                "count": 1,
            },
            "evidence_assessment": {"strength": "strong", "abstention_recommended": False},
        }

        res = RAGEvaluator.evaluate_case(case, output)
        self.assertFalse(res.passed)
        self.assertFalse(res.jurisdiction_alignment.passed)
        self.assertIn("CROSS-JURISDICTION LEAKAGE", res.jurisdiction_alignment.details)

    def test_evaluator_detects_hallucinated_citation(self):
        case = {
            "id": "TEST_003",
            "category": "Patents",
            "query": "Patent inquiry",
            "expected_jurisdiction": "India",
            "should_have_sufficient_evidence": True,
            "expected_abstention": False,
            "expected_keywords": [],
        }
        output = {
            "request_id": "req_003",
            "query": case["query"],
            "answer": "Answer citing cit_fake.",
            "abstained": False,
            "citations": ["cit_fake"],  # Not in selected evidence!
            "evidence": {
                "selected": [
                    {
                        "text": "Legal text.",
                        "citation": {
                            "citation_id": "cit_real",
                            "title": "The Patents Act",
                            "jurisdiction": "india",
                        },
                    }
                ],
                "count": 1,
            },
            "evidence_assessment": {"strength": "strong", "abstention_recommended": False},
        }

        res = RAGEvaluator.evaluate_case(case, output)
        self.assertFalse(res.passed)
        self.assertFalse(res.citation_correctness.passed)
        self.assertIn("Hallucinated citation ID", res.citation_correctness.details)

    def test_evaluator_verifies_abstention_safety_on_out_of_corpus(self):
        case = {
            "id": "TEST_004",
            "category": "Unsupported",
            "query": "Quantum space tax law",
            "expected_jurisdiction": "International",
            "should_have_sufficient_evidence": False,
            "expected_abstention": True,
            "expected_keywords": [],
        }
        output = {
            "request_id": "req_004",
            "query": case["query"],
            "answer": None,
            "abstained": True,
            "abstention_reason": "No evidence found.",
            "evidence_strength": "insufficient",
            "citations": [],
            "evidence": {"selected": [], "count": 0},
            "evidence_assessment": {"strength": "insufficient", "abstention_recommended": True},
        }

        res = RAGEvaluator.evaluate_case(case, output)
        self.assertTrue(res.passed)
        self.assertTrue(res.abstention_safety.passed)
        self.assertTrue(res.groundedness.passed)


class TestFullDatasetEvaluationSuite(unittest.TestCase):

    def test_dataset_runs_and_evaluates(self):
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = curr_dir
        while base_dir and os.path.basename(base_dir) != "Ayushya" and not os.path.exists(os.path.join(base_dir, "data")):
            parent = os.path.dirname(base_dir)
            if parent == base_dir:
                break
            base_dir = parent

        mock_llm = MockLLMProvider()
        use_case = RunRAGEvaluationUseCase(base_dir=base_dir, llm_provider=mock_llm)

        report = use_case.execute(top_k=5)

        self.assertEqual(report.total_cases, 18)
        self.assertGreaterEqual(report.total_cases, 15)
        # Ensure all cases produced a valid result record
        self.assertEqual(len(report.test_results), 18)
        self.assertIsInstance(report.pass_rate_pct, float)
        self.assertEqual(report.citation_failures, 0)
        self.assertEqual(report.grounding_failures, 0)


if __name__ == "__main__":
    unittest.main()
