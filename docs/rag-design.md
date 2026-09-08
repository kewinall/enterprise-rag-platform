# RAG 設計 / RAG Design

## Document Model / 文件模型

**繁體中文**  
v0.2 會為每份文件建立 deterministic document_id。每個 Chunk 會保存 document ID、source filename、content type、ordinal、PDF page（若有）與 Markdown section（若有）。這些 Metadata 會出現在 Search Result 與 Citation，也可直接作為 Exact-match Retrieval Filter。

**English**  
Version 0.2 assigns each ingested file a deterministic document ID. Every chunk stores the document ID, source filename, content type, ordinal, PDF page when available, and Markdown section when available. The same metadata is returned in search results and citations and can be used as an exact-match retrieval filter.

## Parsing 與 Chunking / Parsing and chunking

**繁體中文**  
PDF 逐頁解析；Markdown 先依 Heading 切 Section，再套用可設定的 Character Chunker。TXT 與 CSV 會先視為單一 Parsed Section。Chunker 刻意保持 deterministic，方便重現與測試。

**English**  
PDF files are parsed page by page. Markdown files are split on headings before the configured character chunker runs. TXT and CSV files are represented as single parsed sections. The chunker remains deterministic for reproducibility and testing.

**繁體中文**：正式環境仍應使用 Representative Evaluation Set 比較 Token-aware、Semantic 或其他 Chunking Strategy。  
**English**: Production systems should benchmark token-aware, semantic, or other chunking strategies against a representative evaluation set.

## Retrieval

1. **vector**
   - 繁中：只使用 Qdrant Semantic Retrieval。
   - English: Qdrant semantic retrieval only.
2. **hybrid**
   - 繁中：Vector + BM25 → Reciprocal Rank Fusion → Optional CrossEncoder Reranker。
   - English: vector retrieval plus BM25, Reciprocal Rank Fusion, and an optional CrossEncoder reranker.

**繁體中文**：兩種 Mode 共用 Metadata Filter，方便直接比較 Retrieval Quality。  
**English**: Both modes accept the same metadata filters, making retrieval experiments directly comparable.

## Document Lifecycle / 文件生命週期

**繁體中文**  
相同 deterministic Document ID 重新 Ingest 時會先刪除舊 Chunks，再寫入新 Chunks。另提供 Document List、Delete、Batch Ingest、Reindex API。

**English**  
Re-ingesting a file with the same deterministic document ID replaces existing chunks. Document listing, delete, batch-ingest, and explicit reindex APIs are also provided.

## Generation 與 Citation / Generation and citations

**繁體中文**  
LLM Boundary 採 OpenAI-compatible API。Retrieved Chunks 在 Generation 前會編號，Citation 回傳 Source、Document ID、Chunk ID、Page、Section，讓 UI 可連回原始位置。

**English**  
The LLM boundary is OpenAI-compatible. Retrieved chunks are numbered before generation. Citations return source, document ID, chunk ID, page, and section metadata so a UI can link answers to the original location.
