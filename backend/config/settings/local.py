"""Local development settings."""

from .base import *  # noqa: F401, F403

DEBUG = True

# In dev, allow all origins for convenience
CORS_ALLOW_ALL_ORIGINS = True

# En dev el WS puede venir del proxy de Vite o de localhost directo: abrimos el
# OriginValidator (ver config/asgi.py) a todos los orígenes.
WS_ALLOWED_ORIGINS = ["*"]
