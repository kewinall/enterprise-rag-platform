# Enterprise RAG Platform

**Current release: v0.6.0**

> **Interactive architecture & project overview**  
> [Live GitHub Pages](https://kewinall.github.io/enterprise-rag-platform/) · [Repository HTML](docs/enterprise-rag-platform-guide.html)

Production-oriented **Knowledge AI Platform** for governed enterprise retrieval, grounded generation, citations, evaluation, multi-tenancy, security controls, and agent-ready knowledge access.

## Engineering Scope

This repository owns the portfolio's **knowledge layer**:

- document ingestion and lifecycle management
- parsing, chunking and metadata
- hybrid vector + BM25 retrieval
- Reciprocal Rank Fusion and optional reranking
- grounded answer generation with citations
- retrieval / answer / agent evaluation
- tenant-scoped knowledge isolation
- audit, cache and observability
- controlled tool exposure for advanced agent scenarios

It intentionally does not own model-provider routing, the canonical MCP integration platform, or DataOps remediation logic.

## Knowledge Flow

```text
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
Vector Search         BM25
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
```

Identity, tenant policy, audit, storage, cache and observability wrap the entire flow.

## Core Capabilities

- hybrid retrieval with semantic and lexical signals
- optional CrossEncoder-style reranking
- grounded answer generation and source citations
- retrieval, answer and agent evaluation scripts
- tenant-aware retrieval and state boundaries
- PostgreSQL durable session/checkpoint support
- governed memory with retention controls
- durable async job queue
- token / estimated-cost budget controls
- Redis tenant+subject rate limiting
- Prometheus metrics and Grafana dashboard
- adversarial prompt/tool-injection evaluation
- MCP-compatible tool adapter for advanced integrations

## Key Engineering Decisions

| Decision | Rationale | Trade-off |
|---|---|---|
| Hybrid Vector + BM25 + RRF | Combines semantic similarity with exact keyword/entity matching | Higher query and index complexity than pure vector search |
| Optional reranker | Improves candidate ordering when needed | Adds inference latency and compute cost |
| Grounding + citation + evaluation | Quality can be measured instead of inferred from fluent output | Requires maintained evaluation datasets and thresholds |
| Tenant-scoped retrieval/state | Multi-tenancy is enforced below the UI layer | Filters can reduce recall and complicate cache/index design |
| Tool allow-list + approval boundary | RAG capability does not imply mutation authority | More governance logic for agent integrations |

## Failure Semantics

- insufficient evidence is surfaced rather than hidden behind fluent generation
- cross-tenant access attempts are rejected rather than resolved by disabling filters
- prompt/tool injection is covered by adversarial regression tests
- rate/budget overrun is rejected before uncontrolled resource consumption
- backend failures degrade or fail explicitly without bypassing identity or tenant controls

## Production Evidence

| Claim | Repository Evidence |
|---|---|
| Tenant isolation regression | `tests/test_tenancy.py`, `tests/test_roles.py`, `tests/test_filters.py` |
| Prompt/tool injection tests | `tests/test_security.py`, `tests/test_adversarial.py`, `scripts/evaluate_adversarial.py` |
| Retrieval / answer / agent evaluation | `scripts/evaluate_retrieval.py`, `scripts/evaluate_answers.py`, `scripts/evaluate_agent.py`, `data/eval/*.jsonl` |
| Budget / rate-limit guardrails | `tests/test_budget.py`, `tests/test_rate_limit.py` |
| Agent approval boundary | `tests/test_agent_approval.py`, `docs/tool-policy.md` |
| CI / Security gate | `.github/workflows/ci.yml`, `.github/workflows/security.yml` |

## Quick Start

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:3b
```

Web UI: `http://localhost:8000/`

## Evaluation

```bash
make benchmark
make evaluate-answers
make evaluate-agent
make evaluate-adversarial
```

## Documentation

- `docs/architecture.md`
- `docs/security.md`
- `docs/evaluation.md`
- `docs/observability.md`
- `docs/agent-sessions.md`
- `docs/agent-governance.md`
- `docs/tool-policy.md`
- `docs/mcp-adapter.md`
- `docs/troubleshooting.md`
- `docs/installation.md`
- `docs/roadmap.md`
- `CHANGELOG.md`

## Portfolio Boundary

- **Enterprise RAG Platform:** knowledge ingestion, retrieval, grounding, citations, evaluation, knowledge governance
- **Agentic DataOps Copilot:** operational reasoning and governed remediation
- **Data Platform MCP Server:** standardized tool / integration boundary
- **Multi-LLM AI Gateway:** model routing, resilience, policy and cost control
- **Enterprise ETL Platform:** ETL modernization, metadata, lineage and runtime lifecycle

## License

MIT License. See `LICENSE`.
