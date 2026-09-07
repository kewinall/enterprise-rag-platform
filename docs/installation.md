# Installation

## Docker Compose

1. Copy `.env.example` to `.env`.
2. Change `RAG_API_KEY`.
3. Run `docker compose up -d --build`.
4. Pull the configured Ollama model.
5. Ingest sample content and test `/api/v1/query`.

## Native Python

Python 3.11+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

A reachable Qdrant and OpenAI-compatible LLM endpoint are required.
