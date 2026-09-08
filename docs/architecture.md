# 架構 / Architecture

## v0.4 Architecture

**繁體中文**  
v0.4 將平台切分為 Identity Plane、RAG/Data Plane、State Layer、Model Gateway、Object Storage 與 Observability。Authentication Principal 會決定 Tenant Boundary 與 RBAC，所有文件與 Retrieval Operation 都必須經過 Server-side Tenant Scope。

**English**  
v0.4 separates the platform into an identity plane, RAG/data plane, state layer, model gateway, object storage, and observability. The authentication principal determines tenant boundaries and RBAC, and all document/retrieval operations are server-scoped to the authenticated tenant.

## Runtime Flow / 執行流程

1. Client 使用 API Key Demo 或 OIDC Bearer Token。  
   Client authenticates using API-key demo mode or an OIDC bearer token.
2. FastAPI 建立 Principal，包含 subject、tenant_id、roles。  
   FastAPI builds a principal containing subject, tenant_id, and roles.
3. RBAC 檢查 Endpoint Permission。  
   RBAC validates endpoint permission.
4. Tenant Scope 自動加入 Qdrant Filter / Document CRUD。  
   Tenant scope is automatically added to Qdrant filters and document CRUD.
5. Ingest 原始文件保存到 MinIO / S3，再建立 Chunk / Embedding。  
   Ingest stores the original document in MinIO/S3 before chunking and embedding.
6. Query 先檢查 Tenant-scoped Redis Cache。  
   Query checks the tenant-scoped Redis cache first.
7. Cache Miss 執行 Hybrid Retrieval。  
   Hybrid retrieval runs on cache miss.
8. Context 經 LiteLLM 呼叫 Model。  
   Context is sent through LiteLLM to the model runtime.
9. HTTP Metadata 寫入 PostgreSQL Audit。  
   HTTP metadata is written to PostgreSQL audit storage.
10. Runtime Spans 輸出至 OpenTelemetry Collector。  
    Runtime spans are exported to the OpenTelemetry Collector.

## Tenant Boundary

Tenant Scope 會套用到 / applies to:

- Document ID
- Qdrant Payload
- List
- Search
- Query
- Delete
- Reindex
- Download
- Redis Cache Key
- Cache Revision

Client 提供的 Retrieval Filter 不包含 tenant_id 欄位，因此不能覆蓋 Server Scope。  
Client retrieval filters do not expose tenant_id, so the server scope cannot be overridden.

## Production Topology

**繁體中文**  
正式環境建議 API 使用 Helm 部署；OIDC、Qdrant、Redis、PostgreSQL、Object Storage、LiteLLM、OTel Backend 可使用 Managed Service 或 Shared Platform Service。Secret 由 Secret Manager / External Secrets 注入。

**English**  
For production, deploy the API with Helm while using managed or shared services for OIDC, Qdrant, Redis, PostgreSQL, object storage, LiteLLM, and telemetry backends. Inject secrets through a secret manager or External Secrets.

## Deployment Controls

- Non-root Runtime
- Read-only Root Filesystem
- Health Probes
- HPA
- PDB
- NetworkPolicy
- Existing Secret Reference
- Offline Bundle Support
