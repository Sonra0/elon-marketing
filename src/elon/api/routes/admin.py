"""Operator-facing admin: spend + connector status."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from elon.api.deps import current_user, db_session
from elon.core.models import SocialAccount, Tenant, User
from elon.core.spend import current_spend, get_budget

router = APIRouter(prefix="/admin", tags=["admin"])


class SpendOut(BaseModel):
    tenant_id: str
    period_usd: float
    budget_usd: float
    pct_of_budget: float


@router.get("/spend", response_model=SpendOut)
def spend(user: User = Depends(current_user), db: Session = Depends(db_session)) -> SpendOut:
    tenant_id = str(user.tenant_id)
    tenant = db.get(Tenant, user.tenant_id)
    budget = float(tenant.monthly_budget_usd) if tenant else get_budget(tenant_id)
    cur = current_spend(tenant_id)
    return SpendOut(
        tenant_id=tenant_id,
        period_usd=cur,
        budget_usd=budget,
        pct_of_budget=(cur / budget) if budget > 0 else 0.0,
    )


class ConnectorRow(BaseModel):
    platform: str
    handle: str | None
    status: str


@router.get("/connectors", response_model=list[ConnectorRow])
def connectors(user: User = Depends(current_user), db: Session = Depends(db_session)) -> list[ConnectorRow]:
    rows = db.execute(
        select(SocialAccount).where(SocialAccount.tenant_id == user.tenant_id)
    ).scalars().all()
    return [ConnectorRow(platform=r.platform, handle=r.handle, status=r.status) for r in rows]
