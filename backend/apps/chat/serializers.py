from rest_framework import serializers

from .models import Message, Session


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


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ("id", "mode", "title")
        read_only_fields = ("id",)
