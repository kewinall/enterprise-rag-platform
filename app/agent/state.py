import json
import logging
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import uuid4

import asyncpg

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS agent_session (
    session_id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_checkpoint (
    checkpoint_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES agent_session(session_id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL,
    state JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_job (
    job_id UUID PRIMARY KEY,
    session_id UUID REFERENCES agent_session(session_id) ON DELETE SET NULL,
    tenant_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    roles JSONB NOT NULL,
    request JSONB NOT NULL,
    status TEXT NOT NULL,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agent_job_status_created
ON agent_job(status, created_at);

CREATE TABLE IF NOT EXISTS agent_memory (
    memory_id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES agent_session(session_id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    memory_value TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(session_id, memory_key)
);

CREATE INDEX IF NOT EXISTS idx_agent_memory_expiry
ON agent_memory(expires_at);
"""


class AgentStateStore:
    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def start(self) -> None:
        settings = get_settings()
        if not settings.agent_state_enabled:
            return
        try:
            self.pool = await asyncpg.create_pool(
                dsn=settings.postgres_dsn,
                min_size=1,
                max_size=4,
            )
            await self.pool.execute(SCHEMA_SQL)
            await self.pool.execute(
                "UPDATE agent_job SET status='queued', started_at=NULL "
                "WHERE status='running'"
            )
            await self.cleanup_expired_memory()
        except (asyncpg.PostgresError, OSError) as exc:
            logger.warning("Agent state store unavailable: %s", exc)
            self.pool = None

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    def _require_pool(self) -> asyncpg.Pool:
        if self.pool is None:
            raise RuntimeError("Agent state store is not available")
        return self.pool

    async def create_session(self, tenant_id: str, subject: str, title: str | None) -> dict:
        pool = self._require_pool()
        session_id = uuid4()
        row = await pool.fetchrow(
            """
            INSERT INTO agent_session(session_id, tenant_id, subject, title)
            VALUES($1, $2, $3, $4)
            RETURNING session_id, tenant_id, subject, title, created_at, updated_at
            """,
            session_id,
            tenant_id,
            subject,
            title,
        )
        return dict(row)

    async def get_session(self, session_id: str, tenant_id: str) -> dict | None:
        pool = self._require_pool()
        row = await pool.fetchrow(
            """
            SELECT session_id, tenant_id, subject, title, created_at, updated_at
            FROM agent_session
            WHERE session_id=$1::uuid AND tenant_id=$2
            """,
            session_id,
            tenant_id,
        )
        return dict(row) if row else None

    async def save_checkpoint(self, session_id: str, tenant_id: str, state: dict) -> dict:
        pool = self._require_pool()
        row = await pool.fetchrow(
            """
            INSERT INTO agent_checkpoint(session_id, tenant_id, state)
            VALUES($1::uuid, $2, $3::jsonb)
            RETURNING checkpoint_id, session_id, tenant_id, state, created_at
            """,
            session_id,
            tenant_id,
            json.dumps(state, ensure_ascii=False),
        )
        await pool.execute(
            "UPDATE agent_session SET updated_at=NOW() WHERE session_id=$1::uuid AND tenant_id=$2",
            session_id,
            tenant_id,
        )
        return dict(row)

    async def latest_checkpoint(self, session_id: str, tenant_id: str) -> dict | None:
        pool = self._require_pool()
        row = await pool.fetchrow(
            """
            SELECT checkpoint_id, session_id, tenant_id, state, created_at
            FROM agent_checkpoint
            WHERE session_id=$1::uuid AND tenant_id=$2
            ORDER BY checkpoint_id DESC
            LIMIT 1
            """,
            session_id,
            tenant_id,
        )
        return dict(row) if row else None

    async def create_job(
        self,
        *,
        session_id: str | None,
        tenant_id: str,
        subject: str,
        roles: list[str],
        request: dict,
    ) -> dict:
        pool = self._require_pool()
        job_id = uuid4()
        row = await pool.fetchrow(
            """
            INSERT INTO agent_job(job_id, session_id, tenant_id, subject, roles, request, status)
            VALUES($1, $2::uuid, $3, $4, $5::jsonb, $6::jsonb, 'queued')
            RETURNING job_id, session_id, tenant_id, subject, status, created_at
            """,
            job_id,
            session_id,
            tenant_id,
            subject,
            json.dumps(roles),
            json.dumps(request, ensure_ascii=False),
        )
        return dict(row)

    async def get_job(self, job_id: str, tenant_id: str) -> dict | None:
        pool = self._require_pool()
        row = await pool.fetchrow(
            """
            SELECT job_id, session_id, tenant_id, subject, roles, request, status,
                   result, error, created_at, started_at, completed_at
            FROM agent_job
            WHERE job_id=$1::uuid AND tenant_id=$2
            """,
            job_id,
            tenant_id,
        )
        return dict(row) if row else None

    async def claim_job(self) -> dict | None:
        pool = self._require_pool()
        async with pool.acquire() as conn, conn.transaction():
            row = await conn.fetchrow(
                    """
                    SELECT job_id, session_id, tenant_id, subject, roles, request
                    FROM agent_job
                    WHERE status='queued'
                    ORDER BY created_at
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                    """
            )
            if row is None:
                return None
            await conn.execute(
                "UPDATE agent_job SET status='running', started_at=NOW() WHERE job_id=$1",
                row["job_id"],
            )
            return dict(row)

    async def complete_job(self, job_id: str, result: dict) -> None:
        pool = self._require_pool()
        await pool.execute(
            """
            UPDATE agent_job
            SET status='completed', result=$2::jsonb, completed_at=NOW()
            WHERE job_id=$1::uuid
            """,
            job_id,
            json.dumps(result, ensure_ascii=False),
        )

    async def fail_job(self, job_id: str, error: str) -> None:
        pool = self._require_pool()
        await pool.execute(
            """
            UPDATE agent_job
            SET status='failed', error=$2, completed_at=NOW()
            WHERE job_id=$1::uuid
            """,
            job_id,
            error[:4000],
        )

    async def upsert_memory(
        self,
        *,
        session_id: str,
        tenant_id: str,
        key: str,
        value: str,
        retention_days: int,
    ) -> dict:
        pool = self._require_pool()
        expires_at = datetime.now(UTC) + timedelta(days=retention_days)
        memory_id = uuid4()
        row = await pool.fetchrow(
            """
            INSERT INTO agent_memory(
                memory_id, session_id, tenant_id, memory_key, memory_value, expires_at
            )
            VALUES($1, $2::uuid, $3, $4, $5, $6)
            ON CONFLICT(session_id, memory_key) DO UPDATE
            SET memory_value=EXCLUDED.memory_value,
                expires_at=EXCLUDED.expires_at,
                updated_at=NOW()
            RETURNING memory_id, session_id, tenant_id, memory_key, memory_value,
                      expires_at, created_at, updated_at
            """,
            memory_id,
            session_id,
            tenant_id,
            key,
            value,
            expires_at,
        )
        return dict(row)

    async def list_memory(self, session_id: str, tenant_id: str) -> list[dict]:
        pool = self._require_pool()
        await self.cleanup_expired_memory()
        rows = await pool.fetch(
            """
            SELECT memory_id, session_id, tenant_id, memory_key, memory_value,
                   expires_at, created_at, updated_at
            FROM agent_memory
            WHERE session_id=$1::uuid AND tenant_id=$2 AND expires_at > NOW()
            ORDER BY memory_key
            """,
            session_id,
            tenant_id,
        )
        return [dict(row) for row in rows]

    async def delete_memory(self, session_id: str, tenant_id: str, key: str) -> int:
        pool = self._require_pool()
        result = await pool.execute(
            """
            DELETE FROM agent_memory
            WHERE session_id=$1::uuid AND tenant_id=$2 AND memory_key=$3
            """,
            session_id,
            tenant_id,
            key,
        )
        return int(result.split()[-1])

    async def cleanup_expired_memory(self) -> int:
        if self.pool is None:
            return 0
        result = await self.pool.execute(
            "DELETE FROM agent_memory WHERE expires_at <= NOW()"
        )
        return int(result.split()[-1])


@lru_cache
def get_agent_state_store() -> AgentStateStore:
    return AgentStateStore()
