"""Instagram Graph API publisher.

Flow (image / Reels / carousel):
  1. POST /{ig-user-id}/media (container)
  2. (Reels) poll /{container-id}?fields=status_code until FINISHED
  3. POST /{ig-user-id}/media_publish
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from elon.core.models import Asset, Post, SocialAccount
from elon.publishers.base import asset_public_url, decrypt_token

GRAPH = "https://graph.facebook.com/v20.0"


def _create_image_container(ig_user_id: str, token: str, image_url: str, caption: str) -> str:
    r = httpx.post(
        f"{GRAPH}/{ig_user_id}/media",
        params={"access_token": token},
        data={"image_url": image_url, "caption": caption},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["id"]


def _create_reels_container(ig_user_id: str, token: str, video_url: str, caption: str) -> str:
    r = httpx.post(
        f"{GRAPH}/{ig_user_id}/media",
        params={"access_token": token},
        data={"media_type": "REELS", "video_url": video_url, "caption": caption},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["id"]


def _wait_finished(container_id: str, token: str, timeout_s: int = 300) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = httpx.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=15,
        )
        r.raise_for_status()
        status = r.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"IG container error: {r.json()}")
        time.sleep(3)
    raise TimeoutError("IG container did not finish in time")


def _publish(ig_user_id: str, token: str, container_id: str) -> str:
    r = httpx.post(
        f"{GRAPH}/{ig_user_id}/media_publish",
        params={"access_token": token},
        data={"creation_id": container_id},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["id"]


def publish(post: Post, account: SocialAccount, assets: list[Asset]) -> dict[str, Any]:
    if not assets:
        raise RuntimeError("IG post needs at least one media asset")
    token = decrypt_token(account)
    ig_user_id = account.external_id
    primary = assets[0]
    is_video = (primary.mime or "").startswith("video/")
    media_url = asset_public_url(primary)
    caption = (post.caption or "") + ("\n\n" + post.cta if post.cta else "")
    if is_video:
        container_id = _create_reels_container(ig_user_id, token, media_url, caption)
        _wait_finished(container_id, token)
    else:
        container_id = _create_image_container(ig_user_id, token, media_url, caption)
    external_id = _publish(ig_user_id, token, container_id)
    return {"external_post_id": external_id, "container_id": container_id}
