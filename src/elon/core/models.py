"""SQLAlchemy 2.0 models for all Phase 0 tables.

Multi-tenant: every table carries `tenant_id` (workspace scope), timestamps,
and a soft-delete column. Vectors use pgvector. Heavy/free-form fields are JSONB.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from elon.core.ids import new_id


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TenantScoped:
    @staticmethod
    def tenant_fk() -> Mapped[UUID]:
        return mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False)


# ---------- Identity ----------

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(64), default="free")
    owner_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    settings_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    monthly_budget_usd: Mapped[float] = mapped_column(Float, default=50.0)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(32), default="owner")  # owner|operator|viewer
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    telegram_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    whatsapp_phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    link_token: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    link_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ---------- Connectors ----------

class SocialAccount(Base, TimestampMixin):
    __tablename__ = "social_accounts"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    platform: Mapped[str] = mapped_column(String(16), nullable=False)  # ig|tiktok|fb|wa
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    handle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    oauth_tokens_enc: Mapped[str] = mapped_column(Text, nullable=False)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[str] = mapped_column(String(32), default="connected")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ---------- Memory ----------

class BrandMemory(Base, TimestampMixin):
    __tablename__ = "brand_memory"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    voice_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    visual_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    offering_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    audience_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    positioning_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    pillars_json: Mapped[list] = mapped_column(JSONB, default=list)
    forbidden_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    source_refs: Mapped[list] = mapped_column(JSONB, default=list)


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # image|video|pdf|doc|audio
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    mime: Mapped[str | None] = mapped_column(String(128), nullable=True)
    hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    exif_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="uploaded")  # uploaded|generated|scraped
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)


class MemoryEvent(Base, TimestampMixin):
    __tablename__ = "memory_events"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(16), nullable=False)  # user|agent|system
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)


# ---------- Content ----------

class ContentBrief(Base, TimestampMixin):
    __tablename__ = "content_briefs"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    origin: Mapped[str] = mapped_column(String(16), default="self")  # user|self
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    segment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pillar_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    instructions: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="open")


class Post(Base, TimestampMixin):
    __tablename__ = "posts"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    brief_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("content_briefs.id"), nullable=True
    )
    platform: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    idea: Mapped[str] = mapped_column(Text, default="")
    hook: Mapped[str] = mapped_column(Text, default="")
    caption: Mapped[str] = mapped_column(Text, default="")
    cta: Mapped[str] = mapped_column(Text, default="")
    media_asset_ids: Mapped[list] = mapped_column(JSONB, default=list)
    reason: Mapped[str] = mapped_column(Text, default="")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    score_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    state: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_post_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=True)


class ApprovalRequest(Base, TimestampMixin):
    __tablename__ = "approval_requests"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    post_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("posts.id"), index=True, nullable=False
    )
    channel: Mapped[str] = mapped_column(String(16), nullable=False)  # telegram|whatsapp
    message_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    requested_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    decision: Mapped[str | None] = mapped_column(String(16), nullable=True)  # approved|rejected
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


# ---------- Analytics & learning ----------

class AnalyticsSnapshot(Base, TimestampMixin):
    __tablename__ = "analytics_snapshots"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    post_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("posts.id"), index=True, nullable=False
    )
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    metrics_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    retention_curve_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    variants_json: Mapped[list] = mapped_column(JSONB, default=list)
    primary_metric: Mapped[str] = mapped_column(String(64), nullable=False)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="proposed")
    results_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    learnings: Mapped[str] = mapped_column(Text, default="")


class FeedbackEvent(Base, TimestampMixin):
    __tablename__ = "feedback_events"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(16), nullable=True)
    free_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_delta_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class TrendSignal(Base, TimestampMixin):
    __tablename__ = "trend_signals"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=True
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Competitor(Base, TimestampMixin):
    __tablename__ = "competitors"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    handle: Mapped[str] = mapped_column(String(255), nullable=False)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class CompetitorPost(Base, TimestampMixin):
    __tablename__ = "competitor_posts"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    competitor_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("competitors.id"), index=True, nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    metrics_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    media_refs: Mapped[list] = mapped_column(JSONB, default=list)
    themes: Mapped[list] = mapped_column(JSONB, default=list)


class AgentJob(Base, TimestampMixin):
    __tablename__ = "agent_jobs"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_id)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
