import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.features.rag.infrastructure.embedding_retriever import EmbeddingRetriever
from src.features.rag.infrastructure.embedding_store import EmbeddingStore


class EmbeddingRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_dir = Path(self.temp_dir.name) / "store"
        self.chunks = [
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

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_store_round_trip_preserves_metadata(self):
        vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        store = EmbeddingStore(str(self.store_dir))
        store.save(vectors, self.chunks, "TEST_ONLY-model")

        loaded_vectors, loaded_chunks, model_name = store.load()

        np.testing.assert_array_equal(loaded_vectors, vectors)
        self.assertEqual(loaded_chunks, self.chunks)
        self.assertEqual(model_name, "TEST_ONLY-model")

    def test_retriever_filters_and_returns_similarity(self):
        vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        EmbeddingStore(str(self.store_dir)).save(vectors, self.chunks, "TEST_ONLY-model")
        retriever = EmbeddingRetriever(str(self.store_dir))
        retriever._encode_query = lambda query: np.array([1.0, 0.0], dtype=np.float32)

        results = retriever.search("patent", top_k=1, jurisdiction="India", domain="patents")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk["chunk_id"], "test_1")
        self.assertAlmostEqual(results[0].similarity_score, 1.0)

    def test_rejects_empty_query(self):
        vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        EmbeddingStore(str(self.store_dir)).save(vectors, self.chunks, "TEST_ONLY-model")
        retriever = EmbeddingRetriever(str(self.store_dir))

        with self.assertRaises(ValueError):
            retriever.search("   ")

    def test_excludes_toc_only_chunks_from_results(self):
        toc_chunk = dict(self.chunks[0])
        toc_chunk["chunk_id"] = "toc"
        toc_chunk["text"] = "Introduction................................................................ 1"
        vectors = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]], dtype=np.float32)
        EmbeddingStore(str(self.store_dir)).save(vectors, self.chunks + [toc_chunk], "TEST_ONLY-model")
        retriever = EmbeddingRetriever(str(self.store_dir))
        retriever._encode_query = lambda query: np.array([1.0, 0.0], dtype=np.float32)

        results = retriever.search("introduction", top_k=3)

        self.assertNotIn("toc", [result.chunk["chunk_id"] for result in results])


if __name__ == "__main__":
    unittest.main()