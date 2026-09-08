# 架構 / Architecture

## v0.3 架構概念 / v0.3 architecture concept

**繁體中文**  
平台將 Data Plane、Model Gateway、State Store 與 Observability 分離。FastAPI 負責 API 與 Orchestration；Qdrant / BM25 負責 Retrieval；LiteLLM 隔離 Model Provider；Redis 降低重複 Generation；PostgreSQL 保存 Request Audit；OpenTelemetry 將 Runtime Trace 送往 Collector。

**English**  
The platform separates the data plane, model gateway, state stores, and observability. FastAPI handles APIs and orchestration; Qdrant/BM25 handle retrieval; LiteLLM isolates model providers; Redis reduces duplicate generation; PostgreSQL stores request audit records; and OpenTelemetry exports runtime traces to a collector.

## Runtime Flow / 執行流程

1. Client / Web UI 呼叫 FastAPI / calls FastAPI.
2. API Key 與 Prompt Injection Heuristic 先執行 / security checks run first.
3. Query 先查 Redis Cache / checks Redis cache first.
4. Cache Miss 時執行 Vector 或 Hybrid Retrieval / retrieval runs on cache miss.
5. Context 送至 LiteLLM / context is sent to LiteLLM.
6. LiteLLM 將 enterprise-rag Route 到 Ollama / routes enterprise-rag to Ollama.
7. Answer + Citation 回傳 Client / returned to the client.
8. Response 可寫入 Redis / may be cached in Redis.
9. Request Metadata 寫入 PostgreSQL Audit / request metadata is audited to PostgreSQL.
10. HTTP、Retrieval、LLM、Evaluation Span 送往 OTel Collector / spans are exported to the OTel Collector.

## Security / Privacy Boundary

**繁體中文**  
Audit Store 預設不保存 Request Body、Prompt、Document Content，只記錄 Request ID、Method、Path、Status、Latency 與低敏 Metadata。Telemetry 也不寫入 Prompt / Context 本文。

**English**  
The audit store does not persist request bodies, prompts, or document content by default. It records request ID, method, path, status, latency, and low-sensitivity metadata. Telemetry spans also avoid prompt/context bodies.

## Extension Point / 擴充點

- Cloud LLM / Local LLM Routing through LiteLLM
- PostgreSQL HA / Managed PostgreSQL
- Redis Cluster / Managed Redis
- Grafana Tempo / Jaeger / vendor OTLP backend
- OIDC / RBAC
- MinIO / S3
- Multi-tenant Vector Collections
- Secret Manager / Vault
