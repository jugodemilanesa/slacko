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

import ast
import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

# Some providers (notably Gemini 2.5 Flash in thinking mode) occasionally emit
# their function call as plain text inside ``content`` instead of as a
# structured ``tool_calls`` entry, e.g.::
#
#     tool_code print(default_api.parse_problem(text='...', model={...})) thought ...
#
# When that happens the orchestrator sees no tool call and the turn breaks
# (the tool never runs and the raw ``tool_code`` text reaches the user). We
# detect this signature and salvage the call so dispatch proceeds normally.
_LEAKED_CALL_RE = re.compile(r"default_api\.(\w+)\s*\(")


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

    # Importamos lazily para evitar circular import.
    from . import usage

    last_error: Exception | None = None
    for provider in providers:
        # Skip providers que estén cerca de su cuota — preempt antes del 429.
        if usage.is_near_cap(provider):
            logger.info(
                "LLM provider %s skipped (near quota cap); trying next.",
                provider["name"],
            )
            continue

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
            # OpenAI-compatible providers con base custom (Z.ai, etc.) necesitan
            # api_base. LiteLLM lo passthroughea sin tocar el shape de la request.
            if provider.get("api_base"):
                kwargs["api_base"] = provider["api_base"]
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            # Provider-specific passthrough params (e.g. ``reasoning_effort`` to
            # disable Gemini thinking, which prevents tool-call-as-text leaks).
            if provider.get("extra_params"):
                kwargs.update(provider["extra_params"])

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

    # Safety net: if the provider leaked its tool call into ``content`` as text
    # (no structured ``tool_calls``), recover it so the orchestrator dispatches
    # the tool instead of showing raw ``tool_code`` text to the student.
    if not tool_calls and content:
        salvaged, content = _salvage_leaked_tool_call(content)
        if salvaged:
            logger.warning(
                "Recovered leaked tool call(s) from %s content (provider quirk).",
                provider_name,
            )
            tool_calls = salvaged

    return LLMResponse(
        content=content,
        tool_calls=tool_calls,
        finish_reason=getattr(choice, "finish_reason", "stop"),
        provider=provider_name,
        raw=response,
    )


def _extract_balanced(text: str, open_idx: int) -> str | None:
    """Return the substring inside the parentheses starting at ``open_idx``.

    Scans forward from the opening ``(`` tracking bracket depth while respecting
    string literals (single/double quotes with escapes), and returns the content
    between the outer parentheses (exclusive). ``None`` if unbalanced.
    """

    depth = 0
    in_str: str | None = None
    escaped = False
    for i in range(open_idx, len(text)):
        ch = text[i]
        if in_str is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ("'", '"'):
            in_str = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1 : i]
    return None


def _salvage_leaked_tool_call(content: str) -> tuple[list[dict[str, Any]], str]:
    """Recover a tool call that a provider emitted as text inside ``content``.

    Returns ``(tool_calls, cleaned_content)``. On a successful salvage the
    content is cleared — the surrounding narration was generated by the model as
    if the tool had already run, so we let it re-narrate after the real dispatch.
    On failure the original content is returned untouched.
    """

    match = _LEAKED_CALL_RE.search(content)
    if not match:
        return [], content

    name = match.group(1)
    open_idx = match.end() - 1  # index of the '(' captured by the regex
    args_src = _extract_balanced(content, open_idx)
    if args_src is None:
        return [], content

    try:
        call = ast.parse(f"_f({args_src})", mode="eval").body
        arguments = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
    except (SyntaxError, ValueError) as exc:
        logger.warning("Could not parse leaked tool call %r: %s", name, exc)
        return [], content

    tool_call = {
        "id": f"salvaged_{name}",
        "name": name,
        "arguments": json.dumps(arguments, ensure_ascii=False),
    }
    return [tool_call], ""
