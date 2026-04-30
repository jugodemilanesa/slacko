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
        choices=[("guided", "Guiado"), ("free", "Libre")],
        blank=True,
    )
    state = models.CharField(max_length=30, default="START")
    model_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sesión de chat"
        verbose_name_plural = "Sesiones de chat"
        ordering = ["-created_at"]

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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}"
