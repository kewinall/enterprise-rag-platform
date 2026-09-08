# RAG 設計 / RAG Design

## Document Model / 文件模型

**繁體中文**  
v0.4 每個 Chunk 會保存 document_id、tenant_id、source、object_key、content_type、ordinal、PDF page（若有）與 Markdown section（若有）。Document ID 由 tenant + source deterministic 產生。

**English**  
v0.4 stores document_id, tenant_id, source, object_key, content_type, ordinal, PDF page when available, and Markdown section when available with every chunk. Document IDs are deterministically derived from tenant plus source.

## Parsing 與 Chunking / Parsing and chunking

**繁體中文**  
PDF 逐頁解析；Markdown 先依 Heading 切 Section，再套用 Character Chunker。TXT 與 CSV 會先視為單一 Parsed Section。Chunk ID 也納入 tenant_id，因此不同 Tenant 的 Chunk Identity 不會衝突。

**English**  
PDF files are parsed page by page. Markdown files are split on headings before character chunking. TXT and CSV files are treated as single parsed sections. Chunk IDs also include tenant_id, preventing identity collisions across tenants.

## Retrieval

1. **vector**
   - 繁中：Qdrant Semantic Retrieval。
   - English: Qdrant semantic retrieval.
2. **hybrid**
   - 繁中：Vector + BM25 → Reciprocal Rank Fusion → Optional CrossEncoder Reranker。
   - English: vector plus BM25, Reciprocal Rank Fusion, and an optional CrossEncoder reranker.

**繁體中文**  
Server 會強制在所有 Retrieval Filter 加入 tenant_id。Client 可指定 document_id、source、content_type、page、section，但不能指定 tenant_id。

**English**  
The server enforces tenant_id on all retrieval filters. Clients may filter by document_id, source, content_type, page, and section, but cannot specify tenant_id.

## Original Document Storage / 原始文件

**繁體中文**  
Ingest 時原始文件會保存到 MinIO / S3-compatible Storage，Object Key 採 tenant_id/document_id/filename。Qdrant Payload 保存 object_key 以建立 Citation 與 Original Document 的連結。

**English**  
Original documents are stored in MinIO/S3-compatible storage during ingestion using tenant_id/document_id/filename object keys. Qdrant payloads retain object_key to connect citations with original documents.

## Document Lifecycle / 文件生命週期

- Ingest / Re-ingest
- Batch Ingest
- List
- Reindex
- Delete
- Presigned Download

所有操作皆 Tenant-scoped。  
All operations are tenant-scoped.

## Cache Consistency / Cache 一致性

Ingest、Reindex、Delete 會 bump Tenant Revision，讓舊 RAG Answer Cache 自動失效。  
Ingest, reindex, and delete bump the tenant revision so stale RAG answer caches stop matching.

## Generation 與 Citation / Generation and citations

**繁體中文**  
LLM Boundary 採 OpenAI-compatible API，預設透過 LiteLLM。Citation 回傳 Source、Document ID、Chunk ID、Page、Section；原始文件可透過受 RBAC / Tenant 保護的 Download API 取得 Presigned URL。

**English**  
The LLM boundary uses an OpenAI-compatible API, routed through LiteLLM by default. Citations return source, document ID, chunk ID, page, and section metadata; original documents are available through an RBAC- and tenant-protected download API that issues presigned URLs.
