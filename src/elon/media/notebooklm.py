"""NotebookLM adapter — wraps the unofficial `teng-lin/notebooklm-py` flow.

NotebookLM has no official API; the wrapper drives a Google session. Treat as
brittle: every call that talks to Google is a potential failure point. We isolate
this in a Celery task so retries + dead-letter routing are easy.
"""

from __future__ import annotations

import os
import time
import uuid

from elon.core.logging import get_logger
from elon.core.storage import put_object
from elon.media.base import MediaProvider, MediaResult

log = get_logger(__name__)


class NotebookLMProvider(MediaProvider):
    name = "notebooklm"

    def __init__(self) -> None:
        # Path to a serialized Google session/cookie bundle, mounted into the container.
        self.session_path = os.getenv("NOTEBOOKLM_SESSION_PATH", "")
        self.enabled = bool(self.session_path)

    def generate_image(self, *, tenant_id: str, prompt: str, **kwargs) -> MediaResult:
        raise NotImplementedError("NotebookLM is audio/notebook-only")

    def generate_notebook_audio(self, *, tenant_id: str, sources: list[str], **kwargs) -> MediaResult:
        if not self.enabled:
            raise RuntimeError("notebooklm session not configured")
        try:
            # Lazy import — the dep is optional and may not be installed in all envs.
            from notebooklm import Client  # type: ignore[import-not-found]
        except ImportError as e:
            raise RuntimeError("notebooklm-py not installed") from e
        client = Client.from_session(self.session_path)
        notebook = client.create_notebook(sources=sources)
        audio_bytes = notebook.generate_audio_overview()  # blocking
        key = f"tenants/{tenant_id}/media/notebooklm/{int(time.time())}-{uuid.uuid4().hex}.mp3"
        put_object(key, audio_bytes, content_type="audio/mpeg")
        return MediaResult(
            s3_key=key, mime="audio/mpeg", kind="notebook_audio",
            provider=self.name, prompt=";".join(sources)[:500],
        )
