# 安裝 / Installation

## Docker Compose — 建議方式 / Recommended

1. 複製設定 / Copy configuration:

       cp .env.example .env

2. **繁中**：至少修改 RAG_API_KEY、LITELLM_MASTER_KEY、POSTGRES_PASSWORD。  
   **English**: At minimum, change RAG_API_KEY, LITELLM_MASTER_KEY, and POSTGRES_PASSWORD.

3. 啟動完整 Stack / Start the full stack:

       docker compose up -d --build

4. 下載 Ollama Model / Pull the Ollama model:

       docker compose exec ollama ollama pull llama3.2:3b

5. 開啟 Web UI / Open the Web UI:

       http://localhost:8000/

## Runtime Services

| Service | Default | 用途 / Purpose |
|---|---|---|
| FastAPI | 8000 | API + Web UI |
| Qdrant | 6333 / 6334 | Vector DB |
| Ollama | 11434 | Local LLM Runtime |
| LiteLLM | 4000 | Model Gateway |
| PostgreSQL | 5432 | Audit Store |
| Redis | 6379 | RAG Answer Cache |
| OTel Collector | 4317 / 4318 | Trace Receiver |

## Native Python / 原生 Python

**繁體中文**  
Python 3.11+ 可直接啟動 API，但需要自行提供 Qdrant、LLM Endpoint。若 CACHE_ENABLED 或 AUDIT_ENABLED 為 true，還需要 Redis / PostgreSQL。若 OTEL_ENABLED 為 true，可設定 OTLP Endpoint；未設定時會使用 Console Exporter。

**English**  
Python 3.11+ can run the API directly, but you must provide Qdrant and an LLM endpoint. Redis/PostgreSQL are also needed when cache/audit are enabled. When tracing is enabled without an OTLP endpoint, the console exporter is used.

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env
    uvicorn app.main:app --reload

## Direct Ollama Mode / 不使用 LiteLLM

**繁體中文**  
若只想直接連 Ollama，可將 LLM_BASE_URL 改為 http://localhost:11434/v1、LLM_API_KEY 設為 ollama、LLM_MODEL 改為實際 Ollama Model Name。

**English**  
To bypass LiteLLM, point LLM_BASE_URL to http://localhost:11434/v1, use ollama as the API key, and set LLM_MODEL to the actual Ollama model name.
