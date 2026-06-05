"""Account views.

Keeps the legacy SimpleJWT-only register/me endpoints for backward compat,
and exposes a Google OAuth login view via dj-rest-auth's social adapter.
"""

from __future__ import annotations

from allauth.account.signals import user_signed_up
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.signals import social_account_added
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Legacy registration endpoint (preserved for the existing frontend)."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class MeView(APIView):
    """Current authenticated user (with profile)."""

    def get(self, request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Cierra la sesión blacklisteando el refresh token entregado.

    El access token sigue siendo válido hasta su corta expiración (1h), pero el
    refresh queda invalidado, por lo que la sesión no puede renovarse. Requiere
    ``rest_framework_simplejwt.token_blacklist`` (ya en INSTALLED_APPS).

    Es ``AllowAny``: la posesión del refresh token es la credencial, así que se
    puede cerrar sesión incluso con el access ya expirado.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request) -> Response:
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "Falta el campo 'refresh'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            # Token ya expirado/inválido/blacklisteado: el resultado deseado
            # (no poder renovar) ya se cumple, así que respondemos idempotente.
            return Response(status=status.HTTP_205_RESET_CONTENT)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class GoogleLogin(SocialLoginView):
    """Canjea un ``access_token`` de Google (obtenido por GIS en el frontend)
    por un par de tokens JWT.

    Usamos el flujo de access_token: allauth resuelve el perfil con
    ``_fetch_user_info`` y no hace falta ni ``client_secret`` ni un redirect URI
    registrado en Google Console (sí el Client ID y el origin autorizado).
    """

    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        # Detectamos, vía señales de allauth durante este request, en cuál de los
        # tres casos caímos, para que el frontend pueda avisar al usuario:
        #   - created:         alta nueva (user_signed_up)
        #   - linked_existing: se conectó Google a una cuenta local que YA existía
        #                      con ese email (social_account_added en connect())
        #   - ninguno:         reingreso normal (ya tenía Google vinculado)
        flags = {"created": False, "linked_existing": False}

        def _on_signup(sender, **kw):
            flags["created"] = True

        def _on_connect(sender, **kw):
            flags["linked_existing"] = True

        user_signed_up.connect(_on_signup, weak=False, dispatch_uid="google_signup_probe")
        social_account_added.connect(
            _on_connect, weak=False, dispatch_uid="google_connect_probe"
        )
        try:
            # Un access_token inválido/expirado hace que allauth tire OAuth2Error
            # al pedir el userinfo; sin capturar sube como 500. Lo traducimos a 400.
            response = super().post(request, *args, **kwargs)
        except OAuth2Error:
            return Response(
                {"detail": "No pudimos validar tu cuenta de Google. Probá de nuevo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        finally:
            user_signed_up.disconnect(dispatch_uid="google_signup_probe")
            social_account_added.disconnect(dispatch_uid="google_connect_probe")

        # ``linked_existing`` solo si se vinculó Y no es un alta nueva (en el alta
        # el social account también se agrega, pero ahí el mensaje correcto es otro).
        if response.status_code == 200 and isinstance(response.data, dict):
            flags["linked_existing"] = flags["linked_existing"] and not flags["created"]
            response.data.update(flags)
        return response
