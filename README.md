# Enterprise RAG Platform

**Current release: v0.2.0**

A production-oriented Retrieval-Augmented Generation reference platform for enterprise use
cases. The project demonstrates document ingestion, traceable metadata, vector and hybrid
retrieval, optional reranking, grounded generation, document lifecycle APIs, evaluation,
containerized local deployment, observability, CI and security checks.

> Portfolio/reference implementation only. All included documents are synthetic and no
> customer, company, credential or internal-environment data is stored in this repository.

## What v0.2 adds

- PDF page metadata and Markdown section metadata
- deterministic document IDs and chunk lineage
- batch ingestion
- document list, delete and reindex operations
- metadata filters for document ID, source, content type, page and section
- explicit vector versus hybrid retrieval modes
- vector-versus-hybrid quality and latency benchmark
- expanded tests and synthetic evaluation cases

See [docs/v0.2.md](docs/v0.2.md) and [CHANGELOG.md](CHANGELOG.md).

## Architecture

~~~mermaid
flowchart LR
    U[Client / UI] --> API[FastAPI]
    API --> SEC[API Key + Guardrails]
    SEC --> RAG[RAG Service]

    RAG --> RET[Retrieval Mode]
    RET --> V[Qdrant Vector Search]
    RET --> B[BM25 Lexical Search]
    V --> F[RRF Fusion]
    B --> F
    F --> RR[Optional CrossEncoder Reranker]

    RR --> CTX[Context + Metadata]
    CTX --> LLM[OpenAI-Compatible LLM]
    LLM --> ANS[Answer + Citations]

    ING[PDF / MD / TXT / CSV] --> PARSE[Page / Section Parser]
    PARSE --> CHUNK[Deterministic Chunking]
    CHUNK --> EMB[Sentence-Transformers]
    EMB --> V

    API --> DOC[Document Lifecycle]
    DOC --> Q[Qdrant]
    API --> MET[Prometheus Metrics]
~~~

## Core capabilities

### Ingestion and lifecycle

- PDF, Markdown, TXT and CSV
- configurable chunk size and overlap
- deterministic document and chunk IDs
- PDF page and Markdown section lineage
- single-file and batch ingestion
- idempotent replacement on re-ingest
- list, delete and explicit reindex APIs

### Retrieval

- Qdrant semantic vector retrieval
- BM25 lexical retrieval
- Reciprocal Rank Fusion
- optional CrossEncoder reranking
- vector-only and hybrid modes
- exact-match metadata filters

### Generation

- OpenAI-compatible chat completion boundary
- local Ollama example
- replaceable by LiteLLM, vLLM, OpenAI-compatible managed endpoints, and similar providers
- numbered citations containing document, source, page and section lineage
- basic prompt-injection heuristic

### Platform engineering

- FastAPI
- Docker and Docker Compose
- Prometheus metrics
- API-key gate
- health and readiness endpoints
- Ruff and pytest CI
- pip-audit dependency scan
- Trivy filesystem scan

## Repository structure

~~~text
.
├── app/
│   ├── api/
│   ├── core/
│   ├── evaluation/
│   ├── ingestion/
│   ├── rag/
│   └── retrieval/
├── data/
│   ├── eval/
│   └── sample/
├── docs/
├── scripts/
├── tests/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── Makefile
~~~

## Quick start

### 1. Configure

    git clone https://github.com/kewinall/enterprise-rag-platform.git
    cd enterprise-rag-platform
    cp .env.example .env

Change RAG_API_KEY before exposing the service.

### 2. Start the stack

    docker compose up -d --build
    docker compose exec ollama ollama pull llama3.2:3b

Default endpoints:

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Qdrant | http://localhost:6333 |
| Ollama | http://localhost:11434 |
| Metrics | http://localhost:8000/metrics |

### 3. Batch-ingest the synthetic sample documents

    curl -X POST "http://localhost:8000/api/v1/ingest/batch"       -H "X-API-Key: change-me"       -F "files=@data/sample/platform-handbook.md"       -F "files=@data/sample/security-handbook.md"

### 4. List indexed documents

    curl "http://localhost:8000/api/v1/documents"       -H "X-API-Key: change-me"

### 5. Run filtered hybrid search

    curl -X POST "http://localhost:8000/api/v1/search"       -H "Content-Type: application/json"       -H "X-API-Key: change-me"       -d '{
        "query": "How should administrative access be granted?",
        "top_k": 5,
        "mode": "hybrid",
        "filters": {
          "source": "security-handbook.md",
          "section": "Identity and Access"
        }
      }'

### 6. Ask a grounded question

    curl -X POST "http://localhost:8000/api/v1/query"       -H "Content-Type: application/json"       -H "X-API-Key: change-me"       -d '{
        "question": "What should happen before a production release?",
        "top_k": 5,
        "mode": "hybrid"
      }'

## Document lifecycle API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/v1/ingest | ingest or replace one file |
| POST | /api/v1/ingest/batch | ingest multiple files |
| GET | /api/v1/documents | list indexed documents and metadata |
| DELETE | /api/v1/documents/{document_id} | delete all chunks for a document |
| PUT | /api/v1/documents/{document_id}/reindex | replace a document while keeping its ID |
| POST | /api/v1/search | retrieval only |
| POST | /api/v1/query | RAG answer with citations |

## Retrieval filters

Search and query requests can filter by:

- document_id
- source
- content_type
- page
- section

All supplied fields are combined using AND semantics in Qdrant and the hybrid lexical corpus.

## Evaluation and benchmarking

Evaluate hybrid retrieval:

    python scripts/evaluate_retrieval.py       --dataset data/eval/retrieval_eval.jsonl       --k 5       --mode hybrid

Compare vector and hybrid retrieval:

    make benchmark

The benchmark reports Recall@K, MRR and average retrieval latency.

## Local development

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env
    make lint
    make test

## Documentation

- [Architecture](docs/architecture.md)
- [Installation](docs/installation.md)
- [RAG design](docs/rag-design.md)
- [Evaluation](docs/evaluation.md)
- [v0.2 feature guide](docs/v0.2.md)
- [Security](docs/security.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Roadmap](docs/roadmap.md)
- [Changelog](CHANGELOG.md)

## Design principles

1. **Provider-neutral** — generation is isolated behind an OpenAI-compatible boundary.
2. **Retrieval-first** — retrieval can be benchmarked independently from generation.
3. **Traceable** — document, chunk, page and section lineage are preserved.
4. **Testable** — core deterministic utilities are unit-tested without a live LLM.
5. **Local-first** — the default stack can keep documents and generation local.
6. **Production-aware** — security, lifecycle, observability and evaluation are part of the design.

## License

MIT License. See [LICENSE](LICENSE).
