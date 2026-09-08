from dataclasses import dataclass
from typing import Any

from app.core.audit import get_audit_store
from app.core.cache import get_cache_store
from app.core.object_store import get_object_store
from app.core.security import ROLE_ADMIN, ROLE_VIEWER, Principal
from app.retrieval.hybrid import hybrid_search
from app.retrieval.store import get_vector_store


class ToolPermissionError(PermissionError):
    pass


class ToolApprovalRequired(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolPolicy:
    name: str
    required_role: str
    requires_approval: bool
    description: str


TOOL_POLICIES = {
    "search_knowledge": ToolPolicy(
        "search_knowledge",
        ROLE_VIEWER,
        False,
        "Search tenant-scoped knowledge using vector or hybrid retrieval.",
    ),
    "list_documents": ToolPolicy(
        "list_documents",
        ROLE_VIEWER,
        False,
        "List documents visible to the current tenant.",
    ),
    "get_document_metadata": ToolPolicy(
        "get_document_metadata",
        ROLE_VIEWER,
        False,
        "Read metadata for one tenant-scoped document.",
    ),
    "get_platform_status": ToolPolicy(
        "get_platform_status",
        ROLE_VIEWER,
        False,
        "Read tenant-safe data-platform inventory and index statistics.",
    ),
    "get_recent_audit_events": ToolPolicy(
        "get_recent_audit_events",
        ROLE_VIEWER,
        False,
        "Read recent tenant-scoped operational audit events.",
    ),
    "delete_document": ToolPolicy(
        "delete_document",
        ROLE_ADMIN,
        True,
        "Delete a tenant-scoped document and its stored object.",
    ),
}


def list_tool_policies() -> list[dict]:
    return [
        {
            "name": policy.name,
            "required_role": policy.required_role,
            "requires_approval": policy.requires_approval,
            "description": policy.description,
        }
        for policy in TOOL_POLICIES.values()
    ]


def authorize_tool(principal: Principal, tool_name: str) -> ToolPolicy:
    policy = TOOL_POLICIES.get(tool_name)
    if policy is None:
        raise KeyError(f"Unknown tool: {tool_name}")
    if not principal.has_role(policy.required_role):
        raise ToolPermissionError(
            f"Tool {tool_name} requires role {policy.required_role}"
        )
    return policy


async def execute_tool(
    principal: Principal,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    approved: bool = False,
) -> dict:
    policy = authorize_tool(principal, tool_name)
    if policy.requires_approval and not approved:
        raise ToolApprovalRequired(f"Tool {tool_name} requires human approval")

    if tool_name == "search_knowledge":
        query = str(arguments.get("query", "")).strip()
        if not query:
            raise ValueError("search_knowledge requires query")
        top_k = max(1, min(20, int(arguments.get("top_k", 5))))
        mode = str(arguments.get("mode", "hybrid"))
        if mode not in {"vector", "hybrid"}:
            raise ValueError("mode must be vector or hybrid")
        results = hybrid_search(
            query,
            final_top_k=top_k,
            filters={"tenant_id": principal.tenant_id},
            mode=mode,
        )
        return {"tool": tool_name, "query": query, "mode": mode, "results": results}

    if tool_name == "list_documents":
        documents = get_vector_store().list_document_summaries(principal.tenant_id)
        return {"tool": tool_name, "documents": documents}

    if tool_name == "get_document_metadata":
        document_id = str(arguments.get("document_id", "")).strip()
        if not document_id:
            raise ValueError("get_document_metadata requires document_id")
        documents = get_vector_store().list_document_summaries(principal.tenant_id)
        document = next(
            (item for item in documents if item["document_id"] == document_id),
            None,
        )
        if document is None:
            raise LookupError("Document not found")
        return {"tool": tool_name, "document": document}

    if tool_name == "get_platform_status":
        documents = get_vector_store().list_document_summaries(principal.tenant_id)
        return {
            "tool": tool_name,
            "tenant_id": principal.tenant_id,
            "documents": len(documents),
            "chunks": sum(int(item.get("chunks", 0)) for item in documents),
            "content_types": sorted(
                {str(item.get("content_type")) for item in documents if item.get("content_type")}
            ),
        }

    if tool_name == "get_recent_audit_events":
        limit = max(1, min(50, int(arguments.get("limit", 10))))
        events = await get_audit_store().recent_events(principal.tenant_id, limit)
        safe_events = [
            {
                "event_time": str(event["event_time"]),
                "request_id": event["request_id"],
                "method": event["method"],
                "path": event["path"],
                "status_code": event["status_code"],
                "duration_ms": event["duration_ms"],
            }
            for event in events
        ]
        return {"tool": tool_name, "events": safe_events}

    if tool_name == "delete_document":
        document_id = str(arguments.get("document_id", "")).strip()
        if not document_id:
            raise ValueError("delete_document requires document_id")
        store = get_vector_store()
        if store.count_document(document_id, principal.tenant_id) == 0:
            raise LookupError("Document not found")
        object_key = store.get_document_object_key(document_id, principal.tenant_id)
        await get_object_store().delete_object(object_key)
        deleted_chunks = store.delete_document(document_id, principal.tenant_id)
        revision = await get_cache_store().bump_tenant_revision(principal.tenant_id)
        return {
            "tool": tool_name,
            "document_id": document_id,
            "deleted_chunks": deleted_chunks,
            "tenant_revision": revision,
        }

    raise KeyError(f"Unknown tool: {tool_name}")
