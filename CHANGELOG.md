# 版本異動紀錄 / Changelog

## 0.4.0 - 2026-09-08

### 新增 / Added

- OIDC JWT Validation
- Viewer / Editor / Admin RBAC
- Multi-tenant Server-side Isolation
- Tenant-scoped Document ID and Qdrant Metadata
- Tenant-scoped Redis Cache Revision
- MinIO / S3 Original Document Storage
- Presigned Document Download
- Optional Keycloak Demo Realm
- Kubernetes Helm Chart
- HPA / PDB / NetworkPolicy / SecurityContext
- External Secrets Integration Example
- Offline Bundle Preparation / Verification / Import Scripts
- CI Validation for Docker Compose, Helm, Keycloak JSON, and Shell Syntax
- v0.4 Bilingual Documentation

### 變更 / Changed

- Application Version 更新至 / advanced to 0.4.0
- Cache Key 加入 Tenant ID 與 Tenant Revision
- Ingest / Delete / Reindex 會更新 Tenant Cache Revision
- Document CRUD / Search / Query 改為 Tenant-scoped
- Web UI 支援 API Key + Tenant 與 OIDC Bearer Token
- Readiness Endpoint 新增 Object Store State
- Docker Compose 新增 MinIO 與 Optional Keycloak
- Helm Runtime 採 Non-root + Read-only Root Filesystem

### Upgrade Note / 升級注意

v0.3 既有 Qdrant Chunk 沒有 tenant_id。升級 v0.4 後請重新 Ingest，不建議直接替 Legacy Chunk 指派 Tenant。  
Existing v0.3 Qdrant chunks do not contain tenant_id. Re-ingest documents after upgrading to v0.4 instead of assigning tenants to legacy chunks arbitrarily.

## 0.3.0 - 2026-09-08

### 新增 / Added

- RAGAS-style LLM-as-a-Judge Answer Evaluation
- Faithfulness、Answer Relevance、Context Relevance、Optional Answer Correctness
- OpenTelemetry Manual Instrumentation 與 OTLP HTTP Export
- Request、Retrieval、RAG、LLM、Evaluation Traces
- PostgreSQL Request Audit Store
- Redis RAG Answer Cache
- LiteLLM Gateway Example
- Offline-friendly Web UI：Upload、Document List、Chat、Citation
- Answer Evaluation CLI 與 Synthetic Reference Dataset
- v0.3 Bilingual Documentation

### 變更 / Changed

- Application Version 更新至 / advanced to 0.3.0
- Docker Stack 新增 PostgreSQL、Redis、LiteLLM、OTel Collector
- Default LLM Route 改由 LiteLLM Gateway 進入 Ollama
- Qdrant Container 更新為 / updated to v1.19.0
- Ollama Container 更新為 / updated to 0.33.3
- Query Response 新增 Cache Hit / Miss 狀態
- Readiness Response 新增 Redis / PostgreSQL Dependency State

## 0.2.0 - 2026-09-08

- PDF Page Metadata / Markdown Section Metadata
- Deterministic Document ID
- Batch Ingestion
- Document Lifecycle API
- Metadata Filter
- Vector / Hybrid Retrieval
- Retrieval Benchmark

## 0.1.0 - 2026-09-08

- Initial FastAPI RAG Platform
- Qdrant Vector Retrieval
- BM25 + Reciprocal Rank Fusion
- Optional CrossEncoder Reranking
- Local Ollama Example
- CI / pip-audit / Trivy
