from core.config import get_config
from core.redis import get_redis_client

KEY_PREFIX = "job_registry:"


def register(job_id: str) -> None:
    """Record a job id so status/result can return 404 for unknown ids. TTL matches result expiry."""
    client = get_redis_client()
    key = f"{KEY_PREFIX}{job_id}"
    client.set(key, "1", ex=get_config().RESULT_EXPIRES)


def exists(job_id: str) -> bool:
    """Return True if this job id was ever submitted and not yet expired."""
    client = get_redis_client()
    key = f"{KEY_PREFIX}{job_id}"
    return client.exists(key) > 0

