# RAG Design

## Chunking

The default character-based chunker is intentionally simple and deterministic. Production systems should benchmark semantic, sentence, section-aware and token-aware chunking strategies against a representative evaluation set.

## Retrieval

The MVP implements vector retrieval directly. The repository also includes BM25 and RRF utilities to make hybrid retrieval easy to extend. A production benchmark should compare:
- vector-only
- BM25-only
- hybrid + RRF
- hybrid + reranker

## Generation

The LLM boundary is OpenAI-compatible. This permits local Ollama/vLLM, LiteLLM gateways, managed OpenAI-compatible services and other providers without changing the API layer.

## Citations

Retrieved chunks are numbered before generation, and chunk/source identifiers are returned separately. A production UI should make citations clickable and preserve document/page metadata.
