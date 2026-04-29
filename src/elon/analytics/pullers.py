"""Per-platform metric pullers. Return a normalized dict.

Normalized keys:
  reach, impressions, plays, watch_time_s, likes, comments, shares, saves,
  follows, profile_visits, ctr.
"""

from __future__ import annotations

from typing import Any

import httpx

from elon.core.models import SocialAccount
from elon.core.security import decrypt_secret


def _ig(account: SocialAccount, external_id: str) -> dict[str, Any]:
    token = decrypt_secret(account.oauth_tokens_enc)
    metrics = ",".join([
        "reach", "impressions", "likes", "comments", "shares", "saved",
        "video_views", "total_interactions", "follows", "profile_visits",
    ])
    r = httpx.get(
        f"https://graph.facebook.com/v20.0/{external_id}/insights",
        params={"metric": metrics, "access_token": token},
        timeout=20,
    )
    r.raise_for_status()
    out: dict[str, Any] = {}
    for entry in r.json().get("data", []):
        name = entry.get("name")
        values = entry.get("values") or []
        out[name] = (values[0].get("value") if values else None)
    return {
        "reach": out.get("reach"),
        "impressions": out.get("impressions"),
        "plays": out.get("video_views"),
        "likes": out.get("likes"),
        "comments": out.get("comments"),
        "shares": out.get("shares"),
        "saves": out.get("saved"),
        "follows": out.get("follows"),
        "profile_visits": out.get("profile_visits"),
        "raw": out,
    }


def _fb(account: SocialAccount, external_id: str) -> dict[str, Any]:
    token = decrypt_secret(account.oauth_tokens_enc)
    metrics = "post_impressions,post_engaged_users,post_reactions_by_type_total,post_clicks"
    r = httpx.get(
        f"https://graph.facebook.com/v20.0/{external_id}/insights",
        params={"metric": metrics, "access_token": token},
        timeout=20,
    )
    r.raise_for_status()
    out: dict[str, Any] = {}
    for entry in r.json().get("data", []):
        out[entry["name"]] = (entry.get("values") or [{}])[0].get("value")
    return {
        "impressions": out.get("post_impressions"),
        "reach": out.get("post_engaged_users"),
        "raw": out,
    }


def _tiktok(account: SocialAccount, external_id: str) -> dict[str, Any]:
    bundle = decrypt_secret(account.oauth_tokens_enc)
    token = bundle.split("|", 1)[0]
    r = httpx.post(
        "https://open.tiktokapis.com/v2/video/query/",
        json={"filters": {"video_ids": [external_id]}},
        headers={"Authorization": f"Bearer {token}"},
        params={"fields": "id,view_count,like_count,comment_count,share_count"},
        timeout=20,
    )
    r.raise_for_status()
    items = r.json().get("data", {}).get("videos", [])
    item = items[0] if items else {}
    return {
        "plays": item.get("view_count"),
        "likes": item.get("like_count"),
        "comments": item.get("comment_count"),
        "shares": item.get("share_count"),
        "raw": item,
    }


PULLERS = {"ig": _ig, "fb": _fb, "tiktok": _tiktok}


def pull(account: SocialAccount, external_post_id: str, platform: str) -> dict[str, Any]:
    fn = PULLERS.get(platform)
    if fn is None:
        raise RuntimeError(f"no analytics puller for {platform}")
    return fn(account, external_post_id)
