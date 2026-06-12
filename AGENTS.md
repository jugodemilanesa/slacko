# AGENTS.md — Slacko

Monorepo: `backend/` (Python/Django/Daphne/DRF), `frontend/` (SvelteKit).

## Alcance matemático (rígido)

Solo Programación Lineal continua, exactamente 2 variables, método gráfico. No Simplex, no entera/mixta, no >2 vars. Todo el stack lo presupone.

## LLM: no keys → modo determinístico

Si `backend/.env` no tiene `*_API_KEY`, el orquestador cae automáticamente a responder solo con el matcher del wiki (`data/wiki/concepts/*.md`). El frontend no necesita cambios. Útil para dev sin keys.

## Comandos

```bash
docker compose up -d                     # levantar todo (db + backend + frontend)
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend pytest        # tests backend (SQLite in-memory)
docker compose build backend && docker compose up -d backend   # rebuild tras requirements.txt
cd frontend && npm run dev               # frontend standalone
backend/config/settings/test.py          # DJANGO_SETTINGS_MODULE usado por pytest
```

## Arquitectura clave

- **ASGI vía Daphne** (no WSGI). `config.asgi:application` es la entrypoint.
- **Chat por WebSocket** (`ChatConsumer` en `chat/consumers.py`), no REST.
- **Orquestador** (`orchestrator/orchestrator.py`): loop multi-hop (hasta 5 hops) que alterna LLM → tool dispatch → LLM. Persistencia de mensajes es responsabilidad del caller.
- **LLM client** (`orchestrator/llm.py`): LiteLLM wrapper con fallback chain entre providers definidos en `settings.LLM_PROVIDERS`. Providers sin key se skipean.
- **Quota tracking** (`orchestrator/usage.py`): skipea preventivamente providers cerca de su techo RPM/RPD, contando `Message` rows en ventana de tiempo.
- **Rate limiter** (`chat/throttle.py`): in-memory, ventana deslizante por usuario + global. Por defecto 6/min por user, 9/min global. **No compartido entre workers**.
- **Prompt injection filter** (`chat/security.py`) en WebSocket antes de llegar al orquestador.
- **Tool-call-as-text leak recovery** en `llm.py`: Gemini a veces emite `tool_code` como texto plano en vez de tool_call estructurado. Salvage regex + `ast.parse` lo recupera.

## LP Model JSON (contrato entre todos los módulos)

Es la representación que fluye entre solver, formulation, orchestrator, y frontend. Schema descrito en `CLAUDE.md`. Validado por `formulation/validator.py`.

## Convenciones de código

- Python: black (88), isort (black profile), ruff. Type hints obligatorios en funciones públicas.
- Testing: pytest + pytest-django, SQLite in-memory (`test.py`), `--nomigrations`.
- Código en inglés, UI en español, commits en español, imperativo.
- Django apps en `backend/apps/` cada una con `urls.py`, `serializers.py`, `tests/`.
- Migraciones siempre commiteadas.
- Settings split: `base.py`, `local.py`, `production.py`, `test.py`.

## Wiki / RAG

- Conceptos curados en `data/wiki/concepts/*.md` (YAML frontmatter + markdown).
- Matcher determinístico (`theory/matcher.py`): token overlap + alias matching, sin embeddings.
- Para agregar conceptos: crear archivo `.md` en `data/wiki/concepts/`, actualizar `index.md` y `log.md`.

## Archivos de referencia

- `CLAUDE.md` — documentación completa de arquitectura y convenciones
- `docs/PROJECT_GUIDE.md` — guía para desarrolladores
- `docs/TPI - Slaking Sprint *.md` — especificaciones de sprints
