import unittest
from unittest.mock import MagicMock
from src.features.rag.domain.hybrid_retrieval import HybridRetrievalResult
from src.features.rag.domain.retrieval import RetrievalResult
from src.features.rag.domain.embedding_retrieval import EmbeddingRetrievalResult
from src.features.rag.infrastructure.hybrid_retriever import HybridRetriever

class TestHybridRetrieval(unittest.TestCase):
    def setUp(self):
        self.lexical_mock = MagicMock()
        self.embedding_mock = MagicMock()
        self.retriever = HybridRetriever(self.lexical_mock, self.embedding_mock)

    def test_search_combines_and_deduplicates(self):
        chunk_a = {"chunk_id": "A", "text": "Some substantive legal provision regarding patent."}
        chunk_b = {"chunk_id": "B", "text": "Another provision."}
        chunk_c = {"chunk_id": "C", "text": "Short."}

        self.lexical_mock.search.return_value = [
            RetrievalResult(chunk=chunk_a, score=0.8, similarity=0.5, matched_terms=("patent",)),
            RetrievalResult(chunk=chunk_b, score=0.5, similarity=0.3, matched_terms=()),
        ]
        
        self.embedding_mock.search.return_value = [
            EmbeddingRetrievalResult(chunk=chunk_b, similarity_score=0.9),
            EmbeddingRetrievalResult(chunk=chunk_c, similarity_score=0.8),
        ]

        results = self.retriever.search("patent query")
        
        # We expect 3 unique chunks
        self.assertEqual(len(results), 3)
        
        chunk_ids = [res.chunk["chunk_id"] for res in results]
        self.assertIn("A", chunk_ids)
        self.assertIn("B", chunk_ids)
        self.assertIn("C", chunk_ids)

    def test_text_quality_multiplier_penalizes_short(self):
        chunk = {"chunk_id": "1", "text": "Too short"}
        multiplier = HybridRetriever._text_quality_multiplier(chunk)
        self.assertEqual(multiplier, 0.5)

    def test_text_quality_multiplier_boosts_substantive(self):
        chunk = {"chunk_id": "1", "text": "This section shall apply to patents and provides that a patent is granted for an invention which is new and useful."}
        multiplier = HybridRetriever._text_quality_multiplier(chunk)
        self.assertGreater(multiplier, 1.0)

    def test_lexical_evidence_can_outrank_semantic_only_match(self):
        lexical_chunk = {
            "chunk_id": "lexical",
            "section": "Section 3",
            "section_title": "What are not inventions",
            "text": "An invention may be patentable only when it satisfies the statutory requirements.",
        }
        semantic_chunk = {
            "chunk_id": "semantic",
            "section": "Section 83",
            "section_title": "Working of patents",
            "text": "A patent shall be worked on a commercial scale in India.",
        }
        self.lexical_mock.search.return_value = [
            RetrievalResult(lexical_chunk, 0.8, 0.6, ("invention", "patentable")),
        ]
        self.embedding_mock.search.return_value = [
            EmbeddingRetrievalResult(semantic_chunk, 0.95),
            EmbeddingRetrievalResult(lexical_chunk, 0.7),
        ]

        results = self.retriever.search("What inventions are not patentable?")

        self.assertEqual(results[0].chunk["chunk_id"], "lexical")
        self.assertEqual(results[0].chunk["section"], "Section 3")

    def test_forwards_filters_and_preserves_chunk_metadata(self):
        chunk = {
            "chunk_id": "filtered",
            "title": "TEST_ONLY Act",
            "section": "Section 7",
            "jurisdiction": "India",
            "domain": "patents",
            "source_url": "https://example.test/fixture",
            "text": "A patent may be granted for an invention satisfying requirements.",
        }
        self.lexical_mock.search.return_value = [
            RetrievalResult(chunk, 0.5, 0.4, ("patent",)),
        ]
        self.embedding_mock.search.return_value = [
            EmbeddingRetrievalResult(chunk, 0.8),
        ]

        results = self.retriever.search(
            "patent requirements",
            jurisdiction="India",
            domain="patents",
        )

        self.lexical_mock.search.assert_called_once_with(
            query="patent requirements",
            top_k=20,
            jurisdiction="India",
            domain="patents",
        )
        self.embedding_mock.search.assert_called_once_with(
            query="patent requirements",
            top_k=20,
            jurisdiction="India",
            domain="patents",
        )
        self.assertEqual(results[0].chunk["source_url"], "https://example.test/fixture")
        
if __name__ == '__main__':
    unittest.main()
