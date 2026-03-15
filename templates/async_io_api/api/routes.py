import asyncio

from fastapi import APIRouter

from api.models import HealthResponse, SleepResponse
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/sleep", response_model=SleepResponse)
async def sleep() -> SleepResponse:
    seconds = 10.0
    logger.debug("sleep endpoint: sleeping for %s seconds", seconds)
    await asyncio.sleep(seconds)
    return SleepResponse(slept_seconds=seconds)
