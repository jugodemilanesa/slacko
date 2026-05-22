"""Quota tracking por provider, backed por la tabla Message.

Idea inspirada en `freellmapi` (cherry-pick): antes de intentar un provider,
preguntamos cuántas requests le hicimos en la última ventana relevante. Si
estamos cerca de su techo (RPM/RPD), lo skipeamos preventivamente y vamos al
siguiente — así evitamos pegar contra un 429 y la latencia del fallback.

La fuente de verdad es ``apps.chat.models.Message``: cada turn del asistente
se persiste con ``metadata.provider`` indicando quién contestó. Contando esos
rows en una ventana de tiempo aproximamos las requests recientes.

Aproximación, no medición exacta:
* Multi-hop: un único `Message` puede haber gatillado varias requests al
  proveedor (una por hop). Las contamos como 1. Para el orden de magnitud
  del rate limit free-tier sirve, y nos da margen extra.
* Solo cuenta los providers que efectivamente contestaron (no los que
  fallaron antes en la cadena). Eso es lo que queremos: para Gemini lo
  relevante son las requests que Google realmente vio.

Persistencia gratis: ya tenemos los rows en la DB, no agregamos tabla nueva.
Survives restarts naturalmente.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone

logger = logging.getLogger(__name__)


# Margen de seguridad: si el provider declara 10 RPM, lo tratamos como saturado
# al alcanzar el 90% (9 RPM). Evita golpear el techo exacto.
_SAFETY_FACTOR = 0.90


def _count_in_window(provider_name: str, since) -> int:
    """Cuenta mensajes de assistant con ese provider desde ``since``."""

    # Import lazy para evitar problemas de import circular en arranque.
    from apps.chat.models import Message

    return (
        Message.objects.filter(
            role="assistant",
            metadata__provider=provider_name,
            created_at__gte=since,
        ).count()
    )


def usage_snapshot(provider: dict[str, Any]) -> dict[str, Any]:
    """Devuelve uso reciente del provider ``provider`` para ventanas RPM/RPD.

    Útil para logging, debugging o un dashboard. No tiene side-effects.
    """

    now = timezone.now()
    name = provider["name"]
    snapshot: dict[str, Any] = {"name": name}

    rpm_cap = provider.get("rpm")
    if rpm_cap:
        snapshot["rpm_used"] = _count_in_window(name, now - timedelta(minutes=1))
        snapshot["rpm_cap"] = rpm_cap

    rpd_cap = provider.get("rpd")
    if rpd_cap:
        snapshot["rpd_used"] = _count_in_window(name, now - timedelta(days=1))
        snapshot["rpd_cap"] = rpd_cap

    return snapshot


def is_near_cap(provider: dict[str, Any]) -> bool:
    """``True`` si el provider está dentro del margen del 90% de su techo.

    Si el provider no declara ni RPM ni RPD, asumimos que no hay tope conocido
    y devolvemos ``False`` (no skipear). Eso preserva el comportamiento original
    para providers como Z.ai donde aún no sabemos los límites exactos.
    """

    name = provider["name"]
    now = timezone.now()

    rpm_cap = provider.get("rpm")
    if rpm_cap:
        try:
            used = _count_in_window(name, now - timedelta(minutes=1))
        except Exception as exc:  # noqa: BLE001
            # Si la DB no está disponible (raro), preferimos NO skipear.
            logger.warning("usage: cannot count rpm for %s (%s)", name, exc)
            used = 0
        if used >= int(rpm_cap * _SAFETY_FACTOR):
            logger.info(
                "usage: provider=%s near RPM cap (%d/%d)", name, used, rpm_cap
            )
            return True

    rpd_cap = provider.get("rpd")
    if rpd_cap:
        try:
            used = _count_in_window(name, now - timedelta(days=1))
        except Exception as exc:  # noqa: BLE001
            logger.warning("usage: cannot count rpd for %s (%s)", name, exc)
            used = 0
        if used >= int(rpd_cap * _SAFETY_FACTOR):
            logger.info(
                "usage: provider=%s near RPD cap (%d/%d)", name, used, rpd_cap
            )
            return True

    return False
