"""LP Solver engine for 2-variable linear programming problems.

Handles:
- Axis intersections
- Line-to-line intersections
- Feasible vertex filtering
- Optimal solution via vertex analysis
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class Vertex:
    x1: float
    x2: float

    def as_tuple(self) -> tuple[float, float]:
        return (self.x1, self.x2)


@dataclass
class Constraint:
    coefficients: list[float]
    sign: str  # "<=", ">=", "="
    rhs: float
    label: str = ""

    def satisfies(self, point: Vertex) -> bool:
        value = self.coefficients[0] * point.x1 + self.coefficients[1] * point.x2
        if self.sign == "<=":
            return value <= self.rhs + 1e-9
        elif self.sign == ">=":
            return value >= self.rhs - 1e-9
        else:
            return abs(value - self.rhs) < 1e-9


@dataclass
class LPResult:
    vertices: list[Vertex]
    feasible_vertices: list[Vertex]
    optimal_point: Vertex | None
    optimal_value: float | None
    vertex_analysis: list[dict]


def axis_intersections(constraint: Constraint) -> list[Vertex]:
    """Calculate where a constraint line crosses the axes."""
    a, b = constraint.coefficients
    rhs = constraint.rhs
    points = []

    if abs(a) > 1e-9:
        x1_intercept = rhs / a
        if x1_intercept >= -1e-9:
            points.append(Vertex(max(0, x1_intercept), 0))

    if abs(b) > 1e-9:
        x2_intercept = rhs / b
        if x2_intercept >= -1e-9:
            points.append(Vertex(0, max(0, x2_intercept)))

    return points


def line_intersection(c1: Constraint, c2: Constraint) -> Vertex | None:
    """Solve a 2x2 system to find where two constraint lines intersect."""
    A = np.array(
        [c1.coefficients, c2.coefficients],
        dtype=float,
    )
    b = np.array([c1.rhs, c2.rhs], dtype=float)

    try:
        solution: NDArray = np.linalg.solve(A, b)
        return Vertex(float(solution[0]), float(solution[1]))
    except np.linalg.LinAlgError:
        return None


def find_all_vertices(constraints: list[Constraint]) -> list[Vertex]:
    """Find all candidate vertices: axis intersections + pairwise intersections."""
    vertices: list[Vertex] = [Vertex(0, 0)]

    for c in constraints:
        vertices.extend(axis_intersections(c))

    for i in range(len(constraints)):
        for j in range(i + 1, len(constraints)):
            point = line_intersection(constraints[i], constraints[j])
            if point is not None:
                vertices.append(point)

    seen: set[tuple[float, float]] = set()
    unique: list[Vertex] = []
    for v in vertices:
        key = (round(v.x1, 6), round(v.x2, 6))
        if key not in seen:
            seen.add(key)
            unique.append(v)

    return unique


def filter_feasible(
    vertices: list[Vertex],
    constraints: list[Constraint],
) -> list[Vertex]:
    """Keep only vertices that satisfy all constraints and non-negativity."""
    feasible = []
    for v in vertices:
        if v.x1 < -1e-9 or v.x2 < -1e-9:
            continue
        if all(c.satisfies(v) for c in constraints):
            feasible.append(v)
    return feasible


def solve(
    objective_coefficients: list[float],
    sense: str,
    constraints: list[Constraint],
) -> LPResult:
    """Solve a 2-variable LP problem using vertex enumeration.

    Args:
        objective_coefficients: [c1, c2] for Z = c1*x1 + c2*x2
        sense: "maximize" or "minimize"
        constraints: list of Constraint objects
    """
    all_vertices = find_all_vertices(constraints)
    feasible = filter_feasible(all_vertices, constraints)

    if not feasible:
        return LPResult(
            vertices=all_vertices,
            feasible_vertices=[],
            optimal_point=None,
            optimal_value=None,
            vertex_analysis=[],
        )

    analysis = []
    for v in feasible:
        z = objective_coefficients[0] * v.x1 + objective_coefficients[1] * v.x2
        analysis.append({"x1": v.x1, "x2": v.x2, "z": z})

    if sense == "maximize":
        best = max(analysis, key=lambda a: a["z"])
    else:
        best = min(analysis, key=lambda a: a["z"])

    optimal_point = Vertex(best["x1"], best["x2"])

    return LPResult(
        vertices=all_vertices,
        feasible_vertices=feasible,
        optimal_point=optimal_point,
        optimal_value=best["z"],
        vertex_analysis=analysis,
    )
