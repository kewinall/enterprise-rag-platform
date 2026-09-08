# 驗證、授權與 Multi-tenancy / Authentication, Authorization, and Multi-tenancy

## Auth Mode / 驗證模式

**繁體中文**  
v0.4 支援兩種模式。api_key 只建議用於本機 Demo；oidc 用於 Enterprise-style JWT Validation。

**English**  
v0.4 supports two modes. api_key is intended for local demos, while oidc provides enterprise-style JWT validation.

### API Key Mode

    AUTH_MODE=api_key
    RAG_API_KEY=change-me
    DEFAULT_TENANT_ID=demo

API Key Mode 可使用 X-Tenant-ID 模擬不同 Tenant。  
API Key mode may use X-Tenant-ID to simulate different tenants.

### OIDC Mode

    AUTH_MODE=oidc
    OIDC_ISSUER=http://localhost:8080/realms/enterprise-rag
    OIDC_AUDIENCE=enterprise-rag-api
    OIDC_JWKS_URL=http://keycloak:8080/realms/enterprise-rag/protocol/openid-connect/certs
    OIDC_ROLES_CLAIM=realm_access.roles
    OIDC_TENANT_CLAIM=tenant_id

**繁體中文**  
API 會驗證 JWT Signature、Issuer、Audience，並從 Token Claim 取得 Role 與 Tenant。Client 無法在 Search Filter 裡自行指定 tenant_id 覆蓋 Server Scope。

**English**  
The API validates JWT signature, issuer, and audience, then derives roles and tenant identity from token claims. Clients cannot override the server-enforced tenant scope through retrieval filters.

## RBAC

| Role | Query/Search/List | Ingest/Reindex | Delete |
|---|---:|---:|---:|
| viewer | ✅ | ❌ | ❌ |
| editor | ✅ | ✅ | ❌ |
| admin | ✅ | ✅ | ✅ |

admin 繼承 editor / viewer，editor 繼承 viewer。  
admin inherits editor and viewer; editor inherits viewer.

## Keycloak Demo

啟動 / Start:

    docker compose --profile oidc up -d

Demo Users:

| User | Password | Tenant | Role |
|---|---|---|---|
| viewer-a | viewer-change-me | tenant-a | viewer |
| editor-a | editor-change-me | tenant-a | editor |
| admin-b | admin-b-change-me | tenant-b | admin |

**繁體中文**  
以上帳密僅為 Repository Demo，禁止沿用至正式環境。

**English**  
These credentials are repository demo credentials only and must never be reused in production.

## Tenant Isolation

**繁體中文**  
tenant_id 會寫入每個 Qdrant Chunk，並自動套用到 List、Search、Query、Delete、Reindex、Download。Document ID 也由 tenant + source 共同產生，因此不同 Tenant 的同名文件不會產生相同 ID。

**English**  
tenant_id is stored with every Qdrant chunk and enforced across list, search, query, delete, reindex, and download operations. Document IDs are derived from tenant plus source, so same-named documents in different tenants do not share IDs.

## Cache Isolation

Redis Cache Key 包含 tenant_id 與 tenant_revision。  
Redis cache keys include tenant_id and tenant_revision.

文件異動後會 bump tenant revision，舊 Cache 自動不再命中。  
Document mutations bump the tenant revision, preventing stale cache entries from being reused.
