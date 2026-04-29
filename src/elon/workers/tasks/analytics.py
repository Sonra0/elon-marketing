from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from elon.analytics import anomaly
from elon.analytics.pullers import pull
from elon.core.db import session_scope
from elon.core.logging import get_logger
from elon.core.models import AnalyticsSnapshot, Post, User
from elon.publishers.base import get_social_account
from elon.workers.celery_app import celery_app

log = get_logger(__name__)


@celery_app.task(name="elon.workers.tasks.analytics.pull", bind=True, max_retries=3,
                 default_retry_delay=60)
def pull_post_metrics(self, post_id: str) -> dict:
    with session_scope() as db:
        post = db.get(Post, UUID(post_id))
        if post is None or not post.external_post_id:
            return {"ok": False, "error": "missing_post_or_external_id"}
        account = get_social_account(db, post.tenant_id, post.platform)
        try:
            metrics = pull(account, post.external_post_id, post.platform)
        except Exception as e:
            log.error("analytics_pull_failed", post_id=post_id, error=str(e))
            raise self.retry(exc=e)
        snap = AnalyticsSnapshot(
            tenant_id=post.tenant_id, post_id=post.id, platform=post.platform,
            metrics_json=metrics, taken_at=datetime.now(timezone.utc),
        )
        db.add(snap)
        history = list(db.execute(
            select(AnalyticsSnapshot.metrics_json)
            .where(AnalyticsSnapshot.tenant_id == post.tenant_id,
                   AnalyticsSnapshot.platform == post.platform,
                   AnalyticsSnapshot.post_id != post.id)
            .order_by(AnalyticsSnapshot.taken_at.desc()).limit(50)
        ).scalars())
        anomalies = anomaly.detect(metrics, history)
        owner = db.execute(
            select(User).where(User.tenant_id == post.tenant_id, User.role == "owner")
        ).scalar_one_or_none()
        chat_id = owner.telegram_user_id if owner else None
    if anomalies and chat_id:
        from elon.chat.notify import send_telegram
        text = f"Anomaly on post {post_id}: " + "; ".join(
            f"{a['metric']} {a['kind']} x{a['ratio']:.1f}" for a in anomalies
        )
        send_telegram(chat_id, text)

    # Strategy-weight learning: nudge pillar/platform weights based on this post's
    # reach vs the tenant baseline.
    from elon.strategy.weights import learn_from_post
    with session_scope() as db:
        learn = learn_from_post(db, post.tenant_id, UUID(post_id))
    return {"ok": True, "anomalies": anomalies, "metrics": metrics, "learn": learn}


@celery_app.task(name="elon.workers.tasks.analytics.pull_trends")
def pull_trends() -> dict:
    from datetime import datetime, timezone

    from elon.core.models import TrendSignal
    from elon.signals.news import search as news_search
    from elon.signals.tiktok_trends import fetch_trending_hashtags

    inserted = 0
    with session_scope() as db:
        for entry in fetch_trending_hashtags(limit=30):
            db.add(TrendSignal(
                tenant_id=None, source="tiktok_trend",
                topic=str(entry.get("topic") or "")[:255],
                score=float(entry.get("score") or 0.0),
                evidence_json=entry.get("evidence") or {},
                captured_at=datetime.now(timezone.utc),
            ))
            inserted += 1
        for hit in news_search("marketing trends today", max_results=10):
            db.add(TrendSignal(
                tenant_id=None, source="news",
                topic=str(hit.get("title") or "")[:255],
                score=float(hit.get("score") or 0.0),
                evidence_json={"url": hit.get("url"), "summary": hit.get("content", "")[:500]},
                captured_at=datetime.now(timezone.utc),
            ))
            inserted += 1
    return {"ok": True, "inserted": inserted}


@celery_app.task(name="elon.workers.tasks.analytics.sweep_competitors")
def sweep_competitors() -> dict:
    from datetime import datetime, timezone

    from elon.competitor.gaps import find_gaps
    from elon.competitor.scraper import scrape_instagram, scrape_tiktok
    from elon.core.models import Competitor, CompetitorPost, MemoryEvent
    from elon.memory.brand import get_current as get_brand
    from elon.memory.brand import to_dict as brand_to_dict

    swept = 0
    with session_scope() as db:
        comps = list(db.execute(select(Competitor)).scalars())
        for c in comps:
            if c.platform == "ig":
                posts = scrape_instagram(c.handle)
            elif c.platform == "tiktok":
                posts = scrape_tiktok(c.handle)
            else:
                continue
            c.last_scraped_at = datetime.now(timezone.utc)
            for p in posts:
                db.add(CompetitorPost(
                    competitor_id=c.id, captured_at=datetime.now(timezone.utc),
                    metrics_json={}, media_refs=[p.get("url")], themes=[],
                ))
                swept += 1
            # Per-tenant gap analysis after each competitor refresh
            bm = get_brand(db, c.tenant_id)
            if bm and posts:
                gaps = find_gaps(
                    tenant_id=str(c.tenant_id),
                    brand_pillars=(brand_to_dict(bm) or {}).get("pillars_json", []),
                    competitor_posts=posts,
                )
                db.add(MemoryEvent(
                    tenant_id=c.tenant_id, type="competitor_gaps", actor="agent",
                    payload_json={"competitor": c.handle, "platform": c.platform, "gaps": gaps},
                ))
    return {"ok": True, "swept": swept}


@celery_app.task(name="elon.workers.tasks.analytics.nightly_digest")
def nightly_digest() -> dict:
    """Per-tenant digest: posts published today + headline metrics + tomorrow's plan."""
    from elon.chat.notify import send_telegram

    sent = 0
    today = datetime.now(timezone.utc).date()
    with session_scope() as db:
        users = db.execute(select(User).where(User.role == "owner")).scalars().all()
        for u in users:
            if not u.telegram_user_id:
                continue
            posts = db.execute(
                select(Post).where(Post.tenant_id == u.tenant_id,
                                   Post.published_at.is_not(None))
                .order_by(Post.published_at.desc()).limit(20)
            ).scalars().all()
            todays = [p for p in posts if p.published_at and p.published_at.date() == today]
            lines = [f"Nightly digest — {len(todays)} post(s) today"]
            for p in todays:
                lines.append(f" • {p.platform.upper()}: {p.idea[:80]}")
            lines.append("Tomorrow's plan: see /status")
            send_telegram(u.telegram_user_id, "\n".join(lines))
            sent += 1
    return {"ok": True, "sent": sent}
