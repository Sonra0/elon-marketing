"""Replicate adapter — image + video generation via Replicate's HTTP API.

Set REPLICATE_API_TOKEN and REPLICATE_IMAGE_MODEL / REPLICATE_VIDEO_MODEL.
Defaults to flux-schnell for image, kling/luma for video — override per env.
"""

from __future__ import annotations

import os
import time
import uuid

import httpx

from elon.core.logging import get_logger
from elon.core.storage import put_object
from elon.media.base import MediaProvider, MediaResult

log = get_logger(__name__)
API = "https://api.replicate.com/v1"


class ReplicateProvider(MediaProvider):
    name = "replicate"

    def __init__(self) -> None:
        self.token = os.getenv("REPLICATE_API_TOKEN", "")
        self.image_model = os.getenv("REPLICATE_IMAGE_MODEL", "black-forest-labs/flux-schnell")
        self.video_model = os.getenv("REPLICATE_VIDEO_MODEL", "")
        self.enabled = os.getenv("MEDIA_REPLICATE_ENABLED") == "1" and bool(self.token)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _run(self, model: str, inp: dict) -> str:
        r = httpx.post(
            f"{API}/models/{model}/predictions",
            headers={**self._headers(), "Prefer": "wait"},
            json={"input": inp},
            timeout=300,
        )
        r.raise_for_status()
        body = r.json()
        out = body.get("output")
        if isinstance(out, list) and out:
            return out[0]
        if isinstance(out, str):
            return out
        # Async: poll
        url = body["urls"]["get"]
        deadline = time.time() + 300
        while time.time() < deadline:
            j = httpx.get(url, headers=self._headers(), timeout=30).json()
            if j["status"] == "succeeded":
                out = j.get("output")
                return out[0] if isinstance(out, list) else out
            if j["status"] in {"failed", "canceled"}:
                raise RuntimeError(f"replicate failed: {j.get('error')}")
            time.sleep(3)
        raise TimeoutError("replicate poll timed out")

    def _store(self, tenant_id: str, url: str, mime: str, ext: str, kind: str, prompt: str) -> MediaResult:
        data = httpx.get(url, timeout=120).content
        key = f"tenants/{tenant_id}/media/replicate/{int(time.time())}-{uuid.uuid4().hex}.{ext}"
        put_object(key, data, content_type=mime)
        return MediaResult(s3_key=key, mime=mime, kind=kind, provider=self.name, prompt=prompt)

    def generate_image(self, *, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
        if not self.enabled:
            raise RuntimeError("replicate disabled")
        url = self._run(self.image_model, {"prompt": prompt, **kwargs})
        return self._store(tenant_id, url, "image/png", "png", "image", prompt)

    def generate_video(self, *, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
        if not (self.enabled and self.video_model):
            raise RuntimeError("replicate video disabled or no model configured")
        url = self._run(self.video_model, {"prompt": prompt, **kwargs})
        return self._store(tenant_id, url, "video/mp4", "mp4", "video", prompt)
