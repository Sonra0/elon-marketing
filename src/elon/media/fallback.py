"""Fallback image provider behind a feature flag.

Off by default per the locked decision (higgsfield + NotebookLM are forced).
Enable when MEDIA_FALLBACK_ENABLED=1 to keep MVP unblocked when forced
providers are broken.
"""

from __future__ import annotations

import os
import time
import uuid

import httpx

from elon.core.storage import put_object
from elon.media.base import MediaProvider, MediaResult


class OpenAIImagesFallback(MediaProvider):
    name = "openai_images_fallback"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.enabled = os.getenv("MEDIA_FALLBACK_ENABLED") == "1" and bool(self.api_key)

    def generate_image(self, *, tenant_id: str, prompt: str, size: str = "1024x1024", **kwargs) -> MediaResult:
        if not self.enabled:
            raise RuntimeError("fallback disabled")
        r = httpx.post(
            "https://api.openai.com/v1/images/generations",
            json={"model": "gpt-image-1", "prompt": prompt, "size": size, "n": 1},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120,
        )
        r.raise_for_status()
        b64 = r.json()["data"][0]["b64_json"]
        import base64
        data = base64.b64decode(b64)
        key = f"tenants/{tenant_id}/media/fallback/{int(time.time())}-{uuid.uuid4().hex}.png"
        put_object(key, data, content_type="image/png")
        return MediaResult(
            s3_key=key, mime="image/png", kind="image",
            provider=self.name, prompt=prompt,
        )
