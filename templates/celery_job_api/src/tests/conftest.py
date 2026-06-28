import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def _mock_redis_liveness_for_lifespan(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow in-process tests without a running Redis broker (lifespan check only)."""
    try:
        import core.redis as redis_mod
    except ImportError:
        return
    monkeypatch.setattr(redis_mod, "ping_redis", lambda: True)


from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
