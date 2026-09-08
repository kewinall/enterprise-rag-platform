# 版本異動紀錄 / Changelog

## 0.3.0 - 2026-09-08

### 新增 / Added

- RAGAS-style LLM-as-a-Judge Answer Evaluation
- Faithfulness、Answer Relevance、Context Relevance、Optional Answer Correctness
- OpenTelemetry Manual Instrumentation 與 OTLP HTTP Export
- Request、Retrieval、RAG、LLM、Evaluation Traces
- PostgreSQL Request Audit Store
- Redis RAG Answer Cache
- LiteLLM Gateway Example
- Offline-friendly Web UI：Upload、Document List、Chat、Citation
- Answer Evaluation CLI 與 Synthetic Reference Dataset
- v0.3 Bilingual Documentation

### 變更 / Changed

- Application Version 更新至 / advanced to 0.3.0
- Docker Stack 新增 PostgreSQL、Redis、LiteLLM、OTel Collector
- Default LLM Route 改由 LiteLLM Gateway 進入 Ollama
- Qdrant Container 更新為 / updated to v1.19.0
- Ollama Container 更新為 / updated to 0.33.3
- Query Response 新增 Cache Hit / Miss 狀態
- Readiness Response 新增 Redis / PostgreSQL Dependency State

## 0.2.0 - 2026-09-08

### 新增 / Added

- PDF Page Metadata 與 Markdown Heading Metadata / PDF page metadata and Markdown heading metadata
- Deterministic Document ID / deterministic document IDs
- Batch Ingestion API
- 文件 List、Delete、Reindex API / document list, delete, and reindex APIs
- Metadata Filter：Document ID、Source、Content Type、Page、Section
- Vector 與 Hybrid Retrieval Mode / explicit vector and hybrid retrieval modes
- Retrieval Benchmark：Recall@K、MRR、Average Latency
- 第二份 Synthetic Handbook 與更完整 Evaluation Dataset / second synthetic handbook and broader evaluation dataset
- Metadata Parsing、Filtering、Evaluation Metric Unit Tests

### 變更 / Changed

- Search Endpoint 改用與 RAG Query 相同的 Hybrid Pipeline / search endpoint now supports the same hybrid pipeline used by RAG queries
- Citation 新增 Document ID、Page、Section Metadata / citations now include document ID, page, and section metadata
- 相同文件重新匯入時會取代舊 Chunks / re-ingesting the same document replaces previous chunks
- Application Version 更新至 / advanced to 0.2.0

## 0.1.0 - 2026-09-08

- 初始 FastAPI RAG Platform / initial FastAPI RAG platform
- Qdrant Vector Retrieval
- BM25 + Reciprocal Rank Fusion
- Optional CrossEncoder Reranking
- Local Ollama Example
- CI、pip-audit、Trivy Security Workflow
