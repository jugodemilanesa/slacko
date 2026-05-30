"""Deterministic LP model parser and validator.

This module is used when a JSON model is provided (either by the LLM in a tool
call, or from the REST API). It does NOT call an LLM — all extraction happens
in the orchestrator layer. This module only parses and validates.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .validator import ValidationError, validate_lp_model

logger = logging.getLogger(__name__)


def extract_lp_model(text: str) -> dict[str, Any]:
    """Parse and validate an LP model from a natural-language statement.

    DEPRECATED: The LLM now extracts the model directly in the orchestrator
    tool call. This function remains for backward compatibility with the REST
    API endpoint. It requires the text to contain embedded JSON.

    Args:
        text: The student's problem statement (must contain JSON).

    Returns:
        A dict matching the LPModel schema.

    Raises:
        ValidationError: If the extracted model fails validation.
        ValueError: If the text doesn't contain valid LP model JSON.
    """

    text = (text or "").strip()
    if not text:
        raise ValueError("Empty text")

    model = _parse_json_response(text)
    if isinstance(model, dict) and "error" in model:
        raise ValueError(f"Reported error: {model['error']}")

    validate_lp_model(model)
    return model


def _parse_json_response(raw: str) -> Any:
    """Robust JSON parsing: strip code fences, take first JSON object."""

    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise
