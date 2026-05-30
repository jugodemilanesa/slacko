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

from apps.orchestrator.states import ChatState, next_state

logger = logging.getLogger(__name__)


# ─── Helpers ───────────────────────────────────────────────────────────────


def _save_model_data(session, updates: dict[str, Any]) -> None:
    """Merge ``updates`` into ``session.model_data`` and persist."""
    from apps.chat.models import Session as ChatSession

    if session is None or not isinstance(session, ChatSession):
        return
    current = dict(session.model_data or {})
    current.update(updates)
    session.model_data = current
    session.save(update_fields=["model_data", "updated_at"])


def _advance_state(session) -> str | None:
    """Advance to the next state in the guided flow and persist."""
    from apps.chat.models import Session as ChatSession

    if session is None or not isinstance(session, ChatSession):
        return None
    next_s = next_state(session.state)
    if next_s is None:
        return None
    session.state = next_s
    session.save(update_fields=["state", "updated_at"])
    return next_s


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
                "Registrá un modelo de PL extraído del enunciado del usuario. "
                "PASALE el modelo completo ya estructurado en el campo `model`. "
                "El handler validará el schema automáticamente.\n\n"
                "Usalo cuando el usuario pega un enunciado (menciona cantidades, "
                "recursos, maximizar/minimizar, restricciones). Extraé vos mismo "
                "el modelo del texto y pasalo como JSON en `model`."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Enunciado completo tal como lo escribió el usuario.",
                    },
                    "model": {
                        "type": "object",
                        "description": (
                            "LPModel JSON con variables, objective y constraints. "
                            "Extraé esto del texto del usuario. Schema:\n"
                            '{"variables": [{"name": "x1", "label": "...", "type": "continuous"}], '
                            '"objective": {"sense": "maximize|minimize", "coefficients": [c1, c2]}, '
                            '"constraints": [{"label": "...", "coefficients": [a1, a2], "sign": "<=|>=|=", "rhs": b}]}'
                        ),
                    },
                },
                "required": ["text", "model"],
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
                            "Si no se pasa, usa el modelo guardado en la sesión."
                        ),
                    },
                },
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
            "name": "validate_variables",
            "description": (
                "Validá las variables de decisión propuestas por el alumno. "
                "Verificá que sean exactamente 2, tengan nombres con sentido, "
                "y no sean números o símbolos. Si está OK, guardalas y avanzá "
                "al siguiente paso. Si no, devolvé feedback pedagógico."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "variables": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Nombre de la variable (x1, x2, etc.)"},
                                "label": {"type": "string", "description": "Qué representa (ej: 'balones de fútbol')"},
                            },
                            "required": ["name", "label"],
                        },
                        "description": "Lista de exactamente 2 variables de decisión propuestas por el alumno.",
                    },
                    "context": {
                        "type": "string",
                        "description": "Escenario o enunciado para contextualizar el feedback.",
                    },
                },
                "required": ["variables"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validate_objective",
            "description": (
                "Validá la función objetivo propuesta por el alumno. "
                "Verificá sentido (max/min), coeficientes numéricos, "
                "y que tenga sentido con el escenario. "
                "Si está OK, guardala y avanzá al siguiente paso."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sense": {
                        "type": "string",
                        "enum": ["maximize", "minimize"],
                        "description": "Sentido de optimización.",
                    },
                    "coefficients": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Coeficientes de la función objetivo [c1, c2].",
                    },
                    "context": {
                        "type": "string",
                        "description": "Escenario para contextualizar el feedback.",
                    },
                },
                "required": ["sense", "coefficients"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validate_constraint",
            "description": (
                "Validá una restricción propuesta por el alumno. "
                "Verificá coeficientes, signo, RHS, y coherencia con el escenario. "
                "Si está OK, guardala. Llamá una vez por cada restricción."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "Etiqueta corta (ej: 'Máquina A', 'Materia prima').",
                    },
                    "coefficients": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Coeficientes [a1, a2] de la restricción.",
                    },
                    "sign": {
                        "type": "string",
                        "enum": ["<=", ">=", "="],
                        "description": "Tipo de desigualdad.",
                    },
                    "rhs": {
                        "type": "number",
                        "description": "Lado derecho de la restricción.",
                    },
                    "is_last": {
                        "type": "boolean",
                        "description": "Si es True, después de validar, avanzá al paso VALIDATE_MODEL.",
                    },
                    "context": {
                        "type": "string",
                        "description": "Escenario para contextualizar el feedback.",
                    },
                },
                "required": ["coefficients", "sign", "rhs"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_clarifying_question",
            "description": (
                "Hacé una pregunta aclaratoria al alumno cuando el enunciado "
                "tiene ambigüedades. Por ejemplo: 'esto es diario o mensual?', "
                "'te falta algún recurso?', 'cuál es el objetivo?'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Pregunta para el alumno.",
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Opciones sugeridas (opcional).",
                    },
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_progress_summary",
            "description": (
                "Mostrá un resumen de lo que el alumno ya definió hasta ahora. "
                "Usalo cuando el alumno pide ver su progreso o antes de pasar "
                "al siguiente paso importante."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Mensaje opcional del LLM para acompañar el resumen.",
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
                "de formulación (no negatividad, signo invertido, no lineal, etc.). "
                "Usalo para dar feedback cuando el alumno se equivoca."
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
                            "bad_variable_name",
                            "wrong_coefficient_count",
                            "variable_not_in_objective",
                            "variable_not_in_constraints",
                            "inconsistent_units",
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
    """Validate the model the LLM already extracted and persist it."""
    from apps.formulation.validator import ValidationError, validate_lp_model

    text = (args.get("text") or "").strip()
    model = args.get("model") or {}

    if not text:
        return {"error": "MISSING_TEXT"}
    if not model:
        return {"error": "MISSING_MODEL", "details": "El LLM debe extraer el modelo y pasarlo en el campo `model` del tool call."}

    try:
        validate_lp_model(model)
    except ValidationError as exc:
        return {"ok": False, "error": exc.code, "message": str(exc)}

    model["_raw_text"] = text

    _save_model_data(session, {"parsed_model": model, "scenario": model.get("scenario", {})})
    _advance_state(session)

    return {"ok": True, "model": model}


def _handle_solve_lp(args: dict[str, Any], session) -> dict[str, Any]:
    from apps.formulation.validator import ValidationError, validate_lp_model
    from apps.solver.engine import Constraint as EngineConstraint, solve

    model = args.get("model") or {}
    if not model and session is not None:
        model = (getattr(session, "model_data", None) or {}).get("parsed_model", {})
    if not model:
        return {"ok": False, "error": "MISSING_MODEL", "message": "No hay modelo para resolver."}

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
                "warning": result.warning,
                "vertices": [{"x1": v.x1, "x2": v.x2} for v in result.vertices],
            }

        response: dict[str, Any] = {
            "ok": True,
            "vertices": [{"x1": v.x1, "x2": v.x2} for v in result.vertices],
            "feasible_vertices": result.vertex_analysis,
            "optimal_point": {
                "x1": result.optimal_point.x1,
                "x2": result.optimal_point.x2,
            },
            "optimal_value": result.optimal_value,
        }
        if result.status != "optimal":
            response["ok"] = False
            response["degenerate_case"] = result.status
            response["warning"] = result.warning

        _save_model_data(session, {"solution": response})

        if session is not None and getattr(session, "state", None) in (ChatState.SOLVE_AND_GRAPH,):
            _advance_state(session)

        return response
    except Exception as exc:  # noqa: BLE001
        logger.exception("solve_lp failed")
        return {"ok": False, "error": "SOLVE_FAILED", "details": str(exc)}


def _handle_graph_lp(args: dict[str, Any], session) -> dict[str, Any]:
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
            _save_model_data(session, {"standard_form": standard})

            if session is not None and getattr(session, "state", None) in (ChatState.CONVERT_FORMS,):
                _advance_state(session)

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


def _handle_validate_variables(args: dict[str, Any], session) -> dict[str, Any]:
    variables = args.get("variables") or []
    context = args.get("context", "")

    feedback: list[str] = []

    if len(variables) != 2:
        feedback.append(
            "Necesitás exactamente 2 variables de decisión para usar el método gráfico. "
            "Identificá las dos cantidades principales que querés decidir."
        )

    for i, v in enumerate(variables):
        name = v.get("name", "").strip()
        label = v.get("label", "").strip()
        if not name:
            feedback.append(f"La variable {i+1} no tiene nombre.")
        elif name.isdigit() or (name.startswith("-") and name[1:].isdigit()):
            feedback.append(f"'{name}' no es un nombre válido de variable. Usá algo como 'x{i+1}' o un nombre descriptivo.")
        if not label:
            feedback.append(f"La variable '{name}' necesita una descripción de qué representa.")

    if feedback:
        return {"ok": False, "feedback": feedback}

    _save_model_data(session, {"variables": variables})
    _advance_state(session)

    return {
        "ok": True,
        "variables": variables,
        "feedback": ["Variables registradas correctamente."],
    }


def _handle_validate_objective(args: dict[str, Any], session) -> dict[str, Any]:
    sense = args.get("sense")
    coefficients = args.get("coefficients") or []
    context = args.get("context", "")

    feedback: list[str] = []

    if sense not in ("maximize", "minimize"):
        feedback.append("El sentido debe ser 'maximize' o 'minimize'.")
    if len(coefficients) != 2:
        feedback.append(f"Se necesitan exactamente 2 coeficientes (recibí {len(coefficients)}).")
    for c in coefficients:
        if not isinstance(c, (int, float)):
            feedback.append(f"El coeficiente {c} no es un número válido.")

    if feedback:
        return {"ok": False, "feedback": feedback}

    _save_model_data(session, {"objective": {"sense": sense, "coefficients": coefficients}})
    _advance_state(session)

    return {
        "ok": True,
        "objective": {"sense": sense, "coefficients": coefficients},
        "feedback": ["Función objetivo registrada correctamente."],
    }


def _handle_validate_constraint(args: dict[str, Any], session) -> dict[str, Any]:
    coefficients = args.get("coefficients") or []
    sign = args.get("sign")
    rhs = args.get("rhs")
    label = args.get("label", f"Restricción")
    context = args.get("context", "")
    is_last = args.get("is_last", False)

    feedback: list[str] = []

    if sign not in ("<=", ">=", "="):
        feedback.append(f"El signo '{sign}' no es válido. Usá <=, >=, o =.")
    if len(coefficients) != 2:
        feedback.append(f"Se necesitan exactamente 2 coeficientes (recibí {len(coefficients)}).")
    for c in coefficients:
        if not isinstance(c, (int, float)):
            feedback.append(f"El coeficiente {c} no es un número válido.")
    if not isinstance(rhs, (int, float)):
        feedback.append(f"El RHS {rhs} no es un número válido.")

    if feedback:
        return {"ok": False, "feedback": feedback}

    constraint = {"label": label, "coefficients": coefficients, "sign": sign, "rhs": rhs}
    current = dict(session.model_data or {}) if session is not None else {}
    existing = list(current.get("constraints", []))
    existing.append(constraint)
    _save_model_data(session, {"constraints": existing})

    if is_last:
        _advance_state(session)

    return {
        "ok": True,
        "constraint": constraint,
        "constraint_count": len(existing),
        "feedback": [f"Restricción '{label}' registrada correctamente."],
    }


def _handle_ask_clarifying_question(args: dict[str, Any], session) -> dict[str, Any]:
    """This tool just returns the question — the LLM already said it to the user."""
    question = args.get("question", "")
    options = args.get("options", [])

    _save_model_data(session, {"last_clarifying_question": question, "clarifying_options": options})

    return {
        "ok": True,
        "question": question,
        "options": options,
    }


def _handle_show_progress_summary(args: dict[str, Any], session) -> dict[str, Any]:
    from apps.chat.models import Session as ChatSession

    if session is None or not isinstance(session, ChatSession):
        return {"ok": False, "error": "NO_SESSION"}

    model_data = session.model_data or {}

    variables = model_data.get("variables", [])
    objective = model_data.get("objective", {})
    constraints = model_data.get("constraints", [])
    scenario = model_data.get("scenario", {})
    solution = model_data.get("solution", {})

    if objective and objective.get("coefficients"):
        obj_str = f"{'Max' if objective['sense'] == 'maximize' else 'Min'} Z = " + " + ".join(
            f"{c}x{i+1}" for i, c in enumerate(objective["coefficients"])
        )
    else:
        obj_str = "No definida aún"

    constraints_str = "\n".join(
        f"  {c.get('label', f'R{i+1}')}: {' + '.join(f'{a}x{j+1}' for j, a in enumerate(c['coefficients']))} {c['sign']} {c['rhs']}"
        for i, c in enumerate(constraints)
    ) if constraints else "  Ninguna aún"

    status = {
        "state": session.state,
        "mode": session.mode,
        "scenario_type": scenario.get("type", "No clasificado"),
        "variables_count": len(variables),
        "constraints_count": len(constraints),
    }

    summary_lines = [
        f"**Modo:** {session.mode} | **Paso:** {session.state}",
        f"**Escenario:** {scenario.get('description', 'No ingresado')}",
        "",
        "**Variables de decisión:**",
    ]
    if variables:
        for v in variables:
            summary_lines.append(f"  - {v['name']}: {v.get('label', 'Sin descripción')}")
    else:
        summary_lines.append("  (ninguna definida aún)")

    summary_lines.extend([
        "",
        f"**Función objetivo:** {obj_str}",
        "",
        "**Restricciones:**",
        constraints_str,
    ])

    if solution.get("ok"):
        sp = solution.get("optimal_point", {})
        sv = solution.get("optimal_value")
        summary_lines.extend([
            "",
            f"**Solución óptima:** x1={sp.get('x1')}, x2={sp.get('x2')}, Z={sv}",
        ])

    return {
        "ok": True,
        "summary": "\n".join(summary_lines),
        "status": status,
        "model_data": {
            "variables": variables,
            "objective": objective,
            "constraints": constraints,
            "solution_available": solution.get("ok", False),
        },
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
        "bad_variable_name": (
            "El nombre de la variable no parece válido. Usá nombres cortos "
            "como x1, x2 o palabras que representen cantidades a decidir "
            "(ej: 'balones', 'horas_taller')."
        ),
        "wrong_coefficient_count": (
            "Revisá la cantidad de coeficientes. Cada restricción debe tener "
            "exactamente un coeficiente por variable de decisión."
        ),
        "variable_not_in_objective": (
            "Una de las variables no aparece en la función objetivo. "
            "Revisá el enunciado: ¿todas las variables deberían contribuir al objetivo?"
        ),
        "variable_not_in_constraints": (
            "Una de las variables aparece en el objetivo pero no en ninguna "
            "restricción. Sin restricciones, esa variable puede crecer "
            "indefinidamente y el problema sería no acotado."
        ),
        "inconsistent_units": (
            "Parece haber una inconsistencia de unidades. Asegurate de que "
            "todas las cantidades estén en la misma base (horas, kg, unidades, etc.). "
            "Por ejemplo, si un recurso se mide en horas/día y otro en horas/semana, "
            "convertilos a una misma unidad."
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
    "validate_variables": _handle_validate_variables,
    "validate_objective": _handle_validate_objective,
    "validate_constraint": _handle_validate_constraint,
    "ask_clarifying_question": _handle_ask_clarifying_question,
    "show_progress_summary": _handle_show_progress_summary,
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
        result = handler(args, session)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("Tool %s crashed", name)
        return {"error": "TOOL_CRASHED", "tool": name, "details": str(exc)}
