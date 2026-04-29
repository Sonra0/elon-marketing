"""Per-tenant token-bucket rate limiter (Redis).

Used by publishers + Claude calls to prevent a single tenant from monopolizing
shared resources (Meta/TikTok per-app quotas, Anthropic RPM).

Bucket key:  rl:{scope}:{tenant_id}
Algorithm:   atomic INCR with TTL == window seconds; reject when > capacity.
"""

from __future__ import annotations

import time
from contextlib import contextmanager

import redis

from elon.core.settings import get_settings

_r = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)


class RateLimitExceeded(RuntimeError):
    pass


def hit(scope: str, tenant_id: str, *, capacity: int, window_s: int) -> int:
    key = f"rl:{scope}:{tenant_id}"
    pipe = _r.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_s, nx=True)
    count, _ = pipe.execute()
    if count > capacity:
        raise RateLimitExceeded(f"{scope} over capacity for tenant {tenant_id}: {count}/{capacity} per {window_s}s")
    return int(count)


@contextmanager
def gate(scope: str, tenant_id: str, *, capacity: int, window_s: int, retries: int = 0):
    """Block-and-wait variant for short windows. Raises after retries."""
    for attempt in range(retries + 1):
        try:
            hit(scope, tenant_id, capacity=capacity, window_s=window_s)
            yield
            return
        except RateLimitExceeded:
            if attempt >= retries:
                raise
            time.sleep(min(2 ** attempt, 30))
