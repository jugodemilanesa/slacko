"""Deterministic concept matcher for the theoretical tutor.

Given a free-form student question in Spanish, score every concept in
:mod:`apps.theory.knowledge_base` by how well it matches and return the best
candidate plus a few suggestions. There is **no LLM, no embedding, no external
service** involved — only string normalization and token overlap. This keeps the
tutor fully predictable and trivially testable.

The same module will be replaced (or wrapped) by an embedding-based retriever
when the RAG pipeline lands; the API contract should stay the same.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .knowledge_base import CONCEPTS, Concept


# Spanish stopwords used as connectors in the kind of questions students ask.
# Kept short on purpose — over-aggressive stopword removal hurts more than it
# helps when the surface form *is* the signal (e.g. "para" can be meaningful in
# "para qué sirve la holgura").
_STOPWORDS: frozenset[str] = frozenset(
    {
        "a",
        "al",
        "como",
        "con",
        "cual",
        "cuales",
        "de",
        "del",
        "donde",
        "el",
        "en",
        "es",
        "esa",
        "ese",
        "eso",
        "esta",
        "este",
        "esto",
        "la",
        "las",
        "lo",
        "los",
        "me",
        "mi",
        "o",
        "para",
        "pero",
        "por",
        "que",
        "se",
        "si",
        "son",
        "su",
        "sus",
        "te",
        "un",
        "una",
        "unos",
        "unas",
        "y",
    }
)


# Score weights — tuned by the unit tests in apps/theory/tests.
_FULL_PHRASE_BONUS = 10.0
_PHRASE_LENGTH_WEIGHT = 5.0
_TITLE_TOKEN_WEIGHT = 3.0
_ALIAS_TOKEN_WEIGHT = 1.0
_MIN_SCORE_FOR_MATCH = 3.0
_MAX_SUGGESTIONS = 3


# ─── Normalization ────────────────────────────────────────────────────────


def normalize(text: str) -> str:
    """Lowercase, strip accents, replace punctuation with spaces, collapse spaces.

    Used both to preprocess the user's question and to canonicalize concept
    aliases at scoring time.
    """

    if not text:
        return ""
    text = text.lower()
    # Decompose accents and drop combining marks: "óptima" → "optima".
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text) if not unicodedata.combining(ch)
    )
    # Replace anything that is not a letter or digit with a single space.
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def tokenize(text: str, *, drop_stopwords: bool = True) -> list[str]:
    """Tokenize an already-normalized string and (optionally) drop stopwords."""

    tokens = normalize(text).split() if not _is_normalized(text) else text.split()
    if drop_stopwords:
        tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
    return tokens


def _is_normalized(text: str) -> bool:
    return text == "" or re.fullmatch(r"[a-z0-9]+( [a-z0-9]+)*", text) is not None


# ─── Indexing ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class _IndexedConcept:
    concept: Concept
    title_tokens: frozenset[str]
    alias_tokens: frozenset[str]
    alias_phrases: tuple[str, ...]  # already normalized


def _build_index() -> tuple[_IndexedConcept, ...]:
    """Pre-normalize titles and aliases for every concept (built once at import)."""

    indexed: list[_IndexedConcept] = []
    for concept in CONCEPTS:
        title_tokens = frozenset(tokenize(concept.title))
        alias_phrases: list[str] = []
        alias_tokens: set[str] = set()
        for alias in concept.aliases:
            normalized_alias = normalize(alias)
            if normalized_alias:
                alias_phrases.append(normalized_alias)
                alias_tokens.update(
                    tokenize(normalized_alias, drop_stopwords=True)
                )
        indexed.append(
            _IndexedConcept(
                concept=concept,
                title_tokens=title_tokens,
                alias_tokens=frozenset(alias_tokens),
                alias_phrases=tuple(alias_phrases),
            )
        )
    return tuple(indexed)


_INDEX: tuple[_IndexedConcept, ...] = _build_index()


# ─── Scoring ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Score:
    """Score for a single concept against a question."""

    concept_id: str
    score: float


def _score_concept(
    indexed: _IndexedConcept,
    question_normalized: str,
    question_tokens: frozenset[str],
) -> float:
    """Return a non-negative score for one concept against the question."""

    if not question_tokens:
        return 0.0

    score = 0.0

    # 1. Full-phrase alias substring match (strongest signal). We pick the
    # longest matching alias to reward more specific phrasings.
    longest_match = 0
    for phrase in indexed.alias_phrases:
        if phrase and phrase in question_normalized:
            longest_match = max(longest_match, len(phrase.split()))
    if longest_match:
        score += _FULL_PHRASE_BONUS + longest_match * _PHRASE_LENGTH_WEIGHT

    # 2. Title token overlap.
    title_overlap = question_tokens & indexed.title_tokens
    score += _TITLE_TOKEN_WEIGHT * len(title_overlap)

    # 3. Alias token overlap (excluding tokens already counted in the title to
    # avoid double-counting).
    alias_overlap = (question_tokens & indexed.alias_tokens) - indexed.title_tokens
    score += _ALIAS_TOKEN_WEIGHT * len(alias_overlap)

    return score


# ─── Public API ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MatchResult:
    """Outcome of matching a user question against the knowledge base."""

    matched: bool
    concept: Concept | None
    score: float
    suggestions: tuple[Concept, ...]
    question_normalized: str


def match(question: str) -> MatchResult:
    """Match a free-form question against the knowledge base.

    Returns the best concept above the threshold (``matched=True``) plus a few
    suggestions. If nothing crosses the threshold, ``matched=False`` and the
    suggestions hold the top candidates so the UI can offer "did you mean…?".
    """

    question_normalized = normalize(question)
    question_tokens = frozenset(
        tokenize(question_normalized, drop_stopwords=True)
    )

    scored: list[tuple[_IndexedConcept, float]] = [
        (idx, _score_concept(idx, question_normalized, question_tokens))
        for idx in _INDEX
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)

    if not scored or scored[0][1] <= 0:
        return MatchResult(
            matched=False,
            concept=None,
            score=0.0,
            suggestions=tuple(idx.concept for idx, _ in scored[:_MAX_SUGGESTIONS]),
            question_normalized=question_normalized,
        )

    best_idx, best_score = scored[0]
    matched = best_score >= _MIN_SCORE_FOR_MATCH

    suggestions = tuple(
        idx.concept
        for idx, sc in scored[1 : _MAX_SUGGESTIONS + 1]
        if sc > 0
    )

    return MatchResult(
        matched=matched,
        concept=best_idx.concept if matched else None,
        score=best_score,
        suggestions=suggestions if matched else tuple(
            idx.concept for idx, sc in scored[:_MAX_SUGGESTIONS] if sc > 0
        ),
        question_normalized=question_normalized,
    )


def score_all(question: str) -> list[Score]:
    """Return the score of every concept (debug helper, not used by the API)."""

    question_normalized = normalize(question)
    question_tokens = frozenset(
        tokenize(question_normalized, drop_stopwords=True)
    )
    return [
        Score(
            concept_id=idx.concept.id,
            score=_score_concept(idx, question_normalized, question_tokens),
        )
        for idx in _INDEX
    ]
