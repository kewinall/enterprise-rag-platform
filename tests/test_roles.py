from app.core.security import (
    ROLE_ADMIN,
    ROLE_EDITOR,
    ROLE_VIEWER,
    Principal,
)


def principal(*roles: str) -> Principal:
    return Principal(
        subject="test",
        tenant_id="tenant-a",
        roles=frozenset(roles),
        auth_mode="oidc",
    )


def test_admin_inherits_all_permissions():
    user = principal(ROLE_ADMIN)
    assert user.has_role(ROLE_ADMIN)
    assert user.has_role(ROLE_EDITOR)
    assert user.has_role(ROLE_VIEWER)


def test_editor_inherits_viewer_permission():
    user = principal(ROLE_EDITOR)
    assert user.has_role(ROLE_EDITOR)
    assert user.has_role(ROLE_VIEWER)
    assert not user.has_role(ROLE_ADMIN)


def test_viewer_cannot_edit():
    user = principal(ROLE_VIEWER)
    assert user.has_role(ROLE_VIEWER)
    assert not user.has_role(ROLE_EDITOR)
