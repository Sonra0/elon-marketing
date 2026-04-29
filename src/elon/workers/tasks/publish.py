from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from elon.core.db import session_scope
from elon.core.logging import get_logger
from elon.core.models import Asset, Post
from elon.publishers import fb as fb_pub
from elon.publishers import ig as ig_pub
from elon.publishers import tiktok as tt_pub
from elon.publishers.base import ANALYTICS_DELAYS, get_social_account
from elon.workers.celery_app import celery_app

log = get_logger(__name__)


PUBLISHERS = {"ig": ig_pub.publish, "fb": fb_pub.publish, "tiktok": tt_pub.publish}


@celery_app.task(name="elon.workers.tasks.publish.post", bind=True, max_retries=3,
                 default_retry_delay=30)
def publish_post(self, post_id: str) -> dict:
    with session_scope() as db:
        post = db.get(Post, UUID(post_id))
        if post is None:
            return {"ok": False, "error": "post_not_found"}
        # Per-tenant publisher rate cap: 30 publishes/hour/platform.
        from elon.core.ratelimit import hit, RateLimitExceeded
        try:
            hit(f"publish:{post.platform}", str(post.tenant_id), capacity=30, window_s=3600)
        except RateLimitExceeded as e:
            post.error_json = {**(post.error_json or {}), "ratelimit": str(e)}
            raise self.retry(exc=e, countdown=120)
        # Idempotency: if already published, return cached result.
        if post.state == "published" and post.external_post_id:
            return {"ok": True, "external_post_id": post.external_post_id, "cached": True}
        if post.state not in {"approved", "scheduled"}:
            return {"ok": False, "error": f"bad_state:{post.state}"}
        account = get_social_account(db, post.tenant_id, post.platform)
        asset_ids = [UUID(x) for x in post.media_asset_ids or []]
        assets = []
        if asset_ids:
            assets = list(
                db.execute(select(Asset).where(Asset.id.in_(asset_ids))).scalars()
            )
        publisher = PUBLISHERS.get(post.platform)
        if publisher is None:
            return {"ok": False, "error": f"no_publisher:{post.platform}"}
        try:
            result = publisher(post, account, assets)
        except Exception as e:
            log.error("publish_failed", post_id=post_id, error=str(e))
            post.error_json = {**(post.error_json or {}), "publish": str(e)}
            post.state = "failed"
            raise self.retry(exc=e)
        post.external_post_id = result.get("external_post_id")
        post.published_at = datetime.now(timezone.utc)
        post.state = "published"

    # Schedule analytics pulls outside the DB session.
    from elon.workers.tasks.analytics import pull_post_metrics
    for delay in ANALYTICS_DELAYS:
        pull_post_metrics.apply_async(args=[post_id], countdown=int(delay.total_seconds()))

    return {"ok": True, "external_post_id": result.get("external_post_id")}
