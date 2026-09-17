"""
Infrastructure Layer — Sarvam AI HTTP Client.

Communicates directly with Sarvam AI REST endpoints:
- POST https://api.sarvam.ai/translate
- POST https://api.sarvam.ai/transliterate

Key Security:
- Loaded ONLY from process environment (SARVAM_API_KEY).
- Passed in header 'api-subscription-key'.
- Never logged, printed, or returned in client responses.

Failure Fallback:
- Returns None if key is missing, endpoint times out, or API errors.
- Calling code must handle None safely without crashing or corrupting RAG context.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Dict, Any, Optional

TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"
TRANSLITERATE_ENDPOINT = "https://api.sarvam.ai/transliterate"

# Language BCP-47 mappings for Sarvam
SARVAM_LANG_MAP: Dict[str, str] = {
    "en": "en-IN",
    "hi": "hi-IN",
    "te": "te-IN",
}


class SarvamClient:
    """Direct REST client for Sarvam AI APIs."""

    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 5.0) -> None:
        self._api_key = api_key or os.environ.get("SARVAM_API_KEY", "").strip()
        self._timeout = timeout_seconds

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model: str = "sarvam-translate:v1",
    ) -> Optional[str]:
        """
        Translates text using Sarvam AI POST /translate endpoint.
        Returns translated_text on success, or None on failure/missing key/timeout.
        """
        if not self.is_available or not text or not text.strip():
            return None

        src_code = SARVAM_LANG_MAP.get(source_lang, source_lang)
        tgt_code = SARVAM_LANG_MAP.get(target_lang, target_lang)

        payload = {
            "input": text[:2000],  # Sarvam character limit
            "source_language_code": src_code,
            "target_language_code": tgt_code,
            "model": model,
        }

        req = urllib.request.Request(
            TRANSLATE_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "api-subscription-key": self._api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("translated_text")
        except Exception:
            # Silence internal transport/API errors; caller handles fallback
            pass
        return None

    def transliterate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> Optional[str]:
        """
        Transliterates text between scripts using Sarvam AI POST /transliterate endpoint.
        (e.g., Latin script Indic text -> Indic script).
        Returns transliterated_text on success, or None on failure.
        """
        if not self.is_available or not text or not text.strip():
            return None

        src_code = SARVAM_LANG_MAP.get(source_lang, source_lang)
        tgt_code = SARVAM_LANG_MAP.get(target_lang, target_lang)

        payload = {
            "input": text[:1000],  # Sarvam character limit
            "source_language_code": src_code,
            "target_language_code": tgt_code,
        }

        req = urllib.request.Request(
            TRANSLITERATE_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "api-subscription-key": self._api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("transliterated_text")
        except Exception:
            pass
        return None
