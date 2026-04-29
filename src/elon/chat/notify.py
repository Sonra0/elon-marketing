"""Outbound chat helpers (sync, used from Celery tasks).

For Phase 0, only Telegram. WhatsApp added in Phase 1 with templated messages.
"""

import httpx

from elon.core.logging import get_logger
from elon.core.settings import get_settings

log = get_logger(__name__)


def send_telegram(chat_id: str, text: str, **kwargs) -> dict:
    settings = get_settings()
    if not settings.telegram_bot_token:
        log.warning("send_telegram_skipped_no_token", chat_id=chat_id)
        return {"ok": False, "reason": "no_token"}
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    body = {"chat_id": chat_id, "text": text, **kwargs}
    r = httpx.post(url, json=body, timeout=10)
    r.raise_for_status()
    return r.json()
