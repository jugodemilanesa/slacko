# CLAUDE.md — Slacko (Investigación Operativa - UTN)

## Proyecto

Chatbot educativo ("Slacko") para estudiantes de Investigación Operativa (UTN).
Asiste en la formulación, resolución gráfica e interpretación de problemas de Programación Lineal continua con 2 variables.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12+ · Django · Django REST Framework · Django Channels |
| Frontend | SvelteKit (consume API REST + WebSocket de Django) |
| Base de datos | PostgreSQL + pgvector |
| LLM | LiteLLM, multi-provider con fallback chain (Gemini → Groq → OpenRouter); degrada a modo determinístico si no hay keys |
| Cálculo | NumPy · SciPy · PuLP |
| Graficación | Plotly.js (client-side, interactivo) |
| Autenticación | JWT (djangorestframework-simplejwt) + dj-rest-auth + django-allauth (Google OAuth) |
| Tutor teórico | Wiki estilo Karpathy en `data/wiki/concepts/*.md` (YAML frontmatter + markdown); matcher determinístico por aliases. RAG con bibliografía PDF + embeddings pgvector pendiente. |

## Estructura del monorepo

```
inv-op/
├── backend/
│   ├── manage.py
│   ├── config/                  # settings, urls, asgi, wsgi
│   ├── apps/
│   │   ├── accounts/            # registro, login, JWT, UserProfile, Google OAuth
│   │   ├── chat/                # WebSocket consumer, JWT middleware, Session/Message + REST sidebar
│   │   ├── theory/              # wiki_loader (data/wiki/*.md → dataclasses), matcher, endpoints
│   │   ├── solver/              # motor LP: región factible, vértices, solución
│   │   ├── formulation/         # extractor LLM (texto → LPModel) + validator
│   │   └── orchestrator/        # cliente LLM (LiteLLM, multi-provider) + tools + loop multi-hop
│   └── scripts/
│       └── migrate_kb_to_wiki.py # one-shot: KB Python heredada → data/wiki/concepts/*.md
├── frontend/                    # SvelteKit app
├── docs/                        # sprints y documentación del TPI
├── data/
│   ├── wiki/
│   │   ├── SLACKO.md            # schema y reglas del wiki para el LLM mantenedor
│   │   ├── concepts/*.md        # 32 conceptos curados con YAML frontmatter
│   │   ├── index.md             # autogenerado
│   │   └── log.md               # append-only de cambios
│   └── bibliography/            # PDFs de la cátedra (read-only) — pendiente RAG real
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

## Arquitectura

### Flujo general

```
SvelteKit → (REST/WS) → Django → Orchestrator (LLM + tools)
                                       │
                  ┌────────────────────┼────────────────────┐
                  │              ┌─────┴─────┐              │
              theory_lookup   parse_problem  solve_lp    convert_form
              (wiki matcher)  (LLM extract) (NumPy)      (deterministic)
                              graph_lp · start_guided_mode · explain_error
```

### Orquestador

`apps/orchestrator/orchestrator.py` ejecuta un loop multi-hop (`LLM_MAX_HOPS=5` por default):

1. Carga las últimas 20 turnas del `Session` como historial OpenAI-style.
2. Llama al LLM con el system prompt + tool contract (`apps/orchestrator/tools.py`).
3. Si el LLM responde con `tool_calls`, despacha cada uno y feedea el resultado de vuelta.
4. Repite hasta que el LLM produzca texto final, o se llegue a `LLM_MAX_HOPS`.

**Tools disponibles (provider-agnostic, definidas como JSON Schema):**

| Tool | Cuándo | Módulo destino |
|---|---|---|
| `theory_lookup` | Pregunta teórica | wiki matcher (`apps/theory/matcher.py`) |
| `parse_problem` | Enunciado en lenguaje natural | `apps/formulation/extractor.py` (LLM) |
| `solve_lp` | Resolver modelo de 2 vars | `apps/solver/engine.py` |
| `graph_lp` | Datos para Plotly | solve + payload para frontend |
| `convert_form` | Forma estándar/canónica | `apps/solver/conversion.py` |
| `start_guided_mode` | Pasar a state machine guiada | actualiza `Session.mode/state` |
| `explain_error` | Feedback pedagógico tipado | templates inline en `tools.py` |

**Fallback determinístico:** si `is_configured()` da `False` (no hay keys), el orquestador responde solo con el matcher del wiki — sin LLM hops. El frontend no necesita cambios.

**LLM client (`apps/orchestrator/llm.py`):** wrapper sobre LiteLLM con fallback chain. Lista de proveedores y modelos en `settings.LLM_PROVIDERS`. Agregar uno es modificar settings + .env, no código.

### State machine (modo guiado)

```
START → SELECT_MODE
  ├→ LLM_CHAT (Chat libre)
  ├→ GUIDED (Paso a paso)
  │    ├→ INPUT_ENUNCIADO
  │    ├→ CLASSIFY_SCENARIO
  │    ├→ DEFINE_VARIABLES
  │    ├→ DEFINE_OBJECTIVE
  │    ├→ BUILD_CONSTRAINTS
  │    ├→ VALIDATE_MODEL
  │    ├→ CONVERT_FORMS
  │    ├→ SOLVE_AND_GRAPH
  │    └→ INTERPRET
  ├→ THEORY_QUERY (Consulta teórica)
  └→ TUTORIAL (Tutorial)
```

## Modelo de datos interno (LP Model)

Representación JSON que fluye por todos los módulos. Esta estructura es el contrato entre solver, formulation, orchestrator y frontend:

```json
{
    "scenario": {
        "type": "resource_allocation | blending | production_lots",
        "description": "texto libre describiendo el escenario",
        "hypotheses": ["lista de hipótesis detectadas"]
    },
    "variables": [
        {"name": "x1", "label": "balones", "type": "continuous"},
        {"name": "x2", "label": "ajedrez", "type": "continuous"}
    ],
    "objective": {
        "sense": "maximize | minimize",
        "coefficients": [2, 4],
        "expression": "Z = 2x1 + 4x2"
    },
    "constraints": [
        {
            "label": "Máquina A",
            "coefficients": [4, 6],
            "sign": "<= | >= | =",
            "rhs": 120,
            "expression": "4x1 + 6x2 <= 120"
        }
    ],
    "non_negativity": true,
    "standard_form": {
        "slack_variables": ["s1", "s2"],
        "surplus_variables": ["e1"],
        "artificial_variables": ["a1"],
        "constraints_eq": []
    },
    "solution": {
        "vertices": [{"x1": 0, "x2": 0}, "..."],
        "feasible_vertices": ["..."],
        "optimal_point": {"x1": 15, "x2": 10},
        "optimal_value": 70,
        "interpretation": "Se deben producir 15 balones y 10 sets de ajedrez..."
    }
}
```

## Alcance matemático

- **Solo** Programación Lineal continua
- **Solo** 2 variables de decisión
- **Solo** método gráfico + análisis de vértices
- No Simplex, no entera/mixta, no más de 2 variables

## Convenciones de código

### Python (backend)

- **Formatter:** `black` (line-length 88)
- **Linter:** `ruff`
- **Type hints:** obligatorios en firmas de funciones públicas
- **Testing:** `pytest` + `pytest-django`
- **Docstrings:** solo en módulos y clases públicas, formato Google style
- **Imports:** ordenados con `isort` (profile black)
- **Naming:**
  - Clases: `PascalCase`
  - Funciones/variables: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`
  - Apps Django: sustantivos en singular o plural descriptivo (`solver`, `accounts`, `chat`)
- **Django:**
  - Settings split: `base.py`, `local.py`, `production.py`
  - Cada app en `backend/apps/` con su propio `urls.py`, `serializers.py`, `tests/`
  - Serializers de DRF para validación de entrada/salida de la API
  - Models con `__str__` y `Meta.verbose_name`
  - Migraciones siempre commiteadas

### TypeScript / Svelte (frontend)

- **Formatter:** `prettier`
- **Linter:** `eslint` con config de Svelte
- **Naming:**
  - Componentes: `PascalCase.svelte`
  - Funciones/variables: `camelCase`
  - Tipos/interfaces: `PascalCase`
  - Stores: `camelCase` con sufijo descriptivo
- **Estilos:** Tailwind CSS o el sistema que se defina, sin CSS global suelto
- **Estado:** Svelte stores para estado compartido, props para estado local
- **API calls:** centralizar en un módulo `lib/api/` con funciones tipadas

### General

- **Idioma del código:** inglés (variables, funciones, clases, comentarios técnicos)
- **Idioma de la UI y mensajes al usuario:** español
- **Idioma de commits y PRs:** español
- **Branches:** `feature/<nombre>`, `fix/<nombre>`, `docs/<nombre>`
- **Commits:** mensaje descriptivo en español, imperativo ("Agregar módulo solver", no "Agregado módulo solver")
- **Autoría de commits:** no agregar atribución del asistente (sin líneas `Co-Authored-By: Claude` ni `Generated with Claude Code`). Los commits van solo a nombre del autor humano.
- **No commitear:** `.env`, credenciales, API keys, `__pycache__`, `node_modules`, `.venv`
- **Variables de entorno:** toda config sensible en `.env`, accedida via `django-environ` o equivalente

## Comandos frecuentes

```bash
# Backend
cd backend && python manage.py runserver          # servidor de desarrollo
cd backend && python manage.py migrate             # aplicar migraciones
cd backend && python -m scripts.migrate_kb_to_wiki # regenerar data/wiki desde la KB Python (one-shot)
cd backend && pytest                                # correr tests

# Frontend
cd frontend && npm run dev                         # servidor de desarrollo
cd frontend && npm run build                       # build de producción

# Docker (workflow habitual)
docker compose up -d                               # levantar todo en background
docker compose logs -f backend                     # ver logs
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose build backend && docker compose up -d backend   # tras cambios en requirements.txt
```

**Modo degradado sin LLM:** si `backend/.env` no tiene ninguna `*_API_KEY`, el orquestador detecta la ausencia y responde con el matcher determinístico del wiki. Útil para arrancar el stack sin keys.

## Contexto del proyecto

- **Materia:** Investigación Operativa, UTN
- **Equipo:** SLAKING
- **Chatbot:** "Slacko"
- **Objetivo:** demo funcional
- **Documentación de sprints:** `docs/`
