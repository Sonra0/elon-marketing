"""Per-tenant Celery queue routing.

Phase 2 hardening: while base queues stay (ingest/content/publish/...), tasks
that should isolate per tenant accept a `tenant_id` and dispatch to a
tenant-suffixed queue (e.g. publish:t-<uuid8>). Workers run with a glob
include of the base queues + tenant queues, but a fair-share dispatcher can
weight specific tenants by spinning extra workers on their queue.

For MVP we use a simple helper: `route(base, tenant_id) -> queue_name`.
"""

from __future__ import annotations


def route(base: str, tenant_id: str | None) -> str:
    if not tenant_id:
        return base
    return f"{base}:t-{tenant_id[:8]}"
