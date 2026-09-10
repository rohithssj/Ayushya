"""
Phase 7 — Evidence Selection + Citation Construction (Domain Layer).

Deterministic, framework-independent logic. No LLM, no embedding model, no reranker.
Operates solely on existing hybrid retrieval results and their metadata.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from src.features.rag.domain.chunk_quality import is_retrievable_chunk


# ---------------------------------------------------------------------------
# Citation construction
# ---------------------------------------------------------------------------

def build_citation(chunk: Dict[str, Any], citation_id: str) -> Dict[str, Any]:
    """
    Build a structured citation from actual retrieved chunk metadata only.

    SAFETY: Every field is read directly from the chunk dict.
    No value is fabricated. Missing fields are left None/absent.
    """
    # Support both flat chunk dicts and those with nested 'metadata'
    meta: Dict[str, Any] = chunk.get("metadata") or {}

    def _get(key: str) -> Any:
        # Prefer top-level, fall back to metadata sub-dict.
        val = chunk.get(key)
        if val is None:
            val = meta.get(key)
        return val

    # source_url: return only if explicitly present; never fabricate.
    raw_url = _get("source_url")
    source_url: Optional[str] = raw_url if isinstance(raw_url, str) and raw_url.strip() else None

    # year: only if numeric
    raw_year = _get("year")
    year: Optional[int] = int(raw_year) if raw_year is not None and str(raw_year).isdigit() else None

    # page integers
    def _int_or_none(k: str) -> Optional[int]:
        v = _get(k)
        try:
            return int(v) if v is not None else None
        except (TypeError, ValueError):
            return None

    return {
        "citation_id": citation_id,
        "chunk_id": _get("chunk_id") or "",
        "document_id": _get("document_id") or "",
        "title": _get("title") or "",
        "section": _get("section"),
        "section_title": _get("section_title"),
        "subsection": _get("subsection"),
        "chapter": _get("chapter"),
        "page": _int_or_none("page"),
        "page_start": _int_or_none("page_start"),
        "page_end": _int_or_none("page_end"),
        "jurisdiction": _get("jurisdiction") or "",
        "domain": _get("domain") or "",
        "authority": _get("authority"),
        "year": year,
        "source_url": source_url,
    }


# ---------------------------------------------------------------------------
# Evidence selection
# ---------------------------------------------------------------------------

def _chunk_id(item: Dict[str, Any]) -> str:
    """Return a stable chunk_id from an item dict."""
    cid = item.get("chunk_id") or (item.get("metadata") or {}).get("chunk_id") or ""
    return str(cid)


def _evidence_id(chunk_id: str, rank: int) -> str:
    """Deterministic evidence_id from chunk_id + rank."""
    raw = f"{chunk_id}:{rank}"
    return "ev_" + hashlib.sha1(raw.encode()).hexdigest()[:12]


def _citation_id_for(chunk_id: str) -> str:
    return "cit_" + hashlib.sha1(chunk_id.encode()).hexdigest()[:12]


def _selection_reason(item: Dict[str, Any], rank: int) -> str:
    """Build a deterministic, non-fabricated selection reason from metadata."""
    parts: List[str] = [f"Hybrid rank {rank}"]

    lex = item.get("lexical_rank", 999)
    sem = item.get("semantic_rank", 999)
    if lex <= 20 and sem <= 20:
        parts.append("dual lexical+semantic match")
    elif lex <= 20:
        parts.append("strong lexical match")
    elif sem <= 20:
        parts.append("strong semantic match")

    terms = item.get("matched_terms") or []
    if terms:
        parts.append(f"matched terms: {', '.join(str(t) for t in terms[:3])}")

    section = item.get("section") or (item.get("metadata") or {}).get("section")
    if section:
        parts.append(f"section: {section}")

    return "; ".join(parts) + "."


def select_evidence(
    results: List[Dict[str, Any]],
    assessment: Dict[str, Any],
    jurisdiction: Optional[str] = None,
    domain: Optional[str] = None,
    max_evidence: int = 5,
) -> Dict[str, Any]:
    """
    Select the best evidence from hybrid retrieval results and build citations.

    Rules:
    - Respects abstention: if abstention_recommended=True and strength=insufficient,
      returns empty evidence list without manufacturing anything.
    - Deduplicates by chunk_id.
    - Filters non-substantive chunks (is_retrievable_chunk).
    - Filters chunks outside requested jurisdiction/domain.
    - Preserves hybrid ranking order (results already sorted by rank).
    - Builds citations strictly from retrieved metadata — no fabrication.

    Returns a dict with keys: selected, count.
    """
    abstention: bool = bool(assessment.get("abstention_recommended"))
    strength: str = assessment.get("strength", "insufficient")

    # Hard abstention: no substantive evidence exists → empty
    if strength == "insufficient" or not results:
        return {"selected": [], "count": 0}

    seen_chunk_ids: set = set()
    selected: List[Dict[str, Any]] = []

    for item in results:
        if len(selected) >= max_evidence:
            break

        # --- Deduplication ---
        cid = _chunk_id(item)
        if cid and cid in seen_chunk_ids:
            continue

        # --- Jurisdiction/domain alignment ---
        item_jur = str(item.get("jurisdiction") or (item.get("metadata") or {}).get("jurisdiction") or "").strip().lower()
        item_dom = str(item.get("domain") or (item.get("metadata") or {}).get("domain") or "").strip().lower()

        if jurisdiction and jurisdiction.strip():
            if item_jur != jurisdiction.strip().lower():
                continue
        if domain and domain.strip():
            if item_dom != domain.strip().lower():
                continue

        # --- Substantive quality gate ---
        if not is_retrievable_chunk(item):
            continue

        # For weak evidence: only include if abstention is NOT recommended
        # (EvidenceEvaluator may have set abstention_recommended=True for weak+incomplete)
        if strength == "weak" and abstention:
            continue

        rank = item.get("rank") or (results.index(item) + 1)
        ev_id = _evidence_id(cid, rank)
        cit_id = _citation_id_for(cid)

        evidence_item = {
            "evidence_id": ev_id,
            "chunk_id": cid,
            "text": item.get("text", ""),
            "citation": build_citation(item, cit_id),
            "selection_reason": _selection_reason(item, rank),
        }

        selected.append(evidence_item)
        if cid:
            seen_chunk_ids.add(cid)

    return {"selected": selected, "count": len(selected)}
