"""Inbound Telegram update handler.

Supports the Phase-0 commands needed for onboarding:
- /start         -> greeting + instructions
- /link <token>  -> binds telegram_user_id to a User created via POST /tenants
- /status        -> shows tenant + connector status
- /help          -> command list

We use the raw update payload from FastAPI (no python-telegram-bot dispatcher
needed at this stage — keeps the surface small and easy to debug).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from elon.chat.notify import send_telegram
from elon.core.db import session_scope
from elon.core.logging import get_logger
from elon.core.models import SocialAccount, Tenant, User

log = get_logger(__name__)


HELP = (
    "Elon — your brand marketing agent.\n\n"
    "Commands:\n"
    "/link <token> — connect this Telegram account to your tenant\n"
    "/status — show tenant + connector status\n"
    "/help — this message"
)


async def handle_update(update: dict) -> None:
    if "callback_query" in update:
        from elon.chat.approvals import handle_callback_query
        handle_callback_query(update)
        return
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    chat_id = str(msg["chat"]["id"])
    from_user = msg.get("from") or {}
    tg_user_id = str(from_user.get("id", chat_id))
    text = (msg.get("text") or "").strip()

    if text.startswith("/start"):
        send_telegram(chat_id, "Welcome to Elon. Send /link <token> to connect your tenant.")
        return
    if text.startswith("/help"):
        send_telegram(chat_id, HELP)
        return
    if text.startswith("/link"):
        await _cmd_link(chat_id, tg_user_id, text)
        return
    if text.startswith("/status"):
        await _cmd_status(chat_id, tg_user_id)
        return

    # Fallback: route to agent (Phase 1+). For now, ack + remind.
    send_telegram(chat_id, "I'll think about that in Phase 1. For now, /help.")


async def _cmd_link(chat_id: str, tg_user_id: str, text: str) -> None:
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        send_telegram(chat_id, "Usage: /link <token>")
        return
    token = parts[1].strip()
    with session_scope() as s:
        user = s.execute(select(User).where(User.link_token == token)).scalar_one_or_none()
        if user is None:
            send_telegram(chat_id, "Invalid link token.")
            return
        if user.link_token_expires_at and user.link_token_expires_at < datetime.now(timezone.utc):
            send_telegram(chat_id, "Link token expired. Create a new tenant to get a fresh one.")
            return
        user.telegram_user_id = tg_user_id
        user.link_token = None
        user.link_token_expires_at = None
        tenant = s.get(Tenant, user.tenant_id)
        send_telegram(chat_id, f"Linked to tenant '{tenant.name}'. Welcome.")


async def _cmd_status(chat_id: str, tg_user_id: str) -> None:
    with session_scope() as s:
        user = s.execute(select(User).where(User.telegram_user_id == tg_user_id)).scalar_one_or_none()
        if user is None:
            send_telegram(chat_id, "This Telegram is not linked. Send /link <token>.")
            return
        tenant = s.get(Tenant, user.tenant_id)
        accounts = s.execute(
            select(SocialAccount).where(SocialAccount.tenant_id == user.tenant_id)
        ).scalars().all()
        connected = ", ".join(f"{a.platform}:{a.handle or a.external_id}" for a in accounts) or "none"
        send_telegram(
            chat_id,
            f"Tenant: {tenant.name}\nRole: {user.role}\nConnected: {connected}",
        )
