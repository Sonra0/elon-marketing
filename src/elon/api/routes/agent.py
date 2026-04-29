"""Operator-facing endpoints to trigger ingest + drafting (Celery)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from elon.api.deps import current_user
from elon.core.models import User

router = APIRouter(prefix="/agent", tags=["agent"])


class IngestIn(BaseModel):
    website_url: str | None = None
    asset_keys: list[str] | None = None
    notes: str | None = None


class TaskOut(BaseModel):
    task_id: str
    status: str = "queued"


@router.post("/ingest", response_model=TaskOut)
def ingest(body: IngestIn, user: User = Depends(current_user)) -> TaskOut:
    from elon.workers.tasks.ingest import ingest_brand
    res = ingest_brand.delay(str(user.tenant_id), body.website_url, body.asset_keys, body.notes)
    return TaskOut(task_id=res.id)


class DraftIn(BaseModel):
    instructions: str
    platform: str | None = None


@router.post("/draft", response_model=TaskOut)
def draft(body: DraftIn, user: User = Depends(current_user)) -> TaskOut:
    from elon.workers.tasks.content import draft_post
    res = draft_post.delay(str(user.tenant_id), body.instructions, body.platform)
    return TaskOut(task_id=res.id)
