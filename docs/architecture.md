# 架構 / Architecture

## 設計概念 / Design concept

**繁體中文**  
平台將 Ingestion、Retrieval、Generation 與 Operational Concern 分層，讓各層可以獨立測試、替換與擴充，降低 Provider、Vector DB 或 LLM 的耦合。

**English**  
The platform separates ingestion, retrieval, generation, and operational concerns so each layer can be tested, replaced, and extended independently.

## Runtime Flow / 執行流程

1. Client → FastAPI  
   - 繁中：Client 呼叫 FastAPI Endpoint。  
   - English: A client calls the FastAPI endpoint.
2. Security Gate  
   - 繁中：先執行 API Key 驗證與基本 Prompt Injection Screening。  
   - English: API-key validation and basic prompt-injection screening run first.
3. Retrieval  
   - 繁中：依 Vector 或 Hybrid Mode 查詢 Qdrant / BM25。  
   - English: Retrieval runs against Qdrant and optionally BM25 depending on the selected mode.
4. Context Build  
   - 繁中：將 Retrieved Chunks 與 Page / Section Metadata 組成編號 Context。  
   - English: Retrieved chunks and page/section metadata are converted into numbered context blocks.
5. Generation  
   - 繁中：OpenAI-compatible LLM 產生 Grounded Answer。  
   - English: An OpenAI-compatible LLM generates a grounded answer.
6. Response  
   - 繁中：API 回傳 Answer 與 Citation Lineage。  
   - English: The API returns the answer with citation lineage.

## Extension Point / 擴充點

- Hybrid BM25 + Vector Retrieval
- Reranking
- Metadata Filter
- Tenant Isolation
- PostgreSQL / pgvector
- S3 / MinIO Document Storage
- LiteLLM Model Routing
- OpenTelemetry Tracing
- Production IAM / Secret Management

## Production Topology / 正式環境拓樸

**繁體中文**  
正式環境建議將 API、Vector Database、Object Storage、Telemetry、Model Gateway 拆分成可獨立維運的服務。API 前方應配置 Enterprise Identity-aware Access Control、Reverse Proxy 或 API Gateway，並將 Secret、Audit、Network Policy 與 Egress Control 納入平台治理。

**English**  
For production, run the API, vector database, object storage, telemetry, and model gateway as separately managed services. Place the API behind enterprise identity-aware access control and a reverse proxy/API gateway, with secrets, auditing, network policy, and egress controls managed explicitly.
