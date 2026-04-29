"""Operator-facing post listing + approval decisions for the web UI."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from elon.api.deps import current_user, db_session
from elon.core.models import ApprovalRequest, BrandMemory, FeedbackEvent, Post, User

router = APIRouter(prefix="/posts", tags=["posts"])


class PostOut(BaseModel):
    id: str
    platform: str
    state: str
    idea: str
    hook: str
    caption: str
    cta: str
    score_json: dict
    requires_human_review: bool
    scheduled_at: str | None = None
    published_at: str | None = None
    external_post_id: str | None = None
    created_at: str


def _row(p: Post) -> PostOut:
    return PostOut(
        id=str(p.id), platform=p.platform, state=p.state,
        idea=p.idea, hook=p.hook, caption=p.caption, cta=p.cta,
        score_json=p.score_json or {},
        requires_human_review=p.requires_human_review,
        scheduled_at=str(p.scheduled_at) if p.scheduled_at else None,
        published_at=str(p.published_at) if p.published_at else None,
        external_post_id=p.external_post_id,
        created_at=str(p.created_at),
    )


@router.get("", response_model=list[PostOut])
def list_posts(
    state: str | None = None,
    limit: int = 50,
    user: User = Depends(current_user),
    db: Session = Depends(db_session),
) -> list[PostOut]:
    stmt = select(Post).where(Post.tenant_id == user.tenant_id, Post.deleted_at.is_(None))
    if state:
        stmt = stmt.where(Post.state == state)
    stmt = stmt.order_by(Post.created_at.desc()).limit(min(limit, 200))
    rows = db.execute(stmt).scalars().all()
    return [_row(p) for p in rows]


class DecisionIn(BaseModel):
    decision: str  # "approve" | "reject"
    notes: str | None = None


@router.post("/{post_id}/decide", response_model=PostOut)
def decide(
    post_id: str,
    body: DecisionIn,
    user: User = Depends(current_user),
    db: Session = Depends(db_session),
) -> PostOut:
    post = db.get(Post, UUID(post_id))
    if post is None or post.tenant_id != user.tenant_id:
        raise HTTPException(404, "post not found")
    if body.decision == "approve":
        post.state = "approved"
    elif body.decision == "reject":
        post.state = "rejected"
        db.add(FeedbackEvent(
            tenant_id=user.tenant_id, source="web", target_type="post",
            target_id=post_id, sentiment="negative",
            free_text=body.notes or "", weight_delta_json={},
        ))
    else:
        raise HTTPException(400, "decision must be 'approve' or 'reject'")
    ar = db.execute(
        select(ApprovalRequest).where(ApprovalRequest.post_id == post.id)
        .order_by(ApprovalRequest.created_at.desc())
    ).scalars().first()
    if ar:
        ar.decision = post.state
        ar.decided_at = datetime.now(timezone.utc)
        ar.notes = body.notes
    db.commit()
    if body.decision == "approve":
        from elon.workers.tasks.publish import publish_post
        publish_post.delay(post_id)
    return _row(post)


class BrandOut(BaseModel):
    version: int
    voice_json: dict
    visual_json: dict
    offering_json: dict
    audience_json: dict
    positioning_json: dict
    pillars_json: list
    forbidden_json: dict


@router.get("/_brand", response_model=BrandOut | None)
def current_brand(
    user: User = Depends(current_user),
    db: Session = Depends(db_session),
) -> BrandOut | None:
    bm = db.execute(
        select(BrandMemory).where(
            BrandMemory.tenant_id == user.tenant_id, BrandMemory.is_current.is_(True)
        )
    ).scalar_one_or_none()
    if bm is None:
        return None
    return BrandOut(
        version=bm.version, voice_json=bm.voice_json, visual_json=bm.visual_json,
        offering_json=bm.offering_json, audience_json=bm.audience_json,
        positioning_json=bm.positioning_json, pillars_json=bm.pillars_json,
        forbidden_json=bm.forbidden_json,
    )
