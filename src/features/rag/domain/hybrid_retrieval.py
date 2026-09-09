from dataclasses import dataclass
from typing import Any, Dict, Tuple

@dataclass(frozen=True)
class HybridRetrievalResult:
    """A retrieved legal chunk with hybrid scoring details."""
    
    chunk: Dict[str, Any]
    hybrid_score: float
    lexical_rank: int
    semantic_rank: int
    matched_terms: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        result = dict(self.chunk)
        result["relevance_score"] = round(self.hybrid_score, 6)
        result["lexical_rank"] = self.lexical_rank
        result["semantic_rank"] = self.semantic_rank
        result["matched_terms"] = list(self.matched_terms)
        return result
