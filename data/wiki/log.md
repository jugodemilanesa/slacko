# Log del wiki

Append-only. Cada operación sobre el wiki se registra acá.

## [2026-05-21] bootstrap | Migración inicial desde knowledge_base.py
- 32 conceptos migrados desde `apps/theory/knowledge_base.py` (`Concept` tuples) a `data/wiki/concepts/*.md`.
- 8 categorías registradas en `index.md`.
- `sources: []` en todas las páginas — pendiente backfill desde bibliografía cuando se ingesten PDFs.
