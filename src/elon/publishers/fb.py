"""Facebook Pages publisher: photo or video post."""

from __future__ import annotations

from typing import Any

import httpx

from elon.core.models import Asset, Post, SocialAccount
from elon.publishers.base import asset_public_url, decrypt_token

GRAPH = "https://graph.facebook.com/v20.0"


def publish(post: Post, account: SocialAccount, assets: list[Asset]) -> dict[str, Any]:
    token = decrypt_token(account)
    page_id = account.external_id
    message = (post.caption or "") + ("\n\n" + post.cta if post.cta else "")
    if not assets:
        # text-only post
        r = httpx.post(
            f"{GRAPH}/{page_id}/feed",
            params={"access_token": token},
            data={"message": message},
            timeout=30,
        )
        r.raise_for_status()
        return {"external_post_id": r.json()["id"]}
    primary = assets[0]
    media_url = asset_public_url(primary)
    if (primary.mime or "").startswith("video/"):
        r = httpx.post(
            f"{GRAPH}/{page_id}/videos",
            params={"access_token": token},
            data={"file_url": media_url, "description": message},
            timeout=120,
        )
    else:
        r = httpx.post(
            f"{GRAPH}/{page_id}/photos",
            params={"access_token": token},
            data={"url": media_url, "caption": message},
            timeout=60,
        )
    r.raise_for_status()
    j = r.json()
    return {"external_post_id": j.get("post_id") or j.get("id")}
