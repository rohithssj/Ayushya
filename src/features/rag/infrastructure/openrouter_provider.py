"""
Phase 8 — OpenRouter LLM provider (Infrastructure Layer).

All OpenRouter/HTTP-specific logic is isolated here.
No domain logic. No retrieval logic. No citation construction.

Provider-specific errors are translated into application-level exceptions
so the application layer never leaks raw provider details.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Application-level exceptions (no raw provider details leaked)
# ---------------------------------------------------------------------------

class LLMProviderError(Exception):
    """Base class for all LLM provider errors."""


class LLMConfigError(LLMProviderError):
    """Raised when required configuration (e.g. API key) is missing."""


class LLMRateLimitError(LLMProviderError):
    """Raised on rate-limit (HTTP 429)."""


class LLMAuthError(LLMProviderError):
    """Raised on authentication failure (HTTP 401/403)."""


class LLMTimeoutError(LLMProviderError):
    """Raised when the provider does not respond in time."""


class LLMUnavailableError(LLMProviderError):
    """Raised when the provider is unavailable or returns a server error."""


class LLMResponseError(LLMProviderError):
    """Raised when the provider response is malformed or empty."""


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.0  # Deterministic; grounding requires low temperature


class OpenRouterProvider:
    """
    Thin HTTP wrapper around the OpenRouter API (OpenAI-compatible).

    Responsibilities:
    - Read API key and model from environment (never from code)
    - Send a single chat completion request
    - Return the raw text response
    - Translate HTTP/network errors into typed application exceptions

    Does NOT:
    - Build prompts
    - Validate citations
    - Do any domain logic
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
        self._model = model or os.environ.get("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b").strip()
        self._timeout = timeout

        if not self._api_key:
            raise LLMConfigError(
                "OPENROUTER_API_KEY is not set. "
                "Set it in your environment or .env.local file."
            )
        if not self._model:
            raise LLMConfigError("LLM_MODEL is not set.")

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """
        Call OpenRouter chat completions and return the assistant's text.

        Raises typed LLMProviderError subclasses on failure.
        Never leaks API keys or raw provider error bodies.
        """
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://ayushya.app",
            "X-Title": "AYUSHYA",
        }

        req = urllib.request.Request(
            OPENROUTER_API_URL,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status = e.code
            # Read error body for classification only — never forward it to caller
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                err_body = ""

            if status == 401 or status == 403:
                raise LLMAuthError("OpenRouter authentication failed. Check OPENROUTER_API_KEY.") from None
            if status == 429:
                raise LLMRateLimitError("OpenRouter rate limit exceeded. Try again later.") from None
            if status >= 500:
                raise LLMUnavailableError(f"OpenRouter service error (HTTP {status}).") from None
            raise LLMUnavailableError(f"OpenRouter request failed (HTTP {status}).") from None

        except TimeoutError:
            raise LLMTimeoutError(f"OpenRouter did not respond within {self._timeout}s.") from None
        except OSError as e:
            raise LLMUnavailableError(f"Network error reaching OpenRouter: {type(e).__name__}.") from None

        # Parse response
        try:
            data: Dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError:
            raise LLMResponseError("OpenRouter returned a non-JSON response.") from None

        try:
            text: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            # Check for provider-level error
            if "error" in data:
                raise LLMUnavailableError("OpenRouter returned an error response.") from None
            raise LLMResponseError("OpenRouter response missing expected content field.") from None

        if not text or not text.strip():
            raise LLMResponseError("OpenRouter returned an empty response.")

        return text.strip()
