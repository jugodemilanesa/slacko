"""JWT-aware authentication middleware for Channels WebSocket connections.

The default ``AuthMiddlewareStack`` only reads Django session cookies. Since
Slacko's REST API uses SimpleJWT, we expose a small middleware that pulls
the access token from a ``?token=`` query-string parameter (or from the
``sec-websocket-protocol`` header) and resolves the user.

Frontend usage:
    new WebSocket(`ws://host/ws/chat/${sessionId}/?token=${accessToken}`)
"""

from __future__ import annotations

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def _get_user(token: str):
    try:
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth import get_user_model
    except ImportError:
        return AnonymousUser()

    try:
        UntypedToken(token)
    except (InvalidToken, TokenError):
        return AnonymousUser()

    from rest_framework_simplejwt.authentication import JWTAuthentication

    auth = JWTAuthentication()
    try:
        validated = auth.get_validated_token(token)
        return auth.get_user(validated)
    except Exception:  # noqa: BLE001
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Channels middleware that authenticates connections via JWT."""

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])

        if token_list:
            scope["user"] = await _get_user(token_list[0])
        else:
            scope.setdefault("user", AnonymousUser())

        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """Convenience wrapper mirroring channels' ``AuthMiddlewareStack``."""

    return JWTAuthMiddleware(inner)
