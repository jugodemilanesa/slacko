"""LLM-based extractor: turn a natural-language problem statement into an LPModel.

The LLM is asked to return a JSON object matching the Slacko LPModel schema
(see ``data/wiki/SLACKO.md``). The result is then run through the validator
to enforce 2-variable / linear / well-formed constraints before any solver
call.

This module is provider-agnostic via :mod:`apps.orchestrator.llm`. If no
provider is configured the extractor raises ``RuntimeError`` and the caller
(tool dispatcher) reports a typed error to the LLM/UI.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps.orchestrator import llm

from .validator import ValidationError, validate_lp_model

logger = logging.getLogger(__name__)


EXTRACTOR_SYSTEM = """Sos un asistente especializado en extraer modelos de Programación Lineal a partir de enunciados en español.

Tu única salida válida es JSON. Nada de texto antes o después.

Schema esperado:
{
  "scenario": {
    "type": "resource_allocation | blending | production_lots | other",
    "description": "1-2 oraciones describiendo el escenario",
    "hypotheses": []
  },
  "variables": [
    {"name": "x1", "label": "qué representa x1 + unidad", "type": "continuous"},
    {"name": "x2", "label": "qué representa x2 + unidad", "type": "continuous"}
  ],
  "objective": {
    "sense": "maximize" | "minimize",
    "coefficients": [c1, c2],
    "expression": "Z = c1 x1 + c2 x2"
  },
  "constraints": [
    {
      "label": "etiqueta corta (ej: 'Máquina A')",
      "coefficients": [a1, a2],
      "sign": "<=" | ">=" | "=",
      "rhs": b,
      "expression": "a1 x1 + a2 x2 <op> b"
    }
  ],
  "non_negativity": true
}

REGLAS:
- Exactamente 2 variables (x1, x2). Si el enunciado tiene más, igual elegí las dos más relevantes y mencionalo en `hypotheses`.
- Coeficientes numéricos puros, sin texto. Si un coeficiente es desconocido, usá 0 y agregá una hipótesis explicando.
- `sense` debe ser "maximize" o "minimize" en inglés.
- Si el problema NO es de PL (no lineal, sin objetivo claro, etc.), devolvé {"error": "NOT_LP", "reason": "..."}.
- Si faltan datos clave, devolvé {"error": "MISSING_DATA", "missing": ["..."]}.
"""


def extract_lp_model(text: str) -> dict[str, Any]:
    """Extract an LPModel from a natural-language statement.

    Args:
        text: The student's problem statement.

    Returns:
        A dict matching the LPModel schema.

    Raises:
        RuntimeError: If no LLM provider is configured.
        ValidationError: If the extracted model fails validation.
        ValueError: If the LLM returned an error or invalid JSON.
    """

    if not llm.is_configured():
        raise RuntimeError(
            "parse_problem requiere un proveedor LLM configurado."
        )

    text = (text or "").strip()
    if not text:
        raise ValueError("Empty text")

    messages = [
        {"role": "system", "content": EXTRACTOR_SYSTEM},
        {"role": "user", "content": text},
    ]

    response = llm.complete(messages, temperature=0.0)
    raw = (response.content or "").strip()

    model = _parse_json_response(raw)

    if isinstance(model, dict) and "error" in model:
        raise ValueError(f"LLM reported error: {model['error']} ({model.get('reason') or model.get('missing')})")

    validate_lp_model(model)
    return model


def _parse_json_response(raw: str) -> Any:
    """Robust JSON parsing: strip code fences, take first JSON object."""

    text = raw.strip()
    if text.startswith("```"):
        # ```json ... ``` or ``` ... ```
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
        # Try to extract the first JSON object embedded in the response.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise
