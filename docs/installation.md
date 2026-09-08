# 安裝 / Installation

## Docker Compose

1. **繁中**：複製 .env.example 為 .env。  
   **English**: Copy .env.example to .env.
2. **繁中**：修改 RAG_API_KEY。  
   **English**: Change RAG_API_KEY.
3. **繁中**：啟動 Stack。  
   **English**: Start the stack.

       docker compose up -d --build

4. **繁中**：下載設定的 Ollama Model。  
   **English**: Pull the configured Ollama model.

       docker compose exec ollama ollama pull llama3.2:3b

5. **繁中**：匯入 Sample Content 後測試 /api/v1/query。  
   **English**: Ingest sample content and test /api/v1/query.

## Native Python / 原生 Python

**繁體中文**：建議使用 Python 3.11+。  
**English**: Python 3.11+ is recommended.

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    uvicorn app.main:app --reload

**繁體中文**  
Native Python Mode 仍需要可連線的 Qdrant 與 OpenAI-compatible LLM Endpoint。

**English**  
A reachable Qdrant and OpenAI-compatible LLM endpoint are still required.
