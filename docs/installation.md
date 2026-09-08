# 安裝 / Installation

## Docker Compose — Local Demo

1. 複製設定 / Copy configuration:

       cp .env.example .env

2. 修改 Demo Secret / Change demo secrets:

       RAG_API_KEY
       LITELLM_MASTER_KEY
       POSTGRES_PASSWORD
       S3_SECRET_ACCESS_KEY

3. 啟動 / Start:

       docker compose up -d --build

4. Pull Local Model:

       docker compose exec ollama ollama pull llama3.2:3b

5. Web UI:

       http://localhost:8000/

## Default API Key Mode

    AUTH_MODE=api_key
    DEFAULT_TENANT_ID=demo

Request 可用 X-Tenant-ID 模擬 Tenant。  
Requests may use X-Tenant-ID to simulate tenants.

## OIDC Demo

啟動 Keycloak / Start Keycloak:

    docker compose --profile oidc up -d

修改 .env / Change:

    AUTH_MODE=oidc

OIDC:

    OIDC_ISSUER=http://localhost:8080/realms/enterprise-rag
    OIDC_AUDIENCE=enterprise-rag-api
    OIDC_JWKS_URL=http://keycloak:8080/realms/enterprise-rag/protocol/openid-connect/certs

詳見 / See: docs/auth-tenancy.md

## Object Storage

Default MinIO:

    API:     http://localhost:9000
    Console: http://localhost:9001

設定 / Configuration:

    OBJECT_STORE_ENABLED=true
    S3_ENDPOINT_URL=http://minio:9000
    S3_BUCKET=enterprise-rag

詳見 / See: docs/object-storage.md

## Native Python

Python 3.11+:

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    uvicorn app.main:app --reload

**繁體中文**  
Native Mode 需自行提供 Qdrant、LLM Endpoint，以及啟用功能所需的 Redis、PostgreSQL、S3-compatible Storage、OIDC Provider 與 OTLP Endpoint。

**English**  
Native mode requires externally reachable Qdrant and LLM endpoints plus Redis, PostgreSQL, S3-compatible storage, OIDC provider, and OTLP endpoint when those features are enabled.

## Kubernetes / Helm

    helm upgrade --install rag ./charts/enterprise-rag

詳見 / See: docs/kubernetes.md

## Offline

    bash scripts/offline/prepare-bundle.sh ./offline-bundle
    bash scripts/offline/verify-bundle.sh ./offline-bundle
    bash scripts/offline/import-bundle.sh ./offline-bundle

詳見 / See: docs/offline-deployment.md
