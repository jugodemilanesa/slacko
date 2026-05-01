"""Tests for the theoretical-tutor REST endpoints."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        username="alumno", password="testpass123", email="alumno@utn.edu.ar"
    )


@pytest.fixture
def auth_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def anon_client() -> APIClient:
    return APIClient()


class TestAuth:
    def test_categories_requires_auth(self, anon_client: APIClient) -> None:
        response = anon_client.get(reverse("theory:categories"))
        assert response.status_code == 401

    def test_concepts_requires_auth(self, anon_client: APIClient) -> None:
        response = anon_client.get(reverse("theory:concepts"))
        assert response.status_code == 401

    def test_query_requires_auth(self, anon_client: APIClient) -> None:
        response = anon_client.post(
            reverse("theory:query"), {"question": "qué es PL"}, format="json"
        )
        assert response.status_code == 401


class TestCategoryList:
    def test_returns_all_categories_with_counts(self, auth_client: APIClient) -> None:
        response = auth_client.get(reverse("theory:categories"))
        assert response.status_code == 200

        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 8

        for category in data["categories"]:
            assert {"id", "title", "description", "concept_count"} <= category.keys()
            assert category["concept_count"] >= 1


class TestConceptList:
    def test_returns_all_concepts(self, auth_client: APIClient) -> None:
        response = auth_client.get(reverse("theory:concepts"))
        assert response.status_code == 200

        data = response.json()
        assert "concepts" in data
        assert data["count"] == len(data["concepts"])
        assert data["count"] >= 30

    def test_filters_by_category(self, auth_client: APIClient) -> None:
        response = auth_client.get(
            reverse("theory:concepts"), {"category": "fundamentos"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["count"] >= 3
        assert all(c["category"] == "fundamentos" for c in data["concepts"])

    def test_unknown_category_returns_404(self, auth_client: APIClient) -> None:
        response = auth_client.get(
            reverse("theory:concepts"), {"category": "no-existe"}
        )
        assert response.status_code == 404


class TestConceptDetail:
    def test_returns_full_concept_with_related(self, auth_client: APIClient) -> None:
        response = auth_client.get(
            reverse("theory:concept_detail", args=["region-factible"])
        )
        assert response.status_code == 200

        data = response.json()
        assert data["concept"]["id"] == "region-factible"
        assert data["concept"]["category"] == "geometria"
        assert data["concept"]["content"]
        assert data["concept"]["aliases"]
        assert isinstance(data["related"], list)
        assert all("id" in r and "title" in r for r in data["related"])

    def test_unknown_id_returns_404(self, auth_client: APIClient) -> None:
        response = auth_client.get(
            reverse("theory:concept_detail", args=["no-existe"])
        )
        assert response.status_code == 404


class TestQuery:
    def test_matches_known_question(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            reverse("theory:query"),
            {"question": "¿qué es la región factible?"},
            format="json",
        )
        assert response.status_code == 200

        data = response.json()
        assert data["matched"] is True
        assert data["concept"]["id"] == "region-factible"
        assert data["concept"]["content"]
        assert isinstance(data["related"], list)

    def test_returns_suggestions_when_no_match(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            reverse("theory:query"),
            {"question": "xkcd asdf qwer"},
            format="json",
        )
        assert response.status_code == 200

        data = response.json()
        assert data["matched"] is False
        assert data["concept"] is None
        assert "message" in data
        # Even when nothing matches we return at least a few suggestions to nudge.
        assert isinstance(data["suggestions"], list)

    def test_rejects_empty_question(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            reverse("theory:query"), {"question": ""}, format="json"
        )
        assert response.status_code == 400

    def test_rejects_missing_question(self, auth_client: APIClient) -> None:
        response = auth_client.post(reverse("theory:query"), {}, format="json")
        assert response.status_code == 400
