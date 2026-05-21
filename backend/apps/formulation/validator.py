"""Validate that an LPModel dict matches the Slacko schema and scope.

Catches the kinds of mistakes the LLM extractor (or a hand-written model)
might emit: wrong number of variables, missing fields, non-numeric coefs,
unsupported signs, etc.

Raises :class:`ValidationError` with a typed ``code`` for each failure so the
orchestrator can map it to a feedback template via the ``explain_error`` tool.
"""

from __future__ import annotations

from typing import Any


class ValidationError(ValueError):
    """Raised when an LPModel fails validation."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.details = details or {}


VALID_SIGNS = {"<=", ">=", "="}
VALID_SENSES = {"maximize", "minimize"}
MAX_VARIABLES = 2


def validate_lp_model(model: Any) -> None:
    """Validate the model in-place. Raises :class:`ValidationError` on failure."""

    if not isinstance(model, dict):
        raise ValidationError("BAD_TYPE", "El modelo debe ser un objeto JSON.")

    _require_keys(model, {"variables", "objective", "constraints"})

    variables = model.get("variables") or []
    if not isinstance(variables, list) or not variables:
        raise ValidationError(
            "missing_variable",
            "El modelo debe declarar al menos una variable.",
        )
    if len(variables) > MAX_VARIABLES:
        raise ValidationError(
            "more_than_two_variables",
            f"Slacko soporta como máximo {MAX_VARIABLES} variables (recibí {len(variables)}).",
            {"count": len(variables)},
        )

    objective = model.get("objective") or {}
    _validate_objective(objective, n_vars=len(variables))

    constraints = model.get("constraints") or []
    if not isinstance(constraints, list) or not constraints:
        raise ValidationError(
            "MISSING_CONSTRAINTS",
            "El modelo necesita al menos una restricción.",
        )
    for i, c in enumerate(constraints):
        _validate_constraint(c, n_vars=len(variables), index=i)

    if "non_negativity" in model and not isinstance(model["non_negativity"], bool):
        raise ValidationError("BAD_NON_NEGATIVITY", "`non_negativity` debe ser booleano.")


def _require_keys(d: dict, keys: set[str]) -> None:
    missing = keys - d.keys()
    if missing:
        raise ValidationError(
            "MISSING_FIELDS",
            f"Faltan campos requeridos: {sorted(missing)}",
            {"missing": sorted(missing)},
        )


def _validate_objective(obj: dict, *, n_vars: int) -> None:
    _require_keys(obj, {"sense", "coefficients"})
    if obj["sense"] not in VALID_SENSES:
        raise ValidationError(
            "BAD_OBJECTIVE_SENSE",
            f"`sense` debe ser uno de {sorted(VALID_SENSES)}.",
        )
    coefs = obj.get("coefficients") or []
    if len(coefs) != n_vars:
        raise ValidationError(
            "OBJECTIVE_COEF_COUNT",
            f"`objective.coefficients` debe tener {n_vars} valores (recibí {len(coefs)}).",
        )
    for c in coefs:
        if not isinstance(c, (int, float)):
            raise ValidationError("non_linear", "Coeficiente objetivo no numérico.")


def _validate_constraint(c: Any, *, n_vars: int, index: int) -> None:
    if not isinstance(c, dict):
        raise ValidationError("BAD_CONSTRAINT", f"Restricción #{index} no es objeto.")

    _require_keys(c, {"coefficients", "sign", "rhs"})

    if c["sign"] not in VALID_SIGNS:
        raise ValidationError(
            "wrong_inequality_direction",
            f"Signo inválido en restricción #{index}: {c['sign']!r}.",
            {"index": index},
        )

    coefs = c.get("coefficients") or []
    if len(coefs) != n_vars:
        raise ValidationError(
            "CONSTRAINT_COEF_COUNT",
            f"Restricción #{index}: esperaba {n_vars} coeficientes, recibí {len(coefs)}.",
        )
    for value in coefs:
        if not isinstance(value, (int, float)):
            raise ValidationError("non_linear", f"Coeficiente no numérico en restricción #{index}.")

    if not isinstance(c["rhs"], (int, float)):
        raise ValidationError("non_linear", f"RHS no numérico en restricción #{index}.")
