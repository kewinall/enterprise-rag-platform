# 版本異動紀錄 / Changelog

## Unreleased

### 新增 / Added

- Engineering Knowledge Package Contract v1.0 consumer and validation path.
- Deterministic mapping from canonical `segment_id` to Qdrant-compatible storage UUID while preserving source identity.
- Provenance payload fields for document/segment IDs, source path, line range, content hash, access class, quality score and citation object.
- Lexical/BM25-only retrieval mode for controlled baseline comparison.
- Engineering retrieval benchmark support for multiple acceptable sources, tenant filtering, failed-case evidence and P50/P95 latency.
- Citation fidelity evaluator with zero-broken-citation gate.
- Knowledge package ingestion, benchmark and evidence Make targets.
- Integration documentation and contract tests.

### 變更 / Changed

- Hybrid retrieval now exposes a dedicated lexical baseline without changing existing vector/hybrid behavior.
- Retrieval result payloads preserve source provenance required by the Engineering Knowledge Base.
- Portfolio boundary now explicitly identifies `engineering-knowledge-base` as the canonical engineering knowledge source.

## 0.6.0 - 2026-09-09

### 新增 / Added

- PostgreSQL Durable Agent Session
- Agent Checkpoint Store
- Durable Async Job Queue with restart recovery
- Explicit Agent Memory with retention / expiry policy
- get_platform_status read-only tool
- get_recent_audit_events read-only tool
- MCP-compatible JSON-RPC Tool Adapter
- 2026-07-28 server/discover subset
- 2025-11-25 initialize subset
- Agent token budget
- Estimated cost budget
- Redis tenant+subject rate limit
- Prometheus Agent metrics
- Grafana Agent Dashboard JSON
- Expanded adversarial prompt/tool injection evaluation
- v0.6 Web UI Session / Memory / Async Job controls

### 安全 / Security

- Memory is explicit opt-in and expires by policy.
- MCP uses the same Tool Registry / Tenant / RBAC / Approval controls.
- Destructive tools remain approval-gated.
- Token/cost budgets stop excessive LLM usage.
- Rate limits apply to sync and async Agent entry points.
- Adversarial tests verify prompt and unknown-tool injection defenses.

### 變更 / Changed

- Application / Helm / Offline image advanced to 0.6.0.
- Agent responses include budget usage and optional checkpoint_id.
- Readiness includes agent_state.

## 0.5.0 - 2026-09-09

- Agentic RAG Orchestrator
- Query Planning / Rewrite
- Multi-hop and Corrective Retrieval
- Context / Answer Critic
- Tool Calling / Permission Policy
- Human Approval Gate
- Agent Evaluation / Trace

## 0.4.0 - 2026-09-08

- OIDC / RBAC / Multi-tenancy
- MinIO / S3
- Kubernetes / Helm
- Offline Bundle

## 0.3.0 - 2026-09-08

- Evaluation / OpenTelemetry / Audit / Cache / LiteLLM / Web UI

## 0.2.0 - 2026-09-08

- Document Lifecycle / Hybrid Retrieval / Benchmark

## 0.1.0 - 2026-09-08

- Initial FastAPI / Qdrant RAG Platform
