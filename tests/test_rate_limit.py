import pytest

from app.core.cache import get_cache_store
from app.core.rate_limit import get_agent_rate_limiter


@pytest.mark.asyncio
async def test_rate_limiter_degrades_open_without_redis():
    cache = get_cache_store()
    original = cache.client
    cache.client = None
    try:
        result = await get_agent_rate_limiter().check("tenant-a", "subject-a")
    finally:
        cache.client = original

    assert result.allowed is True
