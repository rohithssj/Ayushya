import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from src.features.rag.domain.retrieval import RetrievalResult
from src.features.rag.domain.chunk_quality import is_retrievable_chunk


class LexicalRetriever:
    """Retrieve legal chunks using TF-IDF cosine similarity.

    This is a retrieval-only baseline for Phase 1. It deliberately does not
    create embeddings or call an external model.
    """

    token_re = re.compile(r"[a-z0-9]+")
    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "how", "in", "is", "it", "of", "on", "or", "the", "to", "under",
        "what", "which", "with", "can", "i", "my", "does", "do", "this",
    }

    def __init__(self, processed_dir: str, chunks: Optional[List[Dict[str, Any]]] = None):
        self.processed_dir = Path(processed_dir)
        self.chunks = chunks if chunks is not None else self._load_chunks()
        self.document_frequency = self._build_document_frequency(self.chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> List[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query must contain at least one non-whitespace character")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        query_terms = self._terms(query)
        query_vector = self._tfidf_vector(query_terms)
        results: List[RetrievalResult] = []
        for chunk in self.chunks:
            if not is_retrievable_chunk(chunk):
                continue
            if jurisdiction and chunk.get("jurisdiction", "").lower() != jurisdiction.lower():
                continue
            if domain and chunk.get("domain", "").lower() != domain.lower():
                continue

            searchable_text = self._searchable_text(chunk)
            chunk_terms = self._terms(searchable_text)
            similarity = self._cosine(query_vector, self._tfidf_vector(chunk_terms))
            score = similarity + self._field_match_boost(query_terms, chunk)
            if score <= 0:
                continue
            matched_terms = tuple(sorted(set(query_terms).intersection(chunk_terms)))
            results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=score,
                    similarity=similarity,
                    matched_terms=matched_terms,
                )
            )

        results.sort(key=lambda result: (-result.score, result.chunk.get("chunk_id", "")))
        return results[:top_k]

    def _load_chunks(self) -> List[Dict[str, Any]]:
        if not self.processed_dir.exists():
            raise FileNotFoundError(f"Processed chunk directory not found: {self.processed_dir}")
        chunks: List[Dict[str, Any]] = []
        for path in sorted(self.processed_dir.glob("*_chunks.json")):
            with path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
            if not isinstance(loaded, list):
                raise ValueError(f"Expected a JSON list in processed chunk file: {path}")
            chunks.extend(loaded)
        if not chunks:
            raise ValueError(f"No processed chunks found in: {self.processed_dir}")
        return chunks

    def _build_document_frequency(self, chunks: Iterable[Dict[str, Any]]) -> Counter[str]:
        frequency: Counter[str] = Counter()
        for chunk in chunks:
            frequency.update(set(self._terms(self._searchable_text(chunk))))
        return frequency

    def _tfidf_vector(self, terms: Iterable[str]) -> Dict[str, float]:
        counts = Counter(terms)
        document_count = max(len(self.chunks), 1)
        return {
            term: count * math.log((document_count + 1) / (self.document_frequency.get(term, 0) + 1))
            for term, count in counts.items()
        }

    @classmethod
    def _terms(cls, text: str) -> List[str]:
        return [term for term in cls.token_re.findall(text.lower()) if term not in cls.stop_words]

    @staticmethod
    def _searchable_text(chunk: Dict[str, Any]) -> str:
        fields = (
            chunk.get("title", ""),
            chunk.get("domain", ""),
            chunk.get("document_type", ""),
            chunk.get("chapter", ""),
            chunk.get("section", ""),
            chunk.get("section_title", ""),
            chunk.get("subsection", ""),
            chunk.get("text", ""),
        )
        return " ".join(str(field) for field in fields if field)

    @staticmethod
    def _cosine(left: Dict[str, float], right: Dict[str, float]) -> float:
        denominator = math.sqrt(sum(value * value for value in left.values())) * math.sqrt(
            sum(value * value for value in right.values())
        )
        if denominator == 0:
            return 0.0
        numerator = sum(value * right.get(term, 0.0) for term, value in left.items())
        return numerator / denominator

    @staticmethod
    def _field_match_boost(query_terms: List[str], chunk: Dict[str, Any]) -> float:
        query_set: Set[str] = set(query_terms)
        title_terms = set(LexicalRetriever._terms(str(chunk.get("title", ""))))
        section_terms = set(LexicalRetriever._terms(" ".join(
            str(chunk.get(field, "")) for field in ("section", "section_title", "subsection")
        )))
        domain_terms = set(LexicalRetriever._terms(str(chunk.get("domain", ""))))
        return (
            0.08 * len(query_set.intersection(title_terms))
            + 0.12 * len(query_set.intersection(section_terms))
            + 0.05 * len(query_set.intersection(domain_terms))
        )