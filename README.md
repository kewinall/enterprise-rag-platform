# Enterprise RAG Platform

**目前版本 / Current release: v0.6.0**

> **繁體中文**：Enterprise RAG Platform 是一個 Enterprise RAG / Agentic AI Reference Platform。v0.6 在 v0.5 Agentic RAG 基礎上加入 Durable Session/Checkpoint、Async Jobs、受治理 Memory、Data Platform Read-only Tools、MCP-compatible Tool Adapter、Token/Cost Budget、Rate Limit 與 Agent Observability Dashboard。
>
> **English**: Enterprise RAG Platform is an enterprise RAG / Agentic AI reference platform. v0.6 adds durable sessions/checkpoints, async jobs, governed memory, read-only data-platform tools, an MCP-compatible tool adapter, token/cost budgets, rate limiting, and an agent observability dashboard.

## v0.6 Highlights

- PostgreSQL Agent Session / Checkpoint
- Durable Async Job Queue with restart recovery
- Explicit Memory with retention / expiration
- Read-only Data Platform Tools
- MCP-compatible Tool Adapter
- Modern 2026-07-28 discovery + legacy 2025-11-25 initialize subset
- Agent Token / Estimated Cost Budget
- Redis Tenant+Subject Rate Limit
- Prometheus Agent Metrics
- Grafana Dashboard JSON
- Expanded Prompt / Tool Injection Evaluation
- Web UI for Session / Memory / Async Job

## Architecture

    User / MCP Client
           |
           v
      OIDC / RBAC
           |
           v
        FastAPI
           |
     Rate Limit / Budget
           |
     +-----+----------------------+
     |                            |
     v                            v
 Durable Session             MCP Tool Adapter
 / Memory / Job                   |
     |                            v
     +------> Agent Runtime <--- Tool Registry
                |
          Planner / Tools
          Retrieval / Critic
                |
                v
          Answer + Checkpoint
                |
        +-------+--------+
        |                |
        v                v
   PostgreSQL         Prometheus
   Durable State      / Grafana

## New APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/v1/agent/sessions | Create durable session |
| GET | /api/v1/agent/sessions/{id} | Session + latest checkpoint |
| GET/PUT | /api/v1/agent/sessions/{id}/memory | Governed memory |
| DELETE | /api/v1/agent/sessions/{id}/memory/{key} | Delete memory |
| POST | /api/v1/agent/jobs | Submit durable async job |
| GET | /api/v1/agent/jobs/{id} | Job status/result |
| GET | /api/v1/agent/evaluate/adversarial | Adversarial evaluation |
| POST | /mcp | MCP-compatible JSON-RPC tool adapter |

Existing RAG / Agent / Document APIs remain available.

## Governance Defaults

    AGENT_STATE_ENABLED=true
    AGENT_ASYNC_JOBS_ENABLED=true
    AGENT_MEMORY_DEFAULT_RETENTION_DAYS=7
    AGENT_MEMORY_MAX_RETENTION_DAYS=30
    AGENT_RATE_LIMIT_PER_MINUTE=30
    AGENT_BUDGET_MAX_TOKENS=12000
    AGENT_BUDGET_MAX_COST_USD=0.25

## Tool Policy

| Tool | Role | Approval |
|---|---|---:|
| search_knowledge | viewer | No |
| list_documents | viewer | No |
| get_document_metadata | viewer | No |
| get_platform_status | viewer | No |
| get_recent_audit_events | viewer | No |
| delete_document | admin | **Required** |

No arbitrary shell, raw SQL, generic HTTP, eval/exec, cloud-admin or secret-read tool is exposed.

## Evaluation

    make benchmark
    make evaluate-answers
    make evaluate-agent
    make evaluate-adversarial

## Observability

Prometheus:

    http://localhost:8000/metrics

Grafana dashboard:

    observability/grafana-agent-dashboard.json

## Quick Start

    cp .env.example .env
    docker compose up -d --build
    docker compose exec ollama ollama pull llama3.2:3b

Web UI:

    http://localhost:8000/

## Documentation

- docs/v0.6.md
- docs/agent-sessions.md
- docs/mcp-adapter.md
- docs/agent-governance.md
- docs/agentic-rag.md
- docs/tool-policy.md
- docs/architecture.md
- docs/security.md
- docs/evaluation.md
- docs/observability.md
- docs/troubleshooting.md
- docs/installation.md
- docs/roadmap.md
- CHANGELOG.md

## License

MIT License. See LICENSE.
