"""Smoke tests for the tool dispatcher.

These tests do NOT call any LLM; they verify the deterministic wiring between
the orchestrator's tool dispatcher and the underlying apps (theory matcher,
solver, conversion).
"""

from __future__ import annotations

import pytest

from apps.orchestrator.tools import TOOLS, dispatch_tool


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


def test_theory_lookup_matches_known_concept():
    result = dispatch_tool("theory_lookup", {"question": "qué es la región factible"})
    assert result["matched"] is True
    assert result["concept"]["id"] == "region-factible"


def test_theory_lookup_returns_suggestions_when_no_match():
    result = dispatch_tool("theory_lookup", {"question": "asdfqwerty"})
    assert result["matched"] is False
    assert isinstance(result["suggestions"], list)


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


def test_unknown_tool_returns_error():
    result = dispatch_tool("does_not_exist", {})
    assert result.get("error") == "UNKNOWN_TOOL"


def test_explain_error_returns_template():
    result = dispatch_tool("explain_error", {"error_type": "non_negativity_missing"})
    assert result["ok"] is True
    assert "no negatividad" in result["message"].lower()


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


def test_parse_problem_requires_llm():
    """Without an LLM provider configured, parse_problem reports the error."""

    result = dispatch_tool("parse_problem", {"text": "Una fábrica produce..."})
    # Either the extractor raised RuntimeError (caught by dispatch_tool and
    # reported as TOOL_CRASHED) or returned a typed PARSE_FAILED.
    assert result.get("ok") is False or "error" in result
