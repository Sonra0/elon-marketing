from elon.content.draft import draft_post as _draft
from elon.workers.celery_app import celery_app


@celery_app.task(name="elon.workers.tasks.content.plan_daily")
def plan_daily() -> dict:
    from elon.content.planner import plan_all_tenants
    return plan_all_tenants()


@celery_app.task(name="elon.workers.tasks.content.draft_post", bind=True, max_retries=2,
                 default_retry_delay=20)
def draft_post(self, tenant_id: str, instructions: str, platform: str | None = None,
               brief_id: str | None = None) -> dict:
    return _draft(
        tenant_id=tenant_id, instructions=instructions, platform=platform, brief_id=brief_id,
    )
