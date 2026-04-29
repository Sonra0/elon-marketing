"""Weekly hypothesis cycle.

Each Monday:
  1. propose(): the agent generates 1-3 hypotheses (via Claude) anchored on
     recent analytics + competitor gaps. Each hypothesis = {hypothesis, variants,
     primary_metric}. Operator approves via chat.
  2. inject(): when an Experiment is approved, the planner picks variants from it
     for the next week's content slots.
  3. evaluate(): once every variant has at least one analytics snapshot,
     compute primary metric per variant; write results + learnings.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select

from elon.core.db import session_scope
from elon.core.llm import call_claude
from elon.core.models import AnalyticsSnapshot, Experiment, MemoryEvent, Post, Tenant, User
from elon.memory.brand import get_current as get_brand
from elon.memory.brand import to_dict as brand_to_dict

PROPOSER_SYSTEM = """\
You are a senior growth marketer designing weekly experiments.
Given the brand pillars + last week's analytics + competitor gaps, propose 1-3
hypothesis-driven A/B tests. Each must specify a primary metric measurable from
platform analytics (reach, plays, comments, ctr, saves). Variants are concrete
content directions (NOT full drafts).

Return ONLY JSON:
{"experiments":[{
  "hypothesis": str,
  "primary_metric": "reach"|"plays"|"comments"|"saves"|"ctr",
  "variants": [{"id": str, "name": str, "direction": str}]
}]}
"""


def propose_for_tenant(tenant_id: UUID) -> list[dict[str, Any]]:
    with session_scope() as db:
        bm = get_brand(db, tenant_id)
        if bm is None:
            return []
        recent_metrics = list(db.execute(
            select(AnalyticsSnapshot.metrics_json).join(Post, Post.id == AnalyticsSnapshot.post_id)
            .where(Post.tenant_id == tenant_id)
            .order_by(AnalyticsSnapshot.taken_at.desc()).limit(20)
        ).scalars())
        gaps = list(db.execute(
            select(MemoryEvent.payload_json).where(
                MemoryEvent.tenant_id == tenant_id, MemoryEvent.type == "competitor_gaps"
            ).order_by(MemoryEvent.created_at.desc()).limit(5)
        ).scalars())
        owner = db.execute(
            select(User).where(User.tenant_id == tenant_id, User.role == "owner")
        ).scalar_one_or_none()
        chat_id = owner.telegram_user_id if owner else None
        bm_dict = brand_to_dict(bm) or {}

    payload = json.dumps({
        "pillars": bm_dict.get("pillars_json", []),
        "recent_metrics": recent_metrics,
        "competitor_gaps": gaps,
    })
    resp = call_claude(
        tenant_id=str(tenant_id),
        system_blocks=[{"type": "text", "text": PROPOSER_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": payload}],
        max_tokens=1200,
    )
    txt = "".join(b.text for b in resp.content if b.type == "text").strip()
    try:
        proposed = json.loads(txt).get("experiments", [])
    except json.JSONDecodeError:
        return []

    # Persist and notify operator (approval = "approved" status set by chat reply).
    out: list[dict[str, Any]] = []
    with session_scope() as db:
        for p in proposed:
            exp = Experiment(
                tenant_id=tenant_id,
                hypothesis=p.get("hypothesis", ""),
                variants_json=p.get("variants", []),
                primary_metric=p.get("primary_metric", "reach"),
                start_at=datetime.now(timezone.utc),
                end_at=datetime.now(timezone.utc) + timedelta(days=7),
                status="proposed",
            )
            db.add(exp)
            db.flush()
            out.append({"id": str(exp.id), **p})

    if chat_id and out:
        from elon.chat.notify import send_telegram
        lines = ["Weekly experiment proposals (reply 'approve <id>' to accept):"]
        for e in out:
            lines.append(f"\n[{e['id'][:8]}] {e.get('hypothesis')}")
            for v in e.get("variants", []):
                lines.append(f"  - {v.get('name')}: {v.get('direction')}")
        send_telegram(chat_id, "\n".join(lines))
    return out


def evaluate_active() -> dict[str, Any]:
    """Walk active experiments; if all variants have at least one snapshot,
    compute the winning variant by primary_metric and finalize.
    """
    finalized = 0
    with session_scope() as db:
        active = list(db.execute(
            select(Experiment).where(Experiment.status == "active")
        ).scalars())
        for exp in active:
            results: dict[str, float] = {}
            complete = True
            for v in exp.variants_json or []:
                # Variants are linked via Posts whose error_json/score_json carries variant_id.
                snaps = db.execute(
                    select(AnalyticsSnapshot.metrics_json).join(Post, Post.id == AnalyticsSnapshot.post_id)
                    .where(Post.tenant_id == exp.tenant_id)
                ).scalars().all()
                vals = [s.get(exp.primary_metric) for s in snaps if isinstance(s.get(exp.primary_metric), (int, float))]
                if not vals:
                    complete = False
                    break
                results[v.get("id", "")] = sum(vals) / len(vals)
            if complete and results:
                winner = max(results, key=results.get)
                exp.results_json = {"per_variant": results, "winner": winner}
                exp.learnings = f"Variant {winner} won on {exp.primary_metric}."
                exp.status = "complete"
                finalized += 1
    return {"ok": True, "finalized": finalized}


def propose_all_tenants() -> dict[str, Any]:
    out = []
    with session_scope() as db:
        ids = [t.id for t in db.execute(select(Tenant)).scalars().all()]
    for tid in ids:
        try:
            r = propose_for_tenant(tid)
            out.append({"tenant_id": str(tid), "proposed": len(r)})
        except Exception as e:
            out.append({"tenant_id": str(tid), "error": str(e)})
    return {"ok": True, "tenants": out}
