import pytest

from app.agent.approval import validate_approval_request
from app.core.security import ROLE_ADMIN, ROLE_VIEWER, Principal


def principal(role: str, tenant: str) -> Principal:
    return Principal(
        subject="approver",
        tenant_id=tenant,
        roles=frozenset({role}),
        auth_mode="oidc",
    )


def test_approval_cannot_cross_tenant():
    payload = {
        "tenant_id": "tenant-a",
        "required_role": ROLE_ADMIN,
    }
    with pytest.raises(PermissionError):
        validate_approval_request(
            payload,
            principal(ROLE_ADMIN, "tenant-b"),
        )


def test_approval_requires_required_role():
    payload = {
        "tenant_id": "tenant-a",
        "required_role": ROLE_ADMIN,
    }
    with pytest.raises(PermissionError):
        validate_approval_request(
            payload,
            principal(ROLE_VIEWER, "tenant-a"),
        )


def test_admin_can_approve_same_tenant():
    payload = {
        "tenant_id": "tenant-a",
        "required_role": ROLE_ADMIN,
    }
    validate_approval_request(
        payload,
        principal(ROLE_ADMIN, "tenant-a"),
    )
