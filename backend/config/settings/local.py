"""Local development settings."""

from .base import *  # noqa: F401, F403

DEBUG = True

# In dev, allow all origins for convenience
CORS_ALLOW_ALL_ORIGINS = True
