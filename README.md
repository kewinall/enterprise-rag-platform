# Enterprise RAG Platform

**目前版本 / Current release: v0.2.0**

> **繁體中文**：這是一個以企業使用情境為目標的 Retrieval-Augmented Generation（RAG）參考平台，涵蓋文件匯入、可追溯 Metadata、Vector / Hybrid Retrieval、Optional Reranking、Grounded Generation、文件生命週期 API、Evaluation、Container 化部署、Observability、CI 與 Security Scan。
>
> **English**: A production-oriented Retrieval-Augmented Generation (RAG) reference platform for enterprise use cases, covering document ingestion, traceable metadata, vector/hybrid retrieval, optional reranking, grounded generation, document lifecycle APIs, evaluation, containerized deployment, observability, CI, and security checks.

> **繁體中文**：本 Repository 為 Portfolio / Reference Implementation。所有內含文件皆為 synthetic sample，不包含任何客戶、公司、憑證或內部環境資料。
>
> **English**: This repository is a portfolio/reference implementation. All included documents are synthetic and contain no customer, company, credential, or internal-environment data.

## v0.2 新增內容 / What v0.2 adds

- PDF Page Metadata 與 Markdown Section Metadata / PDF page metadata and Markdown section metadata
- Deterministic Document ID 與 Chunk Lineage / deterministic document IDs and chunk lineage
- Batch Ingestion / batch ingestion
- 文件 List / Delete / Reindex / document list, delete, and reindex operations
- Metadata Filter：document ID、source、content type、page、section
- Vector 與 Hybrid Retrieval Mode / explicit vector and hybrid retrieval modes
- Vector vs Hybrid 的品質與 Latency Benchmark
- 更完整的 Tests 與 Synthetic Evaluation Cases / expanded tests and synthetic evaluation cases

詳見 / See: docs/v0.2.md 與 / and CHANGELOG.md.

## 架構 / Architecture

    Client / UI
        |
        v
      FastAPI
        |
        v
    API Key + Guardrails
        |
        v
      RAG Service
        |
        +--> Qdrant Vector Search
        +--> BM25 Lexical Search
                 |
                 v
             RRF Fusion
                 |
                 v
       Optional CrossEncoder
                 |
                 v
         Context + Metadata
                 |
                 v
      OpenAI-Compatible LLM
                 |
                 v
        Answer + Citations

## 核心能力 / Core capabilities

### 文件匯入與生命週期 / Ingestion and lifecycle

**繁體中文**
- 支援 PDF、Markdown、TXT、CSV。
- chunk_size 與 chunk_overlap 可設定。
- Document ID 與 Chunk ID 採 deterministic 設計。
- PDF 保留 Page Lineage，Markdown 保留 Section Lineage。
- 支援 Single-file 與 Batch Ingestion。
- 相同 Document 重新匯入時會 idempotent replace。
- 提供 List、Delete、Reindex API。

**English**
- Supports PDF, Markdown, TXT, and CSV.
- Configurable chunk size and overlap.
- Deterministic document and chunk IDs.
- PDF page lineage and Markdown section lineage.
- Single-file and batch ingestion.
- Idempotent replacement on re-ingest.
- List, delete, and explicit reindex APIs.

### Retrieval

**繁體中文**
- Qdrant Semantic Vector Retrieval。
- BM25 Lexical Retrieval。
- Reciprocal Rank Fusion（RRF）。
- Optional CrossEncoder Reranking。
- 支援 Vector-only 與 Hybrid Mode。
- 支援 Metadata Exact-match Filter。

**English**
- Qdrant semantic vector retrieval.
- BM25 lexical retrieval.
- Reciprocal Rank Fusion (RRF).
- Optional CrossEncoder reranking.
- Vector-only and hybrid modes.
- Exact-match metadata filters.

### Generation

**繁體中文**
- 以 OpenAI-compatible Chat Completion 介面作為 LLM Boundary。
- Docker 範例預設使用本機 Ollama。
- 可替換為 LiteLLM、vLLM 或其他 OpenAI-compatible Endpoint。
- Citation 包含 Document、Source、Page、Section Lineage。
- 具備基本 Prompt Injection Heuristic。

**English**
- OpenAI-compatible chat-completion boundary.
- Local Ollama example by default.
- Replaceable with LiteLLM, vLLM, or other OpenAI-compatible endpoints.
- Numbered citations with document, source, page, and section lineage.
- Basic prompt-injection heuristic.

### Platform Engineering

- FastAPI
- Docker / Docker Compose
- Prometheus Metrics
- API Key Gate
- Health / Readiness Endpoint
- Ruff + pytest CI
- pip-audit Dependency Scan
- Trivy Filesystem Scan

## Repository 結構 / Repository structure

    .
    ├── app/
    │   ├── api/
    │   ├── core/
    │   ├── evaluation/
    │   ├── ingestion/
    │   ├── rag/
    │   └── retrieval/
    ├── data/
    ├── docs/
    ├── scripts/
    ├── tests/
    ├── .github/workflows/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── pyproject.toml
    └── Makefile

## 快速開始 / Quick start

### 1. 設定 / Configure

    git clone https://github.com/kewinall/enterprise-rag-platform.git
    cd enterprise-rag-platform
    cp .env.example .env

**繁體中文**：對外提供服務前，請先修改 RAG_API_KEY。  
**English**: Change RAG_API_KEY before exposing the service.

### 2. 啟動服務 / Start the stack

    docker compose up -d --build
    docker compose exec ollama ollama pull llama3.2:3b

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Qdrant | http://localhost:6333 |
| Ollama | http://localhost:11434 |
| Metrics | http://localhost:8000/metrics |

### 3. 批次匯入範例文件 / Batch-ingest synthetic sample documents

    curl -X POST "http://localhost:8000/api/v1/ingest/batch" \
      -H "X-API-Key: change-me" \
      -F "files=@data/sample/platform-handbook.md" \
      -F "files=@data/sample/security-handbook.md"

### 4. 查看已建立索引的文件 / List indexed documents

    curl "http://localhost:8000/api/v1/documents" \
      -H "X-API-Key: change-me"

### 5. Metadata Filter + Hybrid Search

    curl -X POST "http://localhost:8000/api/v1/search" \
      -H "Content-Type: application/json" \
      -H "X-API-Key: change-me" \
      -d '{
        "query": "How should administrative access be granted?",
        "top_k": 5,
        "mode": "hybrid",
        "filters": {
          "source": "security-handbook.md",
          "section": "Identity and Access"
        }
      }'

## 文件生命週期 API / Document lifecycle API

| Method | Endpoint | 用途 / Purpose |
|---|---|---|
| POST | /api/v1/ingest | 匯入或取代單一文件 / ingest or replace one file |
| POST | /api/v1/ingest/batch | 批次匯入 / ingest multiple files |
| GET | /api/v1/documents | 查看文件與 Metadata / list indexed documents and metadata |
| DELETE | /api/v1/documents/{document_id} | 刪除全部 Chunks / delete all chunks for a document |
| PUT | /api/v1/documents/{document_id}/reindex | 保留 ID 並重新建立索引 / replace while keeping its ID |
| POST | /api/v1/search | Retrieval only |
| POST | /api/v1/query | RAG Answer + Citations |

## Retrieval Filter

Search / Query 可使用 / can filter by:

- document_id
- source
- content_type
- page
- section

**繁體中文**：多個 Filter 欄位採 AND Semantics。  
**English**: All supplied fields use AND semantics.

## Evaluation 與 Benchmarking

    python scripts/evaluate_retrieval.py \
      --dataset data/eval/retrieval_eval.jsonl \
      --k 5 \
      --mode hybrid

    make benchmark

**繁體中文**：Benchmark 會輸出 Recall@K、MRR 與平均 Retrieval Latency。  
**English**: The benchmark reports Recall@K, MRR, and average retrieval latency.

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
- docs/rag-design.md — RAG 設計 / RAG design
- docs/evaluation.md — 評測 / Evaluation
- docs/v0.2.md — v0.2 功能指南 / feature guide
- docs/security.md — 安全 / Security
- docs/troubleshooting.md — 故障排除 / Troubleshooting
- docs/roadmap.md — Roadmap
- CHANGELOG.md — 版本異動 / Changelog

## 設計原則 / Design principles

1. **Provider-neutral** — Generation 隔離在 OpenAI-compatible Boundary / generation is isolated behind an OpenAI-compatible boundary.
2. **Retrieval-first** — Retrieval 可獨立 Benchmark / retrieval can be benchmarked independently from generation.
3. **Traceable** — 保留 Document、Chunk、Page、Section Lineage / lineage is preserved.
4. **Testable** — 核心 deterministic utility 可 unit test / deterministic utilities are unit-tested.
5. **Local-first** — 預設 Stack 可將文件與 Generation 留在本機 / documents and generation can remain local.
6. **Production-aware** — Security、Lifecycle、Observability、Evaluation 都納入設計 / are part of the design.

## License

MIT License. See LICENSE.
