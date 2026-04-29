"""Draft a single post.

Produces the structured contract:
  {idea, hook, caption, cta, platform, reason, expected_result, score{impact,effort,risk}}

Pipeline:
  1. Load BrandMemory + recent feedback (volatile).
  2. Build cached system prompt.
  3. Force JSON via tool_choice on a single tool whose schema *is* the contract.
  4. Run voice linter; on violations, ask Claude once to revise.
  5. Run crisis classifier; sensitive => requires_human_review.
  6. Persist Post in state=draft and create ApprovalRequest.
"""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from elon.agent.system_prompt import build_system_blocks
from elon.core.db import session_scope
from elon.core.llm import call_claude
from elon.core.logging import get_logger
from elon.core.models import ApprovalRequest, FeedbackEvent, Post, User
from elon.memory.brand import get_current as get_brand, to_dict as brand_to_dict
from elon.memory.events import recent
from elon.strategy import voice as voice_lint
from elon.strategy.crisis import classify as crisis_classify

log = get_logger(__name__)


DRAFT_TOOL = {
    "name": "submit_draft",
    "description": "Emit the final draft as structured JSON.",
    "input_schema": {
        "type": "object",
        "required": ["idea", "hook", "caption", "cta", "platform", "reason",
                     "expected_result", "score", "pillar_id"],
        "properties": {
            "idea": {"type": "string"},
            "hook": {"type": "string", "maxLength": 200},
            "caption": {"type": "string"},
            "cta": {"type": "string"},
            "platform": {"type": "string", "enum": ["ig", "tiktok", "fb"]},
            "pillar_id": {"type": "string"},
            "reason": {"type": "string"},
            "expected_result": {"type": "string"},
            "score": {
                "type": "object",
                "required": ["impact", "effort", "risk"],
                "properties": {
                    "impact": {"type": "integer", "minimum": 0, "maximum": 100},
                    "effort": {"type": "integer", "minimum": 0, "maximum": 100},
                    "risk":   {"type": "integer", "minimum": 0, "maximum": 100},
                },
            },
        },
    },
}


def _ask_for_draft(*, tenant_id: str, brand_memory: dict, recent_feedback: list[dict],
                   instructions: str, platform: str | None) -> dict[str, Any]:
    sys_blocks = build_system_blocks(brand_memory=brand_memory, recent_feedback=recent_feedback)
    platform_hint = f" Target platform: {platform}." if platform else ""
    user_msg = (
        f"Draft one post.{platform_hint} Operator brief:\n\n{instructions}\n\n"
        f"Use submit_draft to return the final structured object."
    )
    resp = call_claude(
        tenant_id=tenant_id,
        system_blocks=sys_blocks,
        messages=[{"role": "user", "content": user_msg}],
        tools=[DRAFT_TOOL],
        tool_choice={"type": "tool", "name": "submit_draft"},
        max_tokens=1200,
    )
    for blk in resp.content:
        if blk.type == "tool_use" and blk.name == "submit_draft":
            return dict(blk.input)
    raise RuntimeError("model did not call submit_draft")


def _revise_for_voice(*, tenant_id: str, brand_memory: dict, prior: dict,
                      violations: list[voice_lint.Violation]) -> dict[str, Any]:
    sys_blocks = build_system_blocks(brand_memory=brand_memory)
    explain = "\n".join(f"- {v.rule}: {v.detail}" for v in violations)
    user_msg = (
        f"The prior draft violated voice rules:\n{explain}\n\n"
        f"Prior draft JSON:\n{json.dumps(prior)}\n\n"
        f"Return a revised draft via submit_draft, keeping the idea but fixing the issues."
    )
    resp = call_claude(
        tenant_id=tenant_id,
        system_blocks=sys_blocks,
        messages=[{"role": "user", "content": user_msg}],
        tools=[DRAFT_TOOL],
        tool_choice={"type": "tool", "name": "submit_draft"},
        max_tokens=1200,
    )
    for blk in resp.content:
        if blk.type == "tool_use" and blk.name == "submit_draft":
            return dict(blk.input)
    return prior


def draft_post(
    *,
    tenant_id: str,
    instructions: str,
    platform: str | None = None,
    brief_id: str | None = None,
) -> dict[str, Any]:
    tenant_uuid = UUID(tenant_id)
    with session_scope() as db:
        bm = get_brand(db, tenant_uuid)
        if bm is None:
            raise RuntimeError("no brand memory; run ingest first")
        bm_dict = brand_to_dict(bm) or {}
        feedback = [
            {"sentiment": ev.payload_json.get("sentiment"), "free_text": ev.payload_json.get("free_text")}
            for ev in recent(db, tenant_uuid, limit=8, type="feedback")
        ]

    draft = _ask_for_draft(
        tenant_id=tenant_id,
        brand_memory=bm_dict,
        recent_feedback=feedback,
        instructions=instructions,
        platform=platform,
    )

    # Pick language: explicit on draft > segment default > brand default > "en".
    language = (
        draft.get("language")
        or (bm_dict.get("voice_json") or {}).get("default_language")
        or "en"
    )
    violations = voice_lint.lint(
        draft.get("caption", ""),
        voice=bm_dict.get("voice_json") or {},
        forbidden=bm_dict.get("forbidden_json") or {},
        language=language,
    )
    if violations:
        log.info("voice_violations", count=len(violations))
        draft = _revise_for_voice(
            tenant_id=tenant_id, brand_memory=bm_dict, prior=draft, violations=violations
        )

    crisis = crisis_classify(tenant_id=tenant_id, text=draft.get("caption", ""))
    requires_human_review = bool(crisis.get("sensitive", True))

    # Deny-list enforcement (hard block via crisis flag) + crisis playbook hint.
    from elon.strategy import crisis_playbooks
    with session_scope() as db:
        tenant = db.get(__import__("elon.core.models", fromlist=["Tenant"]).Tenant, tenant_uuid)
        denied = crisis_playbooks.violates_deny_list(tenant, draft.get("caption", ""))
        if denied:
            requires_human_review = True
            crisis = {**crisis, "sensitive": True, "topics": (crisis.get("topics") or []) + ["deny_list"],
                      "denied_terms": denied}
            crisis_playbooks.log_crisis(db, tenant_uuid, kind="deny_list",
                                        target="draft", payload={"terms": denied})
        if crisis.get("sensitive"):
            playbook_id = crisis_playbooks.map_topic_to_playbook(crisis.get("topics", []))
            crisis["playbook"] = playbook_id
            crisis["double_signoff"] = crisis_playbooks.double_signoff_required(tenant)

    with session_scope() as db:
        post = Post(
            tenant_id=tenant_uuid,
            brief_id=UUID(brief_id) if brief_id else None,
            platform=draft["platform"],
            idea=draft.get("idea", ""),
            hook=draft.get("hook", ""),
            caption=draft.get("caption", ""),
            cta=draft.get("cta", ""),
            media_asset_ids=[],
            reason=draft.get("reason", ""),
            expected_result=draft.get("expected_result", ""),
            score_json=draft.get("score", {}),
            state="draft",
            requires_human_review=requires_human_review,
            error_json={"crisis": crisis} if crisis.get("sensitive") else {},
        )
        db.add(post)
        db.flush()
        owner = db.execute(
            select(User).where(User.tenant_id == tenant_uuid, User.role == "owner")
        ).scalar_one_or_none()
        chat_id = owner.telegram_user_id if owner else None
        post_id = str(post.id)

        # Approval request placeholder (the chat message id is attached later by the notifier).
        if chat_id:
            ar = ApprovalRequest(post_id=post.id, channel="telegram", requested_by=owner.id)
            db.add(ar)

    if chat_id:
        from elon.chat.approvals import send_post_for_approval
        send_post_for_approval(chat_id=chat_id, post_id=post_id, draft=draft, crisis=crisis)

    return {"post_id": post_id, "draft": draft, "crisis": crisis}


def record_feedback(*, tenant_id: str, post_id: str, sentiment: str, free_text: str) -> None:
    """Persist a FeedbackEvent for a rejected/edited post so future drafts learn."""
    tenant_uuid = UUID(tenant_id)
    with session_scope() as db:
        db.add(FeedbackEvent(
            tenant_id=tenant_uuid,
            source="chat",
            target_type="post",
            target_id=post_id,
            sentiment=sentiment,
            free_text=free_text,
            weight_delta_json={},
        ))
