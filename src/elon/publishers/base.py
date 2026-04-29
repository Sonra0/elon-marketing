"""Common publisher helpers: account lookup + token decrypt + media URLization."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from elon.core.models import Asset, SocialAccount
from elon.core.security import decrypt_secret
from elon.core.settings import get_settings


def get_social_account(db: Session, tenant_id: UUID, platform: str) -> SocialAccount:
    acct = db.execute(
        select(SocialAccount).where(
            SocialAccount.tenant_id == tenant_id,
            SocialAccount.platform == platform,
            SocialAccount.status == "connected",
            SocialAccount.deleted_at.is_(None),
        ).order_by(SocialAccount.created_at.desc())
    ).scalars().first()
    if acct is None:
        raise RuntimeError(f"no connected {platform} account for tenant {tenant_id}")
    return acct


def decrypt_token(acct: SocialAccount) -> str:
    return decrypt_secret(acct.oauth_tokens_enc)


def asset_public_url(asset: Asset) -> str:
    """Build a public-ish URL for a media asset.

    Meta and TikTok require a publicly fetchable URL to upload from. In dev we
    serve via the Cloudflare Tunnel: ELON_BASE_URL + /media/<key>. Production
    swaps to a CDN-fronted bucket.
    """
    settings = get_settings()
    return f"{settings.base_url.rstrip('/')}/media/{asset.s3_key.lstrip('/')}"


ANALYTICS_DELAYS = [timedelta(hours=1), timedelta(hours=24), timedelta(hours=72), timedelta(days=7)]
