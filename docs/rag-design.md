# RAG Design

## Document model

Version 0.2 assigns each ingested file a deterministic document ID and stores metadata with
every chunk:

- document ID
- source filename
- content type
- ordinal
- PDF page when available
- Markdown section when available

This metadata is returned with citations and can be used as an exact-match retrieval filter.

## Parsing and chunking

PDF files are parsed page by page. Markdown files are split on headings before the configured
character chunker runs, preserving the section title on every resulting chunk. TXT and CSV
files are represented as single parsed sections before chunking.

The character-based chunker remains intentionally deterministic. Production systems should
benchmark token-aware or semantic chunking against a representative evaluation set.

## Retrieval

Two explicit modes are available:

1. vector — Qdrant semantic retrieval only
2. hybrid — vector retrieval plus BM25 lexical retrieval, Reciprocal Rank Fusion, and an
   optional CrossEncoder reranker

Both modes accept the same metadata filters, making retrieval experiments directly comparable.

## Document lifecycle

Re-ingesting a file with the same deterministic document ID replaces its existing chunks.
Version 0.2 also exposes document listing, delete, batch ingest, and explicit reindex APIs.

## Generation and citations

The LLM boundary is OpenAI-compatible. Retrieved chunks are numbered before generation.
Citations return source, document ID, chunk ID, page and section metadata so a future UI can
link the answer to the original location.
