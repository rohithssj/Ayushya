from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class EmbeddingRetrievalResult:
    """A semantic retrieval result carrying the original legal chunk metadata."""

    chunk: Dict[str, Any]
    similarity_score: float

    def to_dict(self) -> Dict[str, Any]:
        result = dict(self.chunk)
        result["similarity_score"] = round(self.similarity_score, 6)
        return result


def embedding_text(chunk: Dict[str, Any]) -> str:
    """Build embedding input without repeating the document title in the text."""

    fields = (
        chunk.get("section", ""),
        chunk.get("section_title", ""),
        chunk.get("subsection", ""),
        _remove_context_prefix(str(chunk.get("text", ""))),
    )
    return " ".join(str(field) for field in fields if field).strip()


def _remove_context_prefix(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("[") and lines[0].endswith("]"):
        return "\n".join(lines[1:])
    return text