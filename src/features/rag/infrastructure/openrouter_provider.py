"""
Phase 8 / Reliability — OpenRouter LLM provider (Infrastructure Layer).

Features:
- Configurable primary and fallback model routing via environment variables
  (LLM_MODEL, LLM_FALLBACK_MODELS, LLM_TIMEOUT_SECONDS).
- OpenRouter native multi-model fallback support via the `models` parameter.
- Clean non-repeating fallback traversal (primary → fallback1 → fallback2).
- Zero retries against the same rate-limited model.
- 15-second default timeout per call.
- Safe logging (model slug & status category only; NEVER API keys, prompts, evidence, or raw error bodies).
- Strict application-level exception hierarchy.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application-level exceptions (no raw provider details leaked)
# ---------------------------------------------------------------------------

class LLMProviderError(Exception):
    """Base class for all LLM provider errors."""


class LLMConfigError(LLMProviderError):
    """Raised when required configuration (e.g. API key) is missing."""


class LLMRateLimitError(LLMProviderError):
    """Raised on rate-limit (HTTP 429 or provider rate-limit response)."""


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
DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.0  # Deterministic; grounding requires low temperature


class OpenRouterProvider:
    """
    HTTP client for OpenRouter API with native multi-model fallback support.

    Responsibilities:
    - Read API key, primary model, fallback models, and timeout from environment
    - Send completion requests using OpenRouter's `models` fallback array
    - Fallback gracefully across configured models without repeated retries
    - Translate HTTP/network errors into typed application exceptions immediately
    - Safely log model attempts without leaking user prompts, evidence, or credentials

    Does NOT:
    - Build prompts
    - Validate citations
    - Hardcode model names in logic
    - Expose raw provider credentials
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
        self._model = model or os.environ.get("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b").strip()

        if fallback_models is not None:
            self._fallback_models = fallback_models
        else:
            raw_fallbacks = os.environ.get("LLM_FALLBACK_MODELS", "").strip()
            self._fallback_models = [m.strip() for m in raw_fallbacks.split(",") if m.strip()] if raw_fallbacks else []

        if timeout is not None:
            self._timeout = timeout
        else:
            self._timeout = int(os.environ.get("LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))

        if not self._api_key:
            raise LLMConfigError(
                "OPENROUTER_API_KEY is not set. "
                "Set it in your environment or .env.local file."
            )
        if not self._model:
            raise LLMConfigError("LLM_MODEL is not set.")

    @property
    def model(self) -> str:
        return self._model

    @property
    def fallback_models(self) -> List[str]:
        return list(self._fallback_models)

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """
        Call OpenRouter chat completions with model fallback routing.

        Attempts configured models in order: [primary, fallback_1, fallback_2, ...]
        Uses OpenRouter's native `models` fallback parameter.
        Never retries the same model upon rate limit or failure.
        """
        # Unique list preserving priority order: primary followed by non-duplicate fallbacks
        models_to_try: List[str] = [self._model]
        for fb in self._fallback_models:
            if fb and fb not in models_to_try:
                models_to_try.append(fb)

        last_exception: Optional[Exception] = None

        for idx, current_model in enumerate(models_to_try):
            # Models array passed to OpenRouter starting from the current model
            remaining_models = models_to_try[idx:]

            payload: Dict[str, Any] = {
                "model": current_model,
                "models": remaining_models,
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
                logger.info(f"OpenRouter attempt with model: {current_model} (fallbacks: {remaining_models[1:]})")
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    raw = resp.read().decode("utf-8")

                # Parse JSON response
                try:
                    data: Dict[str, Any] = json.loads(raw)
                except json.JSONDecodeError:
                    raise LLMResponseError("OpenRouter returned a non-JSON response.") from None

                # Check for provider error payload inside JSON response
                if "error" in data:
                    err_obj = data.get("error")
                    if isinstance(err_obj, dict):
                        err_code = err_obj.get("code")
                        err_msg = str(err_obj.get("message", "")).lower()
                        if err_code == 429 or "rate limit" in err_msg or "quota" in err_msg:
                            raise LLMRateLimitError("OpenRouter rate limit exceeded. Try again later.")
                    raise LLMUnavailableError("OpenRouter returned an error response.")

                try:
                    text: str = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError):
                    raise LLMResponseError("OpenRouter response missing expected content field.") from None

                if not text or not text.strip():
                    raise LLMResponseError("OpenRouter returned an empty response.")

                used_model = data.get("model", current_model)
                logger.info(f"OpenRouter completion successful using model: {used_model}")
                return text.strip()

            except urllib.error.HTTPError as e:
                status = e.code
                try:
                    err_body = e.read().decode("utf-8", errors="replace")[:300].lower()
                except Exception:
                    err_body = ""

                if status == 401 or status == 403:
                    logger.warning(f"OpenRouter auth failure (HTTP {status}) for model: {current_model}")
                    raise LLMAuthError("OpenRouter authentication failed. Check OPENROUTER_API_KEY.") from None

                if status == 429 or "rate limit" in err_body or "too many requests" in err_body:
                    logger.warning(f"OpenRouter rate limit (HTTP 429) for model: {current_model}")
                    last_exception = LLMRateLimitError("OpenRouter rate limit exceeded. Try again later.")
                elif status == 408 or status == 504:
                    logger.warning(f"OpenRouter timeout (HTTP {status}) for model: {current_model}")
                    last_exception = LLMTimeoutError(f"OpenRouter request timed out (HTTP {status}).")
                elif status >= 500:
                    logger.warning(f"OpenRouter service error (HTTP {status}) for model: {current_model}")
                    last_exception = LLMUnavailableError(f"OpenRouter service error (HTTP {status}).")
                else:
                    logger.warning(f"OpenRouter request failed (HTTP {status}) for model: {current_model}")
                    last_exception = LLMUnavailableError(f"OpenRouter request failed (HTTP {status}).")

            except TimeoutError:
                logger.warning(f"OpenRouter socket timeout after {self._timeout}s for model: {current_model}")
                last_exception = LLMTimeoutError(f"OpenRouter did not respond within {self._timeout}s.")
            except OSError as e:
                err_str = str(e).lower()
                if "timed out" in err_str:
                    logger.warning(f"OpenRouter connection timed out for model: {current_model}")
                    last_exception = LLMTimeoutError(f"OpenRouter connection timed out after {self._timeout}s.")
                else:
                    logger.warning(f"OpenRouter network error for model: {current_model}")
                    last_exception = LLMUnavailableError(f"Network error reaching OpenRouter: {type(e).__name__}.")
            except (LLMResponseError, LLMUnavailableError, LLMRateLimitError) as e:
                logger.warning(f"OpenRouter provider error for model: {current_model}")
                last_exception = e

        # If all configured models have been exhausted
        logger.error(f"All configured OpenRouter models failed ({len(models_to_try)} models attempted).")
        if last_exception:
            raise last_exception
        raise LLMUnavailableError("All configured OpenRouter models failed to respond.")
