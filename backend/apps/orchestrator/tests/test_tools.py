"""Smoke tests for the tool dispatcher.

These tests do NOT call any LLM; they verify the deterministic wiring between
the orchestrator's tool dispatcher and the underlying apps (theory matcher,
solver, conversion).
"""

from __future__ import annotations

import pytest

from apps.orchestrator.tools import TOOLS, dispatch_tool


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------


def test_tools_contract_has_required_fields():
    """Every tool exposes the OpenAI function-calling shape."""

    names = set()
    for t in TOOLS:
        assert t["type"] == "function"
        fn = t["function"]
        assert "name" in fn and "description" in fn and "parameters" in fn
        names.add(fn["name"])

    # Core tools the orchestrator depends on must exist.
    assert {"theory_lookup", "parse_problem", "solve_lp"}.issubset(names)

    # New guided-mode validation tools must exist.
    for new_tool in ("validate_variables", "validate_objective", "validate_constraint",
                     "ask_clarifying_question", "show_progress_summary", "start_guided_mode"):
        assert new_tool in names, f"Missing tool: {new_tool}"


# ---------------------------------------------------------------------------
# Theory lookup
# ---------------------------------------------------------------------------


def test_theory_lookup_matches_known_concept():
    result = dispatch_tool("theory_lookup", {"question": "qué es la región factible"})
    assert result["matched"] is True
    assert result["concept"]["id"] == "region-factible"


def test_theory_lookup_returns_suggestions_when_no_match():
    result = dispatch_tool("theory_lookup", {"question": "asdfqwerty"})
    assert result["matched"] is False
    assert isinstance(result["suggestions"], list)


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------


def test_solve_lp_returns_optimum_for_balones_ajedrez():
    model = {
        "variables": [
            {"name": "x1", "type": "continuous"},
            {"name": "x2", "type": "continuous"},
        ],
        "objective": {"sense": "maximize", "coefficients": [2, 4]},
        "constraints": [
            {"coefficients": [4, 6], "sign": "<=", "rhs": 120, "label": "Máquina A"},
            {"coefficients": [2, 6], "sign": "<=", "rhs": 72, "label": "Máquina B"},
        ],
    }
    result = dispatch_tool("solve_lp", {"model": model})
    assert result["ok"] is True
    assert result["optimal_point"] is not None
    assert result["optimal_value"] is not None


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_unknown_tool_returns_error():
    result = dispatch_tool("does_not_exist", {})
    assert result.get("error") == "UNKNOWN_TOOL"


def test_explain_error_returns_template():
    result = dispatch_tool("explain_error", {"error_type": "non_negativity_missing"})
    assert result["ok"] is True
    assert "no negatividad" in result["message"].lower()


@pytest.mark.parametrize("error_type,keyword", [
    ("inconsistent_units", "unidades"),
    ("bad_variable_name", "nombre"),
    ("variable_not_in_objective", "objetivo"),
    ("unbounded", "acotada"),
    ("infeasible", "incompatibles"),
])
def test_explain_error_all_types(error_type, keyword):
    """Every error template has a Spanish message and the right key."""
    result = dispatch_tool("explain_error", {"error_type": error_type})
    assert result["ok"] is True
    assert result["error_type"] == error_type
    assert keyword in result["message"].lower()


# ---------------------------------------------------------------------------
# Form conversion
# ---------------------------------------------------------------------------


def test_convert_form_to_standard():
    model = {
        "variables": [{"name": "x1"}, {"name": "x2"}],
        "objective": {"sense": "maximize", "coefficients": [3, 5]},
        "constraints": [
            {"coefficients": [1, 2], "sign": "<=", "rhs": 10, "label": "R1"},
            {"coefficients": [1, 1], "sign": ">=", "rhs": 3, "label": "R2"},
        ],
    }
    result = dispatch_tool("convert_form", {"model": model, "target": "standard"})
    assert result["ok"] is True
    assert "s1" in result["standard_form"]["slack_variables"]
    assert "a1" in result["standard_form"]["artificial_variables"]


# ---------------------------------------------------------------------------
# Parse problem (deterministic path only — LLM provides the model)
# ---------------------------------------------------------------------------


def test_parse_problem_requires_text():
    """parse_problem returns MISSING_TEXT when no text is provided."""
    result = dispatch_tool("parse_problem", {})
    assert result.get("error") == "MISSING_TEXT"


def test_parse_problem_requires_model():
    """parse_problem returns MISSING_MODEL when LLM didn't extract a model."""
    result = dispatch_tool("parse_problem", {"text": "Una fábrica produce..."})
    assert result.get("error") == "MISSING_MODEL"


def test_parse_problem_with_model_validates():
    """parse_problem validates a model the LLM extracted."""
    model = {
        "variables": [{"name": "x1", "type": "continuous"}, {"name": "x2", "type": "continuous"}],
        "objective": {"sense": "maximize", "coefficients": [2, 4]},
        "constraints": [
            {"coefficients": [4, 6], "sign": "<=", "rhs": 120},
        ],
        "non_negativity": True,
    }
    result = dispatch_tool("parse_problem", {"text": "Fabrica balones...", "model": model})
    assert result["ok"] is True
    assert result["model"]["objective"]["sense"] == "maximize"


# ---------------------------------------------------------------------------
# Guided-mode tools
# ---------------------------------------------------------------------------


def test_validate_variables_ok():
    result = dispatch_tool("validate_variables", {
        "variables": [
            {"name": "x1", "label": "balones de fútbol"},
            {"name": "x2", "label": "juegos de ajedrez"},
        ],
    })
    assert result["ok"] is True
    assert len(result["variables"]) == 2


def test_validate_variables_wrong_count():
    result = dispatch_tool("validate_variables", {
        "variables": [
            {"name": "x1", "label": "balones"},
            {"name": "x2", "label": "ajedrez"},
            {"name": "x3", "label": "extra"},
        ],
    })
    assert result["ok"] is False
    assert any("2 variables" in f for f in result["feedback"])


def test_validate_variables_invalid_name():
    result = dispatch_tool("validate_variables", {
        "variables": [
            {"name": "123", "label": "balones"},
            {"name": "x2", "label": "ajedrez"},
        ],
    })
    assert result["ok"] is False
    assert any("válido" in f or "123" in f for f in result["feedback"])


def test_validate_variables_missing_label():
    result = dispatch_tool("validate_variables", {
        "variables": [
            {"name": "x1", "label": ""},
            {"name": "x2", "label": "ajedrez"},
        ],
    })
    assert result["ok"] is False
    assert any("descripción" in f for f in result["feedback"])


def test_validate_objective_ok():
    result = dispatch_tool("validate_objective", {
        "sense": "maximize",
        "coefficients": [3, 5],
    })
    assert result["ok"] is True
    assert result["objective"]["sense"] == "maximize"
    assert result["objective"]["coefficients"] == [3, 5]


def test_validate_objective_bad_sense():
    result = dispatch_tool("validate_objective", {
        "sense": "optimizar",
        "coefficients": [3, 5],
    })
    assert result["ok"] is False
    assert any("maximize" in f or "minimize" in f for f in result["feedback"])


def test_validate_objective_wrong_coeff_count():
    result = dispatch_tool("validate_objective", {
        "sense": "maximize",
        "coefficients": [3],
    })
    assert result["ok"] is False
    assert any("2 coeficientes" in f for f in result["feedback"])


def test_validate_constraint_ok():
    result = dispatch_tool("validate_constraint", {
        "label": "Máquina A",
        "coefficients": [4, 6],
        "sign": "<=",
        "rhs": 120,
    })
    assert result["ok"] is True
    assert result["constraint"]["sign"] == "<="
    assert result["constraint_count"] == 1


def test_validate_constraint_bad_sign():
    result = dispatch_tool("validate_constraint", {
        "coefficients": [4, 6],
        "sign": "==",
        "rhs": 120,
    })
    assert result["ok"] is False
    assert any("<=, >=" in f or "signo" in f for f in result["feedback"])


def test_validate_constraint_wrong_coeff_count():
    result = dispatch_tool("validate_constraint", {
        "coefficients": [4, 6, 8],
        "sign": "<=",
        "rhs": 120,
    })
    assert result["ok"] is False
    assert any("2 coeficientes" in f for f in result["feedback"])


def test_validate_constraint_bad_rhs():
    result = dispatch_tool("validate_constraint", {
        "coefficients": [4, 6],
        "sign": "<=",
        "rhs": "ciento veinte",
    })
    assert result["ok"] is False
    assert any("número válido" in f for f in result["feedback"])


def test_ask_clarifying_question():
    result = dispatch_tool("ask_clarifying_question", {
        "question": "¿Esto es por hora o por día?",
        "options": ["Por hora", "Por día"],
    })
    assert result["ok"] is True
    assert "hora" in result["question"]


def test_show_progress_summary_no_session():
    """Without a session the tool reports the error."""
    result = dispatch_tool("show_progress_summary", {"message": "Avancemos"})
    assert result.get("ok") is False or "error" in result


def test_start_guided_mode_no_session():
    """Without a DB session, start_guided_mode still returns ok with the mode."""
    result = dispatch_tool("start_guided_mode", {"initial_text": "Una fábrica..."})
    assert result["ok"] is True
    assert result["mode"] == "guided"
    assert result["next_step"] == "INPUT_ENUNCIADO"
