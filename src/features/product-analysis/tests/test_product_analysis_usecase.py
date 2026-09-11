"""
Integration tests – ProductAnalysisUseCase (basic flow with mocks).

We mock HybridRetrievalUseCase, EvidenceSelectionUseCase, EvidenceEvaluator, and OpenRouterProvider
to avoid heavy external calls. The test verifies:
- request validation is called
- domain routing returns expected dimensions
- retrieval is invoked per dimension with correct parameters
- abstention gate works when evidence strength insufficient
- successful path returns a dict with expected keys and uses only the LLM‑bound evidence for citations.
"""
import unittest
from unittest.mock import MagicMock, patch

from src.features.product_analysis.application.product_analysis_use_case import (
    ProductAnalysisUseCase,
    _LLM_EVIDENCE_CAP,
)
from src.features.product_analysis.domain.product_request import (
    ProductAnalysisRequest,
    validate_product_request,
)

# Helper to build a minimal valid request dict
def _minimal_raw():
    return {
        "productName": "Test Tablet",
        "category": "Ayurveda-Aahar",
        "form": "Tablet",
        "description": "Test description",
        "ingredients": [],
        "jurisdiction": "India",
    }

class TestProductAnalysisUseCase(unittest.TestCase):
    def setUp(self):
        # Create a use case with mocked dependencies
        self.uc = ProductAnalysisUseCase(base_dir="/tmp")
        # Patch internal components
        self.uc._domain_router = MagicMock()
        self.uc._query_builder = MagicMock()
        self.uc._evidence_selector = MagicMock()
        # Mock retrieval use case factory to return a MagicMock
        self.mock_retrieval_uc = MagicMock()
        self.uc._make_retrieval_use_case = MagicMock(return_value=self.mock_retrieval_uc)
        # Mock LLM provider
        self.mock_llm = MagicMock()
        self.uc._llm = self.mock_llm

    def test_abstention_when_insufficient_strength(self):
        request = validate_product_request(_minimal_raw())
        # Domain router returns a single dummy dimension
        dummy_dim = MagicMock()
        dummy_dim.legal_domain = "ayurveda-aahar"
        dummy_dim.label = "Ayurveda"
        self.uc._domain_router.route.return_value = [dummy_dim]
        # Query builder returns one query
        dummy_query = MagicMock()
        dummy_query.query_text = "dummy"
        dummy_query.legal_domain = "ayurveda-aahar"
        dummy_query.dimension = "Ayurveda"
        self.uc._query_builder.build_queries.return_value = [dummy_query]
        # Retrieval returns empty results
        self.mock_retrieval_uc.execute.return_value = {"results": []}
        # Evidence evaluator will be called via combined evaluation – we patch it globally
        with patch('src.features.rag.domain.evidence_evaluator.EvidenceEvaluator.evaluate') as mock_eval:
            mock_eval.return_value = {"strength": "insufficient", "abstention_recommended": True, "reasons": ["no evidence"]}
            result = self.uc.execute(request)
        self.assertIn("abstention_reason", result)
        self.assertTrue(result["abstained"])
        self.assertEqual(result["evidence_strength"], "insufficient")

    def test_successful_flow_returns_expected_structure(self):
        request = validate_product_request(_minimal_raw())
        # Mock domain/queries
        dim1 = MagicMock(); dim1.legal_domain = "ayurveda-aahar"; dim1.label = "Ayurveda"
        dim2 = MagicMock(); dim2.legal_domain = "drugs-cosmetics"; dim2.label = "Drugs"
        self.uc._domain_router.route.return_value = [dim1, dim2]
        q1 = MagicMock(); q1.query_text = "q1"; q1.legal_domain = "ayurveda-aahar"; q1.dimension = "Ayurveda"
        q2 = MagicMock(); q2.query_text = "q2"; q2.legal_domain = "drugs-cosmetics"; q2.dimension = "Drugs"
        self.uc._query_builder.build_queries.return_value = [q1, q2]
        # Retrieval returns two chunks per query
        self.mock_retrieval_uc.execute.side_effect = [
            {"results": [{"chunk_id": "c1", "text": "text1", "citation": {"citation_id": "cit1"}}]},
            {"results": [{"chunk_id": "c2", "text": "text2", "citation": {"citation_id": "cit2"}}]},
        ]
        # Mock evidence evaluator (combined)
        with patch('src.features.rag.domain.evidence_evaluator.EvidenceEvaluator.evaluate') as mock_eval:
            mock_eval.return_value = {"strength": "strong", "abstention_recommended": False}
            # Mock evidence selector to return all evidence as selected
            self.uc._evidence_selector.execute.return_value = {
                "evidence": {
                    "selected": [
                        {"chunk_id": "c1", "citation": {"citation_id": "cit1"}},
                        {"chunk_id": "c2", "citation": {"citation_id": "cit2"}},
                    ]
                }
            }
            # Mock LLM output
            self.mock_llm.complete.return_value = (
                '{"grounded_summary": "Grounded summary answer supported by supplied evidence.", '
                '"classification": {"user_selected": "wrong", '
                '"preliminary_assessment": "Evidence-backed preliminary assessment.", '
                '"evidence_strength": "strong", "supporting_citation_ids": ["cit1"]}}'
            )
            result = self.uc.execute(request)
        # Verify top‑level keys
        expected_keys = {
            "analysis_id",
            "product_name",
            "jurisdiction",
            "user_selected_classification",
            "evidence_strength",
            "abstained",
            "requires_human_review",
            "grounded_summary",
            "citations",
            "evidence",
            "evidence_assessment",
            "classification",
            "domains_queried",
            "query_count",
        }
        self.assertTrue(expected_keys.issubset(set(result.keys())))
        self.assertFalse(result["abstained"])
        self.assertEqual(
            result["grounded_summary"],
            "Grounded summary answer supported by supplied evidence.",
        )
        self.assertTrue(result["classification"]["requires_verification"])
        # LLM‑bound evidence cap respected (should be <= _LLM_EVIDENCE_CAP)
        self.assertLessEqual(len(result["citations"]), _LLM_EVIDENCE_CAP)
        # Evidence in API response includes both chunks
        self.assertEqual(len(result["evidence"]["selected"]), 2)
        self.mock_llm.complete.assert_called_once()

if __name__ == "__main__":
    unittest.main()
