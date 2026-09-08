# Enterprise RAG Platform

**目前版本 / Current release: v0.4.0**

> **繁體中文**：Enterprise RAG Platform 是一個以企業落地為目標的 Retrieval-Augmented Generation 參考專案。v0.4 在 Hybrid Retrieval、Evaluation、Cache、Audit、Observability 與 LiteLLM Gateway 基礎上，加入 OIDC/RBAC、Multi-tenancy、MinIO/S3 Object Storage、Kubernetes/Helm、External Secret Integration 與 Air-Gapped Deployment。
>
> **English**: Enterprise RAG Platform is a production-oriented Retrieval-Augmented Generation reference project. v0.4 extends hybrid retrieval, evaluation, caching, auditing, observability, and LiteLLM gateway capabilities with OIDC/RBAC, multi-tenancy, MinIO/S3 object storage, Kubernetes/Helm delivery, external secret integration, and air-gapped deployment.

> **繁體中文**：本 Repository 僅使用 synthetic sample，不包含客戶、公司、真實 Credential 或內部環境資料。
>
> **English**: This repository uses synthetic samples only and contains no customer, company, real credential, or internal-environment data.

## v0.4 重點 / v0.4 Highlights

- OIDC JWT Validation
- Viewer / Editor / Admin RBAC
- Server-enforced tenant isolation
- Tenant-scoped Qdrant metadata and document IDs
- Tenant-scoped Redis cache with revision invalidation
- MinIO / S3 original document storage
- Presigned document download
- Optional Keycloak demo realm
- Kubernetes Helm Chart
- HPA / PDB / NetworkPolicy / SecurityContext
- External Secrets example
- Offline bundle scripts
- CI validation for Python, Docker Compose, Helm, Keycloak JSON, and shell syntax

詳見 / See: docs/v0.4.md and CHANGELOG.md.

## 架構 / Architecture

    Browser / API Client
            |
            v
       OIDC or API Key
            |
            v
          FastAPI
            |
      +-----+-------------------------+
      |                               |
      v                               v
    RBAC + Tenant Scope           PostgreSQL Audit
      |
      +------> Redis Cache + Tenant Revision
      |
      +------> MinIO / S3 Original Document
      |
      v
    Hybrid Retrieval
      |            |
      v            v
    Qdrant        BM25
                  /
                 /
        RRF + Optional Reranker
                 |
                 v
              Context
                 |
                 v
              LiteLLM
                 |
                 v
               Ollama

    Runtime Trace --> OpenTelemetry Collector

## RBAC

| Role | Query/Search/List/Download | Ingest/Reindex | Delete |
|---|---:|---:|---:|
| viewer | ✅ | ❌ | ❌ |
| editor | ✅ | ✅ | ❌ |
| admin | ✅ | ✅ | ✅ |

## Multi-tenancy

**繁體中文**
- tenant_id 由 Authentication Principal 決定。
- Client 不能用 Retrieval Filter 覆蓋 Tenant。
- Qdrant Chunk、Document ID、CRUD、Cache Key 都包含 Tenant Boundary。
- 不同 Tenant 的同名文件會產生不同 Document ID。

**English**
- tenant_id is derived from the authentication principal.
- Clients cannot override tenant scope through retrieval filters.
- Qdrant chunks, document IDs, CRUD operations, and cache keys all include the tenant boundary.
- Same-named documents in different tenants receive different document IDs.

## Object Storage

原始文件會保存至 S3-compatible Object Storage。  
Original documents are stored in S3-compatible object storage.

Default demo:

    MinIO API:     http://localhost:9000
    MinIO Console: http://localhost:9001

Object key:

    {tenant_id}/{document_id}/{filename}

下載會先做 Role + Tenant Validation，再產生短效 Presigned URL。  
Downloads require role and tenant validation before a short-lived presigned URL is issued.

## 快速開始 / Quick start

### Local Demo

    git clone https://github.com/kewinall/enterprise-rag-platform.git
    cd enterprise-rag-platform
    cp .env.example .env
    docker compose up -d --build
    docker compose exec ollama ollama pull llama3.2:3b

Web UI:

    http://localhost:8000/

Default auth mode:

    AUTH_MODE=api_key

### OIDC Demo

啟動 Keycloak Profile / Start Keycloak profile:

    docker compose --profile oidc up -d

將 .env 改為 / Set:

    AUTH_MODE=oidc

Demo realm:

    http://localhost:8080/realms/enterprise-rag

詳見 / See: docs/auth-tenancy.md

## Runtime Services

| Service | Default | Purpose |
|---|---|---|
| FastAPI / Web UI | 8000 | RAG API + UI |
| Qdrant | 6333 / 6334 | Vector DB |
| Ollama | 11434 | Local LLM |
| LiteLLM | 4000 | Model Gateway |
| PostgreSQL | 5432 | Audit Store |
| Redis | 6379 | Answer Cache |
| MinIO | 9000 / 9001 | Object Storage |
| OTel Collector | 4317 / 4318 | Trace Receiver |
| Keycloak | 8080 | Optional OIDC Demo |

## Kubernetes / Helm

Chart:

    charts/enterprise-rag

Install:

    helm upgrade --install rag ./charts/enterprise-rag

Chart includes:

- Deployment
- Service
- Optional Ingress
- ConfigMap
- Existing Secret Reference
- HPA
- PDB
- NetworkPolicy
- Health Probes
- Non-root Security Context
- Read-only Root Filesystem + writable /tmp

詳見 / See: docs/kubernetes.md

## Offline / Air-Gapped Deployment

Prepare:

    bash scripts/offline/prepare-bundle.sh ./offline-bundle

Verify:

    bash scripts/offline/verify-bundle.sh ./offline-bundle

Import:

    bash scripts/offline/import-bundle.sh ./offline-bundle

詳見 / See: docs/offline-deployment.md

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/v1/me | Current principal / tenant / roles |
| POST | /api/v1/ingest | Ingest document |
| POST | /api/v1/ingest/batch | Batch ingest |
| GET | /api/v1/documents | Tenant-scoped document list |
| GET | /api/v1/documents/{document_id}/download | Presigned document download |
| PUT | /api/v1/documents/{document_id}/reindex | Reindex |
| DELETE | /api/v1/documents/{document_id} | Delete |
| POST | /api/v1/search | Retrieval only |
| POST | /api/v1/query | RAG answer + citations |
| POST | /api/v1/evaluate/answer | RAGAS-style answer evaluation |

## CI / Security

CI validates:

    ruff check app tests scripts
    pytest -q
    docker compose --env-file .env.example config --quiet
    helm lint charts/enterprise-rag
    helm template ci charts/enterprise-rag
    python -m json.tool keycloak/realm-export.json
    bash -n scripts/offline/*.sh

Security workflow:

- pip-audit
- Trivy filesystem scan

## 文件 / Documentation

- docs/architecture.md — 架構 / Architecture
- docs/installation.md — 安裝 / Installation
- docs/auth-tenancy.md — OIDC / RBAC / Multi-tenancy
- docs/object-storage.md — MinIO / S3
- docs/kubernetes.md — Kubernetes / Helm
- docs/secrets.md — Secret Management
- docs/offline-deployment.md — Air-Gapped Deployment
- docs/rag-design.md — RAG Design
- docs/evaluation.md — Evaluation
- docs/observability.md — OpenTelemetry
- docs/audit-cache.md — Audit + Cache
- docs/litellm.md — LiteLLM
- docs/v0.2.md / docs/v0.3.md / docs/v0.4.md — Release Guides
- docs/security.md — Security
- docs/troubleshooting.md — Troubleshooting
- docs/roadmap.md — Roadmap
- CHANGELOG.md — Changelog

## License

MIT License. See LICENSE.
