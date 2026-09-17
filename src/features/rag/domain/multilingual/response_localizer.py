"""
Phase 2 — Multilingual Response Localizer.

Translates grounded LLM answers into user's language (Hindi, Telugu) using Sarvam AI directly
while keeping original citation IDs strictly intact using a protected-placeholder mechanism.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from src.features.rag.domain.multilingual.language_detector import LanguageCode
from src.features.rag.infrastructure.multilingual.sarvam_client import SarvamClient


class ResponseLocalizer:
    """Localizes grounded LLM responses into target language without breaking citations."""

    def __init__(self, sarvam_client: Optional[SarvamClient] = None) -> None:
        self._sarvam = sarvam_client or SarvamClient()

    def localize_answer(
        self,
        english_answer: str,
        target_language: LanguageCode,
    ) -> str:
        """
        Translates grounded English answer into target_language (hi or te).
        Protects [cit_xxx] citations via placeholders before sending to Sarvam, then restores them.
        """
        if not english_answer or target_language == "en":
            return english_answer

        if not self._sarvam.is_available:
            # Fall back safely to original English answer if Sarvam key is missing
            return english_answer

        # 1. Protect Citations using Placeholders: [cit_abc_123] -> ___CIT_0___
        citations: List[str] = []

        def replace_citation(match: re.Match[str]) -> str:
            cit_id = match.group(0)
            idx = len(citations)
            citations.append(cit_id)
            return f"___CIT_{idx}___"

        protected_text = re.sub(r"\[cit_[a-zA-Z0-9_]+\]", replace_citation, english_answer)

        # 2. Call Sarvam Translation API
        translated = self._sarvam.translate(
            text=protected_text,
            source_lang="en",
            target_lang=target_language,
        )

        if not translated or not translated.strip():
            # Graceful fallback to English if Sarvam call fails
            return english_answer

        # 3. Restore Citations: ___CIT_0___ -> [cit_abc_123]
        final_text = translated
        for idx, orig_cit in enumerate(citations):
            placeholder_pat = re.compile(rf"_{{3,}}CIT_{idx}_{{3,}}", re.IGNORECASE)
            final_text = placeholder_pat.sub(orig_cit, final_text)

        return final_text

