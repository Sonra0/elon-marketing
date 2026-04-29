"""Tenant + user bootstrap. MVP: a single owner per tenant.

Flow:
1. POST /tenants { name } -> creates tenant + owner user, returns JWT and a Telegram link token.
2. Operator opens Telegram bot, sends `/link <token>` to bind their telegram_user_id.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from elon.api.deps import current_user, db_session
from elon.core.models import Tenant, User
from elon.core.security import create_jwt
from elon.core.settings import get_settings

router = APIRouter(prefix="/tenants", tags=["tenants"])


class CreateTenantIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class CreateTenantOut(BaseModel):
    tenant_id: str
    user_id: str
    jwt: str
    telegram_link_token: str
    telegram_link_command: str


@router.post("", response_model=CreateTenantOut)
def create_tenant(body: CreateTenantIn, db: Session = Depends(db_session)) -> CreateTenantOut:
    settings = get_settings()
    tenant = Tenant(name=body.name, monthly_budget_usd=settings.tenant_monthly_budget_usd)
    db.add(tenant)
    db.flush()
    link_token = secrets.token_urlsafe(24)
    user = User(
        tenant_id=tenant.id,
        role="owner",
        link_token=link_token,
        link_token_expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(user)
    db.flush()
    tenant.owner_user_id = user.id
    db.commit()
    return CreateTenantOut(
        tenant_id=str(tenant.id),
        user_id=str(user.id),
        jwt=create_jwt(str(user.id), {"tenant_id": str(tenant.id), "role": "owner"}),
        telegram_link_token=link_token,
        telegram_link_command=f"/link {link_token}",
    )


class MeOut(BaseModel):
    user_id: str
    tenant_id: str
    role: str
    telegram_linked: bool
    whatsapp_linked: bool


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(current_user)) -> MeOut:
    return MeOut(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role,
        telegram_linked=bool(user.telegram_user_id),
        whatsapp_linked=bool(user.whatsapp_phone),
    )
