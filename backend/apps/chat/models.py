"""Chat session and message models.

The session is the long-lived container for a conversation; messages are the
turns. Both have JSONB metadata so the orchestrator can attach tool calls,
citations, token costs and any debug info without further migrations.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class Session(models.Model):
    """A chat session between a user and Slacko."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    mode = models.CharField(
        max_length=10,
        choices=[("guided", "Guiado"), ("free", "Libre"), ("llm", "LLM")],
        blank=True,
    )
    state = models.CharField(max_length=30, default="START")
    model_data = models.JSONField(default=dict, blank=True)

    # ── enrichment for the history sidebar ──
    title = models.CharField(max_length=200, blank=True)
    archived = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sesión de chat"
        verbose_name_plural = "Sesiones de chat"
        ordering = ["-pinned", "-updated_at"]
        indexes = [
            models.Index(fields=["user", "archived"], name="idx_chat_sess_user_arch"),
            models.Index(fields=["user", "-updated_at"], name="idx_chat_sess_user_upd"),
        ]

    def __str__(self) -> str:
        return f"Session {self.id} ({self.user.username})"


class Message(models.Model):
    """A single message in a chat session."""

    ROLE_CHOICES = [("user", "Usuario"), ("assistant", "Asistente"), ("system", "Sistema")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    # ── observability + orchestrator artifacts ──
    tool_calls = models.JSONField(default=list, blank=True)
    citations = models.JSONField(default=list, blank=True)
    cost_tokens = models.IntegerField(default=0)
    parent_id_uuid = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["session", "created_at"], name="idx_chat_msg_sess_created"),
        ]

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}"
