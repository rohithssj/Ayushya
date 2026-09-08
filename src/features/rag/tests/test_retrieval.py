import json
import os
import tempfile
import unittest

from src.features.rag.infrastructure.lexical_retriever import LexicalRetriever


class LexicalRetrieverTests(unittest.TestCase):
    def test_returns_ranked_metadata_with_scores(self):
        chunks = [
            {
                "chunk_id": "test_1",
                "title": "TEST_ONLY Patents Act",
                "jurisdiction": "India",
                "domain": "patents",
                "section": "Section 3",
                "section_title": "What are not inventions",
                "text": "Traditional knowledge is not patentable.",
                "page_start": 11,
                "page_end": 12,
            },
            {
                "chunk_id": "test_2",
                "title": "TEST_ONLY Trademark Act",
                "jurisdiction": "India",
                "domain": "trademarks",
                "section": "Section 9",
                "section_title": "Absolute grounds",
                "text": "A trademark may be refused.",
                "page_start": 4,
                "page_end": 4,
            },
        ]
        retriever = LexicalRetriever(".", chunks=chunks)

        results = retriever.search("traditional knowledge patent", top_k=1, domain="patents")

        self.assertEqual(len(results), 1)
        result = results[0].to_dict()
        self.assertEqual(result["chunk_id"], "test_1")
        self.assertGreater(result["relevance_score"], 0)
        self.assertGreaterEqual(result["similarity_score"], 0)
        self.assertLessEqual(result["similarity_score"], 1)
        self.assertIn("section", result)

    def test_rejects_empty_query(self):
        retriever = LexicalRetriever(".", chunks=[])
        with self.assertRaises(ValueError):
            retriever.search("   ")


if __name__ == "__main__":
    unittest.main()