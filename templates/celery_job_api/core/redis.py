import redis

from core.config import get_config


def get_redis_client() -> redis.Redis:
    return redis.from_url(get_config().REDIS_URL)


def ping_redis() -> bool:
    """Return True if Redis is reachable."""
    try:
        client = get_redis_client()
        client.ping()
        return True
    except Exception:
        return False
