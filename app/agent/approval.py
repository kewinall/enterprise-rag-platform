import json
from datetime import UTC, datetime
from uuid import uuid4

from app.core.cache import get_cache_store
from app.core.config import get_settings
from app.core.security import Principal
from app.agent.tools import authorize_tool


def _approval_key(action_id: str) -> str:
    return f"rag:agent-approval:{action_id}"


async def create_approval_request(
    principal: Principal,
    tool_name: str,
    arguments: dict,
) -> dict:
    policy = authorize_tool(principal, tool_name)
    if not policy.requires_approval:
        raise ValueError(f"Tool {tool_name} does not require approval")

    cache = get_cache_store()
    if cache.client is None:
        raise RuntimeError("Redis is required for approval workflow")

    settings = get_settings()
    action_id = str(uuid4())
    payload = {
        "action_id": action_id,
        "tool_name": tool_name,
        "arguments": arguments,
        "tenant_id": principal.tenant_id,
        "requested_by": principal.subject,
        "required_role": policy.required_role,
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }
    await cache.client.set(
        _approval_key(action_id),
        json.dumps(payload, ensure_ascii=False),
        ex=settings.agent_approval_ttl_seconds,
    )
    return {
        **payload,
        "expires_in_seconds": settings.agent_approval_ttl_seconds,
    }


async def get_approval_request(action_id: str) -> dict | None:
    cache = get_cache_store()
    if cache.client is None:
        return None
    raw = await cache.client.get(_approval_key(action_id))
    if raw is None:
        return None
    payload = json.loads(raw)
    return payload if isinstance(payload, dict) else None


async def consume_approval_request(
    action_id: str,
    principal: Principal,
) -> dict:
    cache = get_cache_store()
    if cache.client is None:
        raise RuntimeError("Redis is required for approval workflow")

    key = _approval_key(action_id)
    raw = await cache.client.get(key)
    if raw is None:
        raise LookupError("Approval request not found or expired")

    payload = json.loads(raw)
    if payload.get("tenant_id") != principal.tenant_id:
        raise PermissionError("Approval request belongs to another tenant")
    if not principal.has_role(str(payload.get("required_role", ""))):
        raise PermissionError("Principal cannot approve this action")

    await cache.client.delete(key)
    return payload
