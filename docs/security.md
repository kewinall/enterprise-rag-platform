# 安全 / Security

## 定位 / Scope

**繁體中文**  
此 Repository 是 Reference Implementation，不是完整 Enterprise Security Control Plane。

**English**  
This repository is a reference implementation, not a complete enterprise security control plane.

## 已包含的 Control / Included controls

- API Key Gate
- Upload Size Limit
- Source Control 不提交 .env / no committed .env secrets
- Non-root API Container
- Prompt Injection Heuristic
- pip-audit
- Trivy Filesystem Scan
- Local-first Model Option
- Audit Record 不保存 Request Body / audit records exclude request bodies
- Trace Span 不保存 Prompt / Context Content
- Web UI 使用 sessionStorage 保存 Demo API Key，不做長期 Persistence

## PostgreSQL Audit Privacy

**繁體中文**  
Audit Table 預設只記錄 Request ID、HTTP Method、Path、Status Code、Duration 與低敏 Metadata，不保存 Question、Answer、Prompt 或 Uploaded Document Content。

**English**  
The audit table records request ID, HTTP method, path, status code, duration, and low-sensitivity metadata. Questions, answers, prompts, and uploaded document content are not stored by default.

## Redis Cache

**繁體中文**  
Redis 會保存 RAG Response，因此正式環境必須評估 Encryption、Network Isolation、TTL、Access Control 與 Data Classification。若內容敏感，可將 CACHE_ENABLED=false。

**English**  
Redis stores RAG responses, so production deployments must consider encryption, network isolation, TTL, access control, and data classification. Disable caching with CACHE_ENABLED=false for sensitive workloads when appropriate.

## 正式環境要求 / Production requirements

- Enterprise SSO / OIDC
- RBAC / ABAC
- Tenant Isolation
- Rate Limiting
- TLS / mTLS
- Centralized Secret Management
- DLP / Malware Scan
- Network Segmentation
- Model Allowlist
- Egress Control
- Data Retention / Deletion Policy
- Managed Redis / PostgreSQL Encryption
- Audit Retention and Access Governance

## Prompt Injection

**繁體中文**  
RAG 不會消除 Prompt Injection。Retrieved Document 應視為 Untrusted Input；若未來加入 Agent / Tool Calling，Tool Permission 必須獨立於 Model Output 控制。

**English**  
RAG does not eliminate prompt injection. Treat retrieved documents as untrusted input. If agents or tools are added later, tool permissions must be controlled independently from model output.
