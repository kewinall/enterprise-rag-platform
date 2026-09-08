# 安裝 / Installation

## Docker Compose

    cp .env.example .env
    docker compose up -d --build
    docker compose exec ollama ollama pull llama3.2:3b

Web UI:

    http://localhost:8000/

## v0.6 Agent Platform Settings

    AGENT_STATE_ENABLED=true
    AGENT_ASYNC_JOBS_ENABLED=true
    AGENT_JOB_POLL_SECONDS=1
    AGENT_MEMORY_DEFAULT_RETENTION_DAYS=7
    AGENT_MEMORY_MAX_RETENTION_DAYS=30
    AGENT_RATE_LIMIT_PER_MINUTE=30
    AGENT_BUDGET_MAX_TOKENS=12000
    AGENT_BUDGET_MAX_COST_USD=0.25
    AGENT_INPUT_COST_PER_1K=0
    AGENT_OUTPUT_COST_PER_1K=0

No new container is required. Durable agent state reuses PostgreSQL; rate limiting reuses Redis.

## MCP

Endpoint:

    POST /mcp

See docs/mcp-adapter.md.

## Evaluation

    make evaluate-agent
    make evaluate-adversarial

## Kubernetes

    helm upgrade --install rag ./charts/enterprise-rag

Helm chart version: 0.6.0

## Offline

    bash scripts/offline/prepare-bundle.sh ./offline-bundle

Default application image:

    enterprise-rag-platform:0.6.0
