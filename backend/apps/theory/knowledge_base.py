"""Curated theoretical concepts of Linear Programming for the deterministic tutor.

The wiki under ``data/wiki/concepts/*.md`` is the source of truth (one ``.md``
file per concept with YAML frontmatter — see ``data/wiki/SLACKO.md`` for the
schema). This module loads those files at import time and exposes the same
public surface as before the migration, so existing callers (matcher, views,
tests) keep working.

There is no LLM, no DB, no embeddings here. Just disk → dataclasses.
"""

from __future__ import annotations

from .wiki_loader import (
    CATEGORIES,
    Category,
    Concept,
    load_concepts,
)


CONCEPTS: tuple[Concept, ...] = load_concepts()


# ─── Index helpers ────────────────────────────────────────────────────────


CONCEPTS_BY_ID: dict[str, Concept] = {c.id: c for c in CONCEPTS}
CATEGORIES_BY_ID: dict[str, Category] = {c.id: c for c in CATEGORIES}


def get_concept(concept_id: str) -> Concept | None:
    """Return the concept with that id, or ``None`` if not found."""

    return CONCEPTS_BY_ID.get(concept_id)


def list_concepts(category: str | None = None) -> list[Concept]:
    """Return all concepts, optionally filtered by category id."""

    if category is None:
        return list(CONCEPTS)
    return [c for c in CONCEPTS if c.category == category]


def list_categories() -> list[Category]:
    """Return all categories in display order."""

    return list(CATEGORIES)


def category_counts() -> dict[str, int]:
    """Return a mapping ``category_id -> number_of_concepts``."""

    counts: dict[str, int] = {c.id: 0 for c in CATEGORIES}
    for concept in CONCEPTS:
        counts[concept.category] = counts.get(concept.category, 0) + 1
    return counts


__all__ = [
    "CATEGORIES",
    "CONCEPTS",
    "CATEGORIES_BY_ID",
    "CONCEPTS_BY_ID",
    "Category",
    "Concept",
    "category_counts",
    "get_concept",
    "list_categories",
    "list_concepts",
]
