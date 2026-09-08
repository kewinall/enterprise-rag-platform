# Changelog

## 0.2.0 - 2026-09-08

### Added

- PDF page metadata and Markdown heading metadata
- deterministic document IDs
- batch ingestion API
- document list, delete and reindex APIs
- metadata filters for document ID, source, content type, page and section
- explicit vector and hybrid retrieval modes
- retrieval benchmark comparing Recall@K, MRR and average latency
- second synthetic handbook and broader evaluation dataset
- unit tests for metadata parsing, filtering and evaluation metrics

### Changed

- search endpoint now supports the same hybrid pipeline used by RAG queries
- citations now include document ID, page and section metadata
- re-ingesting the same document replaces its previous chunks
- application version advanced to 0.2.0

## 0.1.0 - 2026-09-08

- initial FastAPI RAG platform
- Qdrant vector retrieval
- BM25 and Reciprocal Rank Fusion
- optional CrossEncoder reranking
- local Ollama example
- CI, pip-audit and Trivy security workflows
