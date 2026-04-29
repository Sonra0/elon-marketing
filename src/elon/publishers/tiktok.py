"""TikTok Content Posting API publisher (direct post).

Two-step:
  1. POST /v2/post/publish/video/init  -> upload_url + publish_id
  2. PUT bytes to upload_url
  3. Poll /v2/post/publish/status/fetch until status=PUBLISH_COMPLETE

Token is the access_token from the encrypted access|refresh bundle.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from elon.core.logging import get_logger
from elon.core.models import Asset, Post, SocialAccount
from elon.core.storage import get_object
from elon.publishers.base import decrypt_token

log = get_logger(__name__)
API = "https://open.tiktokapis.com"


def _access_token(account: SocialAccount) -> str:
    bundle = decrypt_token(account)
    return bundle.split("|", 1)[0]


def publish(post: Post, account: SocialAccount, assets: list[Asset]) -> dict[str, Any]:
    if not assets:
        raise RuntimeError("TikTok post needs a video asset")
    primary = assets[0]
    if not (primary.mime or "").startswith("video/"):
        raise RuntimeError("TikTok requires a video; got non-video asset")
    data = get_object(primary.s3_key)
    size = len(data)
    token = _access_token(account)

    init = httpx.post(
        f"{API}/v2/post/publish/video/init/",
        json={
            "post_info": {
                "title": (post.caption or "")[:2200],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": size,
                "total_chunk_count": 1,
            },
        },
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30,
    )
    init.raise_for_status()
    j = init.json()["data"]
    upload_url = j["upload_url"]
    publish_id = j["publish_id"]

    up = httpx.put(
        upload_url,
        content=data,
        headers={
            "Content-Type": primary.mime or "video/mp4",
            "Content-Range": f"bytes 0-{size - 1}/{size}",
        },
        timeout=300,
    )
    up.raise_for_status()

    deadline = time.time() + 600
    while time.time() < deadline:
        s = httpx.post(
            f"{API}/v2/post/publish/status/fetch/",
            json={"publish_id": publish_id},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=15,
        )
        s.raise_for_status()
        body = s.json()["data"]
        if body.get("status") == "PUBLISH_COMPLETE":
            return {"external_post_id": body.get("publicaly_available_post_id") or publish_id,
                    "publish_id": publish_id}
        if body.get("status") in {"FAILED", "PUBLISH_FAILED"}:
            raise RuntimeError(f"TikTok publish failed: {body}")
        time.sleep(5)
    raise TimeoutError("TikTok publish status polling timed out")
