"""Provider-agnostic LLM client built on top of LiteLLM.

We expose a single :func:`complete` function used by the orchestrator. It hides
provider details, picks the first provider with a configured API key, and falls
back to the next ones on failure (network error, rate limit, etc.).

Design goals:
- **Provider-agnostic**: the only contract is "messages + tools in → message out".
  Adding/swapping providers means editing ``settings.LLM_PROVIDERS``, no code change.
- **Graceful degradation**: if no provider has an API key, :func:`is_configured`
  returns ``False`` and the orchestrator falls back to deterministic-only mode.
- **Lazy import**: ``litellm`` is heavy; we only import it on first use so that
  unrelated Django commands (migrate, collectstatic, tests for non-LLM apps)
  stay fast.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Normalized response from the LLM."""

    content: str
    tool_calls: list[dict[str, Any]]
    finish_reason: str
    provider: str
    raw: Any = None


def _active_providers() -> list[dict[str, Any]]:
    """Return providers that have an API key configured, in fallback order."""

    return [p for p in settings.LLM_PROVIDERS if p.get("api_key")]


def is_configured() -> bool:
    """``True`` if at least one provider has an API key."""

    return bool(_active_providers())


def complete(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | dict | None = "auto",
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> LLMResponse:
    """Call the LLM with fallback across providers.

    Args:
        messages: OpenAI-style chat messages (``role`` + ``content``).
        tools: Tool definitions (function calling). Optional.
        tool_choice: ``"auto"`` (default), ``"none"``, or specific tool.
        temperature: Sampling temperature. Defaults to ``settings.LLM_TEMPERATURE``.
        max_tokens: Cap on output tokens.

    Raises:
        RuntimeError: If no provider is configured, or all providers fail.
    """

    providers = _active_providers()
    if not providers:
        raise RuntimeError(
            "No LLM provider configured. Set at least one of "
            "GEMINI_API_KEY / GROQ_API_KEY / OPENROUTER_API_KEY in .env."
        )

    # Lazy import — keeps non-LLM workflows snappy.
    import litellm

    last_error: Exception | None = None
    for provider in providers:
        try:
            kwargs: dict[str, Any] = {
                "model": provider["model"],
                "api_key": provider["api_key"],
                "messages": messages,
                "temperature": (
                    temperature
                    if temperature is not None
                    else getattr(settings, "LLM_TEMPERATURE", 0.3)
                ),
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = litellm.completion(**kwargs)
            return _normalize(response, provider["name"])
        except Exception as exc:  # noqa: BLE001 — we genuinely want to try the next provider
            logger.warning(
                "LLM provider %s failed (%s); trying next.",
                provider["name"],
                exc,
            )
            last_error = exc
            continue

    raise RuntimeError(
        f"All LLM providers failed. Last error: {last_error!r}"
    )


def _normalize(response: Any, provider_name: str) -> LLMResponse:
    """Convert a LiteLLM response object into our normalized dataclass."""

    choice = response.choices[0]
    msg = choice.message

    content = getattr(msg, "content", None) or ""

    tool_calls: list[dict[str, Any]] = []
    raw_tool_calls = getattr(msg, "tool_calls", None) or []
    for tc in raw_tool_calls:
        # LiteLLM normalizes to OpenAI shape, but objects vs dicts vary.
        fn = getattr(tc, "function", None) or tc.get("function", {})
        tool_calls.append(
            {
                "id": getattr(tc, "id", None) or tc.get("id"),
                "name": getattr(fn, "name", None) or fn.get("name"),
                "arguments": (
                    getattr(fn, "arguments", None) or fn.get("arguments") or "{}"
                ),
            }
        )

    return LLMResponse(
        content=content,
        tool_calls=tool_calls,
        finish_reason=getattr(choice, "finish_reason", "stop"),
        provider=provider_name,
        raw=response,
    )
