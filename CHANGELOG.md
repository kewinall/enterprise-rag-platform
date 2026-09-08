# 版本異動紀錄 / Changelog

## 0.5.0 - 2026-09-09

### 新增 / Added

- Agentic RAG Orchestrator
- Query Planning and Query Rewrite
- Multi-hop Retrieval
- Context Sufficiency Critic
- Corrective Retrieval
- Answer Critic and Optional Revision
- Tool Calling Registry
- Viewer/Admin Tool Permission Policy
- Human Approval Gate for destructive tools
- Redis-backed Approval Requests with TTL
- Approval Approve / Reject APIs
- Agent Execution Trace
- Agent Evaluation Metrics and CLI
- Standard RAG / Agentic RAG Web UI Switch
- Agentic RAG bilingual documentation

### 安全 / Security

- Unknown planner tools are filtered out.
- Tenant and RBAC are re-validated server-side for every tool.
- delete_document requires Admin role and explicit human approval.
- Approval requests are tenant-scoped and single-consumption.
- Planner/Critic invalid JSON degrades safely instead of enabling unrestricted execution.
- No shell, arbitrary HTTP, SQL, or unrestricted code-execution tool is exposed.

### 變更 / Changed

- Application Version advanced to 0.5.0.
- Helm Chart and default offline application image advanced to 0.5.0.
- Web UI can display Agent Plan, Critic, Tool Trace, Approval and Reject actions.
- Agent Runtime Configuration added to .env.example and Helm values.

## 0.4.0 - 2026-09-08

- OIDC JWT Validation
- Viewer / Editor / Admin RBAC
- Multi-tenant Server-side Isolation
- Tenant-scoped Qdrant / Cache
- MinIO / S3 Object Storage
- Presigned Document Download
- Keycloak Demo Realm
- Kubernetes / Helm
- External Secrets Example
- Offline Bundle
- Deployment-file CI Validation

## 0.3.0 - 2026-09-08

- RAGAS-style Answer Evaluation
- OpenTelemetry
- PostgreSQL Audit
- Redis Cache
- LiteLLM Gateway
- Web UI

## 0.2.0 - 2026-09-08

- Page / Section Metadata
- Batch Ingestion
- Document Lifecycle
- Vector / Hybrid Retrieval
- Retrieval Benchmark

## 0.1.0 - 2026-09-08

- Initial FastAPI RAG Platform
- Qdrant Vector Retrieval
- BM25 + Reciprocal Rank Fusion
- Optional CrossEncoder Reranking
- Local Ollama Example
- CI / pip-audit / Trivy
