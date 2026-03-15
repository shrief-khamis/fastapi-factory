from celery import Celery

from core.config import get_config

config = get_config()

celery_app = Celery(
    "celery_job_api",
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_expires = config.RESULT_EXPIRES
if config.CELERY_WORKER_CONCURRENCY is not None:
    celery_app.conf.worker_concurrency = max(1, config.CELERY_WORKER_CONCURRENCY)

# Import tasks so they are registered
# The import is intentionally not at the top to avoid the circular import
from core import tasks  # noqa: E402, F401
