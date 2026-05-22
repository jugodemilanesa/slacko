"""Serializers for the accounts app.

Two flavors live here:
- The legacy SimpleJWT-only serializers (``RegisterSerializer``, ``UserSerializer``)
  reused by dj-rest-auth via ``REST_AUTH``.
- A profile serializer that exposes UTN-specific fields (legajo, comisión).
"""

from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("legajo", "comision")


class RegisterSerializer(serializers.ModelSerializer):
    """Used by both the legacy ``/api/auth/register/`` and dj-rest-auth."""

    password = serializers.CharField(write_only=True, min_length=6)
    legajo = serializers.CharField(required=False, allow_blank=True, write_only=True)
    comision = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "legajo", "comision")

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
        fields = ("id", "username", "email", "profile")
