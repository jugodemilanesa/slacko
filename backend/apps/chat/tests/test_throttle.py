"""Tests for the sliding window rate limiter."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from apps.chat.throttle import SlidingWindowRateLimiter, ThrottleDecision


@pytest.fixture(autouse=True)
def _isolate_module_state():
    """Each test starts with fresh module-level limiter state."""

    from apps.chat import throttle

    throttle.reset_for_tests()
    yield
    throttle.reset_for_tests()


class TestSlidingWindowSingleBucket:
    def test_allows_under_limit(self) -> None:
        limiter = SlidingWindowRateLimiter([("m", 3, 60.0)])
        for _ in range(3):
            d = limiter.check("u1")
            assert d.allowed is True
            assert d.retry_after_seconds is None

    def test_blocks_at_limit(self) -> None:
        limiter = SlidingWindowRateLimiter([("m", 2, 60.0)])
        assert limiter.check("u1").allowed
        assert limiter.check("u1").allowed
        d = limiter.check("u1")
        assert d.allowed is False
        assert d.scope == "m"
        assert d.retry_after_seconds is not None
        assert 0.0 < d.retry_after_seconds <= 60.0

    def test_keys_are_independent(self) -> None:
        limiter = SlidingWindowRateLimiter([("m", 1, 60.0)])
        assert limiter.check("alice").allowed
        # alice is now exhausted, but bob is fresh
        assert limiter.check("alice").allowed is False
        assert limiter.check("bob").allowed

    def test_window_slides(self) -> None:
        """Once a request falls out of the window, a new one is admitted."""

        limiter = SlidingWindowRateLimiter([("m", 1, 60.0)])

        with patch("apps.chat.throttle.time.monotonic") as mt:
            mt.return_value = 1000.0
            assert limiter.check("u1").allowed
            assert limiter.check("u1").allowed is False

            # Jump 61 seconds — the window has slid past the first hit.
            mt.return_value = 1061.0
            assert limiter.check("u1").allowed


class TestSlidingWindowMultipleBuckets:
    """When a limiter has multiple buckets, the strictest one rules."""

    def test_minute_bucket_blocks_first(self) -> None:
        limiter = SlidingWindowRateLimiter(
            [("min", 2, 60.0), ("hour", 100, 3600.0)]
        )
        assert limiter.check("u1").allowed
        assert limiter.check("u1").allowed
        d = limiter.check("u1")
        assert d.allowed is False
        assert d.scope == "min"

    def test_no_consumption_on_block(self) -> None:
        """A blocked check must not consume cupo against the looser bucket.

        Otherwise a tight per-minute limit would eat away at the hour bucket
        even when nothing was actually answered — exhausting hour capacity
        on rejected requests.
        """

        limiter = SlidingWindowRateLimiter(
            [("min", 1, 60.0), ("hour", 5, 3600.0)]
        )
        with patch("apps.chat.throttle.time.monotonic") as mt:
            mt.return_value = 1000.0
            assert limiter.check("u1").allowed  # 1/1 min, 1/5 hour

            # Spam 10 times at the same instant — all blocked by minute bucket.
            for _ in range(10):
                d = limiter.check("u1")
                assert d.allowed is False
                assert d.scope == "min"

            # If those 10 blocks had consumed from the hour bucket, we'd be at
            # 11/5 already. We verify by stepping past the minute window once
            # per minute and confirming 4 more successes (totalling 5/5 hour).
            for i in range(1, 5):
                mt.return_value = 1000.0 + 60.5 * i
                assert limiter.check("u1").allowed, f"step {i} should pass"

            # We've now used 5/5 hour. Even with a fresh minute bucket,
            # next call must block on the hour scope.
            mt.return_value = 1000.0 + 60.5 * 6
            d = limiter.check("u1")
            assert d.allowed is False
            assert d.scope == "hour"


class TestModuleHelpers:
    def test_check_user_and_global_independent(self) -> None:
        """Burning the global cap should not burn the user cap and vice versa."""

        from apps.chat import throttle

        # With defaults (6/min user, 9/min global), 7 user requests should
        # block on user_min, not on global_min.
        with patch("apps.chat.throttle.time.monotonic") as mt:
            mt.return_value = 0.0
            results = [throttle.check_user(42) for _ in range(7)]

        decisions: list[ThrottleDecision] = results
        assert all(d.allowed for d in decisions[:6])
        assert decisions[6].allowed is False
        assert decisions[6].scope == "user_min"

    def test_settings_knobs_are_read(self, settings) -> None:
        """Settings can lower or raise the limits without code changes."""

        from apps.chat import throttle

        settings.LLM_THROTTLE_USER_PER_MINUTE = 2
        settings.LLM_THROTTLE_USER_PER_HOUR = 10
        settings.LLM_THROTTLE_GLOBAL_PER_MINUTE = 100
        throttle.reset_for_tests()

        assert throttle.check_user(1).allowed
        assert throttle.check_user(1).allowed
        d = throttle.check_user(1)
        assert d.allowed is False
        assert d.scope == "user_min"
