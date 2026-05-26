"""Tool contract exposed to the LLM by the orchestrator.

Every capability of Slacko that can be triggered from natural-language input
is exposed here as a "tool" (in the OpenAI function-calling sense). The LLM
decides which tool to invoke; this module dispatches the call to the right
deterministic module (theory matcher, solver, formulation extractor, etc.).

Adding a new capability is a two-step process:
1. Append a tool definition to :data:`TOOLS`.
2. Add a handler to :data:`_HANDLERS`.

Handlers receive ``(args: dict, session)`` and return a JSON-serializable dict.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ─── Tool definitions (sent to the LLM) ───────────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "theory_lookup",
            "description": (
                "Buscá un concepto teórico de Programación Lineal en el wiki "
                "curado de Slacko. Usalo cuando el usuario pregunta qué es algo, "
                "cómo funciona un concepto, una definición o un supuesto. "
                "Devuelve título, resumen y contenido completo del concepto, "
                "más conceptos relacionados."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": (
                            "Pregunta literal o reformulada del usuario. "
                            "Mejor mantener la fraseología original."
                        ),
                    },
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "parse_problem",
            "description": (
                "Extraé un modelo de Programación Lineal a partir de un "
                "enunciado en lenguaje natural. Usalo cuando el mensaje del "
                "usuario describe un problema (menciona cantidades, recursos, "
                "maximizar/minimizar, restricciones)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Enunciado completo tal como lo escribió el usuario.",
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "solve_lp",
            "description": (
                "Resolvé un modelo de PL de 2 variables por método gráfico. "
                "Devuelve vértices, vértices factibles, punto óptimo y valor "
                "óptimo. Llamar después de tener un modelo validado."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "object",
                        "description": (
                            "LPModel JSON con variables, objective y constraints. "
                            "Schema en data/wiki/SLACKO.md."
                        ),
                    },
                },
                "required": ["model"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "graph_lp",
            "description": (
                "Generá los datos Plotly para el gráfico de la región factible. "
                "Llamar después de solve_lp."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {"type": "object"},
                },
                "required": ["model"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_form",
            "description": (
                "Convertí un modelo a forma estándar (slack/surplus/artificial) "
                "o canónica."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {"type": "object"},
                    "target": {
                        "type": "string",
                        "enum": ["standard", "canonical"],
                    },
                },
                "required": ["model", "target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_guided_mode",
            "description": (
                "Iniciá el modo guiado paso a paso de Slacko. Usar cuando "
                "el alumno pide ayuda guiada explícitamente o se nota que "
                "le vendría bien ir paso a paso."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "initial_text": {
                        "type": "string",
                        "description": "Enunciado del problema si está disponible.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_error",
            "description": (
                "Devolvé un mensaje pedagógico explicando un error específico "
                "de formulación (no negatividad, signo invertido, no lineal, etc.)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "error_type": {
                        "type": "string",
                        "enum": [
                            "non_negativity_missing",
                            "wrong_inequality_direction",
                            "missing_variable",
                            "unbounded",
                            "infeasible",
                            "non_linear",
                            "more_than_two_variables",
                        ],
                    },
                    "context": {
                        "type": "object",
                        "description": "Información adicional sobre el error.",
                    },
                },
                "required": ["error_type"],
            },
        },
    },
]


# ─── Handler implementations ──────────────────────────────────────────────


def _handle_theory_lookup(args: dict[str, Any], session) -> dict[str, Any]:
    from apps.theory.knowledge_base import get_concept
    from apps.theory.matcher import match
    from apps.theory.serializers import (
        serialize_concept_detail,
        serialize_concept_summary,
    )

    question = (args.get("question") or "").strip()
    if not question:
        return {"error": "MISSING_QUESTION"}

    result = match(question)

    if result.matched and result.concept is not None:
        related = [
            get_concept(rid) for rid in result.concept.related
        ]
        return {
            "matched": True,
            "score": result.score,
            "concept": serialize_concept_detail(result.concept),
            "related": [
                serialize_concept_summary(c) for c in related if c is not None
            ],
            "suggestions": [
                serialize_concept_summary(c) for c in result.suggestions
            ],
        }

    return {
        "matched": False,
        "score": result.score,
        "suggestions": [
            serialize_concept_summary(c) for c in result.suggestions
        ],
    }


def _handle_parse_problem(args: dict[str, Any], session) -> dict[str, Any]:
    from apps.formulation.extractor import extract_lp_model

    text = (args.get("text") or "").strip()
    if not text:
        return {"error": "MISSING_TEXT"}

    try:
        model = extract_lp_model(text)
        return {"ok": True, "model": model}
    except Exception as exc:  # noqa: BLE001
        logger.exception("parse_problem failed")
        return {"ok": False, "error": "PARSE_FAILED", "details": str(exc)}


def _handle_solve_lp(args: dict[str, Any], session) -> dict[str, Any]:
    from apps.formulation.validator import ValidationError, validate_lp_model
    from apps.solver.engine import Constraint as EngineConstraint, solve

    model = args.get("model") or {}
    try:
        validate_lp_model(model)
    except ValidationError as exc:
        return {"ok": False, "error": exc.code, "message": str(exc)}

    try:
        constraints = [
            EngineConstraint(
                coefficients=list(c["coefficients"]),
                sign=c["sign"],
                rhs=float(c["rhs"]),
                label=c.get("label", ""),
            )
            for c in model.get("constraints", [])
        ]
        objective = model.get("objective", {})
        coefs = list(objective.get("coefficients", []))
        sense = objective.get("sense", "maximize")

        result = solve(coefs, sense, constraints)

        if result.optimal_point is None:
            return {
                "ok": False,
                "error": "INFEASIBLE",
                "vertices": [{"x1": v.x1, "x2": v.x2} for v in result.vertices],
            }

        return {
            "ok": True,
            "vertices": [{"x1": v.x1, "x2": v.x2} for v in result.vertices],
            "feasible_vertices": result.vertex_analysis,
            "optimal_point": {
                "x1": result.optimal_point.x1,
                "x2": result.optimal_point.x2,
            },
            "optimal_value": result.optimal_value,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("solve_lp failed")
        return {"ok": False, "error": "SOLVE_FAILED", "details": str(exc)}


def _handle_graph_lp(args: dict[str, Any], session) -> dict[str, Any]:
    # Plotly data generation; for now delegate to solver result + frontend.
    # Returns a hint for the frontend to render with the computed solution.
    solved = _handle_solve_lp(args, session)
    if not solved.get("ok"):
        return solved
    return {
        "ok": True,
        "plot_payload": {
            "vertices": solved.get("vertices", []),
            "feasible_vertices": solved.get("feasible_vertices", []),
            "optimal_point": solved.get("optimal_point"),
            "constraints": args.get("model", {}).get("constraints", []),
        },
    }


def _handle_convert_form(args: dict[str, Any], session) -> dict[str, Any]:
    from apps.formulation.validator import ValidationError, validate_lp_model
    from apps.solver.conversion import to_standard_form

    model = args.get("model") or {}
    try:
        validate_lp_model(model)
    except ValidationError as exc:
        return {"ok": False, "error": exc.code, "message": str(exc)}

    target = args.get("target", "standard")
    try:
        if target == "standard":
            variables = [v["name"] for v in model.get("variables", [])]
            objective = model.get("objective", {})
            standard = to_standard_form(
                variables=variables,
                objective_coefficients=list(objective.get("coefficients", [])),
                sense=objective.get("sense", "maximize"),
                constraints=model.get("constraints", []),
            )
            return {"ok": True, "standard_form": standard}
        return {"ok": False, "error": f"UNSUPPORTED_TARGET:{target}"}
    except Exception as exc:  # noqa: BLE001
        logger.exception("convert_form failed")
        return {"ok": False, "error": "CONVERT_FAILED", "details": str(exc)}


def _handle_start_guided_mode(args: dict[str, Any], session) -> dict[str, Any]:
    from apps.chat.models import Session as ChatSession

    if session is not None and isinstance(session, ChatSession):
        session.mode = "guided"
        session.state = "INPUT_ENUNCIADO"
        if args.get("initial_text"):
            session.model_data = dict(session.model_data or {}, initial_text=args["initial_text"])
        session.save(update_fields=["mode", "state", "model_data", "updated_at"])

    return {
        "ok": True,
        "mode": "guided",
        "next_step": "INPUT_ENUNCIADO",
        "ui_action": "switch_to_guided_mode",
    }


def _handle_explain_error(args: dict[str, Any], session) -> dict[str, Any]:
    error_type = args.get("error_type")
    templates = {
        "non_negativity_missing": (
            "Falta la condición de no negatividad: en PL toda variable de "
            "decisión debe ser ≥ 0. Agregá x1 ≥ 0 y x2 ≥ 0 al modelo."
        ),
        "wrong_inequality_direction": (
            "Revisá el sentido de la desigualdad. Si la restricción "
            "representa una disponibilidad (\"se cuenta con\"), va como ≤. "
            "Si es un mínimo a cumplir (\"al menos\"), va como ≥."
        ),
        "missing_variable": (
            "Una de las variables aparece en algunas restricciones pero no en "
            "el objetivo (o viceversa). Verificá que x1 y x2 estén en todas "
            "las expresiones relevantes."
        ),
        "unbounded": (
            "La región factible no está acotada en la dirección de mejora. "
            "Esto suele indicar que falta una restricción: en la realidad "
            "ningún recurso es infinito."
        ),
        "infeasible": (
            "Las restricciones son incompatibles entre sí. Revisá si alguna "
            "demanda mínima supera la disponibilidad total."
        ),
        "non_linear": (
            "Encontré una expresión no lineal (potencias, productos entre "
            "variables, etc.). En PL todas las funciones deben ser lineales."
        ),
        "more_than_two_variables": (
            "El modelo tiene más de 2 variables. Slacko trabaja con el "
            "método gráfico, que solo cubre 2 variables. Para más variables "
            "necesitarías el método símplex."
        ),
    }
    return {
        "ok": True,
        "error_type": error_type,
        "message": templates.get(error_type, "Error no reconocido."),
        "context": args.get("context", {}),
    }


# ─── Dispatcher ───────────────────────────────────────────────────────────


_HANDLERS: dict[str, Callable[[dict[str, Any], Any], dict[str, Any]]] = {
    "theory_lookup": _handle_theory_lookup,
    "parse_problem": _handle_parse_problem,
    "solve_lp": _handle_solve_lp,
    "graph_lp": _handle_graph_lp,
    "convert_form": _handle_convert_form,
    "start_guided_mode": _handle_start_guided_mode,
    "explain_error": _handle_explain_error,
}


def dispatch_tool(name: str, raw_arguments: str | dict, session=None) -> dict[str, Any]:
    """Run the tool by name with the JSON arguments produced by the LLM."""

    if isinstance(raw_arguments, str):
        try:
            args = json.loads(raw_arguments) if raw_arguments else {}
        except json.JSONDecodeError as exc:
            return {"error": "INVALID_ARGUMENTS_JSON", "details": str(exc)}
    else:
        args = raw_arguments or {}

    handler = _HANDLERS.get(name)
    if handler is None:
        return {"error": "UNKNOWN_TOOL", "name": name}

    try:
        return handler(args, session)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Tool %s crashed", name)
        return {"error": "TOOL_CRASHED", "tool": name, "details": str(exc)}
