from fastapi import APIRouter

from api.models import HealthResponse, WebhookPayload
from engine.processor import process_results
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.post("/webhook")
async def receive_webhook(body: WebhookPayload):
    logger.debug("Received webhook: %s", body.model_dump())
    process_results(body.model_dump())
    return {"ok": True}

