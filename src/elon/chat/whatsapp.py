"""WhatsApp Cloud API: send + receive.

Per Meta:
  - Outbound to a user outside an open 24h customer-service window must use
    a pre-approved template. Inside the window, free-form text + interactive
    messages are allowed.
  - Inbound webhooks arrive on /webhooks/meta with object='whatsapp_business_account'.

We bind a User by their `whatsapp_phone` (E.164 without '+'). Onboarding asks the
operator to send the first message themselves, opening the 24h window.
"""

from __future__ import annotations

from typing import Any

import httpx

from elon.core.db import session_scope
from elon.core.logging import get_logger
from elon.core.models import SocialAccount, User
from elon.core.security import decrypt_secret
from sqlalchemy import select

log = get_logger(__name__)
GRAPH = "https://graph.facebook.com/v20.0"


def _phone_number_id_and_token(tenant_id) -> tuple[str, str]:
    with session_scope() as db:
        acct = db.execute(
            select(SocialAccount).where(
                SocialAccount.tenant_id == tenant_id,
                SocialAccount.platform == "wa",
                SocialAccount.status == "connected",
            )
        ).scalars().first()
        if acct is None:
            raise RuntimeError("no whatsapp account connected")
        return acct.external_id, decrypt_secret(acct.oauth_tokens_enc)


def send_text(tenant_id: str, to_phone: str, text: str) -> dict[str, Any]:
    phone_id, token = _phone_number_id_and_token(tenant_id)
    r = httpx.post(
        f"{GRAPH}/{phone_id}/messages",
        json={"messaging_product": "whatsapp", "to": to_phone, "type": "text",
              "text": {"body": text, "preview_url": False}},
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def send_interactive_buttons(
    tenant_id: str, to_phone: str, body_text: str, buttons: list[dict]
) -> dict[str, Any]:
    """`buttons` is a list of {"id": str, "title": str} (max 3, title <= 20 chars)."""
    phone_id, token = _phone_number_id_and_token(tenant_id)
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text[:1024]},
            "action": {"buttons": [{"type": "reply", "reply": b} for b in buttons[:3]]},
        },
    }
    r = httpx.post(
        f"{GRAPH}/{phone_id}/messages",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def handle_whatsapp_event(value: dict) -> None:
    """Route inbound WhatsApp messages.

    Meta payload structure (simplified):
      messages: [{from: phone, type: 'text'|'interactive', text:{body}, interactive:{...}}]
    """
    messages = value.get("messages") or []
    for m in messages:
        from_phone = m.get("from")
        if m.get("type") == "interactive":
            reply = (m.get("interactive") or {}).get("button_reply") or {}
            data = reply.get("id", "")
            if data.startswith("ap:"):
                _handle_button(data, from_phone)
        elif m.get("type") == "text":
            text = (m.get("text") or {}).get("body", "")
            _handle_text(from_phone, text)


def _handle_button(data: str, from_phone: str) -> None:
    parts = data.split(":")
    if len(parts) != 3:
        return
    _, action, post_id = parts
    # Reuse the Telegram approval logic shape.
    from elon.chat.approvals import handle_callback_query
    fake_update = {
        "callback_query": {
            "id": "wa-" + post_id,
            "data": data,
            "message": {"chat": {"id": from_phone}},
        }
    }
    handle_callback_query(fake_update)


def _handle_text(from_phone: str, text: str) -> None:
    with session_scope() as db:
        user = db.execute(select(User).where(User.whatsapp_phone == from_phone)).scalar_one_or_none()
        tenant_id = str(user.tenant_id) if user else None
    if tenant_id and text.lower().startswith("draft"):
        from elon.workers.tasks.content import draft_post as draft_task
        draft_task.delay(tenant_id, "")
        send_text(tenant_id, from_phone, "Drafting…")
