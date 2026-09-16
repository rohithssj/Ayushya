"""
Phase 2 — Multilingual package initialization.
"""

from src.features.rag.domain.multilingual.language_detector import LanguageDetector, LanguageCode
from src.features.rag.domain.multilingual.query_normalizer import QueryNormalizer
from src.features.rag.domain.multilingual.terminology import PROTECTED_TERMS
from src.features.rag.domain.multilingual.response_localizer import ResponseLocalizer

__all__ = [
    "LanguageDetector",
    "LanguageCode",
    "QueryNormalizer",
    "PROTECTED_TERMS",
    "ResponseLocalizer",
]
