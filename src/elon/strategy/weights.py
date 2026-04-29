"""Per-tenant strategy weights.

Weights are stored on Tenant.settings_json under the "weights" key:

  {
    "pillars":  {pillar_id -> float multiplier, default 1.0},
    "hooks":    {hook_style -> float},
    "segments": {segment_id -> float},
    "platforms": {"ig": float, "tiktok": float, "fb": float}
  }

The aggregator nudges these based on analytics deltas vs the tenant baseline
(e.g. a pillar that beats baseline reach by >20% gets +0.05 cap at 3.0).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from elon.core.models import AnalyticsSnapshot, Post, Tenant

DEFAULT_W = 1.0
MIN_W, MAX_W = 0.25, 3.0


def _get_settings(db: Session, tenant_id: UUID) -> dict[str, Any]:
    row = db.get(Tenant, tenant_id)
    return dict(row.settings_json or {}) if row else {}


def _save_settings(db: Session, tenant_id: UUID, settings: dict[str, Any]) -> None:
    db.execute(update(Tenant).where(Tenant.id == tenant_id).values(settings_json=settings))


def get_weights(db: Session, tenant_id: UUID) -> dict[str, dict[str, float]]:
    s = _get_settings(db, tenant_id)
    w = dict(s.get("weights") or {})
    for k in ("pillars", "hooks", "segments", "platforms"):
        w.setdefault(k, {})
    return w


def bump(db: Session, tenant_id: UUID, axis: str, key: str, delta: float) -> float:
    s = _get_settings(db, tenant_id)
    w = dict(s.get("weights") or {})
    table = dict(w.get(axis) or {})
    cur = float(table.get(key, DEFAULT_W))
    new = max(MIN_W, min(MAX_W, cur + delta))
    table[key] = new
    w[axis] = table
    s["weights"] = w
    _save_settings(db, tenant_id, s)
    return new


def baseline(db: Session, tenant_id: UUID, platform: str, metric: str = "reach") -> float | None:
    """Median of `metric` across the tenant's last 30 published posts on a platform."""
    rows = db.execute(
        select(AnalyticsSnapshot.metrics_json)
        .join(Post, Post.id == AnalyticsSnapshot.post_id)
        .where(Post.tenant_id == tenant_id, Post.platform == platform)
        .order_by(AnalyticsSnapshot.taken_at.desc())
        .limit(30)
    ).scalars().all()
    vals = [r.get(metric) for r in rows if isinstance(r.get(metric), (int, float))]
    if not vals:
        return None
    vals.sort()
    return float(vals[len(vals) // 2])


def learn_from_post(db: Session, tenant_id: UUID, post_id: UUID) -> dict[str, Any]:
    """Compare a post's freshest snapshot to the tenant's baseline; nudge weights.
    Returns a summary of bumps applied (used for digest + audit).
    """
    snap = db.execute(
        select(AnalyticsSnapshot)
        .where(AnalyticsSnapshot.post_id == post_id)
        .order_by(AnalyticsSnapshot.taken_at.desc())
    ).scalars().first()
    post = db.get(Post, post_id)
    if snap is None or post is None:
        return {"applied": []}
    base = baseline(db, tenant_id, post.platform, "reach")
    cur = (snap.metrics_json or {}).get("reach")
    if not isinstance(cur, (int, float)) or not base:
        return {"applied": []}
    ratio = cur / base
    delta = 0.05 if ratio >= 1.2 else (-0.05 if ratio <= 0.8 else 0.0)
    if delta == 0:
        return {"applied": [], "ratio": ratio}
    applied = []
    pillar_id = (post.score_json or {}).get("pillar_id") or (post.error_json or {}).get("pillar_id")
    if pillar_id:
        applied.append(("pillars", pillar_id, bump(db, tenant_id, "pillars", str(pillar_id), delta)))
    applied.append(("platforms", post.platform, bump(db, tenant_id, "platforms", post.platform, delta)))
    return {"applied": applied, "ratio": ratio}
