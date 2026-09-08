import pytest

from app.agent.tools import (
    ToolPermissionError,
    authorize_tool,
    list_tool_policies,
)
from app.core.security import ROLE_ADMIN, ROLE_VIEWER, Principal


def make_principal(*roles: str, tenant: str = "tenant-a") -> Principal:
    return Principal(
        subject="test",
        tenant_id=tenant,
        roles=frozenset(roles),
        auth_mode="oidc",
    )


def test_viewer_can_search_but_cannot_delete():
    viewer = make_principal(ROLE_VIEWER)
    assert authorize_tool(viewer, "search_knowledge").requires_approval is False
    with pytest.raises(ToolPermissionError):
        authorize_tool(viewer, "delete_document")


def test_delete_requires_admin_and_approval():
    admin = make_principal(ROLE_ADMIN)
    policy = authorize_tool(admin, "delete_document")
    assert policy.required_role == ROLE_ADMIN
    assert policy.requires_approval is True


def test_tool_policy_catalog_marks_destructive_tool():
    policies = {item["name"]: item for item in list_tool_policies()}
    assert policies["delete_document"]["requires_approval"] is True
