from elon.experiments.pruner import prune_active
from elon.experiments.runner import evaluate_active, propose_all_tenants
from elon.workers.celery_app import celery_app


@celery_app.task(name="elon.workers.tasks.experiments.tick")
def tick() -> dict:
    pruned = prune_active()
    finalized = evaluate_active()
    return {"pruned": pruned, "finalized": finalized}


@celery_app.task(name="elon.workers.tasks.experiments.weekly_propose")
def weekly_propose() -> dict:
    return propose_all_tenants()
