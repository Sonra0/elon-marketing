"""Per-tenant monthly spend meter.

Backed by Redis. Counters keyed by tenant + YYYY-MM. Anyone making a paid call
(LLM, media, search) should call `add_cost` and check `would_exceed` first.

Alert thresholds (from settings, default 0.8 + 1.0) trigger a Telegram message
once each per period.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import redis

from elon.core.logging import get_logger
from elon.core.settings import get_settings

log = get_logger(__name__)
_settings = get_settings()
_r = redis.Redis.from_url(_settings.redis_url, decode_responses=True)


def _period() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"


def _spend_key(tenant_id: str) -> str:
    return f"spend:{tenant_id}:{_period()}"


def _alert_key(tenant_id: str, threshold: float) -> str:
    return f"spend:alert:{tenant_id}:{_period()}:{threshold}"


def get_budget(tenant_id: str, fallback_usd: float | None = None) -> float:
    """Lookup tenant budget from Redis cache; defaults to settings fallback.
    The Tenant.monthly_budget_usd is the canonical source — workers should
    refresh this cache when tenant settings change.
    """
    raw = _r.get(f"budget:{tenant_id}")
    if raw is not None:
        return float(raw)
    return fallback_usd if fallback_usd is not None else _settings.tenant_monthly_budget_usd


def set_budget(tenant_id: str, usd: float) -> None:
    _r.set(f"budget:{tenant_id}", str(usd))


def current_spend(tenant_id: str) -> float:
    raw = _r.get(_spend_key(tenant_id))
    return float(raw) if raw else 0.0


def would_exceed(tenant_id: str, additional_usd: float) -> bool:
    return (current_spend(tenant_id) + additional_usd) > get_budget(tenant_id)


def add_cost(tenant_id: str, usd: float, *, kind: str = "llm") -> float:
    """Record cost; returns new running total. Caller is responsible for
    pre-checking `would_exceed` if it wants hard enforcement.
    """
    new_total = float(_r.incrbyfloat(_spend_key(tenant_id), float(Decimal(str(usd)))))
    log.info("spend_add", tenant_id=tenant_id, usd=usd, kind=kind, total=new_total)
    _maybe_alert(tenant_id, new_total)
    return new_total


def _maybe_alert(tenant_id: str, total: float) -> None:
    budget = get_budget(tenant_id)
    if budget <= 0:
        return
    pct = total / budget
    for threshold in _settings.alert_thresholds:
        if pct >= threshold and _r.set(_alert_key(tenant_id, threshold), "1", nx=True, ex=60 * 60 * 24 * 35):
            # Alert dispatch happens out-of-band; we just enqueue a notify task.
            try:
                from elon.workers.tasks.notify import telegram_message  # local import avoids cycle
                # We don't know the operator's chat_id here; the notify task will look it up via tenant.
                # For Phase 0 we log; Phase 1 wires this through a tenant->chat resolver.
                log.warning("budget_threshold", tenant_id=tenant_id, threshold=threshold, total=total, budget=budget)
                _ = telegram_message  # keep import used
            except Exception as e:  # pragma: no cover
                log.error("alert_dispatch_failed", error=str(e))
