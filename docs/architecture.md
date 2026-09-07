# Architecture

The platform separates ingestion, retrieval, generation and operational concerns so each layer can be tested and replaced independently.

## Runtime flow

1. A client calls the FastAPI endpoint.
2. API-key validation and basic prompt-injection screening run first.
3. The retriever searches Qdrant using sentence-transformer embeddings.
4. Retrieved chunks are converted into numbered context blocks.
5. An OpenAI-compatible LLM generates a grounded answer.
6. The API returns the answer with chunk/source lineage.

## Extension points

The reference implementation intentionally keeps clean boundaries for:
- hybrid BM25 + vector retrieval
- reranking
- metadata filters
- tenant isolation
- PostgreSQL/pgvector
- S3/MinIO document storage
- LiteLLM model routing
- OpenTelemetry tracing
- production IAM and secrets

## Production topology

For production, run the API, vector database, object storage, telemetry and model gateway as separately managed services. Place the API behind enterprise identity-aware access control and a reverse proxy/API gateway.
