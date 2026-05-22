"""Tests for the orchestrator entry point.

Without an LLM provider configured the orchestrator must degrade gracefully
to the deterministic wiki matcher. With a provider, we mock litellm to keep
tests offline and reproducible.
"""

from __future__ import annotations

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
