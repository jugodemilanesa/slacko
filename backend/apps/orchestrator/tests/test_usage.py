"""Tests for quota tracking against the Message table."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.chat.models import Message, Session
from apps.orchestrator import usage


pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="quota_user", password="x")


@pytest.fixture
def session(user: User) -> Session:
    return Session.objects.create(user=user, mode="llm", title="t")


def _add_message(session: Session, provider: str, *, minutes_ago: float = 0) -> Message:
    """Crear un Message del assistant con metadata.provider seteado."""

    msg = Message.objects.create(
        session=session,
        role="assistant",
        content="x",
        metadata={"provider": provider},
    )
    if minutes_ago:
        new_ts = timezone.now() - timedelta(minutes=minutes_ago)
        Message.objects.filter(pk=msg.pk).update(created_at=new_ts)
        msg.refresh_from_db()
    return msg


class TestIsNearCap:
    def test_no_caps_means_not_near(self, session: Session) -> None:
        """Provider sin rpm ni rpd nunca se considera near-cap."""

        prov = {"name": "zai"}
        for _ in range(50):
            _add_message(session, "zai")
        assert usage.is_near_cap(prov) is False

    def test_under_rpm_cap_is_ok(self, session: Session) -> None:
        prov = {"name": "gemini", "rpm": 10}
        for _ in range(5):
            _add_message(session, "gemini")
        assert usage.is_near_cap(prov) is False

    def test_at_rpm_cap_blocks(self, session: Session) -> None:
        """A 9 calls en el último minuto, está al 90% de 10 — blocks."""

        prov = {"name": "gemini", "rpm": 10}
        for _ in range(9):
            _add_message(session, "gemini")
        assert usage.is_near_cap(prov) is True

    def test_messages_outside_window_dont_count(self, session: Session) -> None:
        """Mensajes de hace más de 1 minuto no cuentan para RPM."""

        prov = {"name": "gemini", "rpm": 10}
        for _ in range(9):
            _add_message(session, "gemini", minutes_ago=5)
        assert usage.is_near_cap(prov) is False

    def test_other_providers_dont_count(self, session: Session) -> None:
        """Mensajes del provider X no cuentan contra Y."""

        prov_gemini = {"name": "gemini", "rpm": 10}
        for _ in range(20):
            _add_message(session, "groq")
        assert usage.is_near_cap(prov_gemini) is False

    def test_rpd_cap(self, session: Session) -> None:
        """RPD: contamos las últimas 24h y blockeamos al 90%."""

        prov = {"name": "gemini", "rpm": 100, "rpd": 10}
        # 9 messages en el último día — al 90% de 10.
        for i in range(9):
            _add_message(session, "gemini", minutes_ago=60 * i)
        assert usage.is_near_cap(prov) is True

    def test_rpd_window_correctly_bounded(self, session: Session) -> None:
        """Mensajes de hace 25h no entran en la ventana de RPD."""

        prov = {"name": "gemini", "rpm": 100, "rpd": 5}
        for _ in range(10):
            _add_message(session, "gemini", minutes_ago=60 * 25)
        assert usage.is_near_cap(prov) is False

    def test_deterministic_provider_messages_dont_pollute(
        self, session: Session
    ) -> None:
        """Mensajes con provider='deterministic' no cuentan contra gemini."""

        prov = {"name": "gemini", "rpm": 5}
        for _ in range(20):
            _add_message(session, "deterministic")
        assert usage.is_near_cap(prov) is False


class TestUsageSnapshot:
    def test_snapshot_includes_caps_when_defined(self, session: Session) -> None:
        prov = {"name": "groq", "rpm": 30, "rpd": 14400}
        for _ in range(3):
            _add_message(session, "groq")
        snap = usage.usage_snapshot(prov)
        assert snap["name"] == "groq"
        assert snap["rpm_used"] == 3
        assert snap["rpm_cap"] == 30
        assert snap["rpd_used"] == 3
        assert snap["rpd_cap"] == 14400

    def test_snapshot_omits_caps_not_defined(self, session: Session) -> None:
        prov = {"name": "zai"}
        snap = usage.usage_snapshot(prov)
        assert snap == {"name": "zai"}
