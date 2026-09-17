"""
Phase 2 — Multilingual Query Normalizer.

Extracts entities, normalizes Hindi/Telugu/Romanized text into English legal concept queries
for English corpus retrieval, using Sarvam AI directly when available, while preserving original technical & botanical terms.

Failure Fallback Safety:
If Sarvam is unavailable or normalization fails, the system returns (None, lang) for non-English queries
rather than sending raw untranslated Hindi/Telugu text into the English vector DB.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple, Optional

from src.features.rag.domain.multilingual.language_detector import LanguageDetector, LanguageCode
from src.features.rag.domain.multilingual.terminology import PROTECTED_TERMS
from src.features.rag.infrastructure.multilingual.sarvam_client import SarvamClient

# Local term mappings for simple/offline Romanized and Indic entity extraction
_INDIC_QUERY_MAPPINGS: Dict[str, str] = {
    "पेटेंट": "patent",
    "आवश्यकताएं": "requirements eligibility",
    "अधिकार": "rights protection",
    "नियम": "rules regulations",
    "अनुमति": "approval license permission",
    "संरक्षण": "protection exemption",
    "खाद्य": "food supplement",
    "औषधि": "drug medicine",
    "పేటెంట్": "patent",
    "అవసరం": "requirement eligibility",
    "హక్కులు": "rights protection",
    "నిబంధనలు": "rules regulations",
    "అనుమతి": "approval license permission",
    "రక్షణ": "protection exemption",
    "ఆహార": "food supplement",
    "మందులు": "drug medicine",
}


class QueryNormalizer:
    """Normalizes Indic and Romanized queries into English concept queries for RAG retrieval."""

    def __init__(self, sarvam_client: Optional[SarvamClient] = None) -> None:
        self._sarvam = sarvam_client or SarvamClient()

    def normalize(self, query: str) -> Tuple[Optional[str], LanguageCode]:
        """
        Normalizes query to English for retrieval.
        Returns (english_query, detected_language).
        If input is Hindi/Telugu and normalization/translation fails, returns (None, detected_language)
        to prevent untranslated text from entering English vector DB.
        """
        if not query or not query.strip():
            return "", "en"

        det = LanguageDetector.detect_structured(query)
        lang = det["language"]

        if lang == "en":
            return query.strip(), "en"

        # 1. Romanized Input: Transliterate to Native Script first (if Sarvam available)
        src_text = query.strip()
        if det["romanized"] and self._sarvam.is_available:
            transliterated = self._sarvam.transliterate(
                text=src_text,
                source_lang="en",  # Latin script input
                target_lang=lang,
            )
            if transliterated:
                src_text = transliterated

        # 2. Translate Native Script (or transliterated text) to English via Sarvam
        if self._sarvam.is_available:
            translated = self._sarvam.translate(
                text=src_text,
                source_lang=lang,
                target_lang="en",
            )
            if translated and translated.strip():
                return translated.strip(), lang

        # 3. Offline fallback dictionary mapping
        normalized_words: List[str] = []
        tokens = re.findall(r"\b[\w\u0900-\u097F\u0C00-\u0C7F]+\b", query)

        for token in tokens:
            token_lower = token.lower()
            if token_lower in PROTECTED_TERMS:
                normalized_words.append(token)
            elif token_lower in _INDIC_QUERY_MAPPINGS:
                mapped = _INDIC_QUERY_MAPPINGS[token_lower]
                if mapped:
                    normalized_words.append(mapped)
            elif re.match(r"^[A-Za-z0-9]+$", token):
                normalized_words.append(token)

        normalized_str = " ".join(normalized_words).strip()
        if normalized_str:
            return normalized_str, lang

        # 4. If all normalization options failed for non-English query:
        # Return None to signal that multilingual retrieval query normalization failed safely
        return None, lang

    @staticmethod
    def normalize_query(query: str) -> Tuple[str, LanguageCode]:
        """Legacy static helper for backward compatibility."""
        normalizer = QueryNormalizer()
        res, lang = normalizer.normalize(query)
        return (res if res is not None else query), lang

