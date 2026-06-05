"""Tests de validación de inputs en los serializers de chat."""

from __future__ import annotations

import pytest

from apps.chat.serializers import _MAX_TAGS, SessionUpdateSerializer


def test_tags_acepta_lista_de_strings():
    s = SessionUpdateSerializer(data={"tags": ["pl", "  grafico  ", "vértices"]})
    assert s.is_valid(), s.errors
    # Se trimean y se descartan vacíos.
    assert s.validated_data["tags"] == ["pl", "grafico", "vértices"]


def test_tags_descarta_vacios():
    s = SessionUpdateSerializer(data={"tags": ["ok", "   ", ""]})
    assert s.is_valid(), s.errors
    assert s.validated_data["tags"] == ["ok"]


def test_tags_rechaza_no_lista():
    s = SessionUpdateSerializer(data={"tags": "pl"})
    assert not s.is_valid()
    assert "tags" in s.errors


def test_tags_rechaza_elemento_no_string():
    s = SessionUpdateSerializer(data={"tags": ["ok", 123]})
    assert not s.is_valid()
    assert "tags" in s.errors


def test_tags_rechaza_demasiadas():
    s = SessionUpdateSerializer(data={"tags": [f"t{i}" for i in range(_MAX_TAGS + 1)]})
    assert not s.is_valid()
    assert "tags" in s.errors


def test_tags_rechaza_tag_muy_largo():
    s = SessionUpdateSerializer(data={"tags": ["x" * 41]})
    assert not s.is_valid()
    assert "tags" in s.errors
