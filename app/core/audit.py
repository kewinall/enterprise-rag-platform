import json
import logging
from functools import lru_cache

import asyncpg

from app.core.config import get_settings

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS rag_audit_event (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_id TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    duration_ms DOUBLE PRECISION NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
)
"""


class AuditStore:
    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def start(self) -> None:
        settings = get_settings()
        if not settings.audit_enabled:
            return

        try:
            pool = await asyncpg.create_pool(
                dsn=settings.postgres_dsn,
                min_size=1,
                max_size=4,
            )
            await pool.execute(CREATE_TABLE_SQL)
        except (asyncpg.PostgresError, OSError) as exc:
            logger.warning("PostgreSQL audit store unavailable: %s", exc)
            return

        self.pool = pool
        logger.info("PostgreSQL audit logging enabled")

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def recent_events(
        self,
        tenant_id: str,
        limit: int = 10,
    ) -> list[dict]:
        if self.pool is None:
            return []
        rows = await self.pool.fetch(
            """
            SELECT event_time, request_id, method, path, status_code, duration_ms, metadata
            FROM rag_audit_event
            WHERE metadata->>'tenant_id' = $1
            ORDER BY id DESC
            LIMIT $2
            """,
            tenant_id,
            max(1, min(50, limit)),
        )
        return [dict(row) for row in rows]

    async def record_request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        metadata: dict | None = None,
    ) -> None:
        if self.pool is None:
            return

        payload = json.dumps(metadata or {}, ensure_ascii=False)
        try:
            await self.pool.execute(
                """
                INSERT INTO rag_audit_event
                    (request_id, method, path, status_code, duration_ms, metadata)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                """,
                request_id,
                method,
                path,
                status_code,
                duration_ms,
                payload,
            )
        except (asyncpg.PostgresError, OSError) as exc:
            logger.warning("Audit insert failed: %s", exc)


@lru_cache
def get_audit_store() -> AuditStore:
    return AuditStore()
