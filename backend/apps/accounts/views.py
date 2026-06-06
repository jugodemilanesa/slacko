"""Account views — autenticación por sesión de Django.

El login crea una sesión server-side (cookie httpOnly que maneja el browser);
no se emiten tokens. Incluye el bootstrap de CSRF, login/logout por sesión, el
perfil del usuario actual y el login con Google (que también deja sesión).
"""

from __future__ import annotations

import requests
from allauth.account.signals import user_signed_up
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.signals import social_account_added
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


@method_decorator(ensure_csrf_cookie, name="get")
class CSRFView(APIView):
    """Setea la cookie ``csrftoken``. El front la llama una vez al cargar para
    poder mandar el header ``X-CSRFToken`` en los POST/PATCH/DELETE."""

    permission_classes = (permissions.AllowAny,)

    def get(self, request) -> Response:
        return Response({"detail": "CSRF cookie set"}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    """Alta de usuario. Tras crear, el front llama a login para abrir sesión."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(APIView):
    """Login por sesión: autentica y hace ``django.contrib.auth.login``.

    Acepta usuario o email en ``username`` (allauth backend resuelve ambos).
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request) -> Response:
        identifier = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        if not identifier or not password:
            return Response(
                {"detail": "Usuario y contraseña son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, username=identifier, password=password)
        if user is None:
            return Response(
                {"detail": "Usuario o contraseña incorrectos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        django_login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class MeView(APIView):
    """Current authenticated user (with profile)."""

    def get(self, request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Cierra la sesión de Django (``logout`` borra la sesión server-side y la
    cookie). Idempotente: aunque no haya sesión activa responde OK."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request) -> Response:
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleLogin(SocialLoginView):
    """Canjea un ``access_token`` de Google (obtenido por GIS en el frontend) y
    abre una sesión de Django (``SESSION_LOGIN``).

    Usamos el flujo de access_token: allauth resuelve el perfil con
    ``_fetch_user_info`` y no hace falta ni ``client_secret`` ni un redirect URI
    registrado en Google Console (sí el Client ID y el origin autorizado).
    """

    adapter_class = GoogleOAuth2Adapter

    def _audience_ok(self, access_token: str) -> bool:
        """Verifica que el access_token fue emitido para NUESTRO client_id.

        El flujo access_token resuelve identidad vía el endpoint userinfo de
        Google, que acepta cualquier token válido con scope email — sin chequear
        para qué app fue emitido. Sin esta verificación, un token emitido para
        OTRA app (confused deputy / token substitution) podría reenviarse acá y,
        combinado con el auto-connect por email, loguear al atacante como un
        usuario existente. ``tokeninfo`` expone ``aud``/``azp`` para validar la
        audiencia contra nuestro Client ID.
        """
        client_id = (
            settings.SOCIALACCOUNT_PROVIDERS.get("google", {})
            .get("APP", {})
            .get("client_id", "")
        )
        if not client_id:
            return False
        try:
            resp = requests.get(
                GOOGLE_TOKENINFO_URL,
                params={"access_token": access_token},
                timeout=5,
            )
        except requests.RequestException:
            return False
        if resp.status_code != 200:
            return False
        data = resp.json()
        return client_id in (data.get("aud"), data.get("azp"))

    def post(self, request, *args, **kwargs):
        # Antes de dejar que allauth resuelva la identidad, validamos que el
        # access_token sea para esta app (cierra el confused-deputy del flujo).
        access_token = request.data.get("access_token")
        if access_token and not self._audience_ok(access_token):
            return Response(
                {"detail": "El token de Google no es válido para esta aplicación."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
