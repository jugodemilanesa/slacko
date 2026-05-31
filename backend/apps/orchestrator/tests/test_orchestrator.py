"""Tests for the orchestrator entry point.

Without an LLM provider configured the orchestrator must degrade gracefully
to the deterministic wiki matcher. With a provider, we mock litellm to keep
tests offline and reproducible.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from apps.orchestrator import llm as llm_module
from apps.orchestrator.orchestrator import run_turn


pytestmark = pytest.mark.django_db


@pytest.fixture
def chat_session(django_user_model):
    from apps.chat.models import Session

    user = django_user_model.objects.create_user(username="alumno", password="x")
    return Session.objects.create(user=user, mode="free")


def test_deterministic_fallback_when_no_llm_configured(chat_session, settings):
    settings.LLM_PROVIDERS = []  # no keys

    result = run_turn(chat_session, "¿Qué es la región factible?")

    assert result.provider == "deterministic"
    assert "factible" in result.content.lower() or "región" in result.content.lower()


def test_deterministic_fallback_no_match_lists_suggestions(chat_session, settings):
    settings.LLM_PROVIDERS = []

    result = run_turn(chat_session, "askdjflaskjdf qwerasdf")

    assert result.provider == "deterministic"
    # We expect either suggestions text or a "no encontré" hint.
    assert result.content


def test_orchestrator_with_mocked_llm_returns_content(chat_session, settings, monkeypatch):
    settings.LLM_PROVIDERS = [
        {"name": "test", "model": "test/echo", "api_key": "fake", "rpm": 100}
    ]

    fake_resp = llm_module.LLMResponse(
        content="Hola, soy Slacko.",
        tool_calls=[],
        finish_reason="stop",
        provider="test",
    )
    monkeypatch.setattr(llm_module, "complete", lambda *a, **kw: fake_resp)

    result = run_turn(chat_session, "hola")
    assert result.content == "Hola, soy Slacko."
    assert result.provider == "test"


def test_orchestrator_dispatches_tool_then_finalizes(chat_session, settings, monkeypatch):
    settings.LLM_PROVIDERS = [
        {"name": "test", "model": "test/echo", "api_key": "fake", "rpm": 100}
    ]

    # First hop: LLM asks for theory_lookup. Second hop: LLM produces final text.
    responses = iter(
        [
            llm_module.LLMResponse(
                content="",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "theory_lookup",
                        "arguments": '{"question": "qué es la región factible"}',
                    }
                ],
                finish_reason="tool_calls",
                provider="test",
            ),
            llm_module.LLMResponse(
                content="La región factible es el conjunto de puntos que cumplen todas las restricciones.",
                tool_calls=[],
                finish_reason="stop",
                provider="test",
            ),
        ]
    )
    monkeypatch.setattr(llm_module, "complete", lambda *a, **kw: next(responses))

    result = run_turn(chat_session, "qué es la región factible")
    assert "región factible" in result.content.lower() or "factible" in result.content.lower()
    assert any(tc["name"] == "theory_lookup" for tc in result.tool_calls)
    assert any("region-factible" in c for c in result.citations)


def test_orchestrator_dispatches_leaked_tool_call_end_to_end(
    chat_session, settings, monkeypatch
):
    """A provider that leaks its tool call as text must still drive a dispatch.

    Exercises the real normalization path (mocks ``litellm.completion``, not
    ``llm.complete``) so the salvage of ``tool_code print(default_api...)``
    runs for real and the orchestrator actually invokes the tool.
    """

    import sys

    settings.LLM_PROVIDERS = [
        {"name": "gemini", "model": "gemini/x", "api_key": "fake", "rpm": 100}
    ]

    def _resp(message):
        choice = SimpleNamespace(message=message, finish_reason="stop")
        return SimpleNamespace(choices=[choice])

    # Hop 1: leaked theory_lookup as text. Hop 2: clean final answer.
    completions = iter(
        [
            _resp(
                SimpleNamespace(
                    content=(
                        "tool_code print(default_api.theory_lookup("
                        "question='qué es la región factible')) thought ..."
                    ),
                    tool_calls=None,
                )
            ),
            _resp(
                SimpleNamespace(
                    content="La región factible es el conjunto de puntos válidos.",
                    tool_calls=None,
                )
            ),
        ]
    )
    fake_litellm = SimpleNamespace(completion=lambda **kw: next(completions))
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)
    from apps.orchestrator import usage

    monkeypatch.setattr(usage, "is_near_cap", lambda provider: False)

    result = run_turn(chat_session, "qué es la región factible")

    assert any(tc["name"] == "theory_lookup" for tc in result.tool_calls)
    assert "factible" in result.content.lower()
    # The raw leaked text must never reach the user.
    assert "tool_code" not in result.content
    assert "default_api" not in result.content


# ---------------------------------------------------------------------------
# Guided mode integration tests
# ---------------------------------------------------------------------------


def test_start_guided_mode_transitions_state(chat_session, settings, monkeypatch):
    """Starting guided mode via the tool changes session.mode and .state."""
    settings.LLM_PROVIDERS = [
        {"name": "test", "model": "test/echo", "api_key": "fake", "rpm": 100}
    ]

    responses = iter(
        [
            llm_module.LLMResponse(
                content="",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "start_guided_mode",
                        "arguments": '{"initial_text": "Una fábrica produce balones y juegos de ajedrez..."}',
                    }
                ],
                finish_reason="tool_calls",
                provider="test",
            ),
            llm_module.LLMResponse(
                content="¡Perfecto! Vamos paso a paso. Primero, decime el enunciado del problema.",
                tool_calls=[],
                finish_reason="stop",
                provider="test",
            ),
        ]
    )
    monkeypatch.setattr(llm_module, "complete", lambda *a, **kw: next(responses))

    result = run_turn(chat_session, "Quiero ayuda guiada con un problema")

    # Session should have been updated
    chat_session.refresh_from_db()
    assert chat_session.mode == "guided"
    assert chat_session.state == "INPUT_ENUNCIADO"
    assert result.provider == "test"


def test_guided_mode_full_flow(chat_session, settings, monkeypatch):
    """Full guided-mode walkthrough: 8 hops across the entire state machine."""
    settings.LLM_PROVIDERS = [
        {"name": "test", "model": "test/echo", "api_key": "fake", "rpm": 100}
    ]

    # Pre-set session to guided mode at the first step.
    chat_session.mode = "guided"
    chat_session.state = "INPUT_ENUNCIADO"
    chat_session.model_data = {}
    chat_session.save()

    # Each hop returns a tool call → then the next hop produces text.
    # We simulate the LLM calling parse_problem → validate_variables →
    # validate_objective → validate_constraint (×2) → convert_form → solve_lp.
    def mock_complete(*args, **kwargs):
        messages = args[0] if args else kwargs.get("messages", [])
        last_role = messages[-1]["role"] if messages else None
        n_tool_calls = sum(
            1 for m in messages if m.get("role") == "assistant" and m.get("tool_calls")
        )

        # Determine which step we're on based on state from the system prompt
        system_msgs = [m for m in messages if m["role"] == "system"]
        state_hint = ""
        if system_msgs:
            for line in system_msgs[-1]["content"].split("\n"):
                if "ESTADO ACTUAL" in line:
                    state_hint = line
                    break

        # Map state to expected next tool call
        if "INPUT_ENUNCIADO" in state_hint or "START" in state_hint:
            return llm_module.LLMResponse(
                content="",
                tool_calls=[{
                    "id": "call_p",
                    "name": "parse_problem",
                    "arguments": json.dumps({
                        "text": "Fabrica balones y ajedrez",
                        "model": {
                            "variables": [{"name": "x1", "type": "continuous"}, {"name": "x2", "type": "continuous"}],
                            "objective": {"sense": "maximize", "coefficients": [2, 4]},
                            "constraints": [
                                {"coefficients": [4, 6], "sign": "<=", "rhs": 120},
                            ],
                            "non_negativity": True,
                        },
                    }),
                }],
                finish_reason="tool_calls",
                provider="test",
            )
        elif "DEFINE_VARIABLES" in state_hint:
            return llm_module.LLMResponse(
                content="",
                tool_calls=[{
                    "id": "call_v",
                    "name": "validate_variables",
                    "arguments": json.dumps({
                        "variables": [
                            {"name": "x1", "label": "balones"},
                            {"name": "x2", "label": "ajedrez"},
                        ],
                    }),
                }],
                finish_reason="tool_calls",
                provider="test",
            )
        elif "DEFINE_OBJECTIVE" in state_hint:
            return llm_module.LLMResponse(
                content="",
                tool_calls=[{
                    "id": "call_o",
                    "name": "validate_objective",
                    "arguments": json.dumps({
                        "sense": "maximize",
                        "coefficients": [2, 4],
                    }),
                }],
                finish_reason="tool_calls",
                provider="test",
            )
        elif "BUILD_CONSTRAINTS" in state_hint:
            # First constraint
            if n_tool_calls == 0:
                return llm_module.LLMResponse(
                    content="",
                    tool_calls=[{
                        "id": "call_c1",
                        "name": "validate_constraint",
                        "arguments": json.dumps({
                            "label": "Máquina A",
                            "coefficients": [4, 6],
                            "sign": "<=",
                            "rhs": 120,
                            "is_last": True,
                        }),
                    }],
                    finish_reason="tool_calls",
                    provider="test",
                )
            return llm_module.LLMResponse(
                content="",
                tool_calls=[{
                    "id": "call_c2",
                    "name": "validate_constraint",
                    "arguments": json.dumps({
                        "label": "Máquina B",
                        "coefficients": [2, 6],
                        "sign": "<=",
                        "rhs": 72,
                        "is_last": True,
                    }),
                }],
                finish_reason="tool_calls",
                provider="test",
            )

        # After tool calls are exhausted, produce final text
        return llm_module.LLMResponse(
            content="Todo listo. Resolvamos el modelo.",
            tool_calls=[],
            finish_reason="stop",
            provider="test",
        )

    monkeypatch.setattr(llm_module, "complete", mock_complete)

    result = run_turn(chat_session, "arrancamos")

    assert result.provider == "test"
    assert result.hop_count >= 1
    assert result.content

    # Verify session state advanced from INPUT_ENUNCIADO
    chat_session.refresh_from_db()
    # We expect state to have advanced past constraint validation
    assert chat_session.mode == "guided"


def test_guided_mode_validate_variables_rejects_bad_input(chat_session, settings, monkeypatch):
    """When validate_variables returns ok=False, state should NOT advance."""
    settings.LLM_PROVIDERS = [
        {"name": "test", "model": "test/echo", "api_key": "fake", "rpm": 100}
    ]

    chat_session.mode = "guided"
    chat_session.state = "DEFINE_VARIABLES"
    chat_session.save()

    responses = iter([
        llm_module.LLMResponse(
            content="",
            tool_calls=[{
                "id": "call_bad",
                "name": "validate_variables",
                "arguments": json.dumps({
                    "variables": [
                        {"name": "x1", "label": "solo una"},
                    ],
                }),
            }],
            finish_reason="tool_calls",
            provider="test",
        ),
        # After getting the error, LLM asks the student to try again
        llm_module.LLMResponse(
            content="Necesitás dos variables. ¿Cuáles son las dos decisiones que tomás?",
            tool_calls=[],
            finish_reason="stop",
            provider="test",
        ),
    ])
    monkeypatch.setattr(llm_module, "complete", lambda *a, **kw: next(responses))

    result = run_turn(chat_session, "propongo x1")

    assert result.provider == "test"
    # State should NOT have advanced past DEFINE_VARIABLES
    chat_session.refresh_from_db()
    assert chat_session.state == "DEFINE_VARIABLES"
