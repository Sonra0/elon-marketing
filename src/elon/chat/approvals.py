"""Approval flow over Telegram (and later WhatsApp).

Two pieces:
  - send_post_for_approval(): renders a draft as a Telegram message with inline
    Approve / Reject / Reschedule buttons; persists the message_id on the
    ApprovalRequest row.
  - handle_callback_query(): receives the button tap and updates Post.state +
    decides whether to publish or capture feedback.

Callback data scheme: "ap:{action}:{post_id}" — action in {ok, no, when}.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import select

from elon.core.db import session_scope
from elon.core.logging import get_logger
from elon.core.models import ApprovalRequest, Post
from elon.core.settings import get_settings

log = get_logger(__name__)


def _api(method: str, body: dict) -> dict:
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"
    r = httpx.post(url, json=body, timeout=15)
    r.raise_for_status()
    return r.json()


def _format_card(draft: dict[str, Any], crisis: dict[str, Any] | None) -> str:
    score = draft.get("score", {})
    flag = " [SENSITIVE — human review required]" if crisis and crisis.get("sensitive") else ""
    return (
        f"Draft for {draft.get('platform','?').upper()}{flag}\n\n"
        f"Idea: {draft.get('idea','')}\n"
        f"Hook: {draft.get('hook','')}\n\n"
        f"Caption:\n{draft.get('caption','')}\n\n"
        f"CTA: {draft.get('cta','')}\n"
        f"Reason: {draft.get('reason','')}\n"
        f"Expected: {draft.get('expected_result','')}\n"
        f"Score (impact/effort/risk): {score.get('impact','-')}/{score.get('effort','-')}/{score.get('risk','-')}"
    )


def _keyboard(post_id: str, platform: str) -> dict:
    rows = [[
        {"text": "✓ Approve", "callback_data": f"ap:ok:{post_id}"},
        {"text": "✗ Reject",  "callback_data": f"ap:no:{post_id}"},
        {"text": "⏰ Reschedule", "callback_data": f"ap:when:{post_id}"},
    ]]
    # TikTok requires explicit per-post approval (locked decision); keep flow identical
    # but the button label clarifies it.
    if platform == "tiktok":
        rows[0][0] = {"text": "✓ Approve TikTok post", "callback_data": f"ap:ok:{post_id}"}
    return {"inline_keyboard": rows}


def send_post_for_approval(*, chat_id: str, post_id: str, draft: dict, crisis: dict | None) -> None:
    text = _format_card(draft, crisis)
    body = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": _keyboard(post_id, draft.get("platform", "")),
    }
    resp = _api("sendMessage", body)
    msg_id = str(resp.get("result", {}).get("message_id", ""))
    with session_scope() as db:
        ar = db.execute(
            select(ApprovalRequest).where(ApprovalRequest.post_id == UUID(post_id))
            .order_by(ApprovalRequest.created_at.desc())
        ).scalars().first()
        if ar is not None:
            ar.message_ref = msg_id
        post = db.get(Post, UUID(post_id))
        if post:
            post.state = "review"


def handle_callback_query(update: dict) -> None:
    cb = update.get("callback_query") or {}
    data: str = cb.get("data", "")
    cb_id = cb.get("id")
    chat_id = str((cb.get("message") or {}).get("chat", {}).get("id", ""))
    if not data.startswith("ap:"):
        if cb_id:
            _api("answerCallbackQuery", {"callback_query_id": cb_id})
        return
    try:
        _, action, post_id = data.split(":", 2)
    except ValueError:
        if cb_id:
            _api("answerCallbackQuery", {"callback_query_id": cb_id})
        return

    msg_text = ""
    with session_scope() as db:
        post = db.get(Post, UUID(post_id))
        if post is None:
            msg_text = "Post not found."
        elif action == "ok":
            post.state = "approved"
            ar = db.execute(
                select(ApprovalRequest).where(ApprovalRequest.post_id == post.id)
                .order_by(ApprovalRequest.created_at.desc())
            ).scalars().first()
            if ar:
                ar.decision = "approved"
                ar.decided_at = datetime.now(timezone.utc)
            msg_text = "Approved. Queueing publish."
        elif action == "no":
            post.state = "rejected"
            ar = db.execute(
                select(ApprovalRequest).where(ApprovalRequest.post_id == post.id)
                .order_by(ApprovalRequest.created_at.desc())
            ).scalars().first()
            if ar:
                ar.decision = "rejected"
                ar.decided_at = datetime.now(timezone.utc)
            msg_text = "Rejected. Send any text to record feedback."
        elif action == "when":
            msg_text = "Reply with the desired time, e.g. 'schedule 2026-05-01 09:00 UTC'."

    if cb_id:
        _api("answerCallbackQuery", {"callback_query_id": cb_id, "text": msg_text})
    if chat_id and msg_text:
        _api("sendMessage", {"chat_id": chat_id, "text": msg_text})

    if action == "ok":
        from elon.workers.tasks.publish import publish_post
        publish_post.delay(post_id)


def parse_feedback_intent(text: str) -> dict | None:
    """Detect free-form follow-ups like 'feedback for <id>: …' or post-rejection text.
    Phase 1: keep simple — anything starting with 'fb:' is feedback.
    """
    if text.startswith("fb:"):
        try:
            _, post_id, body = text.split(":", 2)
            return {"post_id": post_id.strip(), "free_text": body.strip(), "sentiment": "negative"}
        except ValueError:
            return None
    return None


def render_post_summary(post: Post) -> str:
    return json.dumps({
        "id": str(post.id),
        "platform": post.platform,
        "state": post.state,
        "scheduled_at": str(post.scheduled_at) if post.scheduled_at else None,
    })
