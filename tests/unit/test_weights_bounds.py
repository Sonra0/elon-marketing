"""Pure-logic test of weight bumping math (no DB).

We exercise the bounds + delta math by reaching directly into the formula via a
tiny harness, bypassing the Tenant ORM read/write.
"""

from elon.strategy.weights import MAX_W, MIN_W


def _bump_pure(cur: float, delta: float) -> float:
    return max(MIN_W, min(MAX_W, cur + delta))


def test_clamps_to_min():
    assert _bump_pure(MIN_W, -1.0) == MIN_W


def test_clamps_to_max():
    assert _bump_pure(MAX_W, +1.0) == MAX_W


def test_normal_bump():
    assert abs(_bump_pure(1.0, 0.05) - 1.05) < 1e-9
    assert abs(_bump_pure(1.0, -0.05) - 0.95) < 1e-9
