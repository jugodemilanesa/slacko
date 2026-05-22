# Slacko - Guía del Proyecto

## Qué es este proyecto

Slacko es un chatbot educativo para estudiantes de **Investigación Operativa** (UTN). Asiste en:

- **Tutoría teórica:** responde preguntas sobre conceptos de la materia consultando un wiki curado (`data/wiki/concepts/*.md`) — RAG sobre la bibliografía oficial está planeado pero pendiente.
- **Formulación de modelos:** guía al estudiante paso a paso para armar un modelo de Programación Lineal (variables, función objetivo, restricciones).
- **Resolución gráfica:** calcula la región factible, vértices, y muestra la solución óptima con gráficos interactivos.
- **Conversión de formas:** transforma el modelo a forma canónica y estándar (slack, surplus, artificial).

## Alcance actual

- Solo **Programación Lineal continua** con **2 variables**
- Solo **método gráfico + análisis de vértices** (no Simplex)
- Deploy **local** con Docker
- Sin OCR/imágenes por ahora

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 · Django 5.1 · DRF · Django Channels (WebSocket) |
| Frontend | SvelteKit · Tailwind CSS · Plotly.js (gráficos interactivos) |
| Base de datos | PostgreSQL 16 + pgvector (embeddings para RAG con bibliografía PDF — pendiente) |
| LLM | LiteLLM, multi-provider con fallback chain (Gemini → Groq → OpenRouter); degrada a modo determinístico sin keys |
| Cálculo | NumPy · SciPy · PuLP |
| Autenticación | JWT (djangorestframework-simplejwt) + dj-rest-auth + django-allauth (Google OAuth) |
| Tutor teórico | Wiki estilo Karpathy en `data/wiki/concepts/*.md` con YAML frontmatter; matcher determinístico por aliases |

## Estructura del monorepo

```
inv-op/
├── backend/                    # Django REST API + WebSocket
│   ├── config/                 # Settings (base/local/production), URLs, ASGI
│   ├── apps/
│   │   ├── accounts/           # Auth: register, login (JWT), UserProfile, Google OAuth
│   │   ├── chat/               # Modelos Session/Message, WebSocket consumer real, JWT middleware
│   │   ├── theory/             # wiki_loader (data/wiki/*.md → dataclasses), matcher, endpoints
│   │   ├── solver/             # Motor LP: engine.py (vértices), conversion.py (formas)
│   │   ├── formulation/        # extractor LLM (texto → LPModel) + validator
│   │   └── orchestrator/       # Cliente LLM (LiteLLM multi-provider) + tools + loop multi-hop
│   ├── scripts/
│   │   └── migrate_kb_to_wiki.py   # one-shot: KB Python → data/wiki/concepts/*.md
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # SvelteKit SPA
│   └── src/
│       ├── lib/api/            # Cliente HTTP con JWT, funciones de auth
│       ├── lib/stores/         # Svelte stores (auth state)
│       ├── lib/components/     # Componentes reutilizables
│       └── routes/             # Páginas: login, register, chat
├── data/
│   ├── wiki/                   # Fuente de verdad del tutor teórico (32 conceptos .md)
│   └── bibliography/           # PDFs de la cátedra (read-only) — RAG pendiente
├── docker/                     # Scripts de inicialización de DB
├── docs/                       # Sprints y documentación
├── docker-compose.yml          # PostgreSQL + backend + frontend
└── CLAUDE.md                   # Convenciones y guía para Claude Code
```

## Arquitectura

### Flujo de datos

```
Frontend (SvelteKit) → REST API / WebSocket → Django Orchestrator (LLM + tools)
                                                    │
                  ┌─────────────────────────────────┼─────────────────────────────────┐
                  │                  ┌──────────────┴──────────────┐                  │
              theory_lookup      parse_problem (LLM)   solve_lp (NumPy)        convert_form
              (wiki matcher)     graph_lp · start_guided_mode · explain_error
```

### Orquestador

`apps/orchestrator/orchestrator.py` corre un loop multi-hop con LiteLLM:

1. Carga las últimas turnas del `Session` como historial OpenAI-style.
2. Llama al LLM con un tool contract (definido en `apps/orchestrator/tools.py`).
3. Si el LLM devuelve `tool_calls`, los despacha y feedea los resultados.
4. Repite hasta texto final o `LLM_MAX_HOPS` (default 5).

| Tool | Cuándo se invoca | Módulo destino |
|---|---|---|
| `theory_lookup` | Pregunta teórica | `apps/theory/matcher.py` (wiki) |
| `parse_problem` | Enunciado en lenguaje natural | `apps/formulation/extractor.py` (LLM) |
| `solve_lp` | Resolver modelo | `apps/solver/engine.py` |
| `graph_lp` | Datos para Plotly | solve + payload para frontend |
| `convert_form` | Forma estándar/canónica | `apps/solver/conversion.py` |
| `start_guided_mode` | Pasar a guiado paso a paso | actualiza `Session.mode/state` |
| `explain_error` | Feedback pedagógico tipado | templates inline en `tools.py` |

**Modo degradado:** si `apps/orchestrator/llm.is_configured()` es `False` (no hay keys), el orquestador responde solo con el matcher determinístico del wiki — sin LLM hops, sin cambios en el frontend.

### State machine (modo guiado)

El modo guiado sigue una secuencia de estados que se persisten en `Session.state` (`apps/chat/models.py`). El orquestador transiciona vía la tool `start_guided_mode`:

```
START → SELECT_MODE → GUIDED | FREE
  GUIDED: INPUT_ENUNCIADO → CLASSIFY_SCENARIO → DEFINE_VARIABLES → DEFINE_OBJECTIVE
          → BUILD_CONSTRAINTS → VALIDATE_MODEL → CONVERT_FORMS → SOLVE_AND_GRAPH → INTERPRET
  FREE:   INPUT_MODEL → PARSE_AND_VALIDATE → SOLVE_AND_GRAPH → INTERPRET
```

### Modelo LP interno (contrato entre módulos)

Todos los módulos comparten esta estructura JSON para representar un problema LP:

```json
{
    "scenario": { "type": "resource_allocation", "description": "...", "hypotheses": [] },
    "variables": [
        {"name": "x1", "label": "balones", "type": "continuous"},
        {"name": "x2", "label": "ajedrez", "type": "continuous"}
    ],
    "objective": { "sense": "maximize", "coefficients": [2, 4] },
    "constraints": [
        {"label": "Máquina A", "coefficients": [4, 6], "sign": "<=", "rhs": 120}
    ],
    "non_negativity": true
}
```

## API endpoints

### Auth (`/api/auth/`)

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/auth/register/` | Registrar usuario (legacy, sigue funcionando) |
| POST | `/api/auth/login/` | Obtener JWT (access + refresh) |
| POST | `/api/auth/refresh/` | Refrescar access token |
| GET | `/api/auth/me/` | Datos del usuario autenticado |
| GET | `/api/auth/user/` | Detalle del usuario (dj-rest-auth) |
| POST | `/api/auth/password/reset/` | Reset password (dj-rest-auth) |
| POST | `/api/auth/registration/` | Registro alternativo (dj-rest-auth) |
| POST | `/api/auth/google/` | Login con Google (id_token o code) |

### Chat (`/api/chat/`)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/chat/sessions/` | Listar sesiones del usuario (sidebar) |
| POST | `/api/chat/sessions/` | Crear nueva sesión |
| GET | `/api/chat/sessions/<uuid>/` | Detalle con mensajes |
| PATCH | `/api/chat/sessions/<uuid>/` | Rename / archive / pin |
| DELETE | `/api/chat/sessions/<uuid>/` | Eliminar |
| GET | `/api/chat/sessions/<uuid>/messages/` | Mensajes paginados |
| GET | `/api/chat/sessions/search/?q=...` | Buscar sesiones/mensajes |
| WS | `/ws/chat/<uuid>/?token=<jwt>` | Chat en tiempo real (rutea por el orquestador) |

### Solver / Theory

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/solver/solve/` | Resolver problema LP (vertex analysis) |
| POST | `/api/solver/standard-form/` | Convertir a forma estándar |
| GET | `/api/theory/concepts/` | Listar conceptos del wiki |
| GET | `/api/theory/concepts/<id>/` | Detalle de un concepto |
| POST | `/api/theory/query/` | Consulta teórica (matcher) |

Todos los endpoints (excepto `register` y `login`) requieren header `Authorization: Bearer <token>`. El WebSocket valida el JWT vía el parámetro `?token=...` (ver `apps/chat/middleware.py`).

## Cómo levantar el proyecto

```bash
# 1. Clonar y entrar al directorio
git clone <repo-url> && cd inv-op

# 2. Copiar variables de entorno
cp backend/.env.example backend/.env
# Opcional: cargá una key en GEMINI_API_KEY (https://aistudio.google.com/apikey)
# Sin keys el chat funciona en modo determinístico (solo matcher del wiki).

# 3. Levantar con Docker
docker compose up -d

# 4. Verificar que todo esté corriendo
docker compose ps

# 5. Acceder
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/api/
# Admin Django: http://localhost:8000/admin/
```

### Crear superusuario para el admin

```bash
docker compose exec backend python manage.py createsuperuser
```

### Ver logs

```bash
docker compose logs -f backend    # logs del backend
docker compose logs -f frontend   # logs del frontend
docker compose logs -f db         # logs de PostgreSQL
```

### Reconstruir después de cambios

```bash
# Cambios en requirements.txt → rebuild del backend
docker compose build backend && docker compose up -d backend

# Cambios en package.json → rebuild del frontend
docker compose build frontend && docker compose up -d frontend

# Nuevos modelos Django → generar y aplicar migraciones
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

## Convenciones de código

- **Idioma del código:** inglés
- **Idioma de UI/commits:** español
- **Python:** formateado con `black`, linting con `ruff`, imports con `isort`, tests con `pytest`
- **Frontend:** formateado con `prettier`, linting con `eslint`
- **Branches:** `feature/<nombre>`, `fix/<nombre>`, `docs/<nombre>`
- **Commits:** imperativo en español ("Agregar endpoint de solver")

Ver `CLAUDE.md` en la raíz del proyecto para la guía completa.

## Qué queda por implementar

> Última actualización: 2026-05-21, tras integrar frontend del modo LLM,
> rate limiter, defensa contra prompt injection y cherry-pick multi-provider.

### Prioridad alta — cerrar el ciclo del modo LLM
1. **Verificación E2E en browser** — abrir `http://localhost:5173`, loguearse,
   click "Chat con Slacko" en el SelectMode. Probar: (a) pregunta teórica → 
   citation abre drawer del wiki; (b) enunciado completo → parsea, muestra
   artifact; (c) sidebar de historial → list/pin/archive/delete; (d) suggestion
   chips → prellenan composer; (e) banner de error con retry tras desconexión
   del WS.
2. **Persistir tool payloads para Plotly desde `graph_lp`** — la tool ya
   devuelve `plot_payload` con vertices/feasible_vertices/optimal_point. Hoy
   `SolveLpArtifact.svelte` muestra un placeholder porque el orquestador no
   guarda el payload estructurado. Cambios: (a) `apps/chat/consumers.py` debe
   incluir `turn.tool_results` en `Message.metadata`; (b) `SolveLpArtifact`
   tiene que parsearlo y renderizar `<SolutionArtifacts variant="compact" />`.
3. **Landing page** — hoy `/` redirige directo a `/chat` o `/login`. Sumar
   una landing con hero + 4 cards (los modos) + CTAs sign-in/register.

### Prioridad media — defense in depth + RAG
4. **Post-filter classifier de prompt injection** — opcional, una segunda
   llamada barata (Flash/Haiku) que pregunta "¿esta respuesta es sobre PL? si/no".
   Hoy hay SYSTEM_PROMPT endurecido + pre-filter por regex; este sería la
   tercer capa.
5. **Logging persistente de blocks** — `apps/chat/security.py` emite WARNING
   con pattern + excerpt. Falta destino estructurado (tabla `SecurityEvent`
   o JSONL rotado) para iterar sobre patrones reales en producción.
6. **Throttle persistente para anti-abuso** — el quota tracking por provider
   ya persiste vía `Message`. El throttle anti-spam in-memory pierde la
   ventana minutal en restart. Opciones: snapshot JSON, Redis, o queryear
   `Message` también.
7. **RAG real con bibliografía** — el wiki cubre 32 conceptos curados; falta
   PDF (pdfplumber) → chunking → embeddings (pgvector) → matcher híbrido KB+RAG.
   `DocumentChunk` ya existe como modelo placeholder.
8. **Validación semántica más profunda** — parcial en
   `apps/formulation/validator.py`. Sumar detección de ambigüedades, datos
   faltantes, hipótesis no cubiertas.
9. **Modo guiado backend-driven** — hoy la state machine guiada vive solo en
   frontend; integrar `Session.state` + tool `start_guided_mode` para que el
   orquestador maneje el flujo.

### Prioridad media — auth + provider hygiene
10. **Google OAuth E2E** — `/api/auth/google/` existe; falta OAuth client en
    Google Cloud, configurar `Site` en admin, wirear el botón en el frontend.
11. **Verificar límites reales de Z.ai** — los docs públicos no especifican
    free tier RPM/RPD. Crear cuenta, probar, completar `rpm`/`rpd` en
    `LLM_PROVIDERS` para `zai`.
12. **Markdown rico en `ChatMessage.svelte` viejo** — el componente del flujo
    guiado usa regex para `**bold**`. `marked` ya está instalado (lo usa el
    nuevo `ChatBubbleLLM`). Migrar para consistencia sin romper el modo
    determinístico.

### Prioridad baja — polish
13. **Sidebar de historial — polish**: rename inline del título, filter por
    fecha, tags. UI básica ya funciona.
14. **Más ejemplos en Tutorial** — sumar 2-3 cubriendo casos especiales
    (no acotado, infactible, óptimos múltiples).
15. **Historial exportable** — endpoints REST listos; falta UI de export a
    PDF/markdown/JSON.
16. **Modelo 3D interactivo** — del backlog de sprint, no priorizado.

### Investigaciones cerradas
- **freellmapi** (https://github.com/tashfeenahmed/freellmapi) — evaluado y
  descartado como reemplazo del cliente LLM. Es un proxy Node.js con
  dashboard y SQLite-backed quota. Aporta persistencia y 14 providers, pero
  agrega un servicio Node al stack y asume single-user. Cherry-pick aplicado
  en su lugar: más providers + quota tracking via Message table. Si Slacko
  escala a varias cohortes simultáneas, vale revisitar.
