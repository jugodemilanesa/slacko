"""Account models — extends the built-in User with UTN-specific profile fields.

We keep ``django.contrib.auth.User`` as the main user model (no AUTH_USER_MODEL
swap) and attach UTN fields via a one-to-one profile, created on demand. This
keeps existing migrations clean and lets us add more profile fields later
without touching auth.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """UTN-specific profile attached to ``auth.User``."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    legajo = models.CharField(max_length=20, blank=True)
    comision = models.CharField(max_length=20, blank=True)
    accepted_terms_at = models.DateTimeField(null=True, blank=True)
    # Última actividad real del usuario (se refresca al abrir un WebSocket de
    # chat). Complementa ``User.last_login`` —que solo marca el login— con una
    # señal de presencia más fina para auditoría y métricas de uso.
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self) -> str:
        return f"Profile<{self.user.username}>"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def _ensure_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
