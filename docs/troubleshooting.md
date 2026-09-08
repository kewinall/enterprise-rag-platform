# 故障排除 / Troubleshooting

## API Not Ready

確認 Dependency State / Check dependency state:

    curl http://localhost:8000/ready

Qdrant:

    curl http://localhost:6333/collections

## LiteLLM / LLM Request 失敗

確認 LiteLLM Container / Check LiteLLM:

    docker compose logs litellm

確認 Ollama Model / Check Ollama model:

    docker compose exec ollama ollama list

若不存在 / Pull if missing:

    docker compose exec ollama ollama pull llama3.2:3b

## Redis 顯示 degraded / Redis degraded

    docker compose exec redis redis-cli ping

預期 / Expected:

    PONG

## PostgreSQL Audit 顯示 degraded / PostgreSQL audit degraded

    docker compose exec postgres pg_isready -U rag -d rag

查看 Audit Table / Inspect audit rows:

    docker compose exec postgres psql -U rag -d rag       -c "select id,event_time,method,path,status_code,duration_ms from rag_audit_event order by id desc limit 10;"

## Trace 沒有輸出 / No trace output

檢查 Collector / Check collector:

    docker compose logs otel-collector

確認 .env:

    OTEL_ENABLED=true
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://otel-collector:4318/v1/traces

## Cache 不生效 / Cache not working

**繁體中文**  
相同 Question、Top-K、Mode、Filter、Model 才會命中相同 Cache Key。Response 的 cache.hit 可確認是否 Hit。

**English**  
The question, top-k, mode, filters, and model must match to hit the same cache key. Check cache.hit in the query response.

## 第一次 Request 很慢 / Slow first request

**繁體中文**  
Sentence-Transformer Model 採 Lazy Load，第一次執行可能下載 Model。Offline Environment 應預先準備 Model Artifact。

**English**  
Sentence-transformer models are loaded lazily and may be downloaded on first use. Pre-stage model artifacts in offline environments.
