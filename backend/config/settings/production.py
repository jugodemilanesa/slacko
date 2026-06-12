"""Production settings."""

from .base import *  # noqa: F401, F403

DEBUG = False

# Persistent DB connections (10 min) to avoid TCP reconnection overhead
# in WebSocket consumers that issue multiple queries per turn.
DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa: F405

# Use Redis for channel layers in production
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL", default="redis://localhost:6379/0")],  # noqa: F405
        },
    },
}
