"""
Phase 2 — Multilingual Query Normalizer.

Extracts entities, normalizes Hindi/Telugu/Romanized text into English legal concept queries
for English corpus retrieval, while preserving original technical & botanical terms.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from src.features.rag.domain.multilingual.language_detector import LanguageDetector, LanguageCode
from src.features.rag.domain.multilingual.terminology import PROTECTED_TERMS

# Term Mappings for English retrieval normalization
_INDIC_QUERY_MAPPINGS: Dict[str, str] = {
    # Hindi terms
    "पेटेंट": "patent",
    "आवश्यकताएं": "requirements eligibility",
    "अधिकार": "rights protection",
    "नियम": "rules regulations",
    "अनुमति": "approval license permission",
    "संरक्षण": "protection exemption",
    "खाद्य": "food supplement",
    "औषधि": "drug medicine",
    
    # Telugu terms
    "పేటెంట్": "patent",
    "అవసరం": "requirement eligibility",
    "హక్కులు": "rights protection",
    "నిబంధనలు": "rules regulations",
    "అనుమతి": "approval license permission",
    "రక్షణ": "protection exemption",
    "ఆహార": "food supplement",
    "మందులు": "drug medicine",

    # Romanized terms
    "cheyyacha": "apply eligibility",
    "kavali": "required application",
    "avashyakta": "requirement eligibility",
    "anumati": "approval permission",
    "kya": "",
    "hai": "",
    "hain": "",
    "ki": "",
    "ka": "",
    "ke": "",
    "ko": "",
}


class QueryNormalizer:
    """Normalizes Indic and Romanized queries into English concept queries for RAG retrieval."""

    @staticmethod
    def normalize_query(query: str) -> Tuple[str, LanguageCode]:
        if not query or not query.strip():
            return "", "en"

        lang = LanguageDetector.detect_language(query)
        if lang == "en":
            return query.strip(), "en"

        normalized_words: List[str] = []
        tokens = re.findall(r"\b[\w\u0900-\u097F\u0C00-\u0C7F]+\b", query)

        for token in tokens:
            token_lower = token.lower()
            # If protected term, keep in original form
            if token_lower in PROTECTED_TERMS:
                normalized_words.append(token)
            elif token_lower in _INDIC_QUERY_MAPPINGS:
                mapped = _INDIC_QUERY_MAPPINGS[token_lower]
                if mapped:
                    normalized_words.append(mapped)
            elif token in _INDIC_QUERY_MAPPINGS:
                mapped = _INDIC_QUERY_MAPPINGS[token]
                if mapped:
                    normalized_words.append(mapped)
            else:
                # Retain token if alphanumeric/English
                if re.match(r"^[A-Za-z0-9]+$", token):
                    normalized_words.append(token)

        normalized_str = " ".join(normalized_words).strip()
        if not normalized_str:
            normalized_str = query  # Fallback to original text if empty

        return normalized_str, lang
