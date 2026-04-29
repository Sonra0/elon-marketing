"""Compare a fresh snapshot to the tenant's recent baseline; if a metric is
> 3x or < 0.3x of the rolling median, flag an anomaly.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable
from typing import Any

WATCHED = ("reach", "impressions", "plays", "likes")


def detect(current: dict[str, Any], history: Iterable[dict[str, Any]]) -> list[dict]:
    hist = list(history)
    out: list[dict] = []
    for k in WATCHED:
        cur = current.get(k)
        if cur is None or not isinstance(cur, (int, float)):
            continue
        prev = [h.get(k) for h in hist if isinstance(h.get(k), (int, float))]
        if len(prev) < 5:
            continue
        med = statistics.median(prev)
        if med <= 0:
            continue
        ratio = cur / med
        if ratio >= 3.0:
            out.append({"metric": k, "kind": "spike", "ratio": ratio, "median": med, "current": cur})
        elif ratio <= 0.3:
            out.append({"metric": k, "kind": "drop", "ratio": ratio, "median": med, "current": cur})
    return out
