import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(level=logging.INFO)
    logger.info("application startup")
    yield
    logger.info("application shutdown")


app = FastAPI(lifespan=lifespan)
app.include_router(router)

