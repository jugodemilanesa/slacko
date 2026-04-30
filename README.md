# Slacko - Tutor de Investigación Operativa

Chatbot educativo que asiste a estudiantes de Investigación Operativa (UTN) en la formulación, resolución gráfica e interpretación de problemas de Programación Lineal.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose

## Levantar el proyecto

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd inv-op

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env si se necesita (API keys, etc.)

# 3. Levantar los servicios
docker compose up -d

# 4. Verificar que todo esté corriendo
docker compose ps
```

Los servicios disponibles:

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |
| Admin Django | http://localhost:8000/admin/ |

## Uso básico

1. Abrir http://localhost:5173
2. Registrarse con usuario, email y contraseña
3. Iniciar una conversación con Slacko

## Comandos útiles

```bash
# Ver logs
docker compose logs -f backend
docker compose logs -f frontend

# Crear superusuario para acceder al admin
docker compose exec backend python manage.py createsuperuser

# Aplicar migraciones (después de cambios en modelos)
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# Rebuild después de cambios en dependencias
docker compose build backend && docker compose up -d backend
docker compose build frontend && docker compose up -d frontend

# Detener todo
docker compose down

# Detener y borrar datos (incluye base de datos)
docker compose down -v
```

## Stack

- **Backend:** Python 3.12 / Django / DRF / Django Channels
- **Frontend:** SvelteKit / Tailwind CSS / Plotly.js
- **Base de datos:** PostgreSQL 16 + pgvector
- **LLM:** LiteLLM → OpenRouter

## Documentación

- `CLAUDE.md` — Convenciones de código y arquitectura
- `docs/PROJECT_GUIDE.md` — Guía completa del proyecto para desarrolladores
- `docs/TPI - Slaking Sprint 2.md` — Especificaciones del Sprint 2
- `docs/TPI - Slaking Sprint 3.md` — Especificaciones del Sprint 3

## Equipo

**SLAKING** — UTN, Investigación Operativa 2026
