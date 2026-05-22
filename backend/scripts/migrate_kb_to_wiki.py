"""One-shot script: migrate the in-memory KB into a markdown wiki on disk.

Reads ``apps.theory.knowledge_base`` (the Python tuples ``CATEGORIES`` and
``CONCEPTS``) and writes one ``.md`` file per concept under ``data/wiki/concepts/``
plus a generated ``data/wiki/index.md``.

After running this once, the Python module is rewritten to load from disk
(``apps/theory/loader.py``) and the hardcoded data goes away.

Usage:
    cd backend && python -m scripts.migrate_kb_to_wiki
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# Allow running as a plain script from anywhere inside the repo. We import the
# KB module directly without booting Django (it's pure dataclasses, no ORM).
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import yaml  # noqa: E402

from apps.theory.knowledge_base import CATEGORIES, CONCEPTS  # noqa: E402


WIKI_DIR = ROOT / "data" / "wiki"
CONCEPTS_DIR = WIKI_DIR / "concepts"
INDEX_PATH = WIKI_DIR / "index.md"


def _yaml_block(data: dict) -> str:
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=10_000,
    )


def write_concept(concept) -> Path:
    """Render one Concept to a Markdown file with YAML frontmatter."""

    frontmatter = {
        "name": concept.id,
        "title": concept.title,
        "category": concept.category,
        "aliases": list(concept.aliases),
        "related": list(concept.related),
        "sources": [],
        "updated": date.today().isoformat(),
        "summary": concept.summary,
    }

    body = concept.content.strip() + "\n"

    page = f"---\n{_yaml_block(frontmatter)}---\n\n# {concept.title}\n\n{body}"

    path = CONCEPTS_DIR / f"{concept.id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")
    return path


def write_index() -> Path:
    lines: list[str] = [
        "# Index del wiki",
        "",
        "_Autogenerado — no editar a mano. Regenerar con `python -m scripts.migrate_kb_to_wiki` o el lint del wiki._",
        "",
    ]

    by_category: dict[str, list] = {cat.id: [] for cat in CATEGORIES}
    for concept in CONCEPTS:
        by_category.setdefault(concept.category, []).append(concept)

    for cat in CATEGORIES:
        items = by_category.get(cat.id, [])
        if not items:
            continue
        lines.append(f"## {cat.title}")
        lines.append("")
        lines.append(f"_{cat.description}_")
        lines.append("")
        for concept in items:
            summary_one_line = concept.summary.replace("\n", " ").strip()
            lines.append(
                f"- [{concept.title}](concepts/{concept.id}.md) — {summary_one_line}"
            )
        lines.append("")

    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
    return INDEX_PATH


def main() -> None:
    CONCEPTS_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for concept in CONCEPTS:
        written.append(write_concept(concept))

    index = write_index()

    print(f"Wrote {len(written)} concept pages to {CONCEPTS_DIR}")
    print(f"Wrote index to {index}")


if __name__ == "__main__":
    main()
