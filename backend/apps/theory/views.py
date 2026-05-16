"""REST endpoints for the deterministic theoretical tutor.

These views wrap :mod:`apps.theory.knowledge_base` and :mod:`apps.theory.matcher`
and expose four read-only endpoints (no LLM, no DB hits):

* ``GET  /api/theory/categories/`` — list all categories with counts.
* ``GET  /api/theory/concepts/``   — list concepts (optional ``?category=`` filter).
* ``GET  /api/theory/concepts/<id>/`` — detail of a single concept.
* ``POST /api/theory/query/``      — search the knowledge base by free-form question.
"""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import knowledge_base as kb
from .matcher import match
from .serializers import (
    QuerySerializer,
    serialize_category,
    serialize_concept_detail,
    serialize_concept_summary,
)


class CategoryListView(APIView):
    """List the knowledge-base categories with their concept counts."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        counts = kb.category_counts()
        payload = [
            serialize_category(category, concept_count=counts.get(category.id, 0))
            for category in kb.list_categories()
        ]
        return Response({"categories": payload})


class ConceptListView(APIView):
    """List concepts. Optional query param ``category`` filters by category id."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        category = request.query_params.get("category")
        if category and category not in kb.CATEGORIES_BY_ID:
            return Response(
                {"detail": f"Categoría '{category}' no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        concepts = kb.list_concepts(category=category)
        return Response(
            {
                "concepts": [serialize_concept_summary(c) for c in concepts],
                "count": len(concepts),
            }
        )


class ConceptDetailView(APIView):
    """Return a single concept by id, including its related concept references."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request, concept_id: str) -> Response:
        concept = kb.get_concept(concept_id)
        if concept is None:
            return Response(
                {"detail": f"Concepto '{concept_id}' no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        related_concepts = [
            kb.get_concept(related_id)
            for related_id in concept.related
        ]
        return Response(
            {
                "concept": serialize_concept_detail(concept),
                "related": [
                    serialize_concept_summary(c)
                    for c in related_concepts
                    if c is not None
                ],
            }
        )


class TheoryQueryView(APIView):
    """Match a free-form question against the knowledge base (deterministic)."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question: str = serializer.validated_data["question"]

        result = match(question)

        if result.matched and result.concept is not None:
            related_concepts = [
                kb.get_concept(rid) for rid in result.concept.related
            ]
            return Response(
                {
                    "matched": True,
                    "score": result.score,
                    "concept": serialize_concept_detail(result.concept),
                    "related": [
                        serialize_concept_summary(c)
                        for c in related_concepts
                        if c is not None
                    ],
                    "suggestions": [
                        serialize_concept_summary(c) for c in result.suggestions
                    ],
                }
            )

        return Response(
            {
                "matched": False,
                "score": result.score,
                "concept": None,
                "related": [],
                "suggestions": [
                    serialize_concept_summary(c) for c in result.suggestions
                ],
                "message": (
                    "No encontré un concepto que coincida con tu pregunta. "
                    "Probá reformularla o elegí uno de los temas sugeridos."
                ),
            }
        )
