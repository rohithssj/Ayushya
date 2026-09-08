import re
from typing import Any, Dict, List, Optional

import numpy as np

from src.features.rag.domain.embedding_retrieval import EmbeddingRetrievalResult
from src.features.rag.infrastructure.embedding_store import EmbeddingStore


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
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                raise RuntimeError(
                    "sentence-transformers is required; install it before searching embeddings"
                ) from error
            self._model = SentenceTransformer(self.model_name)
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
        """Exclude extracted contents/heading-only records from evidence ranking."""

        text = str(chunk.get("text", ""))
        lines = text.splitlines()
        body = "\n".join(lines[1:]) if lines and lines[0].startswith("[") else text
        words = re.findall(r"[A-Za-z]{2,}", body)
        has_toc_dots = bool(re.search(r"(?:\.\.\.|…{2,})", body))
        has_legal_provision = bool(
            re.search(r"\b(?:shall|must|may|means|provided|prohibited|patent|approval|requirement)\b", body, re.IGNORECASE)
        )
        if len(words) < 4:
            return False
        if has_toc_dots and len(words) < 60 and not has_legal_provision:
            return False
        return True