"""Production settings."""

from .base import *  # noqa: F401, F403

DEBUG = False

# Railway healthcheck usa Host: healthcheck.railway.app — Django lo rechaza
# si no está en ALLOWED_HOSTS.
ALLOWED_HOSTS.append("healthcheck.railway.app")  # noqa: F405

# Persistent DB connections (10 min) to avoid TCP reconnection overhead
# in WebSocket consumers that issue multiple queries per turn.
DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa: F405

# Static files via whitenoise (Django admin assets en producción)
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Cookies cross-site (deploy split: frontend en Vercel, backend en otro
# dominio). Para que el browser mande la cookie de sesión a otro origen hace
# falta SameSite=None + Secure. Requiere HTTPS (Railway/Vercel lo dan).
# Limitación conocida: Safari/iOS bloquean cookies third-party → el chat no
# autentica en esos browsers. Para soporte universal habría que migrar a JWT.
SESSION_COOKIE_SAMESITE = "None"  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"  # noqa: F405
CSRF_COOKIE_SECURE = True

# Channel layer: si hay REDIS_URL usamos Redis (multi-worker); si no —caso
# típico de una demo single-process en Railway— heredamos InMemoryChannelLayer
# de base.py. Redis requiere agregar `channels-redis` a requirements.txt.
REDIS_URL = env("REDIS_URL", default="")  # noqa: F405
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        },
    }
