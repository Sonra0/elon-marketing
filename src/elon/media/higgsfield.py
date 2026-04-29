"""higgsfield.ai adapter.

higgsfield.ai does not (at time of writing) expose a stable, documented public API,
so this adapter wraps whatever endpoint we have credentials for. The class is structured
so the actual HTTP call can be swapped without changing callers.

Failure semantics: on any non-2xx or schema mismatch, raise; the caller (planner)
will fall back to the configured fallback provider when the feature flag is set.
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


class HiggsfieldProvider(MediaProvider):
    name = "higgsfield"

    def __init__(self) -> None:
        self.api_key = os.getenv("HIGGSFIELD_API_KEY", "")
        self.base_url = os.getenv("HIGGSFIELD_BASE_URL", "https://api.higgsfield.ai")
        self.enabled = bool(self.api_key)

    def _post(self, path: str, json: dict) -> dict:
        r = httpx.post(
            f"{self.base_url}{path}",
            json=json,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()

    def _download(self, url: str) -> bytes:
        r = httpx.get(url, timeout=120)
        r.raise_for_status()
        return r.content

    def generate_image(self, *, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
        if not self.enabled:
            raise RuntimeError("higgsfield not configured")
        # Endpoint shape is provisional; replace with actual once contract is firm.
        resp = self._post("/v1/images/generate", {"prompt": prompt, **kwargs})
        url = resp.get("url") or resp.get("output", {}).get("url")
        if not url:
            raise RuntimeError(f"higgsfield response missing url: {resp}")
        data = self._download(url)
        key = f"tenants/{tenant_id}/media/higgsfield/{int(time.time())}-{uuid.uuid4().hex}.png"
        put_object(key, data, content_type="image/png")
        return MediaResult(
            s3_key=key, mime="image/png", kind="image",
            provider=self.name, prompt=prompt,
        )

    def generate_video(self, *, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
        if not self.enabled:
            raise RuntimeError("higgsfield not configured")
        resp = self._post("/v1/videos/generate", {"prompt": prompt, **kwargs})
        # Often async — poll status if needed.
        status_url = resp.get("status_url")
        url = resp.get("url")
        if status_url and not url:
            for _ in range(60):
                time.sleep(5)
                s = httpx.get(status_url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=30).json()
                if s.get("status") == "succeeded":
                    url = s.get("url")
                    break
        if not url:
            raise RuntimeError(f"higgsfield video did not complete: {resp}")
        data = self._download(url)
        key = f"tenants/{tenant_id}/media/higgsfield/{int(time.time())}-{uuid.uuid4().hex}.mp4"
        put_object(key, data, content_type="video/mp4")
        return MediaResult(
            s3_key=key, mime="video/mp4", kind="video",
            provider=self.name, prompt=prompt,
        )
