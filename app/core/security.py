import asyncio
import re
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Header, HTTPException, Request, status
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from app.core.config import get_settings

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+hidden\s+instructions",
]

ROLE_VIEWER = "viewer"
ROLE_EDITOR = "editor"
ROLE_ADMIN = "admin"


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str]
    auth_mode: str

    def has_role(self, role: str) -> bool:
        if ROLE_ADMIN in self.roles:
            return True
        if role == ROLE_VIEWER and ROLE_EDITOR in self.roles:
            return True
        return role in self.roles


def _nested_claim(claims: dict, path: str):
    value = claims
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


@lru_cache
def get_jwk_client() -> PyJWKClient:
    return PyJWKClient(get_settings().oidc_jwks_url, cache_keys=True)


async def _decode_oidc_token(token: str) -> dict:
    settings = get_settings()
    jwk_client = get_jwk_client()
    try:
        signing_key = await asyncio.to_thread(jwk_client.get_signing_key_from_jwt, token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
        )
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OIDC token",
        ) from exc


async def get_principal(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
) -> Principal:
    settings = get_settings()

    if settings.auth_mode == "api_key":
        if settings.rag_api_key and x_api_key != settings.rag_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        principal = Principal(
            subject="api-key-user",
            tenant_id=x_tenant_id or settings.default_tenant_id,
            roles=frozenset({ROLE_VIEWER, ROLE_EDITOR, ROLE_ADMIN}),
            auth_mode="api_key",
        )
        request.state.principal = principal
        return principal

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )

    claims = await _decode_oidc_token(authorization.split(" ", 1)[1].strip())
    tenant = _nested_claim(claims, settings.oidc_tenant_claim)
    role_value = _nested_claim(claims, settings.oidc_roles_claim)

    if not isinstance(tenant, str) or not tenant.strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OIDC token does not contain a tenant claim",
        )

    roles = (
        frozenset(str(role) for role in role_value)
        if isinstance(role_value, list)
        else frozenset()
    )
    principal = Principal(
        subject=str(claims.get("sub", "unknown")),
        tenant_id=tenant.strip(),
        roles=roles,
        auth_mode="oidc",
    )
    request.state.principal = principal
    return principal


def require_role(principal: Principal, role: str) -> None:
    if not principal.has_role(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role required: {role}",
        )


def looks_like_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS)
