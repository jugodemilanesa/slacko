"""Tests for the provider-agnostic LLM client (``apps.orchestrator.llm``).

Two concerns are covered:

1. **Leaked tool-call salvage** — some providers (notably Gemini 2.5 Flash in
   thinking mode) emit their function call as plain text inside ``content``
   (``tool_code print(default_api.foo(...))``) instead of as a structured
   ``tool_calls`` entry. ``_normalize`` must detect and recover these so the
   orchestrator still dispatches the tool instead of showing raw garbage.
2. **Per-provider extra params** — providers can carry ``extra_params`` (e.g.
   ``reasoning_effort`` to disable Gemini thinking) that must reach LiteLLM.
"""

from __future__ import annotations

import json
import sys
from types import SimpleNamespace

from apps.orchestrator import llm as llm_module


def _fake_response(content, tool_calls=None):
    """Build a minimal object shaped like a LiteLLM completion response."""

    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    choice = SimpleNamespace(message=message, finish_reason="stop")
    return SimpleNamespace(choices=[choice])


# Reproduces the exact shape observed in the bug report screenshot.
LEAKED_CONTENT = (
    "tool_code print(default_api.parse_problem("
    "text='caso de prueba 1: maximización', "
    "model={'variables': [{'name': 'x1', 'label': 'Producto A', "
    "'type': 'continuous'}, {'name': 'x2', 'label': 'Producto B', "
    "'type': 'continuous'}], 'objective': {'sense': 'maximize', "
    "'coefficients': [50, 60]}, 'constraints': [{'label': 'Corte', "
    "'coefficients': [2, 4], 'sign': '<=', 'rhs': 40}]})) "
    "thought The user provided a problem statement. The parse_problem tool "
    "is suitable. ¡Excelente! Ya tengo el enunciado de tu problema."
)


def test_normalize_salvages_leaked_gemini_tool_call():
    resp = _fake_response(LEAKED_CONTENT, tool_calls=None)

    result = llm_module._normalize(resp, "gemini")

    assert len(result.tool_calls) == 1
    tc = result.tool_calls[0]
    assert tc["name"] == "parse_problem"

    args = json.loads(tc["arguments"])
    assert args["text"].startswith("caso de prueba 1")
    assert args["model"]["objective"]["sense"] == "maximize"
    assert args["model"]["objective"]["coefficients"] == [50, 60]
    assert args["model"]["constraints"][0]["rhs"] == 40

    # The raw leaked technical text must NOT survive into user-facing content.
    assert "tool_code" not in result.content
    assert "default_api" not in result.content
    assert "thought" not in result.content


def test_normalize_does_not_touch_normal_content():
    resp = _fake_response("Hola, soy Slacko. ¿En qué te ayudo?", tool_calls=None)

    result = llm_module._normalize(resp, "gemini")

    assert result.tool_calls == []
    assert result.content == "Hola, soy Slacko. ¿En qué te ayudo?"


def test_normalize_keeps_real_structured_tool_calls():
    real_tc = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(name="solve_lp", arguments='{"model": {}}'),
    )
    # Even if content happens to mention default_api, real tool_calls win and
    # content is left untouched (no spurious salvage).
    resp = _fake_response("texto normal", tool_calls=[real_tc])

    result = llm_module._normalize(resp, "groq")

    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["name"] == "solve_lp"
    assert result.content == "texto normal"


def test_complete_passes_provider_extra_params(settings, monkeypatch):
    """``extra_params`` on a provider must be forwarded to ``litellm.completion``."""

    settings.LLM_PROVIDERS = [
        {
            "name": "gemini",
            "model": "gemini/gemini-2.5-flash",
            "api_key": "fake",
            "rpm": 100,
            "extra_params": {"reasoning_effort": "none"},
        }
    ]

    captured = {}

    def fake_completion(**kwargs):
        captured.update(kwargs)
        return _fake_response("ok", tool_calls=None)

    fake_litellm = SimpleNamespace(completion=fake_completion)
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)
    monkeypatch.setattr(llm_module, "_active_providers", lambda: settings.LLM_PROVIDERS)
    from apps.orchestrator import usage

    monkeypatch.setattr(usage, "is_near_cap", lambda provider: False)

    llm_module.complete([{"role": "user", "content": "hola"}])

    assert captured.get("reasoning_effort") == "none"
