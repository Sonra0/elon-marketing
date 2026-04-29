"""Crisis playbooks + escalation.

When the crisis classifier flags a post (or an inbound comment from a webhook),
the playbook routes it through a hardened workflow:

  1. Hard block: the post never auto-publishes; state stays in 'review' until
     a designated approver explicitly accepts.
  2. Double sign-off (when enabled per tenant): two distinct User rows must
     approve before publish.
  3. Templated responses: per-topic suggested replies the operator can use
     for inbound comments (negative reviews, controversy, etc.).
  4. Audit log: every crisis event becomes a MemoryEvent with type=crisis.

Topic taxonomy (kept short; expand per tenant via settings_json["crisis"]):
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from elon.core.models import MemoryEvent, Tenant


DEFAULT_PLAYBOOKS: dict[str, dict[str, Any]] = {
    "negative_review": {
        "response_template": (
            "Thank you for the feedback. We take this seriously and would like to "
            "make it right — could you DM us so we can dig into the details?"
        ),
        "escalate": "support_lead",
        "tone": ["sincere", "non-defensive", "concrete"],
    },
    "controversy": {
        "response_template": (
            "We hear you. We're listening, gathering facts, and will share an update "
            "shortly. We won't speculate before we know more."
        ),
        "escalate": "founder",
        "tone": ["calm", "factual", "no-promises"],
    },
    "sensitive_health": {
        "response_template": (
            "We don't make medical claims. Please consult a qualified professional. "
            "Happy to share product details if helpful."
        ),
        "escalate": "legal",
        "tone": ["neutral", "deflective", "compliant"],
    },
    "default": {
        "response_template": (
            "Thanks for reaching out — we're looking into it and will follow up shortly."
        ),
        "escalate": "operator",
        "tone": ["neutral"],
    },
}


def get_playbooks(tenant: Tenant | None) -> dict[str, dict[str, Any]]:
    s = (tenant.settings_json or {}) if tenant else {}
    overrides = dict(s.get("crisis", {}).get("playbooks") or {})
    return {**DEFAULT_PLAYBOOKS, **overrides}


def double_signoff_required(tenant: Tenant | None) -> bool:
    s = (tenant.settings_json or {}) if tenant else {}
    return bool(s.get("crisis", {}).get("double_signoff", False))


def deny_list_terms(tenant: Tenant | None) -> list[str]:
    s = (tenant.settings_json or {}) if tenant else {}
    terms = s.get("crisis", {}).get("deny_list") or []
    return [str(t).lower() for t in terms]


def violates_deny_list(tenant: Tenant | None, text: str) -> list[str]:
    txt = (text or "").lower()
    return [t for t in deny_list_terms(tenant) if t and t in txt]


def log_crisis(db: Session, tenant_id: UUID, *, kind: str, target: str, payload: dict[str, Any]) -> None:
    db.add(MemoryEvent(
        tenant_id=tenant_id, type="crisis", actor="system",
        payload_json={"kind": kind, "target": target, **payload},
    ))


def map_topic_to_playbook(topics: list[str]) -> str:
    lowered = [t.lower() for t in topics or []]
    if any("review" in t or "complaint" in t for t in lowered):
        return "negative_review"
    if any("controvers" in t or "backlash" in t for t in lowered):
        return "controversy"
    if any("health" in t or "medical" in t for t in lowered):
        return "sensitive_health"
    return "default"
