"""Mid-experiment auto-pruning.

Rule: a variant is pruned if, after >=48h of measurement, its primary metric
mean trails the leading variant by >40%. Pruned variants are recorded in
Experiment.results_json["pruned"] and removed from variants_json so the
planner stops injecting them.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select

from elon.core.db import session_scope
from elon.core.models import AnalyticsSnapshot, Experiment, Post

PRUNE_THRESHOLD = 0.6  # variant must be >= 60% of leader to survive
MIN_AGE = timedelta(hours=48)


def _variant_score(db, exp: Experiment, variant_id: str) -> float | None:
    """Average of primary_metric across published posts tagged for this variant.
    Variant tagging convention: Post.score_json["variant_id"].
    """
    posts = db.execute(
        select(Post).where(
            Post.tenant_id == exp.tenant_id,
            Post.published_at.is_not(None),
        )
    ).scalars().all()
    posts = [p for p in posts if (p.score_json or {}).get("variant_id") == variant_id]
    if not posts:
        return None
    snaps_vals: list[float] = []
    for p in posts:
        snap = db.execute(
            select(AnalyticsSnapshot)
            .where(AnalyticsSnapshot.post_id == p.id)
            .order_by(AnalyticsSnapshot.taken_at.desc())
        ).scalars().first()
        if snap and isinstance((snap.metrics_json or {}).get(exp.primary_metric), (int, float)):
            snaps_vals.append(float(snap.metrics_json[exp.primary_metric]))
    if not snaps_vals:
        return None
    return sum(snaps_vals) / len(snaps_vals)


def prune_active() -> dict[str, Any]:
    pruned_total = 0
    now = datetime.now(timezone.utc)
    with session_scope() as db:
        actives = list(db.execute(select(Experiment).where(Experiment.status == "active")).scalars())
        for exp in actives:
            if not exp.start_at or now - exp.start_at < MIN_AGE:
                continue
            variants = list(exp.variants_json or [])
            scored: dict[str, float] = {}
            for v in variants:
                s = _variant_score(db, exp, v.get("id", ""))
                if s is not None:
                    scored[v["id"]] = s
            if len(scored) < 2:
                continue
            leader_score = max(scored.values())
            survivors = [v for v in variants
                         if scored.get(v.get("id"), 0.0) >= leader_score * PRUNE_THRESHOLD]
            pruned = [v for v in variants if v not in survivors]
            if not pruned:
                continue
            exp.variants_json = survivors
            results = dict(exp.results_json or {})
            results.setdefault("pruned", []).extend([
                {"id": p.get("id"), "name": p.get("name"), "score": scored.get(p.get("id", ""))}
                for p in pruned
            ])
            results["mid_scores"] = scored
            exp.results_json = results
            pruned_total += len(pruned)
    return {"ok": True, "pruned": pruned_total}
