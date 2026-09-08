from app.agent.mcp import mcp_tools_list
from app.core.security import ROLE_ADMIN, ROLE_VIEWER, Principal


def principal(*roles: str) -> Principal:
    return Principal(
        subject="mcp-test",
        tenant_id="tenant-a",
        roles=frozenset(roles),
        auth_mode="oidc",
    )


def test_mcp_viewer_only_sees_allowed_tools():
    payload = mcp_tools_list(principal(ROLE_VIEWER))
    names = {item["name"] for item in payload["tools"]}
    assert "search_knowledge" in names
    assert "get_platform_status" in names
    assert "get_recent_audit_events" in names
    assert "delete_document" not in names


def test_mcp_admin_sees_destructive_tool_annotation():
    payload = mcp_tools_list(principal(ROLE_ADMIN))
    tools = {item["name"]: item for item in payload["tools"]}
    assert tools["delete_document"]["annotations"]["destructiveHint"] is True
    assert tools["delete_document"]["annotations"]["readOnlyHint"] is False
