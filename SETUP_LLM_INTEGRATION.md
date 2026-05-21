# Setup post-merge — LLM integration branch

Esta rama (`llm-integration`) agrega: orquestador LLM, tools, wiki estilo Karpathy, dj-rest-auth + Google OAuth, persistencia enriquecida.

## 1. Variables de entorno (`backend/.env`)

Agregar al menos una de estas para que el orquestador hable con un LLM. Si **ninguna** está seteada, el chat funciona en modo determinístico (solo `theory_lookup` del wiki) — la infra está pensada para arrancar sin keys.

```bash
# Recomendado: Gemini primario, Groq fallback, OpenRouter experimental
GEMINI_API_KEY=                  # https://aistudio.google.com/apikey
GROQ_API_KEY=                    # https://console.groq.com
OPENROUTER_API_KEY=              # https://openrouter.ai/keys (opcional)

# Modelos por proveedor (defaults en backend/config/settings/base.py)
# GEMINI_MODEL=gemini/gemini-2.5-flash
# GROQ_MODEL=groq/llama-3.3-70b-versatile
# OPENROUTER_MODEL=openrouter/meta-llama/llama-3.3-70b-instruct:free

# Tuning del orquestador
# LLM_MAX_HOPS=5
# LLM_TEMPERATURE=0.3

# Google OAuth (vacío hasta tener credenciales del Cloud Console)
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=

# URL del frontend (para reset password y callbacks OAuth)
FRONTEND_BASE_URL=http://localhost:5173
```

## 2. Levantar la stack

```bash
docker compose down
docker compose build backend         # nuevas deps (dj-rest-auth, allauth, PyYAML)
docker compose up
```

## 3. Migraciones

Las migraciones nuevas se generan automáticamente con `makemigrations` (los model changes son aditivos, sin riesgo):

```bash
docker compose exec backend python manage.py makemigrations chat accounts
docker compose exec backend python manage.py migrate
```

Migración `chat`: agrega `title`, `archived`, `pinned`, `tags` a Session; `tool_calls`, `citations`, `cost_tokens`, `parent_id_uuid` a Message.
Migración `accounts`: crea `UserProfile` (one-to-one con `auth.User`).

## 4. Google OAuth (opcional)

1. Ir a https://console.cloud.google.com → APIs & Services → Credentials.
2. Create credentials → OAuth client ID → Web application.
3. Authorized JavaScript origins: `http://localhost:5173`.
4. Authorized redirect URIs: `http://localhost:5173/auth/google/callback`.
5. Copiar Client ID y Client Secret a `.env`.
6. En el admin de Django (`/admin/`), crear un **Site** con domain `localhost:5173`.

## 5. Migrar / regenerar el wiki

Si modificás el knowledge base en Python o agregás fuentes:

```bash
docker compose exec backend python -m scripts.migrate_kb_to_wiki
```

Este script lee la KB Python y reescribe `data/wiki/concepts/*.md` + `index.md`. El loader (`apps/theory/wiki_loader.py`) lee de disco al iniciar Django.

## 6. Endpoints nuevos

| Método | Path | Descripción |
|---|---|---|
| GET    | `/api/auth/user/`                 | Detalle del usuario (dj-rest-auth) |
| POST   | `/api/auth/password/reset/`       | Reset password (dj-rest-auth) |
| POST   | `/api/auth/registration/`         | Registro alternativo (dj-rest-auth) |
| POST   | `/api/auth/google/`               | Login con Google (id_token o code) |
| GET    | `/api/chat/sessions/`             | Lista de sesiones del usuario (sidebar) |
| POST   | `/api/chat/sessions/`             | Crear sesión nueva |
| GET    | `/api/chat/sessions/<id>/`        | Detalle con mensajes |
| PATCH  | `/api/chat/sessions/<id>/`        | Rename / archive / pin |
| DELETE | `/api/chat/sessions/<id>/`        | Eliminar |
| GET    | `/api/chat/sessions/<id>/messages/` | Mensajes paginados |
| GET    | `/api/chat/sessions/search?q=...` | Buscar sesiones/mensajes |

## 7. WebSocket

`ws://localhost:8000/ws/chat/<session_id>/` ahora rutea cada mensaje por el orquestador, persiste request+response en `Message`, y devuelve metadata con `tool_calls`, `citations`, `provider`.

## 8. Modo sin LLM (degradado controlado)

Si no hay ninguna API key, el orquestador detecta `llm.is_configured() == False` y responde con el matcher determinístico del wiki. El frontend no necesita cambios.
