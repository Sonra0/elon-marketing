"""MemoryEvent append-only log + RAG retrieval over pgvector embeddings."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from elon.core.models import MemoryEvent


def append(
    db: Session,
    tenant_id: UUID,
    *,
    type: str,
    actor: str,
    payload: dict[str, Any],
    embedding: list[float] | None = None,
) -> MemoryEvent:
    ev = MemoryEvent(
        tenant_id=tenant_id, type=type, actor=actor, payload_json=payload, embedding=embedding
    )
    db.add(ev)
    db.flush()
    return ev


def recent(db: Session, tenant_id: UUID, limit: int = 20, type: str | None = None) -> list[MemoryEvent]:
    stmt = select(MemoryEvent).where(MemoryEvent.tenant_id == tenant_id)
    if type:
        stmt = stmt.where(MemoryEvent.type == type)
    stmt = stmt.order_by(MemoryEvent.created_at.desc()).limit(limit)
    return list(db.execute(stmt).scalars())


def search_similar(
    db: Session, tenant_id: UUID, query_embedding: list[float], k: int = 8
) -> list[MemoryEvent]:
    """Top-k nearest neighbors by cosine distance via pgvector."""
    stmt = (
        select(MemoryEvent)
        .where(MemoryEvent.tenant_id == tenant_id, MemoryEvent.embedding.is_not(None))
        .order_by(MemoryEvent.embedding.cosine_distance(query_embedding))
        .limit(k)
    )
    return list(db.execute(stmt).scalars())
