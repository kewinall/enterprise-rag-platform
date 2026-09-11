# Enterprise RAG Platform

**目前版本：v0.6.0**

> **互動式架構與專案總覽**  
> [GitHub Pages](https://kewinall.github.io/enterprise-rag-platform/) · [Repository HTML](docs/enterprise-rag-platform-guide.html)

這是一套 production-oriented **Knowledge AI Platform**，聚焦企業知識的 governed retrieval、grounded generation、citation、evaluation、multi-tenancy、安全控制與 Agent-ready knowledge access。

## 專案定位

本 Repository 負責 Portfolio 中的 **Knowledge Layer**：

- document ingestion 與 lifecycle management
- parsing、chunking 與 metadata
- Hybrid Retrieval：Vector + BM25
- Reciprocal Rank Fusion（RRF）與 optional reranker
- grounded answer generation 與 citations
- retrieval / answer / agent evaluation
- tenant-scoped knowledge isolation
- audit、cache 與 observability
- advanced agent scenario 的 controlled tool exposure

本專案刻意不負責 model-provider routing、canonical MCP integration platform 或 DataOps remediation logic。

## Knowledge Flow

```text
Documents / Governed Knowledge Package
   |
   v
Parsing / Contract Validation / Chunking
   |
   v
Embedding + Metadata + Provenance
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

Identity、tenant policy、audit、storage、cache 與 observability 會包覆整個流程，而不是只存在 UI 層。

## 核心能力

- Hybrid Retrieval，結合 semantic 與 lexical signals
- optional CrossEncoder-style reranking
- grounded answer generation 與 source citations
- retrieval、answer 與 agent evaluation scripts
- tenant-aware retrieval 與 state boundaries
- PostgreSQL durable session / checkpoint
- governed memory 與 retention controls
- durable async job queue
- token / estimated-cost budget controls
- Redis tenant+subject rate limiting
- Prometheus metrics 與 Grafana dashboard
- adversarial prompt / tool-injection evaluation
- MCP-compatible tool adapter
- Engineering Knowledge Package v1.0 contract validation / ingestion
- source provenance preservation through vector storage and retrieval
- vector / lexical / hybrid engineering knowledge benchmark path
- citation-fidelity regression evidence

## Engineering Knowledge Package Integration

`kewinall/engineering-knowledge-base` 是 canonical engineering Knowledge Source of Truth；本 Repository 作為 consumer，直接消費其 deterministic Knowledge Package，而不複製 source ownership。

```bash
make validate-knowledge-package
make ingest-knowledge-package
make benchmark-knowledge
make evaluate-knowledge-citations
```

完整說明：[`docs/knowledge-package-integration.md`](docs/knowledge-package-integration.md)。

Consumer 會保留：

- `document_id`
- `segment_id`
- `source_path`
- source line range
- content SHA-256
- citation object
- access / quality metadata

Golden retrieval dataset 仍由 Knowledge Base version control；本專案負責 Vector、BM25、Hybrid/RRF、latency 與 citation runtime evidence。

## 關鍵工程決策

| 決策 | 原因 / 效益 | Trade-off |
|---|---|---|
| Hybrid Vector + BM25 + RRF | 同時處理 semantic similarity 與 exact keyword/entity match | Query 與 index complexity 高於 pure vector search |
| Optional reranker | 需要時改善 candidate ordering | 增加 inference latency 與 compute cost |
| Grounding + Citation + Evaluation | 讓品質可被量化，而不是只看文字是否流暢 | 需要維護 evaluation dataset 與 threshold |
| Tenant-scoped retrieval / state | Multi-tenancy 在 retrieval/runtime 層 enforce | Filter 可能降低 recall，cache/index key 也更複雜 |
| Tool allow-list + approval boundary | RAG capability 不等於 mutation authority | Agent integration 的 governance path 更複雜 |
| Source-owned Knowledge Contract | Canonical content 與 expected sources 同步 version control，consumer 只負責 runtime | 跨 repo 需要明確 compatibility contract |

## 失敗語意與復原原則

- retrieval evidence 不足時，明確暴露 insufficient evidence，而不是用流暢文字掩蓋缺口
- cross-tenant access attempt 直接拒絕，不以關閉 filter 換取 recall
- prompt / tool injection 透過 adversarial regression tests 驗證
- rate / budget 超限時在資源持續消耗前拒絕 request
- backend failure 可以 degraded 或 fail，但不可繞過 identity / tenant controls
- Knowledge Package hash、count、source/citation contract 不一致時拒絕 ingestion，不以 best-effort silently repair provenance

## 可驗證 Evidence

| Claim | Repository Evidence |
|---|---|
| Tenant isolation regression | `tests/test_tenancy.py`, `tests/test_roles.py`, `tests/test_filters.py` |
| Prompt / tool injection tests | `tests/test_security.py`, `tests/test_adversarial.py`, `scripts/evaluate_adversarial.py` |
| Retrieval / answer / agent evaluation | `scripts/evaluate_retrieval.py`, `scripts/evaluate_answers.py`, `scripts/evaluate_agent.py`, `data/eval/*.jsonl` |
| Knowledge Package compatibility | `app/ingestion/knowledge_package.py`, `tests/test_knowledge_package.py` |
| Engineering retrieval evidence | `scripts/benchmark_retrieval.py`, `docs/knowledge-package-integration.md` |
| Citation fidelity | `app/evaluation/citation_fidelity.py`, `scripts/evaluate_citation_fidelity.py`, `tests/test_citation_fidelity.py` |
| Budget / rate-limit guardrails | `tests/test_budget.py`, `tests/test_rate_limit.py` |
| Agent approval boundary | `tests/test_agent_approval.py`, `docs/tool-policy.md` |
| CI / Security gate | `.github/workflows/ci.yml`, `.github/workflows/security.yml` |

## 快速開始

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:3b
```

Web UI：`http://localhost:8000/`

## Evaluation

```bash
make benchmark
make evaluate-answers
make evaluate-agent
make evaluate-adversarial
```

Engineering Knowledge evidence：

```bash
make knowledge-evidence
```

## 工程文件

- `docs/architecture.md`
- `docs/security.md`
- `docs/evaluation.md`
- `docs/knowledge-package-integration.md`
- `docs/observability.md`
- `docs/agent-sessions.md`
- `docs/agent-governance.md`
- `docs/tool-policy.md`
- `docs/mcp-adapter.md`
- `docs/troubleshooting.md`
- `docs/installation.md`
- `docs/roadmap.md`
- `CHANGELOG.md`

## Portfolio 責任邊界

- **Enterprise RAG Platform**：knowledge ingestion、retrieval、grounding、citations、evaluation、knowledge governance
- **Engineering Knowledge Base**：canonical engineering knowledge、stable source identity、provenance、Knowledge Package contract、golden retrieval cases
- **Agentic DataOps Copilot**：operational reasoning 與 governed remediation
- **Data Platform MCP Server**：standardized tool / integration boundary
- **Multi-LLM AI Gateway**：model routing、resilience、policy、cost control
- **Enterprise ETL Platform**：ETL modernization、metadata、lineage、runtime lifecycle

## 授權

MIT License，詳見 `LICENSE`。
