# Slacko - Guía del Proyecto

## Qué es este proyecto

Slacko es un chatbot educativo para estudiantes de **Investigación Operativa** (UTN). Asiste en:

- **Tutoría teórica:** responde preguntas sobre conceptos de la materia usando RAG sobre la bibliografía oficial.
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
| Base de datos | PostgreSQL 16 + pgvector (embeddings para RAG) |
| LLM | LiteLLM → OpenRouter (agnóstico al proveedor) |
| Cálculo | NumPy · SciPy · PuLP |
| Autenticación | JWT (djangorestframework-simplejwt) |

## Estructura del monorepo

```
inv-op/
├── backend/                    # Django REST API + WebSocket
│   ├── config/                 # Settings (base/local/production), URLs, ASGI
│   ├── apps/
│   │   ├── accounts/           # Auth: register, login (JWT), me
│   │   ├── chat/               # Modelos Session/Message, WebSocket consumer
│   │   ├── theory/             # RAG: DocumentChunk (pgvector), ingesta, búsqueda
│   │   ├── solver/             # Motor LP: engine.py (vértices), conversion.py (formas)
│   │   ├── formulation/        # Extracción de variables/restricciones (LLM-assisted)
│   │   └── orchestrator/       # State machine, routing de intenciones
│   ├── feedback_templates/     # Templates de retroalimentación por tipo de error
│   ├── scripts/                # Scripts de ingesta de bibliografía
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # SvelteKit SPA
│   └── src/
│       ├── lib/api/            # Cliente HTTP con JWT, funciones de auth
│       ├── lib/stores/         # Svelte stores (auth state)
│       ├── lib/components/     # Componentes reutilizables
│       └── routes/             # Páginas: login, register, chat
├── data/bibliography/          # PDFs de la cátedra (read-only)
├── docker/                     # Scripts de inicialización de DB
├── docs/                       # Sprints y documentación
├── docker-compose.yml          # PostgreSQL + backend + frontend
└── CLAUDE.md                   # Convenciones y guía para Claude Code
```

## Arquitectura

### Flujo de datos

```
Frontend (SvelteKit) → REST API / WebSocket → Django Orchestrator
                                                    │
                                    ┌───────────────┼───────────────┐
                                    │               │               │
                                  LiteLLM       Solver          RAG
                                (OpenRouter)  (NumPy/SciPy)   (pgvector)
```

### Orquestador

El orquestador (`apps/orchestrator/`) recibe cada mensaje del usuario y decide qué módulo lo maneja:

| Tipo de mensaje | Destino |
|---|---|
| Pregunta teórica | `theory/` → RAG + LLM |
| Enunciado de problema | `formulation/` → LLM extrae modelo |
| Solicitud de resolución | `solver/` → cálculo determinista |
| Pide gráfico | `solver/` → datos JSON → Plotly en frontend |
| Error del usuario | `feedback_templates/` → template predefinido |

### State machine (modo guiado)

El chat guiado sigue una máquina de estados definida en `apps/orchestrator/states.py`:

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

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/auth/register/` | Registrar usuario |
| POST | `/api/auth/login/` | Obtener JWT (access + refresh) |
| POST | `/api/auth/refresh/` | Refrescar access token |
| GET | `/api/auth/me/` | Datos del usuario autenticado |
| GET | `/api/chat/sessions/` | Listar sesiones del usuario |
| POST | `/api/chat/sessions/` | Crear nueva sesión |
| GET | `/api/chat/sessions/<uuid>/` | Detalle de sesión con mensajes |
| POST | `/api/solver/solve/` | Resolver problema LP (vertex analysis) |
| POST | `/api/solver/standard-form/` | Convertir a forma estándar |
| POST | `/api/theory/query/` | Consulta teórica (RAG, pendiente) |
| WS | `/ws/chat/<uuid>/` | WebSocket para chat en tiempo real |

Todos los endpoints (excepto register y login) requieren header `Authorization: Bearer <token>`.

## Cómo levantar el proyecto

```bash
# 1. Clonar y entrar al directorio
git clone <repo-url> && cd inv-op

# 2. Copiar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tu API key de OpenRouter si vas a usar LLM

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

### Prioridad alta
1. **Orquestador completo** — routing de intenciones con la state machine
2. **Integración LLM** — conectar LiteLLM/OpenRouter para extracción de texto y tutoría
3. **RAG/Ingesta** — pipeline de procesamiento de PDFs → embeddings en pgvector
4. **WebSocket funcional** — conectar el consumer de chat con el orquestador
5. **Gráficos Plotly** — componente Svelte que renderice la región factible interactivamente
6. **Validación semántica** — detección de ambigüedades, datos faltantes, hipótesis

### Prioridad media
7. **Templates de feedback** — mensajes de error explicativos por tipo de error
8. **Modo guiado completo** — preguntas secuenciales con ejemplos y validaciones

### Prioridad baja
9. **Historial y exportación** — guardar sesiones, exportar a PDF
