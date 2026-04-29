from celery import Celery
from celery.schedules import crontab

from elon.core.settings import get_settings

_settings = get_settings()

celery_app = Celery(
    "elon",
    broker=_settings.redis_url,
    backend=_settings.redis_url,
    include=[
        "elon.workers.tasks.notify",
        "elon.workers.tasks.ingest",
        "elon.workers.tasks.content",
        "elon.workers.tasks.publish",
        "elon.workers.tasks.analytics",
        "elon.workers.tasks.experiments",
    ],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="notify",
    task_routes={
        "elon.workers.tasks.ingest.*": {"queue": "ingest"},
        "elon.workers.tasks.content.*": {"queue": "content"},
        "elon.workers.tasks.publish.*": {"queue": "publish"},
        "elon.workers.tasks.analytics.*": {"queue": "analytics"},
        "elon.workers.tasks.experiments.*": {"queue": "experiments"},
        "elon.workers.tasks.notify.*": {"queue": "notify"},
    },
    timezone="UTC",
)

celery_app.conf.beat_schedule = {
    "daily-content-plan": {
        "task": "elon.workers.tasks.content.plan_daily",
        "schedule": crontab(hour=6, minute=0),
    },
    "daily-trend-pull": {
        "task": "elon.workers.tasks.analytics.pull_trends",
        "schedule": crontab(hour=5, minute=30),
    },
    "competitor-sweep": {
        "task": "elon.workers.tasks.analytics.sweep_competitors",
        "schedule": crontab(hour=4, minute=0),
    },
    "nightly-digest": {
        "task": "elon.workers.tasks.analytics.nightly_digest",
        "schedule": crontab(hour=22, minute=0),
    },
    "weekly-experiments": {
        "task": "elon.workers.tasks.experiments.weekly_propose",
        "schedule": crontab(day_of_week=1, hour=8, minute=0),  # Monday 08:00 UTC
    },
    "experiments-evaluate": {
        "task": "elon.workers.tasks.experiments.tick",
        "schedule": crontab(hour=23, minute=30),
    },
}
