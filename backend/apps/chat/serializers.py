from rest_framework import serializers

from .models import Message, Session

# Tope de tags por sesión y largo de cada tag — evita que un cliente infle el
# JSONField con payloads arbitrarios.
_MAX_TAGS = 12
_MAX_TAG_LEN = 40


def _validate_tags(value):
    """Valida que ``tags`` sea una lista de strings cortos y no vacíos."""
    if not isinstance(value, list):
        raise serializers.ValidationError("Las etiquetas deben ser una lista.")
    if len(value) > _MAX_TAGS:
        raise serializers.ValidationError(
            f"Máximo {_MAX_TAGS} etiquetas por sesión."
        )
    cleaned = []
    for tag in value:
        if not isinstance(tag, str):
            raise serializers.ValidationError("Cada etiqueta debe ser texto.")
        tag = tag.strip()
        if not tag:
            continue
        if len(tag) > _MAX_TAG_LEN:
            raise serializers.ValidationError(
                f"Cada etiqueta admite hasta {_MAX_TAG_LEN} caracteres."
            )
        cleaned.append(tag)
    return cleaned


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id",
            "role",
            "content",
            "metadata",
            "tool_calls",
            "citations",
            "cost_tokens",
            "created_at",
        )
        read_only_fields = (
            "id",
            "role",
            "metadata",
            "tool_calls",
            "citations",
            "cost_tokens",
            "created_at",
        )


class SessionSummarySerializer(serializers.ModelSerializer):
    """Lightweight payload for the history sidebar (no messages)."""

    last_message_at = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Session
        fields = (
            "id",
            "title",
            "mode",
            "state",
            "archived",
            "pinned",
            "tags",
            "created_at",
            "updated_at",
            "last_message_at",
        )


class SessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = (
            "id",
            "title",
            "mode",
            "state",
            "model_data",
            "archived",
            "pinned",
            "tags",
            "created_at",
            "updated_at",
            "messages",
        )
        read_only_fields = ("id", "state", "model_data", "created_at", "updated_at")


class SessionUpdateSerializer(serializers.ModelSerializer):
    """PATCH-able subset of session fields."""

    class Meta:
        model = Session
        fields = ("title", "archived", "pinned", "tags")

    def validate_tags(self, value):
        return _validate_tags(value)


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ("id", "mode", "title")
        read_only_fields = ("id",)
