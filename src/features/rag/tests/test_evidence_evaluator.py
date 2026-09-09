import unittest
from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
from src.features.rag.domain.hybrid_retrieval import HybridRetrievalResult


class TestEvidenceEvaluator(unittest.TestCase):
    """Synthetic unit tests for Phase 6 Evidence Confidence, Abstention, and Escalation."""

    def test_strong_evidence(self):
        chunk = {
            "chunk_id": "test_001",
            "document_id": "patents_act_1970",
            "title": "The Patents Act, 1970",
            "section": "Section 3",
            "jurisdiction": "India",
            "domain": "patents",
            "text": "The following are not inventions within the meaning of this Act, namely, a substance obtained by a mere admixture resulting only in the aggregation of the properties of the components thereof.",
        }
        item = HybridRetrievalResult(
            chunk=chunk,
            hybrid_score=0.0450,
            lexical_rank=1,
            semantic_rank=1,
            matched_terms=("patent", "admixture"),
        )
        res = EvidenceEvaluator.evaluate(
            results=[item],
            query="patentability of herbal formulation",
            jurisdiction="India",
            domain="patents",
        )

        self.assertEqual(res["strength"], "strong")
        self.assertFalse(res["abstention_recommended"])
        self.assertFalse(res["requires_human_review"])
        self.assertGreater(len(res["reasons"]), 0)

    def test_moderate_evidence(self):
        chunk = {
            "chunk_id": "test_002",
            "document_id": "patents_act_1970",
            "title": "The Patents Act, 1970",
            "section": "Section 83",
            "jurisdiction": "India",
            "domain": "patents",
            "text": "General principles applicable to working of patented inventions in India shall be given due weightage.",
        }
        item = HybridRetrievalResult(
            chunk=chunk,
            hybrid_score=0.0180,
            lexical_rank=10,
            semantic_rank=2,
            matched_terms=(),
        )
        res = EvidenceEvaluator.evaluate(
            results=[item],
            query="working of patents",
            jurisdiction="India",
            domain="patents",
        )

        self.assertEqual(res["strength"], "moderate")
        self.assertFalse(res["abstention_recommended"])
        self.assertFalse(res["requires_human_review"])

    def test_weak_evidence(self):
        chunk = {
            "chunk_id": "test_003",
            "document_id": "patents_act_1970",
            "jurisdiction": "India",
            "domain": "patents",
            "text": "General provisions relating to applications for patent.",
        }
        item = HybridRetrievalResult(
            chunk=chunk,
            hybrid_score=0.0110,
            lexical_rank=999,
            semantic_rank=18,
            matched_terms=(),
        )
        res = EvidenceEvaluator.evaluate(
            results=[item],
            query="patent procedure",
            jurisdiction="India",
            domain="patents",
        )

        self.assertEqual(res["strength"], "weak")
        self.assertTrue(res["abstention_recommended"])
        self.assertTrue(res["requires_human_review"])

    def test_insufficient_zero_results(self):
        res = EvidenceEvaluator.evaluate(
            results=[],
            query="nonexistent law",
            jurisdiction="India",
            domain="patents",
        )

        self.assertEqual(res["strength"], "insufficient")
        self.assertTrue(res["abstention_recommended"])
        self.assertTrue(res["requires_human_review"])

    def test_abstention_on_non_substantive_chunk(self):
        chunk = {
            "chunk_id": "test_toc",
            "document_id": "patents_act_1970",
            "title": "Index",
            "jurisdiction": "India",
            "domain": "patents",
            "text": "Contents ... 12",
        }
        item = HybridRetrievalResult(
            chunk=chunk,
            hybrid_score=0.0250,
            lexical_rank=1,
            semantic_rank=1,
            matched_terms=(),
        )
        res = EvidenceEvaluator.evaluate(
            results=[item],
            query="patent details",
            jurisdiction="India",
            domain="patents",
        )

        self.assertEqual(res["strength"], "insufficient")
        self.assertTrue(res["abstention_recommended"])
        self.assertTrue(res["requires_human_review"])

    def test_abstention_on_filter_mismatch(self):
        chunk = {
            "chunk_id": "test_mismatch",
            "document_id": "copyright_act_1957",
            "title": "Copyright Act",
            "jurisdiction": "India",
            "domain": "copyright",
            "text": "Copyright shall subsist throughout India in original literary works.",
        }
        item = HybridRetrievalResult(
            chunk=chunk,
            hybrid_score=0.0350,
            lexical_rank=1,
            semantic_rank=1,
            matched_terms=("copyright",),
        )
        res = EvidenceEvaluator.evaluate(
            results=[item],
            query="patentability",
            jurisdiction="India",
            domain="patents",  # Requested patents, but result is copyright
        )

        self.assertEqual(res["strength"], "insufficient")
        self.assertTrue(res["abstention_recommended"])
        self.assertTrue(res["requires_human_review"])


if __name__ == "__main__":
    unittest.main()
