"""
Product Analysis — Structured LLM Response Parser and Validator.

The LLM is instructed to return a JSON object. This module:

1. Strips markdown code fences (```json...```)
2. Parses the raw output as JSON, with regex fallback extraction
3. Validates every field:
   - evidence_strength in {strong, moderate, weak, insufficient}
   - relevance in {potentially_relevant, low_relevance, insufficient_evidence}
   - priority in {high, medium, low}
   - requires_verification is always forced True (non-negotiable)
   - All supporting_citation_ids / supporting_citation_id values are
     filtered against the valid_citation_ids set (LLM-bound evidence only)
   - Empty/missing strings get safe default values; never fabricated content
4. On any parse or validation failure: returns a safe fallback dict with
   grounded_summary = raw text, empty structured fields — never crashes.

RULES:
- Never fabricate data on parse failure
- Never allow citation IDs that were not in the supplied evidence
- Never convert non-preliminary language; it passes through but the UI
  labels all output as preliminary
- On failure: fallback preserves raw LLM text as grounded_summary
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Valid enum values — must stay in sync with analysis_result.py and analysis_api.ts
# ---------------------------------------------------------------------------

_VALID_EVIDENCE_STRENGTHS: frozenset = frozenset(
    {"strong", "moderate", "weak", "insufficient"}
)
_VALID_RELEVANCE_VALUES: frozenset = frozenset(
    {"potentially_relevant", "low_relevance", "insufficient_evidence"}
)
_VALID_PRIORITIES: frozenset = frozenset({"high", "medium", "low"})

# Minimum grounded_summary length to accept from JSON (otherwise use raw text)
_MIN_SUMMARY_LEN = 50


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_structured_analysis_response(
    raw_llm_output: str,
    valid_citation_ids: Set[str],
) -> Dict[str, Any]:
    """
    Parse and validate the structured JSON response from the product analysis LLM call.

    Args:
        raw_llm_output:      Raw string from OpenRouterProvider.complete()
        valid_citation_ids:  citation_id values from the LLM-bound evidence only
                             (≤10 items, selected by _select_llm_evidence).
                             Any citation ID not in this set is discarded.

    Returns:
        A dict with keys:
          grounded_summary     str | None
          classification       dict | None
          ip_assessment        list[dict]
          regulatory_assessment list[dict]
          tk_biodiversity      dict | None
          compliance_checklist list[dict]
          _parse_fallback      bool  (True if JSON parsing failed)
          _fallback_reason     str   (explanation, only present on fallback)

        Never raises. Never returns None.
    """
    if not raw_llm_output or not raw_llm_output.strip():
        return _empty_fallback("LLM returned empty output.")

    cleaned = _strip_markdown_fences(raw_llm_output)

    # ── Attempt JSON parse ─────────────────────────────────────────────────
    parsed: Optional[Dict[str, Any]] = None
    try:
        candidate = json.loads(cleaned)
        if isinstance(candidate, dict):
            parsed = candidate
    except json.JSONDecodeError:
        pass

    if parsed is None:
        # Try extracting the first {...} block from mixed output
        parsed = _extract_json_object(cleaned)

    if parsed is None:
        return _fallback_with_summary(
            raw_llm_output, "LLM output could not be parsed as JSON."
        )

    # ── Extract and validate each field ───────────────────────────────────
    result: Dict[str, Any] = {"_parse_fallback": False}

    # grounded_summary — use raw text if JSON summary is too short
    summary = parsed.get("grounded_summary", "")
    if isinstance(summary, str) and len(summary.strip()) >= _MIN_SUMMARY_LEN:
        result["grounded_summary"] = summary.strip()
    else:
        result["grounded_summary"] = None

    result["classification"] = _validate_classification(
        parsed.get("classification"), valid_citation_ids
    )
    result["ip_assessment"] = _validate_ip_assessment(
        parsed.get("ip_assessment"), valid_citation_ids
    )
    result["regulatory_assessment"] = _validate_regulatory_assessment(
        parsed.get("regulatory_assessment"), valid_citation_ids
    )
    result["tk_biodiversity"] = _validate_tk_biodiversity(
        parsed.get("tk_biodiversity"), valid_citation_ids
    )
    result["compliance_checklist"] = _validate_compliance_checklist(
        parsed.get("compliance_checklist"), valid_citation_ids
    )

    return result


# ---------------------------------------------------------------------------
# Field validators
# ---------------------------------------------------------------------------


def _validate_citation_ids(raw_ids: Any, valid: Set[str]) -> List[str]:
    """Return only the citation IDs that exist in the valid set. Discard all others."""
    if not isinstance(raw_ids, list):
        return []
    validated = []
    for cid in raw_ids:
        if isinstance(cid, str) and cid.strip() in valid:
            validated.append(cid.strip())
    return validated


def _validate_single_citation_id(raw: Any, valid: Set[str]) -> Optional[str]:
    """Validate a single citation_id string. Returns None if invalid."""
    if not isinstance(raw, str):
        return None
    cid = raw.strip()
    return cid if cid in valid else None


def _validate_classification(
    raw: Any, valid_citation_ids: Set[str]
) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    strength = raw.get("evidence_strength", "insufficient")
    if strength not in _VALID_EVIDENCE_STRENGTHS:
        strength = "insufficient"

    assessment = raw.get("preliminary_assessment", "")
    if not isinstance(assessment, str) or not assessment.strip():
        assessment = (
            "Classification assessment not available from the retrieved evidence. "
            "Professional verification is recommended."
        )

    return {
        "user_selected": str(raw.get("user_selected", "")).strip() or "other",
        "preliminary_assessment": assessment.strip(),
        "evidence_strength": strength,
        "requires_verification": True,  # always True — non-negotiable
        "supporting_citation_ids": _validate_citation_ids(
            raw.get("supporting_citation_ids", []), valid_citation_ids
        ),
    }


def _validate_ip_assessment(
    raw: Any, valid_citation_ids: Set[str]
) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []

    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        ip_type = str(item.get("ip_type", "")).strip()
        if not ip_type:
            continue  # skip entries without a type

        relevance = item.get("relevance", "insufficient_evidence")
        if relevance not in _VALID_RELEVANCE_VALUES:
            relevance = "insufficient_evidence"

        strength = item.get("evidence_strength", "insufficient")
        if strength not in _VALID_EVIDENCE_STRENGTHS:
            strength = "insufficient"

        assessment = str(item.get("preliminary_assessment", "")).strip()
        if not assessment:
            assessment = "Insufficient evidence for preliminary IP assessment."

        reasoning = str(item.get("reasoning", "")).strip()

        citation_ids = _validate_citation_ids(
            item.get("supporting_citation_ids", []), valid_citation_ids
        )
        if not citation_ids and relevance != "insufficient_evidence":
            continue

        result.append(
            {
                "ip_type": ip_type,
                "relevance": relevance,
                "preliminary_assessment": assessment,
                "reasoning": reasoning,
                "evidence_strength": strength,
                "requires_verification": True,
                "supporting_citation_ids": citation_ids,
            }
        )

    return result


def _validate_regulatory_assessment(
    raw: Any, valid_citation_ids: Set[str]
) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []

    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        framework = str(item.get("framework", "")).strip()
        if not framework:
            continue

        strength = item.get("evidence_strength", "insufficient")
        if strength not in _VALID_EVIDENCE_STRENGTHS:
            strength = "insufficient"

        why = str(item.get("why_applicable", "")).strip()

        provisions_raw = item.get("relevant_provisions", [])
        provisions: List[str] = []
        if isinstance(provisions_raw, list):
            for p in provisions_raw:
                ps = str(p).strip()
                if ps:
                    provisions.append(ps)

        citation_ids = _validate_citation_ids(
            item.get("supporting_citation_ids", []), valid_citation_ids
        )
        if not citation_ids and strength != "insufficient":
            continue

        result.append(
            {
                "framework": framework,
                "why_applicable": why or "Insufficient evidence for a preliminary assessment.",
                "relevant_provisions": provisions,
                "evidence_strength": strength,
                "requires_verification": True,
                "supporting_citation_ids": citation_ids,
            }
        )

    return result


def _validate_tk_biodiversity(
    raw: Any, valid_citation_ids: Set[str]
) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    strength = raw.get("evidence_strength", "insufficient")
    if strength not in _VALID_EVIDENCE_STRENGTHS:
        strength = "insufficient"

    # If the LLM says insufficient or evidence_strength is insufficient → mark it
    insufficient = bool(
        raw.get("insufficient", False) or strength == "insufficient"
    )

    citation_ids = _validate_citation_ids(
        raw.get("supporting_citation_ids", []), valid_citation_ids
    )
    return {
        "tk_considerations": str(raw.get("tk_considerations", "")).strip()
        or "Not available from retrieved evidence.",
        "biodiversity_considerations": str(
            raw.get("biodiversity_considerations", "")
        ).strip()
        or "Not available from retrieved evidence.",
        "abs_note": str(raw.get("abs_note", "")).strip()
        or "Not available from retrieved evidence.",
        "evidence_strength": strength,
        "requires_verification": True,
        "supporting_citation_ids": citation_ids,
        "insufficient": insufficient,
    }


def _validate_compliance_checklist(
    raw: Any, valid_citation_ids: Set[str]
) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []

    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        action = str(item.get("action", "")).strip()
        reason = str(item.get("reason", "")).strip()
        if not action or not reason:
            continue  # skip items without both required fields

        legal_area = str(item.get("legal_area", "")).strip() or "General Regulatory"

        priority = item.get("priority", "medium")
        if priority not in _VALID_PRIORITIES:
            priority = "medium"

        entry: Dict[str, Any] = {
            "action": action,
            "reason": reason,
            "legal_area": legal_area,
            "priority": priority,
            "requires_verification": True,
        }

        # Checklist items must be traceable to supplied evidence.
        cid = _validate_single_citation_id(
            item.get("supporting_citation_id"), valid_citation_ids
        )
        if not cid:
            continue
        entry["supporting_citation_id"] = cid

        result.append(entry)

    return result


# ---------------------------------------------------------------------------
# Extraction utilities
# ---------------------------------------------------------------------------


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json...``` or ```...``` code fences from the text."""
    stripped = text.strip()
    # Match optional json language specifier
    pattern = r"^```(?:json)?\s*\n?(.*?)\n?```\s*$"
    match = re.match(pattern, stripped, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return stripped


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """
    Try to extract a JSON object from text that may contain surrounding prose.
    Scans candidate '{' positions to find the top-level valid JSON object.
    """
    matches = [m.start() for m in re.finditer(r"\{", text)]
    for start in matches:
        depth = 0
        end = -1
        for i, ch in enumerate(text[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break

        if end != -1:
            candidate = text[start : end + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict) and (
                    "grounded_summary" in parsed
                    or "classification" in parsed
                    or "ip_assessment" in parsed
                ):
                    return parsed
            except json.JSONDecodeError:
                pass

    return None


# ---------------------------------------------------------------------------
# Fallback helpers
# ---------------------------------------------------------------------------


def _empty_fallback(reason: str) -> Dict[str, Any]:
    return {
        "grounded_summary": None,
        "classification": None,
        "ip_assessment": [],
        "regulatory_assessment": [],
        "tk_biodiversity": None,
        "compliance_checklist": [],
        "_parse_fallback": True,
        "_fallback_reason": reason,
    }


def _fallback_with_summary(raw_text: str, reason: str) -> Dict[str, Any]:
    return {
        "grounded_summary": None,
        "classification": None,
        "ip_assessment": [],
        "regulatory_assessment": [],
        "tk_biodiversity": None,
        "compliance_checklist": [],
        "_parse_fallback": True,
        "_fallback_reason": reason,
    }
