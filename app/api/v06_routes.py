from fastapi import APIRouter, Depends, Header, HTTPException

from app.agent.mcp import mcp_tools_call, mcp_tools_list
from app.agent.state import get_agent_state_store
from app.api.schemas import (
    AgentJobRequest,
    AgentMemoryRequest,
    AgentSessionCreateRequest,
    MCPRequest,
)
from app.core.config import get_settings
from app.core.metrics import AGENT_RATE_LIMITED
from app.core.rate_limit import get_agent_rate_limiter
from app.core.security import ROLE_VIEWER, Principal, get_principal, require_role
from app.evaluation.adversarial import evaluate_adversarial_cases

v06_router = APIRouter(prefix="/api/v1")
mcp_router = APIRouter()
PrincipalDep = Depends(get_principal)


async def _check_rate(principal: Principal) -> None:
    rate = await get_agent_rate_limiter().check(
        principal.tenant_id,
        principal.subject,
    )
    if not rate.allowed:
        AGENT_RATE_LIMITED.inc()
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Agent rate limit exceeded",
                "limit": rate.limit,
                "retry_after_seconds": rate.retry_after_seconds,
            },
        )


@v06_router.post("/agent/sessions")
async def create_agent_session(
    request: AgentSessionCreateRequest,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    return await get_agent_state_store().create_session(
        principal.tenant_id,
        principal.subject,
        request.title,
    )


@v06_router.get("/agent/sessions/{session_id}")
async def get_agent_session(
    session_id: str,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    session = await get_agent_state_store().get_session(
        session_id,
        principal.tenant_id,
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Agent session not found")
    checkpoint = await get_agent_state_store().latest_checkpoint(
        session_id,
        principal.tenant_id,
    )
    return {"session": session, "latest_checkpoint": checkpoint}


@v06_router.get("/agent/sessions/{session_id}/checkpoint")
async def get_agent_checkpoint(
    session_id: str,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    checkpoint = await get_agent_state_store().latest_checkpoint(
        session_id,
        principal.tenant_id,
    )
    if checkpoint is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint


@v06_router.get("/agent/sessions/{session_id}/memory")
async def list_agent_memory(
    session_id: str,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    store = get_agent_state_store()
    if await store.get_session(session_id, principal.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Agent session not found")
    items = await store.list_memory(session_id, principal.tenant_id)
    return {"session_id": session_id, "count": len(items), "items": items}


@v06_router.put("/agent/sessions/{session_id}/memory")
async def put_agent_memory(
    session_id: str,
    request: AgentMemoryRequest,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    settings = get_settings()
    store = get_agent_state_store()
    if await store.get_session(session_id, principal.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Agent session not found")
    retention = request.retention_days or settings.agent_memory_default_retention_days
    retention = min(retention, settings.agent_memory_max_retention_days)
    return await store.upsert_memory(
        session_id=session_id,
        tenant_id=principal.tenant_id,
        key=request.key,
        value=request.value,
        retention_days=retention,
    )


@v06_router.delete("/agent/sessions/{session_id}/memory/{key}")
async def delete_agent_memory(
    session_id: str,
    key: str,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    deleted = await get_agent_state_store().delete_memory(
        session_id,
        principal.tenant_id,
        key,
    )
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"session_id": session_id, "key": key, "deleted": True}


@v06_router.post("/agent/jobs")
async def create_agent_job(
    request: AgentJobRequest,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    await _check_rate(principal)
    store = get_agent_state_store()
    if request.session_id is not None:
        session = await store.get_session(request.session_id, principal.tenant_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Agent session not found")
    return await store.create_job(
        session_id=request.session_id,
        tenant_id=principal.tenant_id,
        subject=principal.subject,
        roles=sorted(principal.roles),
        request=request.model_dump(),
    )


@v06_router.get("/agent/jobs/{job_id}")
async def get_agent_job(
    job_id: str,
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    job = await get_agent_state_store().get_job(job_id, principal.tenant_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Agent job not found")
    return job


@v06_router.get("/agent/evaluate/adversarial")
async def evaluate_agent_adversarial(
    principal: Principal = PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    return {
        "tenant_id": principal.tenant_id,
        **evaluate_adversarial_cases(),
    }


def _mcp_error(request_id, code: int, message: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


@mcp_router.post("/mcp")
async def mcp_endpoint(
    request: MCPRequest,
    principal: Principal = PrincipalDep,
    mcp_protocol_version: str | None = Header(
        default=None,
        alias="MCP-Protocol-Version",
    ),
) -> dict:
    require_role(principal, ROLE_VIEWER)
    supported = {"2026-07-28", "2025-11-25"}
    if mcp_protocol_version and mcp_protocol_version not in supported:
        return _mcp_error(request.id, -32022, "Unsupported MCP protocol version")

    if request.method == "server/discover":
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "protocolVersions": ["2026-07-28", "2025-11-25"],
                "serverInfo": {
                    "name": "enterprise-rag-platform",
                    "version": get_settings().app_version,
                },
                "capabilities": {"tools": {}},
            },
        }

    if request.method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "protocolVersion": "2025-11-25",
                "serverInfo": {
                    "name": "enterprise-rag-platform",
                    "version": get_settings().app_version,
                },
                "capabilities": {"tools": {}},
            },
        }

    if request.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": mcp_tools_list(principal),
        }

    if request.method == "tools/call":
        name = str(request.params.get("name", "")).strip()
        arguments = request.params.get("arguments") or {}
        if not name or not isinstance(arguments, dict):
            return _mcp_error(request.id, -32602, "Invalid tools/call parameters")
        try:
            result = await mcp_tools_call(principal, name, arguments)
        except PermissionError as exc:
            return _mcp_error(request.id, -32001, str(exc))
        except RuntimeError as exc:
            return _mcp_error(request.id, -32002, str(exc))
        except (KeyError, LookupError, ValueError) as exc:
            return _mcp_error(request.id, -32602, str(exc))
        return {"jsonrpc": "2.0", "id": request.id, "result": result}

    return _mcp_error(request.id, -32601, "Method not found")
