# 版本異動紀錄 / Changelog

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
