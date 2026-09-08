# 故障排除 / Troubleshooting

## API 顯示 Not Ready / API is not ready

**繁體中文**：先確認 Qdrant 是否可連線。  
**English**: Check Qdrant connectivity first.

    curl http://localhost:6333/collections

## LLM Request 失敗 / LLM request fails

**繁體中文**：確認 Ollama Model 是否存在。  
**English**: Verify that the configured Ollama model exists.

    docker compose exec ollama ollama list

若尚未下載 / Pull it if necessary:

    docker compose exec ollama ollama pull llama3.2:3b

## 第一次 Request 很慢 / Slow first request

**繁體中文**  
Sentence-Transformer Model 採 Lazy Load，第一次執行可能需要下載 Model。若是 Offline Environment，請預先準備 Model Artifact，並固定到 Image 或 Mounted Model Cache。

**English**  
Sentence-transformer models are loaded lazily and may need to be downloaded on first use. For offline environments, pre-stage model artifacts and pin them in the image or mounted model cache.
