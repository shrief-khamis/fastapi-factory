from core.celery_app import celery_app
from engine.work import do_work


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def run_work(self, payload: dict) -> dict:
    """Execute the work in the engine; result is stored in the backend."""
    return do_work(payload)

