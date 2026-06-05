"""Tests de registro, validación de inputs y ciclo de sesión JWT."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def client() -> APIClient:
    return APIClient()


# ─── Registro / validación ────────────────────────────────────────────────


def test_register_valido_crea_usuario_y_perfil(client):
    resp = client.post(
        reverse("accounts:register"),
        {
            "username": "alumno1",
            "email": "Alumno1@utn.edu.ar",
            "password": "Slacko-2026-pl",
            "legajo": "12345",
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    user = User.objects.get(username="alumno1")
    # El email se normaliza a minúsculas para que sea identificador unívoco.
    assert user.email == "alumno1@utn.edu.ar"
    assert user.profile.legajo == "12345"


def test_register_rechaza_password_debil(client):
    resp = client.post(
        reverse("accounts:register"),
        {"username": "alumno2", "email": "a2@utn.edu.ar", "password": "123456"},
        format="json",
    )
    assert resp.status_code == 400
    assert "password" in resp.json()


def test_register_rechaza_username_invalido(client):
    resp = client.post(
        reverse("accounts:register"),
        {"username": "a b", "email": "a3@utn.edu.ar", "password": "Slacko-2026-pl"},
        format="json",
    )
    assert resp.status_code == 400
    assert "username" in resp.json()


def test_register_email_duplicado_case_insensitive(client):
    User.objects.create_user("uno", email="dup@utn.edu.ar", password="Slacko-2026-pl")
    resp = client.post(
        reverse("accounts:register"),
        {"username": "dos", "email": "DUP@utn.edu.ar", "password": "Slacko-2026-pl"},
        format="json",
    )
    assert resp.status_code == 400
    assert "email" in resp.json()


def test_register_exige_email(client):
    resp = client.post(
        reverse("accounts:register"),
        {"username": "alumno4", "password": "Slacko-2026-pl"},
        format="json",
    )
    assert resp.status_code == 400
    assert "email" in resp.json()


def test_register_legajo_no_numerico_rechazado(client):
    resp = client.post(
        reverse("accounts:register"),
        {
            "username": "alumno5",
            "email": "a5@utn.edu.ar",
            "password": "Slacko-2026-pl",
            "legajo": "no-soy-legajo",
        },
        format="json",
    )
    assert resp.status_code == 400
    assert "legajo" in resp.json()


# ─── Ciclo de sesión JWT (login → refresh → logout/blacklist) ─────────────


def _login(client, username="alumno1", password="Slacko-2026-pl"):
    User.objects.create_user(username, email=f"{username}@utn.edu.ar", password=password)
    resp = client.post(
        reverse("accounts:login"),
        {"username": username, "password": password},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    return resp


def test_login_abre_sesion_y_me_responde(client):
    _login(client)
    # La sesión queda en la cookie del client; /me/ responde autenticado.
    me = client.get(reverse("accounts:me"))
    assert me.status_code == 200
    assert me.json()["username"] == "alumno1"


def test_login_actualiza_last_login(client):
    _login(client)
    assert User.objects.get(username="alumno1").last_login is not None


def test_login_credenciales_invalidas_da_400(client):
    User.objects.create_user("alumno1", email="a@utn.edu.ar", password="Slacko-2026-pl")
    resp = client.post(
        reverse("accounts:login"),
        {"username": "alumno1", "password": "incorrecta"},
        format="json",
    )
    assert resp.status_code == 400


def test_me_sin_sesion_da_403(client):
    assert client.get(reverse("accounts:me")).status_code == 403


def test_logout_cierra_la_sesion(client):
    _login(client)
    assert client.get(reverse("accounts:me")).status_code == 200

    logout = client.post(reverse("accounts:logout"))
    assert logout.status_code == 204

    # Sin sesión, /me/ ya no responde autenticado.
    assert client.get(reverse("accounts:me")).status_code == 403


def test_logout_sin_sesion_es_idempotente(client):
    assert client.post(reverse("accounts:logout")).status_code == 204


# ─── Google OAuth (flujo access_token) ────────────────────────────────────


def test_google_login_token_invalido_da_400(client):
    """Un access_token inválido se traduce a 400, no 500 (OAuth2Error capturado)."""
    with patch(
        "allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter.complete_login",
        side_effect=OAuth2Error("Request to user info failed"),
    ):
        resp = client.post(
            reverse("accounts:google_login"),
            {"access_token": "bogus"},
            format="json",
        )
    assert resp.status_code == 400
    assert "Google" in resp.json().get("detail", "")
