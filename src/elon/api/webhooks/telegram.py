"""Telegram webhook entrypoint.

Validates the secret header set when registering the webhook with setWebhook.
Dispatches updates to the chat bot module.
"""

from fastapi import APIRouter, Header, HTTPException, Request, status

from elon.chat.telegram_bot import handle_update
from elon.core.settings import get_settings

router = APIRouter(prefix="/webhooks/telegram", tags=["webhooks"])


@router.post("")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, str]:
    settings = get_settings()
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad secret")
    update = await request.json()
    await handle_update(update)
    return {"ok": "true"}
