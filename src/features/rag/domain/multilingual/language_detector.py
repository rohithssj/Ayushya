"""
Phase 2 — Multilingual Language Detector.

Detects language code: 'en', 'hi', 'te'.
Supports Devanagari script (Hindi), Telugu script (Telugu), and Romanized/transliterated Indian queries.
Returns structured object with language, script, romanized status, and confidence score.
"""

from __future__ import annotations

import re
from typing import Dict, Any, Literal, TypedDict

LanguageCode = Literal["en", "hi", "te", "unknown"]

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
_TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]")

_ROMAN_HINDI_PATTERNS = re.compile(
    r"\b(?:ka|ke|ko|par|se|mein|hai|hain|kya|kyun|patta|karein|karna|tatha|aur|avashyakta|kaise|milega|bhaarath)\b",
    re.IGNORECASE,
)
_ROMAN_TELUGU_PATTERNS = re.compile(
    r"\b(?:cheyyacha|kavali|ala|kosam|undhi|avasam|eyyali|loni|dwara|leka|gurinchi|ee|vastunda|ela|cheyyali)\b",
    re.IGNORECASE,
)



class LanguageDetectionResult(TypedDict):
    language: LanguageCode
    script: str
    romanized: bool
    confidence: float


class LanguageDetector:
    """Detects query language (en, hi, te) from native scripts and Romanized text."""

    @staticmethod
    def detect_structured(text: str, fallback_language: LanguageCode = "en") -> LanguageDetectionResult:
        if not text or not text.strip():
            return {
                "language": fallback_language,
                "script": "latin" if fallback_language == "en" else "unknown",
                "romanized": False,
                "confidence": 1.0,
            }

        devanagari_chars = len(_DEVANAGARI_RE.findall(text))
        telugu_chars = len(_TELUGU_RE.findall(text))
        total_len = len(text.strip())

        # 1. Native Script Checks
        if devanagari_chars > telugu_chars and devanagari_chars > 2:
            conf = min(0.99, max(0.70, devanagari_chars / (total_len + 1)))
            return {
                "language": "hi",
                "script": "devanagari",
                "romanized": False,
                "confidence": round(conf, 2),
            }

        if telugu_chars > devanagari_chars and telugu_chars > 2:
            conf = min(0.99, max(0.70, telugu_chars / (total_len + 1)))
            return {
                "language": "te",
                "script": "telugu",
                "romanized": False,
                "confidence": round(conf, 2),
            }

        # 2. Romanized Script Pattern Checks
        has_roman_te = bool(_ROMAN_TELUGU_PATTERNS.search(text))
        has_roman_hi = bool(_ROMAN_HINDI_PATTERNS.search(text))

        if has_roman_te and not has_roman_hi:
            return {
                "language": "te",
                "script": "latin",
                "romanized": True,
                "confidence": 0.90,
            }

        if has_roman_hi and not has_roman_te:
            return {
                "language": "hi",
                "script": "latin",
                "romanized": True,
                "confidence": 0.90,
            }

        if has_roman_te and has_roman_hi:
            # Mixed romanized Indic intent
            return {
                "language": "hi",  # default candidate for mixed
                "script": "latin",
                "romanized": True,
                "confidence": 0.85,
            }

        return {
            "language": fallback_language,
            "script": "latin",
            "romanized": False,
            "confidence": 0.95,
        }

    @staticmethod
    def detect_language(text: str, fallback_language: LanguageCode = "en") -> LanguageCode:
        res = LanguageDetector.detect_structured(text, fallback_language)
        return res["language"]

