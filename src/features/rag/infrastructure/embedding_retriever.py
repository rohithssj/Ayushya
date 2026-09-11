from typing import Any, Dict, List, Optional

import numpy as np

from src.features.rag.domain.embedding_retrieval import EmbeddingRetrievalResult
from src.features.rag.domain.chunk_quality import is_retrievable_chunk
from src.features.rag.infrastructure.embedding_store import EmbeddingStore


_MODEL_CACHE: Dict[str, Any] = {}


class EmbeddingRetriever:
    """Semantic search over the local normalized embedding store."""

    def __init__(self, store_dir: str):
        self.store = EmbeddingStore(store_dir)
        self.vectors, self.chunks, self.model_name = self.store.load()
        self._model = None

    def search(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> List[EmbeddingRetrievalResult]:
        if not query.strip():
            raise ValueError("Query must contain at least one non-whitespace character")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        candidates = [
            (index, chunk)
            for index, chunk in enumerate(self.chunks)
            if self._matches_filter(chunk, jurisdiction, domain)
            and self._is_retrievable_chunk(chunk)
        ]
        if not candidates:
            return []

        query_vector = self._encode_query(query)
        candidate_indices = np.array([index for index, _ in candidates], dtype=np.int64)
        scores = self.vectors[candidate_indices] @ query_vector
        ranked = np.argsort(-scores, kind="stable")[:top_k]
        return [
            EmbeddingRetrievalResult(
                chunk=candidates[position][1],
                similarity_score=float(scores[position]),
            )
            for position in ranked
        ]

    def _encode_query(self, query: str) -> np.ndarray:
        if self.model_name in _MODEL_CACHE:
            self._model = _MODEL_CACHE[self.model_name]

        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                raise RuntimeError(
                    "sentence-transformers is required; install it before searching embeddings"
                ) from error

            try:
                # Try loading from local HuggingFace cache first to avoid remote Hub timeouts
                self._model = SentenceTransformer(self.model_name, local_files_only=True)
            except Exception:
                # Fall back to remote lookup/download if model weights are not cached locally yet
                self._model = SentenceTransformer(self.model_name, local_files_only=False)

            _MODEL_CACHE[self.model_name] = self._model

        vector = self._model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]
        return vector.astype(np.float32)

    @staticmethod
    def _matches_filter(
        chunk: Dict[str, Any],
        jurisdiction: Optional[str],
        domain: Optional[str],
    ) -> bool:
        if jurisdiction and chunk.get("jurisdiction", "").lower() != jurisdiction.lower():
            return False
        if domain and chunk.get("domain", "").lower() != domain.lower():
            return False
        return True

    @staticmethod
    def _is_retrievable_chunk(chunk: Dict[str, Any]) -> bool:
        return is_retrievable_chunk(chunk)