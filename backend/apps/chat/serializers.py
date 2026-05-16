from rest_framework import serializers

from .models import Message, Session


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "role", "content", "metadata", "created_at")
        read_only_fields = ("id", "role", "created_at")


class SessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ("id", "mode", "state", "model_data", "created_at", "updated_at", "messages")
        read_only_fields = ("id", "state", "model_data", "created_at", "updated_at")


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ("id", "mode")
        read_only_fields = ("id",)
