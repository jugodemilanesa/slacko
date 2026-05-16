"""Serializers for the deterministic theoretical tutor API."""

from __future__ import annotations

from rest_framework import serializers

from .knowledge_base import Category, Concept


class CategorySerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    concept_count = serializers.IntegerField(required=False)


class ConceptSummarySerializer(serializers.Serializer):
    """Lightweight payload used in lists and as `related` references."""

    id = serializers.CharField()
    title = serializers.CharField()
    category = serializers.CharField()
    summary = serializers.CharField()


class ConceptDetailSerializer(serializers.Serializer):
    """Full concept payload — matches the canonical answer the tutor displays."""

    id = serializers.CharField()
    title = serializers.CharField()
    category = serializers.CharField()
    aliases = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()
    content = serializers.CharField()
    related = serializers.ListField(child=serializers.CharField())


def serialize_concept_summary(concept: Concept) -> dict:
    return {
        "id": concept.id,
        "title": concept.title,
        "category": concept.category,
        "summary": concept.summary,
    }


def serialize_concept_detail(concept: Concept) -> dict:
    return {
        "id": concept.id,
        "title": concept.title,
        "category": concept.category,
        "aliases": list(concept.aliases),
        "summary": concept.summary,
        "content": concept.content,
        "related": list(concept.related),
    }


def serialize_category(category: Category, concept_count: int | None = None) -> dict:
    payload = {
        "id": category.id,
        "title": category.title,
        "description": category.description,
    }
    if concept_count is not None:
        payload["concept_count"] = concept_count
    return payload


class QuerySerializer(serializers.Serializer):
    """Validates the body of POST /api/theory/query/."""

    question = serializers.CharField(min_length=1, max_length=500, trim_whitespace=True)
