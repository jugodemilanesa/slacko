"""Load theory concepts from the markdown wiki on disk.

The wiki (`data/wiki/concepts/*.md`) is the source of truth. Each file has a
YAML frontmatter block followed by the markdown body. This loader parses every
file and exposes them as :class:`apps.theory.knowledge_base.Concept` dataclasses.

Caching: the wiki is parsed once at import time and held in module-level state.
For a dev server reload, restart Django.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from django.conf import settings


# ─── Schema ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Concept:
    """A single theoretical concept loaded from the wiki."""

    id: str
    title: str
    category: str
    aliases: tuple[str, ...]
    summary: str
    content: str
    related: tuple[str, ...] = field(default_factory=tuple)
    sources: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Category:
    """A grouping of concepts by topic."""

    id: str
    title: str
    description: str


# Categories are stable metadata — kept in code (also documented in SLACKO.md).
CATEGORIES: tuple[Category, ...] = (
    Category(
        id="fundamentos",
        title="Fundamentos",
        description="¿Qué es la Programación Lineal y por qué se llama así?",
    ),
    Category(
        id="supuestos",
        title="Supuestos del modelo",
        description="Las hipótesis que tiene que cumplir un problema para modelarse como PL.",
    ),
    Category(
        id="componentes",
        title="Componentes básicos",
        description="Las piezas que conforman cualquier modelo de PL.",
    ),
    Category(
        id="geometria",
        title="Geometría de la PL",
        description="Región factible, vértices y solución óptima.",
    ),
    Category(
        id="formas",
        title="Formas de representación",
        description="Forma canónica, forma estándar y conversión entre ambas.",
    ),
    Category(
        id="variables-auxiliares",
        title="Variables auxiliares",
        description="Holgura, excedente y artificial.",
    ),
    Category(
        id="metodo-grafico",
        title="Método gráfico",
        description="Resolución geométrica de problemas de PL con dos variables.",
    ),
    Category(
        id="casos-particulares",
        title="Casos particulares",
        description="Situaciones especiales que pueden aparecer en un modelo de PL.",
    ),
)


# ─── Parsing ──────────────────────────────────────────────────────────────


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def _wiki_dir() -> Path:
    """Resolve the wiki directory.

    Honors ``settings.WIKI_DIR`` when set; otherwise falls back to
    ``<repo-root>/data/wiki`` so tests and migrations Just Work.
    """

    configured = getattr(settings, "WIKI_DIR", None)
    if configured:
        return Path(configured)
    # backend/apps/theory/wiki_loader.py → repo root is 4 levels up.
    return Path(__file__).resolve().parents[3] / "data" / "wiki"


def _parse_page(path: Path) -> Concept:
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"Missing YAML frontmatter: {path}")

    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = text[match.end():].strip()

    # Strip the leading '# Title' if present — already in frontmatter.
    body = re.sub(r"^#[^\n]*\n+", "", body, count=1).strip()

    required = {"name", "title", "category", "summary"}
    missing = required - frontmatter.keys()
    if missing:
        raise ValueError(f"{path}: missing required fields {missing}")

    return Concept(
        id=str(frontmatter["name"]),
        title=str(frontmatter["title"]),
        category=str(frontmatter["category"]),
        aliases=tuple(frontmatter.get("aliases") or ()),
        summary=str(frontmatter["summary"]).strip(),
        content=body,
        related=tuple(frontmatter.get("related") or ()),
        sources=tuple(frontmatter.get("sources") or ()),
    )


def load_concepts() -> tuple[Concept, ...]:
    """Parse all ``concepts/*.md`` files. Sorted by category index then title."""

    concepts_dir = _wiki_dir() / "concepts"
    if not concepts_dir.exists():
        return ()

    concepts = [_parse_page(p) for p in concepts_dir.glob("*.md")]

    category_order = {cat.id: i for i, cat in enumerate(CATEGORIES)}
    concepts.sort(
        key=lambda c: (category_order.get(c.category, 999), c.title.lower())
    )
    return tuple(concepts)
