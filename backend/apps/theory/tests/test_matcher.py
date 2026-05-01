"""Tests for the deterministic matcher.

These tests pin the scoring contract: how questions get normalized, which
concepts win for representative phrasings, and what happens when nothing
matches. They run as plain pytest tests (no Django fixtures needed).
"""

from __future__ import annotations

import pytest

from apps.theory import knowledge_base as kb
from apps.theory.matcher import match, normalize, score_all, tokenize


# ─── Normalization ────────────────────────────────────────────────────────


class TestNormalize:
    def test_lowercases(self) -> None:
        assert normalize("Programación LINEAL") == "programacion lineal"

    def test_strips_accents(self) -> None:
        assert normalize("región factible") == "region factible"

    def test_strips_punctuation(self) -> None:
        assert normalize("¿Qué es la PL?") == "que es la pl"

    def test_collapses_whitespace(self) -> None:
        assert normalize("hola    mundo\n\ttest") == "hola mundo test"

    def test_handles_empty(self) -> None:
        assert normalize("") == ""
        assert normalize("   ") == ""

    def test_keeps_digits(self) -> None:
        assert normalize("X1 + X2 ≤ 24") == "x1 x2 24"


class TestTokenize:
    def test_drops_stopwords(self) -> None:
        tokens = tokenize("que es la region factible")
        assert "que" not in tokens
        assert "es" not in tokens
        assert "la" not in tokens
        assert "region" in tokens
        assert "factible" in tokens

    def test_drops_short_tokens(self) -> None:
        # Single chars filtered out (after stopword removal).
        tokens = tokenize("a b c region")
        assert tokens == ["region"]


# ─── Matching ─────────────────────────────────────────────────────────────


class TestMatch:
    @pytest.mark.parametrize(
        "question, expected_id",
        [
            ("¿Qué es la programación lineal?", "programacion-lineal"),
            ("definicion de PL", "programacion-lineal"),
            ("por qué se llama lineal?", "por-que-lineal"),
            ("por qué programación", "por-que-programacion"),
            ("qué es un modelo de PL", "modelo-pl"),
            ("cuáles son los supuestos", "supuestos-pl"),
            ("qué es la proporcionalidad", "proporcionalidad"),
            ("qué es la aditividad", "aditividad"),
            ("qué es la divisibilidad", "divisibilidad"),
            ("qué es la certidumbre", "certidumbre"),
            ("componentes básicos de PL", "componentes-pl"),
            ("qué son las variables de decisión", "variables-decision"),
            ("qué es la función objetivo", "funcion-objetivo"),
            ("qué son las restricciones", "restricciones"),
            ("qué son los coeficientes tecnológicos", "coeficientes-tecnologicos"),
            ("qué representa bi", "terminos-independientes"),
            ("condición de no negatividad", "no-negatividad"),
            ("qué es la región factible", "region-factible"),
            ("qué es el cuerpo factible", "region-factible"),
            ("cuál es la solución óptima", "solucion-optima"),
            ("qué es un vértice", "punto-extremo"),
            ("qué es un punto extremo", "punto-extremo"),
            ("teorema fundamental de la PL", "teorema-fundamental"),
            ("qué es la forma canónica", "forma-canonica"),
            ("qué es la forma estándar", "forma-estandar"),
            ("cómo paso de canónica a estándar", "conversion-canonica-estandar"),
            ("qué es una variable de holgura", "variable-holgura"),
            ("qué es slack", "variable-holgura"),
            ("qué es una variable de excedente", "variable-excedente"),
            ("qué es surplus", "variable-excedente"),
            ("qué es una variable artificial", "variable-artificial"),
            ("método de la gran M", "variable-artificial"),
            ("elementos del método gráfico", "metodo-grafico-elementos"),
            ("pasos del método gráfico", "metodo-grafico-pasos"),
            ("qué es la degeneración", "caso-degeneracion"),
            ("óptimos alternativos", "caso-optimos-alternativos"),
            ("infinitas soluciones", "caso-optimos-alternativos"),
            ("solución no acotada", "caso-no-acotada"),
            ("solución no factible", "caso-no-factible"),
            ("restricciones incompatibles", "caso-no-factible"),
        ],
    )
    def test_known_questions_resolve_to_expected_concept(
        self, question: str, expected_id: str
    ) -> None:
        result = match(question)
        assert result.matched is True, (
            f"Question {question!r} did not match anything; "
            f"top suggestions={[s.id for s in result.suggestions]}"
        )
        assert result.concept is not None
        assert result.concept.id == expected_id

    def test_returns_suggestions_when_below_threshold(self) -> None:
        result = match("xkcd asdfgh foobar")
        assert result.matched is False
        assert result.concept is None

    def test_returns_suggestions_for_partial_match(self) -> None:
        # "factible" alone is ambiguous between region-factible and case
        # concepts. The scorer should still surface region-factible at the top
        # because its title carries the token.
        result = match("factible")
        assert result.matched is True
        assert result.concept is not None
        assert result.concept.id == "region-factible"

    def test_empty_question_does_not_match(self) -> None:
        result = match("")
        assert result.matched is False
        assert result.concept is None

    def test_match_includes_related_in_suggestions_position(self) -> None:
        # Suggestions exclude the matched concept itself.
        result = match("región factible")
        assert result.matched is True
        assert result.concept is not None
        assert result.concept.id == "region-factible"
        assert result.concept.id not in {s.id for s in result.suggestions}

    def test_score_all_returns_one_score_per_concept(self) -> None:
        scores = score_all("región factible")
        assert len(scores) == len(kb.CONCEPTS)
        # All scores non-negative.
        assert all(s.score >= 0 for s in scores)
        # The top score belongs to region-factible.
        scores.sort(key=lambda s: s.score, reverse=True)
        assert scores[0].concept_id == "region-factible"


class TestKnowledgeBaseIntegrity:
    """Sanity checks on the curated data itself."""

    def test_no_duplicate_concept_ids(self) -> None:
        ids = [c.id for c in kb.CONCEPTS]
        assert len(ids) == len(set(ids))

    def test_no_duplicate_category_ids(self) -> None:
        ids = [c.id for c in kb.CATEGORIES]
        assert len(ids) == len(set(ids))

    def test_every_concept_has_a_known_category(self) -> None:
        valid_categories = {c.id for c in kb.CATEGORIES}
        for concept in kb.CONCEPTS:
            assert concept.category in valid_categories, (
                f"{concept.id} points at unknown category {concept.category!r}"
            )

    def test_every_related_id_exists(self) -> None:
        for concept in kb.CONCEPTS:
            for related_id in concept.related:
                assert related_id in kb.CONCEPTS_BY_ID, (
                    f"{concept.id} references unknown concept {related_id!r}"
                )

    def test_every_concept_has_at_least_one_alias(self) -> None:
        for concept in kb.CONCEPTS:
            assert concept.aliases, f"{concept.id} has no aliases"

    def test_every_concept_has_non_empty_summary_and_content(self) -> None:
        for concept in kb.CONCEPTS:
            assert concept.summary.strip()
            assert concept.content.strip()
