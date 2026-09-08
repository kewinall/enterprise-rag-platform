# Enterprise RAG Platform

**目前版本 / Current release: v0.3.0**

> **繁體中文**：這是一個以企業使用情境為目標的 Retrieval-Augmented Generation（RAG）參考平台。v0.3 在原有 Hybrid Retrieval 與 Document Lifecycle 基礎上，加入 Redis Cache、PostgreSQL Audit、OpenTelemetry Tracing、LiteLLM Gateway、RAGAS-style Answer Evaluation 與離線友善的 Web UI。
>
> **English**: A production-oriented Retrieval-Augmented Generation (RAG) reference platform. v0.3 extends the existing hybrid retrieval and document lifecycle foundation with Redis caching, PostgreSQL auditing, OpenTelemetry tracing, a LiteLLM gateway, RAGAS-style answer evaluation, and an offline-friendly Web UI.

> **繁體中文**：本 Repository 為 Portfolio / Reference Implementation。所有內含文件皆為 synthetic sample，不包含任何客戶、公司、憑證或內部環境資料。
>
> **English**: This repository is a portfolio/reference implementation. All included documents are synthetic and contain no customer, company, credential, or internal-environment data.

## v0.3 新增內容 / What v0.3 adds

- RAGAS-style Faithfulness、Answer Relevance、Context Relevance、Optional Answer Correctness
- OpenTelemetry Trace：HTTP Request、Retrieval、RAG、LLM Completion、Evaluation
- PostgreSQL Request Audit Record
- Redis Answer Cache，降低重複 LLM Request 成本
- LiteLLM Gateway，將 RAG API 與 Model Provider 解耦
- Web UI：Batch Upload、Document List、Chat、Citation Inspection
- Docker Compose Runtime：Qdrant、Ollama、LiteLLM、PostgreSQL、Redis、OTel Collector
- Qdrant 更新至 v1.19.0，Ollama 更新至 0.33.3，LiteLLM 使用 v1.100.0

詳見 / See: docs/v0.3.md 與 / and CHANGELOG.md.

## 架構 / Architecture

    Browser / Client
          |
          v
        FastAPI
          |
          +--------------------------+
          |                          |
          v                          v
    Document / RAG API          PostgreSQL Audit
          |
          +------> Redis Answer Cache
          |
          v
    Hybrid Retrieval
      |          |
      v          v
    Qdrant      BM25
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

    FastAPI / Retrieval / LLM / Evaluation
                 |
                 v
          OpenTelemetry OTLP
                 |
                 v
           OTel Collector

## 核心能力 / Core capabilities

### Ingestion 與 Lifecycle / 文件匯入與生命週期

**繁體中文**
- PDF、Markdown、TXT、CSV。
- PDF Page 與 Markdown Section Lineage。
- Deterministic Document / Chunk ID。
- Single / Batch Ingestion。
- List、Delete、Reindex API。
- 相同文件重新 Ingest 會取代舊 Chunks。

**English**
- PDF, Markdown, TXT, and CSV.
- PDF page and Markdown section lineage.
- Deterministic document and chunk IDs.
- Single and batch ingestion.
- List, delete, and reindex APIs.
- Re-ingesting the same document replaces previous chunks.

### Retrieval

- Qdrant Semantic Vector Retrieval
- BM25 Lexical Retrieval
- Reciprocal Rank Fusion
- Optional CrossEncoder Reranking
- Vector / Hybrid Mode
- Metadata Exact-match Filter

### Generation 與 Gateway / Generation and gateway

**繁體中文**
- FastAPI 不直接綁死特定 Model Provider，而是透過 OpenAI-compatible Boundary。
- Docker Stack 預設由 LiteLLM 將 enterprise-rag Model Route 到 Ollama。
- 可將 LiteLLM Config 改成其他 Cloud / Local Provider。

**English**
- FastAPI is not coupled directly to one model provider and uses an OpenAI-compatible boundary.
- The default Docker stack routes the enterprise-rag model through LiteLLM to Ollama.
- LiteLLM configuration can be changed to other cloud or local providers.

### Cache 與 Audit / Cache and audit

**繁體中文**
- Redis 以 Question、Top-K、Mode、Filter、Model 組成 deterministic Cache Key。
- PostgreSQL Audit 僅記錄 Request Metadata，不預設保存 Query Body 或文件內容。

**English**
- Redis uses question, top-k, mode, filters, and model to build a deterministic cache key.
- PostgreSQL auditing records request metadata without storing query bodies or document content by default.

### Observability

- OpenTelemetry SDK
- OTLP HTTP Export
- Request / Retrieval / LLM / Evaluation Span
- Prometheus Metrics Endpoint
- OTel Collector Debug Exporter Example

### RAGAS-style Evaluation

**繁體中文**
內建 LLM-as-a-Judge 評測器，不強制依賴特定 Evaluation Framework；Metrics 概念對齊常見 RAGAS 指標。

**English**
The built-in LLM-as-a-Judge evaluator does not hard-depend on a specific evaluation framework; its metrics are aligned with common RAGAS-style concepts.

Metrics:
- Faithfulness
- Answer Relevance
- Context Relevance
- Answer Correctness（有 Reference 時 / when a reference is provided）

## 快速開始 / Quick start

### 1. 設定 / Configure

    git clone https://github.com/kewinall/enterprise-rag-platform.git
    cd enterprise-rag-platform
    cp .env.example .env

**繁體中文**：正式或共用環境請務必修改 RAG_API_KEY、LITELLM_MASTER_KEY、POSTGRES_PASSWORD。  
**English**: Change RAG_API_KEY, LITELLM_MASTER_KEY, and POSTGRES_PASSWORD for shared or production environments.

### 2. 啟動完整 Stack / Start the full stack

    docker compose up -d --build

### 3. 準備 Local Model / Pull the local model

    docker compose exec ollama ollama pull llama3.2:3b

### 4. 開啟 Web UI / Open the Web UI

Browser:

    http://localhost:8000/

### Runtime Services

| Service | URL / Port | 用途 / Purpose |
|---|---|---|
| FastAPI / Web UI | http://localhost:8000 | RAG API + UI |
| Swagger UI | http://localhost:8000/docs | API Docs |
| LiteLLM | http://localhost:4000 | LLM Gateway |
| Qdrant | http://localhost:6333 | Vector DB |
| Ollama | http://localhost:11434 | Local LLM |
| PostgreSQL | localhost:5432 | Audit Store |
| Redis | localhost:6379 | Answer Cache |
| OTel OTLP HTTP | localhost:4318 | Trace Receiver |
| Prometheus | http://localhost:8000/metrics | Metrics |

## API

| Method | Endpoint | 用途 / Purpose |
|---|---|---|
| POST | /api/v1/ingest | 單檔匯入 / ingest one document |
| POST | /api/v1/ingest/batch | 批次匯入 / batch ingestion |
| GET | /api/v1/documents | 文件清單 / list indexed documents |
| DELETE | /api/v1/documents/{document_id} | 刪除文件 / delete document |
| PUT | /api/v1/documents/{document_id}/reindex | 重建索引 / reindex document |
| POST | /api/v1/search | Retrieval only |
| POST | /api/v1/query | RAG answer + citations + cache state |
| POST | /api/v1/evaluate/answer | RAGAS-style answer evaluation |

## Evaluation

Retrieval Benchmark:

    make benchmark

RAGAS-style Answer Evaluation:

    make evaluate-answers

**繁體中文**：Answer Evaluation 需要已啟動的 Vector DB 與 LLM Gateway，並先匯入 Sample Documents。  
**English**: Answer evaluation requires a running vector database and LLM gateway and assumes the sample documents have already been ingested.

## 本機開發 / Local development

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env
    make lint
    make test

## 文件 / Documentation

- docs/architecture.md — 架構 / Architecture
- docs/installation.md — 安裝 / Installation
- docs/rag-design.md — RAG Design
- docs/evaluation.md — Evaluation
- docs/observability.md — OpenTelemetry
- docs/audit-cache.md — PostgreSQL Audit + Redis Cache
- docs/litellm.md — LiteLLM Gateway
- docs/v0.2.md — v0.2 Feature Guide
- docs/v0.3.md — v0.3 Feature Guide
- docs/security.md — Security
- docs/troubleshooting.md — Troubleshooting
- docs/roadmap.md — Roadmap
- CHANGELOG.md — Changelog

## 設計原則 / Design principles

1. **Provider-neutral** — Model access is isolated behind an OpenAI-compatible gateway.
2. **Retrieval-first** — Retrieval can be tested independently from generation.
3. **Traceable** — Document and runtime lineage are explicit.
4. **Observable** — Metrics, traces, audit records, and request IDs are first-class features.
5. **Cost-aware** — Redis avoids repeated generation for identical requests.
6. **Local-first** — The default stack can run without sending documents to an external LLM.
7. **Production-aware** — Security, lifecycle, audit, cache, and evaluation are part of the design.

## License

MIT License. See LICENSE.
