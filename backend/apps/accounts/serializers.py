"""Serializers for the accounts app.

Two flavors live here:
- The legacy SimpleJWT-only serializers (``RegisterSerializer``, ``UserSerializer``)
  reused by dj-rest-auth via ``REST_AUTH``.
- A profile serializer that exposes UTN-specific fields (legajo, comisión).
"""

from __future__ import annotations

import re

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import UserProfile

# Username: 3–30 chars, letras/números/._- (sin espacios). Mantiene los
# usernames limpios para mostrarlos en UI y evita colisiones raras.
_USERNAME_RE = re.compile(r"^[\w.\-]{3,30}$")
# Legajo UTN: dígitos (algunas comisiones agregan un guion). Permisivo pero
# rechaza basura tipo texto libre.
_LEGAJO_RE = re.compile(r"^[\d\-]{3,20}$")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("legajo", "comision", "last_seen")
        read_only_fields = ("last_seen",)


class RegisterSerializer(serializers.ModelSerializer):
    """Used by both the legacy ``/api/auth/register/`` and dj-rest-auth."""

    password = serializers.CharField(write_only=True)
    legajo = serializers.CharField(required=False, allow_blank=True, write_only=True)
    comision = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "legajo", "comision")
        extra_kwargs = {
            # Email obligatorio y validado: es la identidad única que después
            # comparte el login con Google (ver SocialAccountAdapter).
            "email": {"required": True, "allow_blank": False},
        }

    def validate_username(self, value: str) -> str:
        value = value.strip()
        if not _USERNAME_RE.match(value):
            raise serializers.ValidationError(
                "El usuario debe tener 3–30 caracteres y solo letras, números, "
                "punto, guion o guion bajo."
            )
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ese nombre de usuario ya está en uso.")
        return value

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        # ``EmailField`` ya valida el formato; acá garantizamos unicidad
        # case-insensitive para que el email sea identificador unívoco.
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Ya existe una cuenta con ese correo."
            )
        return value

    def validate_password(self, value: str) -> str:
        # Corremos los AUTH_PASSWORD_VALIDATORS de Django (longitud mínima,
        # password común, demasiado numérica, similar a datos del usuario).
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate_legajo(self, value: str) -> str:
        value = value.strip()
        if value and not _LEGAJO_RE.match(value):
            raise serializers.ValidationError(
                "El legajo debe ser numérico (3–20 dígitos)."
            )
        return value

    def create(self, validated_data: dict) -> User:
        legajo = validated_data.pop("legajo", "")
        comision = validated_data.pop("comision", "")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        # Signal already created the profile; update UTN fields if provided.
        if legajo or comision:
            user.profile.legajo = legajo
            user.profile.comision = comision
            user.profile.save(update_fields=["legajo", "comision", "updated_at"])
        return user

    # dj-rest-auth's registration view calls .save(request=request).
    def save(self, request=None, **kwargs):  # noqa: ARG002 — request is part of the contract
        return super().save(**kwargs)


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "last_login", "date_joined", "profile")
        read_only_fields = ("last_login", "date_joined")
