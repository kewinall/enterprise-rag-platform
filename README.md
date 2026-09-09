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

## Engineering Decisions & Production Evidence

### Problem

企業 RAG 的真正問題不是「能不能從 Vector DB 找到文字」，而是 **retrieval 是否完整、answer 是否 grounded、citation 是否可信、tenant 是否隔離、prompt/tool injection 是否受控，而且品質是否能量化**。沒有 evaluation 與 governance 的 RAG 很容易成為不可驗證的 demo。

### Key Engineering Decisions & Trade-offs

| Decision | Why / Benefit | Trade-off |
|---|---|---|
| **Hybrid Retrieval：Vector + BM25 + RRF** | 同時處理 semantic similarity 與 exact keyword/entity match，降低單一路徑 blind spot | Query latency、index 維護與 tuning complexity 高於 pure vector search |
| **Optional Reranker** | 在 candidate retrieval 後再提升 relevance ordering | 增加 inference latency / compute cost |
| **Grounded Generation + Citation + Evaluation** | 回答能對應 evidence，品質可以透過 retrieval / answer / agent evaluation 量化 | 需要維護 evaluation dataset 與 threshold，citation 也可能暴露「其實沒有好 evidence」 |
| **Tenant-scoped retrieval / state / rate / budget** | 將 enterprise multi-tenancy 放在 retrieval 與 runtime guardrail，而不是只靠 UI | Tenant filters 可能降低 recall，並增加 cache/index key design complexity |
| **Tool allow-list + approval for destructive action** | Knowledge AI 可以延伸到 Agent，但 destructive action 不因 RAG capability 自動取得 authority | Integration capability 更完整，但 governance path 更複雜 |

### Production Failure & Recovery

| Scenario | Engineering Behavior / Detection | Recovery Strategy |
|---|---|---|
| Retrieval 找不到足夠 evidence | Citation / evaluation 讓 unsupported answer 可被辨識，而不是把 fluency 當 correctness | 調整 query、ingestion、chunking、index 或明確回覆 evidence insufficient |
| Cross-tenant access attempt | Tenant filters / role checks 應拒絕或隔離非本 tenant knowledge | 修正 identity / tenant mapping；不可透過關閉 tenant filter 來「提高 recall」 |
| Prompt / Tool injection | Adversarial evaluation 與 tool policy 用來驗證模型是否被非授權 instruction 誘導 | 更新 policy / prompt / test cases，再通過 adversarial regression |
| Budget / rate limit exceeded | Runtime guardrail 應在資源消耗持續擴張前拒絕 request | 調整 quota / budget 或等待 window reset，不直接 bypass |
| Vector / embedding / state backend unavailable | Request / job 應明確失敗或 degraded，不應繞過 tenant/security governance | 恢復依賴後 retry；必要時依 durable job/session state 繼續 |

### Production Evidence

| Claim | Repository Evidence |
|---|---|
| Tenant isolation 有 regression tests | `tests/test_tenancy.py`, `tests/test_roles.py`, `tests/test_filters.py` |
| Security / prompt-tool injection 有測試 | `tests/test_security.py`, `tests/test_adversarial.py`, `scripts/evaluate_adversarial.py` |
| Retrieval / answer / agent evaluation 可執行 | `scripts/evaluate_retrieval.py`, `scripts/evaluate_answers.py`, `scripts/evaluate_agent.py`, `data/eval/*.jsonl` |
| Budget / rate-limit guardrails 有測試 | `tests/test_budget.py`, `tests/test_rate_limit.py` |
| Agent approval boundary 有測試 | `tests/test_agent_approval.py`, `docs/tool-policy.md` |
| CI / Security gate | `.github/workflows/ci.yml`, `.github/workflows/security.yml` |

### Interview Questions This Project Can Answer

- 為什麼不是只用 Vector Search？
- Reranker 的品質收益是否值得 latency / cost？
- 如何證明 answer 是 grounded，而不是模型自己說「有引用」？
- Multi-tenancy 為什麼可能降低 recall，但仍不能拿掉？
- Prompt injection 要如何從「Prompt 寫得更嚴格」提升到可測試的工程控制？


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
