"""ASGI config for Slacko project.

HTTP traffic goes through Django's normal ASGI app. WebSocket traffic is
authenticated por la sesión de Django (cookie) vía ``AuthMiddlewareStack`` de
Channels — el mismo login que usa la API REST habilita el chat, sin tokens en
la URL.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django_asgi_app = get_asgi_application()

from apps.chat.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # AllowedHostsOriginValidator rechaza handshakes WS de orígenes no
        # permitidos (defensa CSRF-like para WebSocket con cookies).
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
