"""Account views.

Keeps the legacy SimpleJWT-only register/me endpoints for backward compat,
and exposes a Google OAuth login view via dj-rest-auth's social adapter.
"""

from __future__ import annotations

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

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


class GoogleLogin(SocialLoginView):
    """Exchange a Google OAuth code/id_token for a JWT pair."""

    adapter_class = GoogleOAuth2Adapter
    callback_url = f"{settings.FRONTEND_BASE_URL}/auth/google/callback"
    client_class = OAuth2Client
