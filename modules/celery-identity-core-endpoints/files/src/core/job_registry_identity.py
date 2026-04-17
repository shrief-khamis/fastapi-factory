from core.config import get_config
from core.redis import get_redis_client

KEY_PREFIX = "job_identity_registry:"


def register(job_id: str, user_id: str) -> None:
    """Record job owner id. TTL matches result expiry."""
    client = get_redis_client()
    key = f"{KEY_PREFIX}{job_id}"
    client.set(key, user_id, ex=get_config().RESULT_EXPIRES)


def exists_for_user(job_id: str, user_id: str) -> bool:
    """Return True if job id exists and belongs to user_id."""
    client = get_redis_client()
    key = f"{KEY_PREFIX}{job_id}"
    owner = client.get(key)
    if owner is None:
        return False
    if isinstance(owner, bytes):
        owner = owner.decode("utf-8")
    return owner == user_id
