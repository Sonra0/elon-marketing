"""ElevenLabs voiceover adapter."""

from __future__ import annotations

import os
import time
import uuid

import httpx

from elon.core.storage import put_object
from elon.media.base import MediaProvider, MediaResult


class ElevenLabsProvider(MediaProvider):
    name = "elevenlabs"

    def __init__(self) -> None:
        self.key = os.getenv("ELEVENLABS_API_KEY", "")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")
        self.model = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
        self.enabled = bool(self.key and self.voice_id)

    def generate_image(self, *, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
        raise NotImplementedError("voice-only provider")

    def generate_voiceover(self, *, tenant_id: str, text: str, **kwargs) -> MediaResult:
        if not self.enabled:
            raise RuntimeError("elevenlabs disabled")
        r = httpx.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
            headers={"xi-api-key": self.key, "Accept": "audio/mpeg"},
            json={"text": text, "model_id": self.model, "voice_settings": kwargs.get("voice_settings", {})},
            timeout=120,
        )
        r.raise_for_status()
        key = f"tenants/{tenant_id}/media/elevenlabs/{int(time.time())}-{uuid.uuid4().hex}.mp3"
        put_object(key, r.content, content_type="audio/mpeg")
        return MediaResult(
            s3_key=key, mime="audio/mpeg", kind="voiceover",
            provider=self.name, prompt=text[:500],
        )
