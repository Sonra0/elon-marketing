"""Meta webhooks: WhatsApp + Instagram + Facebook.

Single endpoint per Meta convention; Meta sends a `hub.mode=subscribe` GET to verify,
then POSTs events. Signature verification uses META_APP_SECRET (X-Hub-Signature-256).
"""

import hashlib
import hmac

from fastapi import APIRouter, HTTPException, Query, Request, status

from elon.core.logging import get_logger
from elon.core.settings import get_settings

router = APIRouter(prefix="/webhooks/meta", tags=["webhooks"])
log = get_logger(__name__)


@router.get("")
def verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> int:
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return int(hub_challenge)
    raise HTTPException(status.HTTP_403_FORBIDDEN, "verify token mismatch")


@router.post("")
async def receive(request: Request) -> dict[str, str]:
    settings = get_settings()
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")
    if settings.meta_app_secret:
        expected = "sha256=" + hmac.new(
            settings.meta_app_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad signature")
    payload = await request.json()
    obj = payload.get("object")
    if obj == "whatsapp_business_account":
        from elon.chat.whatsapp import handle_whatsapp_event
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                handle_whatsapp_event(change.get("value") or {})
    else:
        log.info("meta_webhook_unhandled", obj=obj)
    return {"ok": "true"}
