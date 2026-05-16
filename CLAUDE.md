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
| LLM | LiteLLM → OpenRouter (agnóstico al proveedor) |
| Cálculo | NumPy · SciPy · PuLP |
| Graficación | Plotly.js (client-side, interactivo) |
| Autenticación | JWT (djangorestframework-simplejwt) |
| RAG | pgvector para embeddings, ingesta via management command |

## Estructura del monorepo

```
inv-op/
├── backend/
│   ├── manage.py
│   ├── config/                  # settings, urls, asgi, wsgi
│   ├── apps/
│   │   ├── accounts/            # registro, login, JWT
│   │   ├── chat/                # WebSocket consumers, sesiones de chat
│   │   ├── theory/              # RAG: ingesta de PDFs, búsqueda semántica
│   │   ├── solver/              # motor LP: región factible, vértices, solución
│   │   ├── formulation/         # extracción de variables, restricciones, validación semántica
│   │   └── orchestrator/        # routing de intenciones, state machine del chat
│   ├── feedback_templates/      # templates de retroalimentación por tipo de error
│   └── scripts/
│       └── ingest_docs.py       # ingesta de bibliografía → embeddings
├── frontend/                    # SvelteKit app
├── docs/                        # sprints y documentación del TPI
├── data/
│   └── bibliography/            # PDFs de la cátedra (read-only)
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

## Arquitectura

### Flujo general

```
SvelteKit → (REST/WS) → Django → Orchestrator → { LiteLLM | Solver | RAG | Templates }
```

### Orquestador

El orquestador recibe cada mensaje del usuario y decide el pipeline:

- **Pregunta teórica** → RAG + LLM con contexto de bibliografía
- **Enunciado (modo libre)** → LLM extrae modelo → validación → Solver
- **Modo guiado** → State machine paso a paso con validaciones
- **Error de formulación** → Template de feedback
- **Solicitud de gráfico** → Solver calcula → datos JSON → Plotly renderiza en frontend
- **Conversión de forma** → Módulo determinista de conversión canónica/estándar

### State machine (modo guiado)

```
START → SELECT_MODE
  ├→ GUIDED
  │    ├→ INPUT_ENUNCIADO
  │    ├→ CLASSIFY_SCENARIO
  │    ├→ DEFINE_VARIABLES
  │    ├→ DEFINE_OBJECTIVE
  │    ├→ BUILD_CONSTRAINTS
  │    ├→ VALIDATE_MODEL
  │    ├→ CONVERT_FORMS
  │    ├→ SOLVE_AND_GRAPH
  │    └→ INTERPRET
  └→ FREE
       ├→ INPUT_MODEL
       ├→ PARSE_AND_VALIDATE
       ├→ SOLVE_AND_GRAPH
       └→ INTERPRET
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
- **No commitear:** `.env`, credenciales, API keys, `__pycache__`, `node_modules`, `.venv`
- **Variables de entorno:** toda config sensible en `.env`, accedida via `django-environ` o equivalente

## Comandos frecuentes

```bash
# Backend
cd backend && python manage.py runserver          # servidor de desarrollo
cd backend && python manage.py migrate             # aplicar migraciones
cd backend && python manage.py ingest_docs         # ingestar bibliografía
cd backend && pytest                                # correr tests

# Frontend
cd frontend && npm run dev                         # servidor de desarrollo
cd frontend && npm run build                       # build de producción

# Docker
docker-compose up                                  # levantar todo
docker-compose exec backend python manage.py migrate
```

## Contexto del proyecto

- **Materia:** Investigación Operativa, UTN
- **Equipo:** SLAKING
- **Chatbot:** "Slacko"
- **Objetivo:** demo funcional
- **Documentación de sprints:** `docs/`
