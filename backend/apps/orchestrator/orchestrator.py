"""Main orchestrator: routes each user message through LLM + tools.

The orchestrator is the brain of the chat. It:
1. Loads recent conversation history.
2. Calls the LLM with the tool contract.
3. Dispatches any tool calls deterministically.
4. Feeds tool results back to the LLM.
5. Repeats until the LLM produces a final text response (or max hops hit).

Falls back to a deterministic-only path when no LLM provider is configured —
useful for early development and demo environments without API keys.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings

from . import llm, tools

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Sos Slacko, un tutor de Programación Lineal para estudiantes de UTN.

ALCANCE:
- Programación Lineal continua, exactamente 2 variables de decisión.
- Método gráfico, vértices, análisis de sensibilidad básico.
- NO simplex, NO programación entera, NO más de 2 variables, NO no lineal.

CÓMO RESPONDÉS:
- Tono: cordial, breve, didáctico. Español rioplatense neutro.
- Si el alumno pregunta teoría, usá `theory_lookup` para citar el wiki.
- Si pega un enunciado, usá `parse_problem` para extraer el modelo.
- Si tiene un modelo y quiere resolver, usá `solve_lp` y narrá el resultado.
- Si nada de eso aplica, conversá normal (saludo, aclaración).

REGLAS DURAS:
- NUNCA inventes valores numéricos finales. Si hay que resolver, llamá `solve_lp`.
- NUNCA respondas teoría fuera del wiki. Si `theory_lookup` no matchea, decilo.
- Si el problema excede el alcance (3+ variables, no lineal, simplex), explicá amablemente que está fuera de alcance.
- Para responder al alumno, escribí tu respuesta en `content`. NO devuelvas solo tool calls sin texto al final.
"""


@dataclass
class TurnResult:
    """Outcome of one orchestrator turn (one user message in → one assistant out)."""

    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    provider: str = "deterministic"
    error: str | None = None


def _history_to_messages(session) -> list[dict[str, Any]]:
    """Load recent messages from the DB as OpenAI-style chat messages."""

    from apps.chat.models import Message

    qs = (
        Message.objects.filter(session=session)
        .order_by("-created_at")[:20]
    )
    history = list(reversed(list(qs)))

    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history:
        if m.role == "system":
            continue  # already injected
        messages.append({"role": m.role, "content": m.content})
    return messages


def _deterministic_fallback(user_text: str, session) -> TurnResult:
    """Best-effort response without an LLM: just try the theory matcher."""

    result = tools.dispatch_tool("theory_lookup", {"question": user_text}, session)

    if result.get("matched"):
        concept = result["concept"]
        body = f"**{concept['title']}**\n\n{concept['content']}"
        return TurnResult(
            content=body,
            tool_calls=[{"name": "theory_lookup", "result_summary": "matched"}],
            citations=[f"wiki/concepts/{concept['id']}.md"],
            provider="deterministic",
        )

    suggestions = result.get("suggestions") or []
    if suggestions:
        listed = ", ".join(s["title"] for s in suggestions[:3])
        msg = (
            "No tengo un proveedor LLM configurado todavía y no encontré un "
            f"concepto exacto en el wiki. ¿Querías preguntar sobre alguno de "
            f"estos? {listed}."
        )
    else:
        msg = (
            "No tengo un proveedor LLM configurado y no encontré nada en el "
            "wiki. Probá una pregunta más específica sobre Programación Lineal."
        )
    return TurnResult(
        content=msg,
        tool_calls=[{"name": "theory_lookup", "result_summary": "no_match"}],
        provider="deterministic",
    )


def run_turn(session, user_text: str) -> TurnResult:
    """Process one user message and return the assistant response.

    Persistence (saving Message rows) is the caller's responsibility — this
    function is pure orchestration so it stays testable.
    """

    user_text = (user_text or "").strip()
    if not user_text:
        return TurnResult(content="Decime en qué te puedo ayudar.", error="EMPTY_INPUT")

    if not llm.is_configured():
        return _deterministic_fallback(user_text, session)

    messages = _history_to_messages(session)
    messages.append({"role": "user", "content": user_text})

    aggregated_tool_calls: list[dict[str, Any]] = []
    citations: list[str] = []
    provider_used = "unknown"

    max_hops = getattr(settings, "LLM_MAX_HOPS", 5)

    for hop in range(max_hops):
        try:
            resp = llm.complete(messages, tools=tools.TOOLS, tool_choice="auto")
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLM call failed at hop %d", hop)
            # Fall back to deterministic.
            fb = _deterministic_fallback(user_text, session)
            fb.error = f"LLM_ERROR: {exc}"
            return fb

        provider_used = resp.provider

        if not resp.tool_calls:
            # LLM produced a final answer.
            return TurnResult(
                content=resp.content or "...",
                tool_calls=aggregated_tool_calls,
                citations=citations,
                provider=provider_used,
            )

        # Append the assistant message with tool calls.
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": resp.content or "",
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                    },
                }
                for tc in resp.tool_calls
            ],
        }
        messages.append(assistant_msg)

        # Run every tool call and feed results back.
        for tc in resp.tool_calls:
            tool_result = tools.dispatch_tool(tc["name"], tc["arguments"], session)
            aggregated_tool_calls.append(
                {
                    "name": tc["name"],
                    "arguments": tc["arguments"],
                    "result_summary": _summarize_result(tool_result),
                }
            )
            if tc["name"] == "theory_lookup" and tool_result.get("matched"):
                concept = tool_result.get("concept") or {}
                if concept.get("id"):
                    citations.append(f"wiki/concepts/{concept['id']}.md")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(tool_result, ensure_ascii=False),
                }
            )

    return TurnResult(
        content=(
            "Disculpá, me llevó demasiados pasos resolverlo. "
            "¿Lo intentamos en modo guiado paso a paso?"
        ),
        tool_calls=aggregated_tool_calls,
        citations=citations,
        provider=provider_used,
        error="MAX_HOPS_EXCEEDED",
    )


def _summarize_result(result: dict[str, Any]) -> str:
    if "error" in result:
        return f"error:{result.get('error')}"
    if result.get("matched"):
        return "matched"
    if result.get("ok"):
        return "ok"
    return "no_match"
