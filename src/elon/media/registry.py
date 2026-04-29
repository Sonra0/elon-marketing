"""Provider selection. Forced providers first; fallback only if enabled."""

from __future__ import annotations

from elon.core.logging import get_logger
from elon.media.base import MediaProvider, MediaResult
from elon.media.elevenlabs import ElevenLabsProvider
from elon.media.fallback import OpenAIImagesFallback
from elon.media.higgsfield import HiggsfieldProvider
from elon.media.notebooklm import NotebookLMProvider
from elon.media.replicate import ReplicateProvider

log = get_logger(__name__)


def _image_chain() -> list[MediaProvider]:
    # Forced provider first per locked decision; Replicate then OpenAI as fallbacks.
    return [HiggsfieldProvider(), ReplicateProvider(), OpenAIImagesFallback()]


def _video_chain() -> list[MediaProvider]:
    return [HiggsfieldProvider(), ReplicateProvider()]


def _audio_chain() -> list[MediaProvider]:
    return [NotebookLMProvider()]


def _voice_chain() -> list[MediaProvider]:
    return [ElevenLabsProvider()]


def generate_voiceover(*, tenant_id: str, text: str, **kwargs) -> MediaResult:
    last_err: Exception | None = None
    for p in _voice_chain():
        if not p.enabled:
            continue
        try:
            return p.generate_voiceover(tenant_id=tenant_id, text=text, **kwargs)
        except Exception as e:
            log.warning("media_voice_provider_failed", provider=p.name, error=str(e))
            last_err = e
    raise RuntimeError(f"no voice provider succeeded: {last_err}")


def generate_image(*, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
    last_err: Exception | None = None
    for p in _image_chain():
        if not p.enabled:
            continue
        try:
            return p.generate_image(tenant_id=tenant_id, prompt=prompt, **kwargs)
        except Exception as e:
            log.warning("media_image_provider_failed", provider=p.name, error=str(e))
            last_err = e
    raise RuntimeError(f"no image provider succeeded: {last_err}")


def generate_video(*, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
    last_err: Exception | None = None
    for p in _video_chain():
        if not p.enabled:
            continue
        try:
            return p.generate_video(tenant_id=tenant_id, prompt=prompt, **kwargs)
        except Exception as e:
            log.warning("media_video_provider_failed", provider=p.name, error=str(e))
            last_err = e
    raise RuntimeError(f"no video provider succeeded: {last_err}")


def generate_notebook_audio(*, tenant_id: str, sources: list[str], **kwargs) -> MediaResult:
    last_err: Exception | None = None
    for p in _audio_chain():
        if not p.enabled:
            continue
        try:
            return p.generate_notebook_audio(tenant_id=tenant_id, sources=sources, **kwargs)
        except Exception as e:
            log.warning("media_audio_provider_failed", provider=p.name, error=str(e))
            last_err = e
    raise RuntimeError(f"no audio provider succeeded: {last_err}")
