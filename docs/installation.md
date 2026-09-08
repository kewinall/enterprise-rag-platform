# 安裝 / Installation

## Docker Compose — Local Demo

    cp .env.example .env
    docker compose up -d --build
    docker compose exec ollama ollama pull llama3.2:3b

Web UI:

    http://localhost:8000/

## Agentic RAG Configuration

Default:

    AGENT_ENABLED=true
    AGENT_MAX_STEPS=10
    AGENT_MAX_SUBQUERIES=3
    AGENT_MAX_TOOL_CALLS=6
    AGENT_APPROVAL_TTL_SECONDS=600
    AGENT_ENABLE_ANSWER_REVISION=true

**繁體中文**  
Agentic RAG 不需要新增 Container；它使用既有 FastAPI、Redis、Qdrant、LiteLLM/Ollama、PostgreSQL Audit 與 OpenTelemetry。

**English**  
Agentic RAG does not require an additional container. It reuses FastAPI, Redis, Qdrant, LiteLLM/Ollama, PostgreSQL audit, and OpenTelemetry.

## Authentication

Local Demo:

    AUTH_MODE=api_key

OIDC Demo:

    docker compose --profile oidc up -d

then set:

    AUTH_MODE=oidc

詳見 / See: docs/auth-tenancy.md

## Agent Test

先匯入 Sample Documents，再執行 / Ingest sample documents first, then run:

    make evaluate-agent

## Native Python

Python 3.11+:

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    uvicorn app.main:app --reload

## Kubernetes / Helm

    helm upgrade --install rag ./charts/enterprise-rag

v0.5 Helm values 已包含 Agent Runtime Config。  
v0.5 Helm values include agent runtime configuration.

## Offline

    bash scripts/offline/prepare-bundle.sh ./offline-bundle
    bash scripts/offline/verify-bundle.sh ./offline-bundle
    bash scripts/offline/import-bundle.sh ./offline-bundle

Default application image:

    enterprise-rag-platform:0.5.0
