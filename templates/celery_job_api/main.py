import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from core.redis import ping_redis
from utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(level=logging.DEBUG)
    logger.info("application startup")
    if not ping_redis():
        logger.error("Redis is not reachable; exiting")
        sys.exit(1)
    logger.info("Redis is live")
    yield
    logger.info("application shutdown")


app = FastAPI(lifespan=lifespan)
app.include_router(router)
