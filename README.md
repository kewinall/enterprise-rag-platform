# Enterprise RAG Platform

**目前版本 / Current release: v0.5.0**

> **繁體中文**：Enterprise RAG Platform 是一個以企業落地為目標的 RAG / Agentic AI Reference Project。v0.5 在 v0.4 的 OIDC/RBAC、Multi-tenancy、Object Storage、Audit、Cache、Observability、Kubernetes 與 Offline Delivery 基礎上，加入 Query Planning、Query Rewrite、Multi-hop Retrieval、Corrective Retrieval、Tool Calling、Context/Answer Critic、Human Approval Gate 與 Agent Evaluation。
>
> **English**: Enterprise RAG Platform is a production-oriented RAG / Agentic AI reference project. v0.5 extends the v0.4 identity, multi-tenancy, object storage, audit, cache, observability, Kubernetes, and offline-delivery foundation with query planning, query rewrite, multi-hop retrieval, corrective retrieval, tool calling, context/answer critics, human approval gates, and agent evaluation.

> **繁體中文**：本 Repository 僅使用 synthetic sample，不包含客戶、公司、真實 Credential 或內部環境資料。
>
> **English**: This repository uses synthetic samples only and contains no customer, company, real credential, or internal-environment data.

## v0.5 重點 / v0.5 Highlights

- Agentic RAG Orchestrator
- Query Planning / Rewrite
- Multi-hop Retrieval
- Corrective Retrieval
- Context Sufficiency Critic
- Answer Critic + Optional Revision
- Tool Calling
- Tool Permission Policy
- Human Approval Gate for destructive tools
- Redis-backed Approval TTL
- Agent Trace
- Agent Evaluation
- Standard RAG / Agentic RAG Web UI switch
- Helm / Offline bundle version advanced to 0.5.0

詳見 / See: docs/v0.5.md, docs/agentic-rag.md, docs/tool-policy.md.

## Agentic RAG Flow / Agentic RAG 流程

    User Question
         |
         v
    Query Planner
         |
         +--> Rewrite
         +--> Tool Calls
         +--> Subqueries
         |
         v
    Permission Policy
         |
         +--> Read-only Tool --------+
         |                           |
         +--> Destructive Tool       |
                 |                   |
                 v                   |
          Human Approval Gate        |
                 |                   |
                 +-------------------+
                         |
                         v
                 Multi-hop Retrieval
                         |
                         v
                   Context Critic
                    /          \
             sufficient      insufficient
                 |               |
                 |               v
                 |       Corrective Retrieval
                 |               |
                 +-------+-------+
                         |
                         v
                    Generation
                         |
                         v
                    Answer Critic
                    /          \
                  pass        revise
                    |           |
                    +-----+-----+
                          |
                          v
                 Answer + Citations
                 + Agent Trace

## Tool Policy

| Tool | Role | Approval |
|---|---|---|
| search_knowledge | viewer | No |
| list_documents | viewer | No |
| get_document_metadata | viewer | No |
| delete_document | admin | **Required** |

**繁體中文**：模型只能提出 Tool Call；真正執行仍受 Server-side Role、Tenant 與 Approval Policy 控制。  
**English**: The model may propose tool calls, but execution remains controlled by server-side role, tenant, and approval policies.

## Human Approval

Agent 若提出 delete_document：

    Agent
      |
      v
    Approval Request
      |
      v
    Redis TTL
      |
      +--> Reject
      |
      +--> Admin Approve
              |
              v
       Re-check Tenant/Role
              |
              v
          Execute Tool

## 快速開始 / Quick start

    git clone https://github.com/kewinall/enterprise-rag-platform.git
    cd enterprise-rag-platform
    cp .env.example .env
    docker compose up -d --build
    docker compose exec ollama ollama pull llama3.2:3b

Web UI:

    http://localhost:8000/

Web UI 可切換 / supports:

- Standard RAG
- Agentic RAG
- Agent Trace
- Human Approval / Reject

## Agent Configuration

    AGENT_ENABLED=true
    AGENT_MAX_STEPS=10
    AGENT_MAX_SUBQUERIES=3
    AGENT_MAX_TOOL_CALLS=6
    AGENT_APPROVAL_TTL_SECONDS=600
    AGENT_ENABLE_ANSWER_REVISION=true

## Agent API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/v1/agent/tools | Tool policy / permission view |
| POST | /api/v1/agent/query | Agentic RAG query |
| GET | /api/v1/agent/approvals/{action_id} | Pending approval |
| POST | /api/v1/agent/approvals/{action_id}/approve | Approve and execute |
| POST | /api/v1/agent/approvals/{action_id}/reject | Reject action |
| POST | /api/v1/agent/evaluate | Evaluate an agent result |

Existing RAG / Document APIs remain available.

## Evaluation

Retrieval:

    make benchmark

RAG Answer:

    make evaluate-answers

Agent:

    make evaluate-agent

Agent evaluation includes:

- Expected Tool Recall
- Approval Safety
- Groundedness
- Relevance
- Expected Status Match

## Enterprise Controls retained from v0.4

- OIDC / JWT Validation
- Viewer / Editor / Admin RBAC
- Server-enforced Multi-tenancy
- MinIO / S3
- PostgreSQL Audit
- Redis Cache + Tenant Revision
- OpenTelemetry
- LiteLLM
- Kubernetes / Helm
- NetworkPolicy / HPA / PDB
- External Secrets Example
- Air-Gapped Bundle
- pip-audit / Trivy / CI

## 文件 / Documentation

- docs/agentic-rag.md — Agentic RAG
- docs/tool-policy.md — Tool Permission / Approval Policy
- docs/v0.5.md — v0.5 Feature Guide
- docs/architecture.md — Architecture
- docs/evaluation.md — Evaluation
- docs/security.md — Security
- docs/troubleshooting.md — Troubleshooting
- docs/installation.md — Installation
- docs/auth-tenancy.md — OIDC / RBAC / Multi-tenancy
- docs/object-storage.md — MinIO / S3
- docs/kubernetes.md — Kubernetes / Helm
- docs/offline-deployment.md — Air-Gapped Deployment
- docs/observability.md — OpenTelemetry
- docs/roadmap.md — Roadmap
- CHANGELOG.md — Changelog

## License

MIT License. See LICENSE.
