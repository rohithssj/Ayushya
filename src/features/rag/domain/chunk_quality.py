import re
from typing import Any, Dict


_LEGAL_PROVISION_PATTERN = re.compile(
    r"\b(?:shall|must|may|means|provided|prohibited|patent|approval|requirement)\b",
    re.IGNORECASE,
)
_WORD_PATTERN = re.compile(r"[A-Za-z]{2,}")
_TOC_PATTERN = re.compile(r"(?:\.\.\.|…{2,})")


def chunk_body(chunk: Dict[str, Any]) -> str:
    """Return chunk text without the generated metadata prefix."""

    text = str(chunk.get("text", ""))
    lines = text.splitlines()
    if lines and lines[0].startswith("["):
        return "\n".join(lines[1:]).strip()
    return text.strip()


def is_retrievable_chunk(chunk: Dict[str, Any]) -> bool:
    """Keep chunks with enough substantive text to serve as evidence."""

    body = chunk_body(chunk)
    words = _WORD_PATTERN.findall(body)
    has_legal_provision = bool(_LEGAL_PROVISION_PATTERN.search(body))
    if len(words) < 4:
        return False
    if _TOC_PATTERN.search(body) and len(words) < 60 and not has_legal_provision:
        return False

    heading = " ".join(
        str(chunk.get(field, ""))
        for field in ("section", "section_title", "subsection")
        if chunk.get(field)
    ).strip()
    if (
        len(body.splitlines()) == 1
        and len(words) <= 12
        and not has_legal_provision
        and heading
        and body.rstrip(" .:") in heading
    ):
        return False
    return True