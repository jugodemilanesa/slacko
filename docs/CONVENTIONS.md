# CONVENTIONS.md — Slacko

Convenciones técnicas y de proceso del proyecto Slacko (chatbot tutor de
Investigación Operativa, UTN — equipo SLAKING). Este documento se construye en
forma incremental: cada vez que se acuerda una práctica nueva en una sesión,
queda anotada acá para que las próximas sesiones (humanos o asistentes) sigan
el mismo criterio.

> **Cómo se usa:** cuando dudes sobre dónde poner algo o cómo nombrar algo,
> buscá primero acá. Si la convención no existe, definila y agregala.

---

## 1. Stack y arquitectura

| Capa | Tecnología | Notas |
|---|---|---|
| Backend | Django 5 + DRF + Channels | apps en `backend/apps/<nombre>/` |
| Frontend | SvelteKit 2 + Svelte 5 (runes) | TS estricto, Tailwind 4 |
| DB | PostgreSQL + pgvector | la extensión se crea en una migración con `RunSQL` idempotente |
| LLM | LiteLLM → OpenRouter (pendiente) | aún no integrado |
| Cálculo | NumPy / SciPy / PuLP | en `apps/solver/engine.py` |
| Plot | Plotly.js client-side | el backend devuelve JSON; nada de imágenes |
| Auth | JWT (`djangorestframework-simplejwt`) | tokens en `localStorage`, refresh manual |
| Tests backend | pytest + pytest-django | `pyproject.toml` con `[tool.pytest.ini_options]` |
| Tests frontend | svelte-check para tipos | sin runner E2E todavía |

### Estructura del monorepo

```
inv-op/
├── backend/apps/<feature>/        # una app Django por feature
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py                    # `app_name = "<feature>"`
│   ├── views.py                   # APIView por endpoint
│   ├── serializers.py             # validación DRF
│   ├── models.py                  # solo si hay persistencia
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_<modulo>.py
│   │   └── test_views.py
│   └── <modulos específicos>.py   # ej: matcher.py, knowledge_base.py, engine.py
├── frontend/src/
│   ├── lib/
│   │   ├── api/<feature>.ts       # cliente tipado por feature
│   │   ├── stores/<feature>.ts    # un store por feature/dominio
│   │   └── components/
│   │       ├── steps/             # un componente por estado del flujo guiado
│   │       └── <feature>/         # componentes auxiliares de cada feature
│   └── routes/                    # SvelteKit routing
├── docs/                          # sprints, este archivo, contenido teórico
└── data/bibliography/             # PDFs de la cátedra (read-only)
```

---

## 2. Idiomas

| Qué | Idioma |
|---|---|
| Variables, funciones, clases, módulos | **inglés** |
| Comentarios técnicos en código | **inglés** |
| Strings de UI, mensajes al usuario | **español rioplatense** ("vos") |
| Mensajes de commit, descripciones de PR | **español** |
| Docs (incluido este archivo) | **español** |

---

## 3. Backend (Python / Django)

### 3.1 Estilo

- `black` line-length 88, `ruff` con `["E", "F", "I", "W"]`, `isort` profile black.
- Type hints **obligatorios** en firmas públicas; `from __future__ import annotations`
  cuando ayuda a evitar imports en tiempo de ejecución.
- Docstrings Google-style **solo** en módulos y clases públicas; nunca docstring
  vacío ni paráfrasis del nombre.
- Imports ordenados (stdlib → terceros → locales).
- `dataclass(frozen=True)` para datos inmutables (ej: `Concept`, `Category`,
  `MatchResult`).

### 3.2 Apps Django

- Una app por feature (`solver`, `theory`, `chat`, `accounts`, etc.).
- En `apps.py`: `name = "apps.<feature>"`, `verbose_name` en español.
- Cada app trae su `urls.py` con `app_name`.
- Las URLs montadas siempre con `path("api/<feature>/", include("apps.<feature>.urls"))`
  desde `config/urls.py`.

### 3.3 API REST

- Una `APIView` por endpoint (no `ViewSet` salvo CRUD obvio).
- Permission `IsAuthenticated` por default; documentar excepciones (registro,
  refresh token).
- Serializers DRF para **validar entradas** (POST). Para responses helpers
  `serialize_<obj>(...)` que devuelven `dict`.
- Status codes:
  - `200` éxito GET / POST con resultado.
  - `400` validación falla (deja que DRF lo gestione con `is_valid(raise_exception=True)`).
  - `401` no autenticado.
  - `404` recurso no encontrado.
- Mensajes de error (`detail`) en **español**.

### 3.4 Migraciones

- Toda migración va al repo. Nunca `--fake` salvo última opción.
- Si una migración requiere extensiones de Postgres (ej: `pgvector`), se incluye
  como **primera operación** del initial con `RunSQL("CREATE EXTENSION IF NOT EXISTS …", reverse_sql=migrations.RunSQL.noop)`. Idempotente, sirve para test DB y prod.

### 3.5 Tests

- `pytest` + `pytest-django`. Tests en `apps/<feature>/tests/`.
- Patrón: `test_<modulo>.py` por archivo de producción.
- Estructura por clase (`class TestX`) cuando hay 3+ casos relacionados.
- Fixtures comunes en cada `test_views.py`: `user`, `auth_client`, `anon_client`.
- Verificar:
  - Auth (anon → 401).
  - Happy path (200 + payload esperado).
  - 404 / 400 cuando aplica.
- Tests de "integridad de datos curados" (sin duplicados de id, refs válidas,
  contenido no vacío) — ver `apps/theory/tests/test_matcher.py::TestKnowledgeBaseIntegrity`.

### 3.6 Patrones específicos

- **Knowledge bases curadas en código**: para datos pequeños y revisables (≤
  ~100 entradas) preferir `dataclass(frozen=True)` en un módulo Python (ej:
  `apps/theory/knowledge_base.py`) antes que tablas de DB. Más fácil de
  diff/code-review, deploy = restart. Cuando el volumen lo justifique se migra
  a modelo Django + admin.
- **Determinístico antes que LLM**: en cada feature, primero implementar el
  camino determinístico (matcher por aliases, rule-based, etc.) con su API y
  tests; recién después agregar la capa LLM como reemplazo o enriquecimiento.
  La API contractual no debe cambiar al hacer el switch.

---

## 4. Frontend (SvelteKit + Svelte 5)

### 4.1 Estilo

- `prettier` + `eslint` con config Svelte.
- TypeScript en todos los `<script>` (`<script lang="ts">`).
- **Svelte 5 runes**: `$state`, `$derived`, `$effect`, `$props`, `$bindable`.
  No usar la API legacy (`export let`, stores reactivos vía `$:`) en código nuevo.
- Naming:
  - Componentes: `PascalCase.svelte`.
  - Funciones / variables / props: `camelCase`.
  - Tipos / interfaces: `PascalCase`.
  - Stores: `camelCase` con sufijo descriptivo.

### 4.2 Organización

- **API clients** por feature en `lib/api/<feature>.ts`, tipados, una función por endpoint.
- **Stores** por feature en `lib/stores/<feature>.ts`. Mantener cada store enfocado;
  no acoplar `chat` con `theory`.
- **Componentes**:
  - Pasos del flujo guiado (state machine principal): `lib/components/steps/<Step>.svelte`.
  - Componentes auxiliares de un feature: `lib/components/<feature>/<X>.svelte`.
  - Globales (header, sidebar): `lib/components/<X>.svelte`.

### 4.3 State machine del chat

- El estado vive en `lib/stores/chat.ts` (`currentState: ChatState`).
- Estados que forman el **flujo guiado lineal** están en `STEP_ORDER`. Estados
  que son **parallel branches** (ej: `THEORY_QUERY`) **no** se incluyen en
  `STEP_ORDER` y se tratan aparte.
- `isGuidedFlow` derivado para esconder/mostrar la barra de progreso y la
  sidebar de modelo según corresponda.
- `advanceState()` solo avanza dentro de `STEP_ORDER`. Para entrar a una rama
  paralela usar `goToState('THEORY_QUERY')`.

### 4.4 Diseño visual

Sistema de design ya en `app.css` con `@theme` (Tailwind 4):

| Token | Valor | Uso |
|---|---|---|
| `--font-display` | Instrument Serif | títulos, hero, drop-caps |
| `--font-body` | Plus Jakarta Sans | cuerpo |
| `--font-mono` | JetBrains Mono | código, math, etiquetas tipo "01", kbd |
| `--color-surface` / `surface-warm` / `surface-card` | `#faf9f7` / `#f5f0eb` / `#fff` | fondos en tres niveles |
| `--color-ink` / `-light` / `-muted` | `#1a1a2e` / `#4a4a6a` / `#8888a4` | texto en tres niveles |
| `--color-primary` | indigo `#3b4cc0` | acción principal, focus, CTA |
| `--color-accent` | gold `#d4a853` | énfasis editorial, ornamentos, drop-cap, pills |
| `--color-success` / `warning` / `error` | verde / naranja / rojo | feedback semántico |

**Reglas de uso**:
- Botones primarios → `bg-primary text-white`.
- Pills / etiquetas / ornamentos cálidos → `accent` (con opacidad para fondos).
- Errores siempre con border-left de 3px en `--color-error` y fondo `rgba(212,72,72,0.07)`.
- Math inline: clase `.math` ya provista (mono + bg surface-warm + radius).

### 4.5 Markdown rendering

- Usar `marked` (instalado). Componente reusable en
  `lib/components/theory/MarkdownBody.svelte`. Estilos en `:global()` dentro del
  componente para mantenerlos encapsulados.
- Soportar mínimo: párrafos, **bold**, *italic*, `<ul>`/`<ol>`, blockquote,
  code inline (math), code blocks (ecuaciones multilínea).
- Listas ordenadas usan numeración mono `01, 02, ...` con `counter()` y color
  acento — coherente con el estilo editorial.

### 4.6 Microinteracciones

- Animaciones globales ya disponibles: `.step-enter` (slideUp 0.35s) y
  `.fade-in` (0.3s). Usarlas para entrada de paso/contenido.
- Hover en cards: `transition-all` + `translate-y(-1px)` + sombra suave.
- No usar emojis en UI a menos que el usuario lo pida explícitamente.

### 4.7 Strings y voz

- **Voseo rioplatense** ("podés", "querés", "tenés"). Nunca "tú".
- Tono: tutor amable, no infantilizante, no excesivamente formal.
- Microcopy:
  - Action labels cortos ("Preguntar", "Volver al inicio", "Ver alias").
  - Hints discretos ("Enter para preguntar · Shift+Enter para nueva línea").
  - Empty states con ornamento + 1-2 líneas + CTA visible.

---

## 5. Flujo de trabajo

### 5.1 Branches y commits

- Branches: `feature/<nombre>`, `fix/<nombre>`, `docs/<nombre>`.
- Commits en español, modo imperativo: "Agregar matcher determinístico", no
  "Agregado matcher".
- Trailers en commits que se hacen vía Claude:
  `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.

### 5.2 Antes de cerrar una sesión de trabajo

1. Tests backend: `pytest apps/<feature>/tests/` desde el container.
2. Static check frontend: `npm run check` desde el container.
3. Si la sesión deja convenciones nuevas → actualizar este archivo.
4. Si la sesión deja trabajo pendiente identificable → actualizar
   `pending_work` en memoria persistente.

### 5.3 Docker / dev local

- `docker-compose up` levanta DB, backend (daphne en `:8000`) y frontend (vite en `:5173`).
- Cambios en código Python: **el container actual usa daphne sin auto-reload**.
  Después de cambios en URLConf hay que reiniciar el container del backend
  (`docker compose restart backend`). Cambios en views/serializers que no
  alteran rutas suelen no necesitarlo.
- Cambios en frontend: vite hace HMR automático.
- Para correr comandos de Python fuera del container (no hay Python global del
  usuario), usar siempre `docker exec inv-op-backend-1 …`.

---

## 6. Convenciones específicas por módulo

### 6.1 `apps/solver/`

- Modelo internoLP en JSON ya documentado en CLAUDE.md (sección "Modelo de datos
  interno").
- `engine.py` calcula vértices, factibilidad, óptimo — **puro NumPy/itertools**.
- `conversion.py` transforma a forma estándar.
- Las views envuelven al motor; nunca lógica matemática en views.

### 6.2 `apps/theory/`

- **Knowledge base** en `knowledge_base.py`: `Concept` y `Category` como
  `@dataclass(frozen=True)`, listas tipadas exportadas (`CONCEPTS`, `CATEGORIES`).
- **Matcher** en `matcher.py`: pipeline determinístico
  `normalize → tokenize → score → MatchResult`. Los pesos
  (`_FULL_PHRASE_BONUS`, `_PHRASE_LENGTH_WEIGHT`, etc.) se ajustan con tests
  parametrizados en `test_matcher.py::TestMatch`.
- API:
  - `GET /api/theory/categories/` — listado con `concept_count`.
  - `GET /api/theory/concepts/?category=<id>` — listado, filtro opcional.
  - `GET /api/theory/concepts/<id>/` — detalle + `related`.
  - `POST /api/theory/query/ {question}` — match determinístico.
- Cada concepto tiene: `id` (slug), `title`, `category`, `aliases` (tuple), `summary`, `content` (markdown), `related` (tuple de ids).

### 6.3 `apps/orchestrator/` (pendiente)

- Pendiente de implementar. Contrato esperado: recibe mensaje + estado actual,
  decide pipeline (LLM | solver | RAG | template), devuelve respuesta + nuevo
  estado.

### 6.4 `apps/formulation/` (pendiente)

- Pendiente. Va a usar el "Diccionario de Patrones NLP" que está en
  `docs/TPI - Slaking - Preguntas teoricas.md` (sección final). Esos ejemplos
  resueltos (Ej. 4 y Ej. 2) son parte de **modo libre / extracción**, no del
  tutor teórico.

---

## 7. Decisiones tomadas y registradas

Cuando se toma una decisión arquitectónica importante en una sesión, va a
`memory/architecture_decisions.md` (memoria persistente del asistente). Las que
afectan código del día a día se reflejan acá. Las decisiones vivas a la fecha
de la última actualización:

- LP continua, 2 variables, método gráfico — alcance fijo.
- Orquestador central — todo mensaje pasa por él.
- State machine lineal para modo guiado, ramas paralelas para modo libre y
  consulta teórica.
- Modelo LP interno como contrato JSON entre módulos.
- Frontend stateless para lógica de negocio; toda la matemática vive en backend.
- Determinístico primero, LLM después — sin cambiar el contrato de API.

---

## 8. Cosas que **no** hacemos

- Ni `Simplex`, ni PL entera/mixta, ni más de 2 variables (fuera de scope).
- Ni OCR, ni manejo de imágenes (diferido).
- Ni feature flags ni shims de compatibilidad sin discusión previa.
- Ni docs auto-generados (ej: README.md, archivos `.md`) salvo que el usuario lo pida.
- Ni emojis en UI sin pedido explícito.
- Ni mocks en tests cuando el componente real corre rápido (preferir hits
  reales al solver / KB).

---

*Última actualización: 2026-04-30 — sesión de implementación del modo "Consulta
teórica" determinístico.*
