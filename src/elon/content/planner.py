"""Daily content planner.

Cadence (locked default; per-tenant override via Tenant.settings_json["cadence"]):
  - IG: 1/day
  - TT: 1/day
  - FB: 3/week (Mon, Wed, Fri)

Per tenant per Beat-tick:
  1. Compute today's slate from cadence rules (which platforms publish today).
  2. For each platform: choose a pillar weighted by `weights["pillars"]`,
     pick the lightest segment, build a ContentBrief, queue draft_post.
  3. Avoid over-queueing: if a draft/review/scheduled post for that platform
     already exists for today, skip.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from elon.core.db import session_scope
from elon.core.logging import get_logger
from elon.core.models import ContentBrief, Post, Tenant
from elon.memory.brand import get_current as get_brand, to_dict as brand_to_dict
from elon.strategy import audience as audience_mod
from elon.strategy import pillars as pillars_mod
from elon.strategy.weights import get_weights

log = get_logger(__name__)

DEFAULT_CADENCE: dict[str, Any] = {
    "ig":     {"per_week": 7, "weekdays": [0, 1, 2, 3, 4, 5, 6]},  # 1/day
    "tiktok": {"per_week": 7, "weekdays": [0, 1, 2, 3, 4, 5, 6]},
    "fb":     {"per_week": 3, "weekdays": [0, 2, 4]},               # Mon/Wed/Fri
}


def _cadence(tenant: Tenant) -> dict[str, Any]:
    s = dict((tenant.settings_json or {}).get("cadence") or {})
    out = {}
    for p, default in DEFAULT_CADENCE.items():
        out[p] = {**default, **(s.get(p) or {})}
    return out


def _platforms_for_today(cadence: dict[str, Any], today_idx: int) -> list[str]:
    return [p for p, rule in cadence.items() if today_idx in rule["weekdays"]]


def _pick_pillar(brand_memory: dict, weights: dict) -> dict | None:
    pillars = pillars_mod.list_pillars(brand_memory)
    if not pillars:
        return None
    pw = weights.get("pillars") or {}
    weighted = [(p, float(pw.get(p.get("id", ""), 1.0)) * float(p.get("weight", 1.0))) for p in pillars]
    total = sum(w for _, w in weighted) or 1.0
    r = random.random() * total
    acc = 0.0
    for p, w in weighted:
        acc += w
        if r <= acc:
            return p
    return weighted[-1][0]


def _has_open_post_today(db: Session, tenant_id: UUID, platform: str) -> bool:
    today = datetime.now(timezone.utc).date()
    rows = db.execute(
        select(Post.id, Post.created_at, Post.state)
        .where(Post.tenant_id == tenant_id, Post.platform == platform,
               Post.state.in_(["draft", "review", "approved", "scheduled"]))
        .order_by(Post.created_at.desc()).limit(5)
    ).all()
    return any(r.created_at and r.created_at.date() == today for r in rows)


def plan_for_tenant(tenant_id: UUID) -> dict[str, Any]:
    from elon.workers.tasks.content import draft_post

    with session_scope() as db:
        tenant = db.get(Tenant, tenant_id)
        if tenant is None:
            return {"ok": False, "error": "tenant_not_found"}
        bm = get_brand(db, tenant_id)
        if bm is None:
            return {"ok": False, "error": "no_brand_memory"}
        bm_dict = brand_to_dict(bm) or {}
        weights = get_weights(db, tenant_id)
        cadence = _cadence(tenant)
        today_idx = datetime.now(timezone.utc).weekday()
        platforms = _platforms_for_today(cadence, today_idx)
        queued: list[dict] = []
        skipped: list[dict] = []
        for platform in platforms:
            if _has_open_post_today(db, tenant_id, platform):
                skipped.append({"platform": platform, "reason": "already_queued"})
                continue
            pillar = _pick_pillar(bm_dict, weights)
            persona = audience_mod.pick_default(bm_dict)
            brief = ContentBrief(
                tenant_id=tenant_id,
                origin="self",
                platform=platform,
                pillar_id=(pillar or {}).get("id"),
                segment_id=(persona or {}).get("id"),
                instructions=(
                    f"Pillar: {(pillar or {}).get('name','-')} — {(pillar or {}).get('description','')}. "
                    f"Audience: {(persona or {}).get('name','-')} — {(persona or {}).get('summary','')}."
                ),
                status="open",
            )
            db.add(brief)
            db.flush()
            queued.append({"platform": platform, "brief_id": str(brief.id)})

    # Dispatch outside the session
    for q in queued:
        draft_post.delay(str(tenant_id), "(autonomous daily plan)", q["platform"], q["brief_id"])
    return {"ok": True, "queued": queued, "skipped": skipped}


def plan_all_tenants() -> dict[str, Any]:
    out = []
    with session_scope() as db:
        ids = [t.id for t in db.execute(
            select(Tenant).where(Tenant.deleted_at.is_(None))
        ).scalars().all()]
    for tid in ids:
        try:
            r = plan_for_tenant(tid)
            out.append({"tenant_id": str(tid), **r})
        except Exception as e:
            log.error("plan_failed", tenant_id=str(tid), error=str(e))
            out.append({"tenant_id": str(tid), "ok": False, "error": str(e)})
    return {"ok": True, "tenants": out}


# Schedule a published post: pick the next-soonest cadence slot for that platform.
def next_slot(tenant: Tenant, platform: str, after: datetime | None = None) -> datetime:
    after = after or datetime.now(timezone.utc)
    cadence = _cadence(tenant)
    weekdays = cadence[platform]["weekdays"]
    # Find next weekday in the rule list >= today; default to a fixed posting hour.
    hour = int((tenant.settings_json or {}).get("post_hour_utc", 14))
    for i in range(7):
        d = (after + timedelta(days=i)).date()
        if d.weekday() in weekdays:
            slot = datetime(d.year, d.month, d.day, hour, 0, tzinfo=timezone.utc)
            if slot > after:
                return slot
    return after + timedelta(days=1)
