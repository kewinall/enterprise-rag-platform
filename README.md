# Enterprise RAG Platform

**目前版本 / Current release: v0.6.0**


> **📘 Interactive Project Guide / 專案互動式說明文件**  
> [Open Live Project Guide](https://kewinall.github.io/enterprise-rag-platform/) · [Repository HTML](docs/enterprise-rag-platform-guide.html) — 架構、RAG/Agent 流程、功能矩陣、安全治理、部署、CI/Security、版本演進與面試官速讀集中於單一自包含 HTML。

> **繁體中文**：Enterprise RAG Platform 是一個以企業知識為核心的 **Knowledge AI Platform**，展示文件如何經過 Ingestion、Hybrid Retrieval、Reranking、Grounded Generation、Citation 與 Evaluation，並套用 OIDC/RBAC、Multi-tenancy、Audit 與安全治理。
>
> **English**: Enterprise RAG Platform is a production-oriented **Knowledge AI Platform** showing how enterprise documents become governed, grounded AI context through ingestion, hybrid retrieval, reranking, generation, citations, evaluation, and enterprise security controls.

## Portfolio Role / 作品集角色

**Primary role: Knowledge AI Platform / 企業知識 AI 平台**

此 Repository 主要回答：**企業知識如何安全、可治理、可評測地提供給 RAG 與 Agent？**  
This repository primarily answers: **How can enterprise knowledge be safely retrieved, governed, evaluated, and supplied to RAG/agent workloads?**

Portfolio responsibility boundary:

- **This repository:** knowledge ingestion, retrieval, grounding, citations, evaluation, knowledge governance.
- [Agentic DataOps Copilot](https://github.com/kewinall/agentic-dataops-copilot): reasoning, incident analysis, and governed DataOps operations.
- [Data Platform MCP Server](https://github.com/kewinall/data-platform-mcp-server): canonical MCP tool and enterprise data-platform integration layer.
- [Multi-LLM AI Gateway](https://github.com/kewinall/multi-llm-ai-gateway): centralized model routing, resilience, policy, and cost control.

> v0.6 includes agent, MCP, durable-session, memory, and Data Platform tool examples as **advanced integration capabilities**. They are not the primary portfolio identity of this repository.

## Core Knowledge Flow / 核心知識流程

    Documents
       |
       v
    Parsing / Chunking
       |
       v
    Embedding + Metadata
       |
       +-------------------+
       |                   |
       v                   v
    Qdrant Vector        BM25
       |                   |
       +--------+----------+
                v
               RRF
                |
          Optional Reranker
                |
                v
          Grounded Context
                |
                v
              LLM
                |
                v
       Answer + Citations
                |
                v
             Evaluation

Identity, Tenant, Audit, Cache, Object Storage, and Observability wrap the entire flow.

## Core RAG Capabilities / 核心 RAG 能力

- Document ingestion and lifecycle management
- PDF page / Markdown section metadata
- Hybrid vector + BM25 retrieval
- Reciprocal Rank Fusion and optional CrossEncoder reranking
- Grounded generation with citations
- Retrieval and answer evaluation
- Tenant-scoped knowledge isolation
- S3/MinIO original-document storage
- Audit, cache, and OpenTelemetry observability

## Advanced v0.6 Capabilities / v0.6 進階能力

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

## Advanced Agent Runtime / 進階 Agent Runtime

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
