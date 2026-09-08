from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class RetrievalResult:
    """A retrieved legal chunk with a transparent lexical relevance score."""

    chunk: Dict[str, Any]
    score: float
    similarity: float
    matched_terms: tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        result = dict(self.chunk)
        result["relevance_score"] = round(self.score, 6)
        result["similarity_score"] = round(self.similarity, 6)
        result["matched_terms"] = list(self.matched_terms)
        return result