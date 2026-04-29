"""BrandMemory accessor: load current version, write a new version (versioned, immutable history)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from elon.core.models import BrandMemory


def get_current(db: Session, tenant_id: UUID) -> BrandMemory | None:
    return db.execute(
        select(BrandMemory).where(
            BrandMemory.tenant_id == tenant_id,
            BrandMemory.is_current.is_(True),
            BrandMemory.deleted_at.is_(None),
        )
    ).scalar_one_or_none()


def to_dict(bm: BrandMemory | None) -> dict[str, Any] | None:
    if bm is None:
        return None
    return {
        "version": bm.version,
        "voice_json": bm.voice_json,
        "visual_json": bm.visual_json,
        "offering_json": bm.offering_json,
        "audience_json": bm.audience_json,
        "positioning_json": bm.positioning_json,
        "pillars_json": bm.pillars_json,
        "forbidden_json": bm.forbidden_json,
        "source_refs": bm.source_refs,
    }


def write_new_version(db: Session, tenant_id: UUID, **fields: Any) -> BrandMemory:
    """Mark prior current as stale, insert a new current version."""
    db.execute(
        update(BrandMemory)
        .where(BrandMemory.tenant_id == tenant_id, BrandMemory.is_current.is_(True))
        .values(is_current=False)
    )
    last = db.execute(
        select(BrandMemory.version)
        .where(BrandMemory.tenant_id == tenant_id)
        .order_by(BrandMemory.version.desc())
    ).scalars().first() or 0
    bm = BrandMemory(tenant_id=tenant_id, version=last + 1, is_current=True, **fields)
    db.add(bm)
    db.flush()
    return bm
