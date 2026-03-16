import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@lru_cache
def get_config() -> "Config":
    return Config()


def _parse_optional_int(name: str) -> int | None:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return None
    try:
        return int(raw)
    except ValueError:
        return None


class Config:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RESULT_EXPIRES: int = int(os.getenv("RESULT_EXPIRES", "3600"))  # seconds
    # If set, overrides Celery's default (number of logical CPUs). Otherwise Celery uses its default.
    CELERY_WORKER_CONCURRENCY: int | None = _parse_optional_int("CELERY_WORKER_CONCURRENCY")

