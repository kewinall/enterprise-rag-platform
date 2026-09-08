import hashlib
import json
import logging
from functools import lru_cache

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def make_rag_cache_key(
    question: str,
    top_k: int,
    mode: str,
    filters: dict | None,
    model: str,
    tenant_id: str = "default",
) -> str:
    payload = {
        "tenant_id": tenant_id,
        "question": question,
        "top_k": top_k,
        "mode": mode,
        "filters": filters or {},
        "model": model,
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    return f"rag:answer:{digest}"


class CacheStore:
    def __init__(self) -> None:
        self.client: Redis | None = None

    async def start(self) -> None:
        settings = get_settings()
        if not settings.cache_enabled:
            return

        client = Redis.from_url(settings.redis_url, decode_responses=True)
        try:
            await client.ping()
        except (RedisError, OSError) as exc:
            logger.warning("Redis cache unavailable: %s", exc)
            await client.aclose()
            return

        self.client = client
        logger.info("Redis cache enabled")

    async def close(self) -> None:
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def get_json(self, key: str) -> dict | None:
        if self.client is None:
            return None
        try:
            value = await self.client.get(key)
        except (RedisError, OSError) as exc:
            logger.warning("Redis GET failed: %s", exc)
            return None
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning("Invalid cached JSON for key %s", key)
            return None

    async def set_json(self, key: str, value: dict, ttl_seconds: int) -> None:
        if self.client is None:
            return
        try:
            await self.client.set(
                key,
                json.dumps(value, ensure_ascii=False),
                ex=ttl_seconds,
            )
        except (RedisError, OSError) as exc:
            logger.warning("Redis SET failed: %s", exc)


@lru_cache
def get_cache_store() -> CacheStore:
    return CacheStore()
