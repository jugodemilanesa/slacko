from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .engine import Constraint, solve
from .conversion import to_standard_form


class SolveView(APIView):
    """Solve a 2-variable LP problem and return vertex analysis + graph data."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request) -> Response:
        data = request.data
        constraints = [
            Constraint(
                coefficients=c["coefficients"],
                sign=c["sign"],
                rhs=c["rhs"],
                label=c.get("label", ""),
            )
            for c in data.get("constraints", [])
        ]

        result = solve(
            objective_coefficients=data["objective_coefficients"],
            sense=data["sense"],
            constraints=constraints,
        )

        return Response(
            {
                "vertices": [v.as_tuple() for v in result.vertices],
                "feasible_vertices": [v.as_tuple() for v in result.feasible_vertices],
                "optimal_point": result.optimal_point.as_tuple() if result.optimal_point else None,
                "optimal_value": result.optimal_value,
                "vertex_analysis": result.vertex_analysis,
            },
            status=status.HTTP_200_OK,
        )


class StandardFormView(APIView):
    """Convert an LP model to standard form."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request) -> Response:
        data = request.data
        result = to_standard_form(
            variables=data["variables"],
            objective_coefficients=data["objective_coefficients"],
            sense=data["sense"],
            constraints=data["constraints"],
        )
        return Response(result, status=status.HTTP_200_OK)
