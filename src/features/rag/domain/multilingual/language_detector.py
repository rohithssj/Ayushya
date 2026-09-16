"""
Phase 2 — Multilingual Language Detector.

Detects language code: 'en', 'hi', 'te'.
Supports Devanagari script (Hindi), Telugu script (Telugu), and Romanized/transliterated Indian queries.
"""

from __future__ import annotations

import re
from typing import Literal

LanguageCode = Literal["en", "hi", "te"]

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
_TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]")

_ROMAN_HINDI_PATTERNS = re.compile(
    r"\b(?:ki|ka|ke|ko|par|se|mein|hai|hain|kya|kyun|patta|karein|karna|tatha|aur|avashyakta)\b",
    re.IGNORECASE,
)
_ROMAN_TELUGU_PATTERNS = re.compile(
    r"\b(?:cheyyacha|kavali|ala|kosam|undhi|avasam|eyyali|loni|dwara|leka|gurinchi)\b",
    re.IGNORECASE,
)


class LanguageDetector:
    """Detects query language (en, hi, te) from native scripts and Romanized text."""

    @staticmethod
    def detect_language(text: str, fallback_language: LanguageCode = "en") -> LanguageCode:
        if not text or not text.strip():
            return fallback_language

        # 1. Native Script Checks
        devanagari_chars = len(_DEVANAGARI_RE.findall(text))
        telugu_chars = len(_TELUGU_RE.findall(text))

        if devanagari_chars > telugu_chars and devanagari_chars > 2:
            return "hi"
        if telugu_chars > devanagari_chars and telugu_chars > 2:
            return "te"

        # 2. Romanized Script Pattern Checks
        if _ROMAN_TELUGU_PATTERNS.search(text):
            return "te"
        if _ROMAN_HINDI_PATTERNS.search(text):
            return "hi"

        return fallback_language
