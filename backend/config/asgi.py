"""ASGI config for Slacko project.

HTTP traffic goes through Django's normal ASGI app. WebSocket traffic is
authenticated por la sesión de Django (cookie) vía ``AuthMiddlewareStack`` de
Channels — el mismo login que usa la API REST habilita el chat, sin tokens en
la URL.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django_asgi_app = get_asgi_application()

from django.conf import settings  # noqa: E402

from apps.chat.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # OriginValidator rechaza handshakes WS de orígenes fuera de la lista
        # blanca (defensa CSRF-like para WebSocket con cookies). En el deploy
        # split el frontend vive en otro dominio (Vercel), así que la lista se
        # configura por settings.WS_ALLOWED_ORIGINS en vez de ALLOWED_HOSTS.
        "websocket": OriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
            settings.WS_ALLOWED_ORIGINS,
        ),
    }
)
