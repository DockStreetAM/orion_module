"""Thread-safety regression tests for orionapi.

These tests exercise the internal locking added in 1.10.0:

- RateLimiter under contention (PRD acceptance #1)
- Per-instance _custom_field_cache isolation (PRD #4 shape check)
- _get_auth_header raises AuthenticationError when not logged in

They do not require Orion credentials.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from orionapi import AuthenticationError, EclipseAPI, OrionAPI, RateLimiter


class TestRateLimiterThreadSafety:
    def test_n_concurrent_calls_take_at_least_n_minus_one_intervals(self):
        """N callers releasing at the same instant should serialize across
        ~(N-1)/rate seconds.

        Without the lock the calls would all fire immediately and the
        elapsed time would be ~0. PRD acceptance #1.
        """
        rate = 20  # 20/s → 50ms per slot
        n_calls = 20
        limiter = RateLimiter(calls_per_second=rate)
        barrier = threading.Barrier(n_calls)

        def worker():
            barrier.wait()
            limiter.wait()
            return time.monotonic()

        start = time.monotonic()
        with ThreadPoolExecutor(max_workers=n_calls) as ex:
            finishes = [f.result() for f in [ex.submit(worker) for _ in range(n_calls)]]
        elapsed = max(finishes) - start

        # (N-1) inter-call gaps × 1/rate seconds each. Allow some slack
        # below (10%) for timer resolution; the upper bound is generous
        # to absorb CI jitter without becoming a flaky test.
        expected = (n_calls - 1) / rate
        assert elapsed >= expected * 0.9, (
            f"limiter let calls slip through: finished in {elapsed:.3f}s, "
            f"expected ≥ {expected * 0.9:.3f}s"
        )
        assert (
            elapsed < expected + 0.5
        ), f"limiter took too long: {elapsed:.3f}s vs expected ~{expected:.3f}s"

    def test_zero_rate_skips_locking(self):
        limiter = RateLimiter(calls_per_second=0)
        # Should return immediately without contention.
        for _ in range(100):
            limiter.wait()

    def test_single_threaded_still_paces(self):
        """The lock change must not break the non-contended common case."""
        limiter = RateLimiter(calls_per_second=20)
        start = time.time()
        for _ in range(5):
            limiter.wait()
        # 5 calls at 20/s = 4 inter-call gaps of 50ms = ~200ms minimum.
        # (The first wait reserves a slot at t=0; subsequent waits each
        # add one min_interval.)
        elapsed = time.time() - start
        assert elapsed >= 0.2, f"expected ≥200ms, got {elapsed:.3f}s"


class TestCacheIsolation:
    def test_custom_field_cache_is_per_instance(self):
        """Two OrionAPI clients must not share custom-field caches."""
        a = OrionAPI()
        b = OrionAPI()
        a._custom_field_cache["client"] = {"AAA": "udfAAA"}
        assert "client" not in b._custom_field_cache, (
            "1.10.0 moved _custom_field_cache to instance state; "
            "if this fails the class-level dict has crept back in"
        )

    def test_each_client_has_its_own_locks(self):
        a = OrionAPI()
        b = OrionAPI()
        assert a._custom_field_lock is not b._custom_field_lock
        assert a._token_lock is not b._token_lock
        assert a._rate_limiter is not b._rate_limiter


class TestAuthHeaderWithoutLogin:
    def test_orion_raises_when_not_logged_in(self):
        api = OrionAPI()
        with pytest.raises(AuthenticationError):
            api._get_auth_header()

    def test_eclipse_raises_when_not_logged_in(self):
        api = EclipseAPI()
        with pytest.raises(AuthenticationError):
            api._get_auth_header()
