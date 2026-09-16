"""
Phase 2 — Multilingual Response Localizer.

Translates grounded LLM answers into user's language (Hindi, Telugu)
while keeping original English legal evidence, citation IDs, and protected terms strictly intact.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

from src.features.rag.domain.multilingual.language_detector import LanguageCode
from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider, LLMProviderError

_LOCALIZATION_SYSTEM_PROMPT = """You are AYUSHYA's legal translation assistant.
Translate the provided grounded legal answer accurately into {target_language_name}.

CRITICAL CONSTRAINTS:
1. Translate the prose content accurately into fluent {target_language_name}.
2. DO NOT translate citation IDs (e.g. cit_abc123, ev_xyz123). Keep them EXACTLY as they appear in the source text.
3. DO NOT translate protected technical and botanical terms: Ashwagandha, Withania somnifera, Pippali, Piper longum, patent, novelty, inventive step, traditional knowledge, TKDL, biodiversity, ABS, Ayurveda-Aahara, FSSAI, Drugs and Cosmetics, TRIPS, PCT, CBD, Nagoya Protocol.
4. DO NOT add any legal claims, conclusions, or facts that are not present in the original answer.
5. Preserve formatting, bullet points, line breaks, and headers intact.
6. Output ONLY the translated text."""


class ResponseLocalizer:
    """Localizes grounded LLM responses into target language without breaking citations."""

    def __init__(self, llm_provider: Optional[OpenRouterProvider] = None) -> None:
        self._llm = llm_provider

    def _get_llm(self) -> OpenRouterProvider:
        if self._llm is None:
            self._llm = OpenRouterProvider()
        return self._llm

    def localize_answer(
        self,
        english_answer: str,
        target_language: LanguageCode,
    ) -> str:
        if not english_answer or target_language == "en":
            return english_answer

        lang_name = "Hindi" if target_language == "hi" else "Telugu"
        sys_prompt = _LOCALIZATION_SYSTEM_PROMPT.format(target_language_name=lang_name)
        user_prompt = f"Original Grounded English Answer:\n\n{english_answer}"

        try:
            translated = self._get_llm().complete(
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                max_tokens=1024,
                temperature=0.0,
                timeout_seconds=20,
            )
            return translated.strip() if translated else english_answer
        except Exception:
            # Fall back safely to original English answer if translation fails
            return english_answer
