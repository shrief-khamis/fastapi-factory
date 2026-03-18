from fastapi import APIRouter

from api.models import SubmitJobResponse, SubmitJobWithWebhookRequest
from core.job_registry import register as job_register
from core.tasks import run_work_with_webhook
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/submit-job-with-webhook", response_model=SubmitJobResponse)
async def submit_job_with_webhook(body: SubmitJobWithWebhookRequest) -> SubmitJobResponse:
    # Use JSON mode so HttpUrl becomes a plain string for Celery's JSON serializer
    payload = body.model_dump(mode="json")
    task = run_work_with_webhook.delay(payload)
    job_register(task.id)
    logger.debug("job submitted with webhook: job_id=%s", task.id)
    return SubmitJobResponse(job_id=task.id)

