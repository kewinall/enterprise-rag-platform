import asyncio
import logging
from functools import lru_cache

from app.agent.orchestrator import run_agent
from app.agent.state import get_agent_state_store
from app.core.config import get_settings
from app.core.security import Principal

logger = logging.getLogger(__name__)


class AgentJobWorker:
    def __init__(self) -> None:
        self.task: asyncio.Task | None = None
        self.stopping = asyncio.Event()

    async def start(self) -> None:
        settings = get_settings()
        if not settings.agent_async_jobs_enabled or self.task is not None:
            return
        self.stopping.clear()
        self.task = asyncio.create_task(self._loop(), name="agent-job-worker")

    async def stop(self) -> None:
        self.stopping.set()
        if self.task is not None:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

    async def _loop(self) -> None:
        settings = get_settings()
        store = get_agent_state_store()
        while not self.stopping.is_set():
            try:
                job = await store.claim_job()
            except RuntimeError:
                await asyncio.sleep(settings.agent_job_poll_seconds)
                continue

            if job is None:
                await asyncio.sleep(settings.agent_job_poll_seconds)
                continue

            job_id = str(job["job_id"])
            request = dict(job["request"])
            principal = Principal(
                subject=str(job["subject"]),
                tenant_id=str(job["tenant_id"]),
                roles=frozenset(str(role) for role in job["roles"]),
                auth_mode="job",
            )
            try:
                result = await run_agent(
                    str(request["question"]),
                    principal,
                    top_k=int(request.get("top_k", 5)),
                    mode=str(request.get("mode", "hybrid")),
                    session_id=(
                        str(job["session_id"]) if job.get("session_id") else None
                    ),
                    use_memory=bool(request.get("use_memory", True)),
                )
                await store.complete_job(job_id, result)
            except Exception as exc:
                logger.exception("Agent job %s failed", job_id)
                await store.fail_job(job_id, str(exc))


@lru_cache
def get_agent_job_worker() -> AgentJobWorker:
    return AgentJobWorker()
