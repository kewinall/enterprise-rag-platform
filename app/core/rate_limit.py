from dataclasses import dataclass
from functools import lru_cache

from redis.exceptions import RedisError

from app.core.cache import get_cache_store
from app.core.config import get_settings


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: int


class AgentRateLimiter:
    async def check(self, tenant_id: str, subject: str) -> RateLimitResult:
        settings = get_settings()
        limit = settings.agent_rate_limit_per_minute
        if limit <= 0:
            return RateLimitResult(True, 0, 0, 0)

        client = get_cache_store().client
        if client is None:
            return RateLimitResult(True, limit, limit, 0)

        key = f"rag:agent-rate:{tenant_id}:{subject}"
        try:
            count = int(await client.incr(key))
            if count == 1:
                await client.expire(key, 60)
            ttl = max(1, int(await client.ttl(key)))
        except (RedisError, OSError, ValueError):
            return RateLimitResult(True, limit, limit, 0)

        remaining = max(0, limit - count)
        return RateLimitResult(
            allowed=count <= limit,
            limit=limit,
            remaining=remaining,
            retry_after_seconds=ttl if count > limit else 0,
        )


@lru_cache
def get_agent_rate_limiter() -> AgentRateLimiter:
    return AgentRateLimiter()
