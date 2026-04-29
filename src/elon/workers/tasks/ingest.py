from elon.ingestor.brand import ingest_brand as _ingest
from elon.workers.celery_app import celery_app


@celery_app.task(name="elon.workers.tasks.ingest.brand", bind=True, max_retries=2)
def ingest_brand(self, tenant_id: str, website_url: str | None = None,
                 asset_keys: list[str] | None = None, notes: str | None = None) -> dict:
    return _ingest(
        tenant_id=tenant_id,
        website_url=website_url,
        asset_keys=asset_keys,
        notes=notes,
    )
