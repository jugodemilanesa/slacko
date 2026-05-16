"""Production settings."""

from .base import *  # noqa: F401, F403

DEBUG = False

# Use Redis for channel layers in production
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL", default="redis://localhost:6379/0")],  # noqa: F405
        },
    },
}
