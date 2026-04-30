"""Conversion between canonical and standard LP forms.

Handles adding slack, surplus, and artificial variables.
"""

from dataclasses import dataclass


@dataclass
class StandardConstraint:
    original_coefficients: list[float]
    sign: str
    rhs: float
    label: str
    slack_var: str | None = None
    surplus_var: str | None = None
    artificial_var: str | None = None
    equation: str = ""


def to_standard_form(
    variables: list[str],
    objective_coefficients: list[float],
    sense: str,
    constraints: list[dict],
) -> dict:
    """Convert an LP model to standard form.

    Adds slack (<=), surplus + artificial (>=), or artificial (=) variables.

    Returns a dict with the standard form representation.
    """
    slack_count = 0
    surplus_count = 0
    artificial_count = 0

    standard_constraints: list[StandardConstraint] = []

    for c in constraints:
        sc = StandardConstraint(
            original_coefficients=c["coefficients"],
            sign=c["sign"],
            rhs=c["rhs"],
            label=c.get("label", ""),
        )

        if c["sign"] == "<=":
            slack_count += 1
            sc.slack_var = f"s{slack_count}"
        elif c["sign"] == ">=":
            surplus_count += 1
            sc.surplus_var = f"e{surplus_count}"
            artificial_count += 1
            sc.artificial_var = f"a{artificial_count}"
        elif c["sign"] == "=":
            artificial_count += 1
            sc.artificial_var = f"a{artificial_count}"

        sc.equation = _build_equation(sc, variables)
        standard_constraints.append(sc)

    return {
        "variables": variables,
        "objective_coefficients": objective_coefficients,
        "sense": sense,
        "constraints": [
            {
                "label": sc.label,
                "original_coefficients": sc.original_coefficients,
                "original_sign": sc.sign,
                "rhs": sc.rhs,
                "slack_var": sc.slack_var,
                "surplus_var": sc.surplus_var,
                "artificial_var": sc.artificial_var,
                "equation": sc.equation,
            }
            for sc in standard_constraints
        ],
        "slack_variables": [
            sc.slack_var for sc in standard_constraints if sc.slack_var
        ],
        "surplus_variables": [
            sc.surplus_var for sc in standard_constraints if sc.surplus_var
        ],
        "artificial_variables": [
            sc.artificial_var for sc in standard_constraints if sc.artificial_var
        ],
    }


def _build_equation(sc: StandardConstraint, variables: list[str]) -> str:
    """Build the string representation of the standard form equation."""
    terms = []
    for i, coeff in enumerate(sc.original_coefficients):
        if coeff == 0:
            continue
        var = variables[i] if i < len(variables) else f"x{i + 1}"
        if coeff == 1:
            terms.append(var)
        elif coeff == -1:
            terms.append(f"-{var}")
        else:
            terms.append(f"{coeff}{var}")

    equation = " + ".join(terms).replace("+ -", "- ")

    if sc.slack_var:
        equation += f" + {sc.slack_var}"
    if sc.surplus_var:
        equation += f" - {sc.surplus_var}"
    if sc.artificial_var:
        equation += f" + {sc.artificial_var}"

    equation += f" = {sc.rhs}"
    return equation
