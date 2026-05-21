"""Rate limiter para el chat con el orquestador LLM.

Dos ventanas deslizantes en memoria:

* **Por usuario**: limita la actividad de un solo alumno (evita que uno solo
  spamee la key compartida y bloquee al resto).
* **Global**: limita la actividad total del proceso para honrar el techo real
  de la API key de Gemini (10 RPM en el tier free de AI Studio).

Los valores por default se eligen con margen frente al límite de Gemini
free tier (10 RPM, 1.500 RPD por key) — son configurables desde settings.

Limitaciones conocidas:

* In-memory. Si corrés varios workers de daphne, cada uno tiene su propia
  ventana y los límites efectivos se multiplican. Para producción escalada
  habría que mover el estado a Redis (el `channel_layers` ya está pensado
  para reemplazarse por `channels_redis`).
* Sin persistencia de la ventana diaria. Reinicios "resetean" la cuota
  diaria, lo cual es bueno para dev y aceptable para una demo. Para
  producción seria también iría a Redis o a una tabla con TTL.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from threading import Lock
from typing import Optional


@dataclass(frozen=True)
class ThrottleDecision:
    """Resultado de un chequeo de rate-limit."""

    allowed: bool
    retry_after_seconds: Optional[float] = None
    scope: Optional[str] = None  # "user_min", "user_hour", "global_min" si bloqueado


class SlidingWindowRateLimiter:
    """Sliding window con múltiples buckets simultáneos.

    Cada bucket es ``(max_requests, window_seconds)``. Una request se acepta
    solo si pasa todos los buckets; el primero que la rechaza dicta el motivo.
    Esto permite, por ejemplo, limitar "6 por minuto y 60 por hora" en un solo
    chequeo.
    """

    def __init__(self, buckets: list[tuple[str, int, float]]):
        """``buckets``: lista de ``(name, max_requests, window_seconds)``."""

        self._buckets = buckets
        # Per-key state: {scope_key -> {bucket_name -> deque[timestamp]}}
        self._state: dict[str, dict[str, deque[float]]] = {}
        self._lock = Lock()

    def check(self, key: str) -> ThrottleDecision:
        """Chequea (y consume si pasa) un request para ``key``."""

        now = time.monotonic()
        with self._lock:
            user_state = self._state.setdefault(key, {})

            # First pass: prune expired and check all buckets.
            for name, max_req, window in self._buckets:
                q = user_state.setdefault(name, deque())
                while q and now - q[0] > window:
                    q.popleft()
                if len(q) >= max_req:
                    # The oldest entry decides when the user can retry.
                    retry_after = window - (now - q[0])
                    return ThrottleDecision(
                        allowed=False,
                        retry_after_seconds=max(retry_after, 0.0),
                        scope=name,
                    )

            # Second pass: every bucket has room — record the timestamp.
            for name, _max_req, _window in self._buckets:
                user_state[name].append(now)

            return ThrottleDecision(allowed=True)

    def reset(self, key: Optional[str] = None) -> None:
        """Limpia el estado de ``key`` (o todo si es ``None``). Útil para tests."""

        with self._lock:
            if key is None:
                self._state.clear()
            else:
                self._state.pop(key, None)


# ──────────────────────────────────────────────────────────────────────────
# Default instances used by the chat consumer. Bucket sizes can be tuned via
# settings without code change (see config.settings.base.LLM_THROTTLE_*).
# ──────────────────────────────────────────────────────────────────────────


def _read_settings():
    """Read tunable knobs from Django settings with sane defaults."""

    from django.conf import settings

    user_min = getattr(settings, "LLM_THROTTLE_USER_PER_MINUTE", 6)
    user_hour = getattr(settings, "LLM_THROTTLE_USER_PER_HOUR", 60)
    global_min = getattr(settings, "LLM_THROTTLE_GLOBAL_PER_MINUTE", 9)

    return {
        "user_min": int(user_min),
        "user_hour": int(user_hour),
        "global_min": int(global_min),
    }


_user_limiter: Optional[SlidingWindowRateLimiter] = None
_global_limiter: Optional[SlidingWindowRateLimiter] = None
_GLOBAL_KEY = "__global__"


def _get_limiters() -> tuple[SlidingWindowRateLimiter, SlidingWindowRateLimiter]:
    """Lazy-init both limiters from settings on first call."""

    global _user_limiter, _global_limiter
    if _user_limiter is None or _global_limiter is None:
        cfg = _read_settings()
        _user_limiter = SlidingWindowRateLimiter(
            [
                ("user_min", cfg["user_min"], 60.0),
                ("user_hour", cfg["user_hour"], 3600.0),
            ]
        )
        _global_limiter = SlidingWindowRateLimiter(
            [
                ("global_min", cfg["global_min"], 60.0),
            ]
        )
    return _user_limiter, _global_limiter


def check_user(user_id: int) -> ThrottleDecision:
    """Chequea + consume cupo del usuario ``user_id``."""

    user_limiter, _ = _get_limiters()
    return user_limiter.check(str(user_id))


def check_global() -> ThrottleDecision:
    """Chequea + consume cupo global del proceso (proxy del límite por API key)."""

    _, global_limiter = _get_limiters()
    return global_limiter.check(_GLOBAL_KEY)


def reset_for_tests() -> None:
    """Limpia el estado de ambos limiters. Solo para tests."""

    global _user_limiter, _global_limiter
    _user_limiter = None
    _global_limiter = None
