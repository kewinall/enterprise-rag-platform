# 安全 / Security

## 定位 / Scope

**繁體中文**  
此 Repository 是 Reference Implementation，不是完整的 Enterprise Security Control Plane。

**English**  
This repository is a reference implementation, not a complete enterprise security control plane.

## 已包含的 Control / Included controls

- API Key Gate
- Upload Size Limit
- Source Control 不提交 Secret / no committed secrets
- Non-root API Container
- Prompt Injection Heuristic
- Dependency Audit Workflow
- Trivy Filesystem Scan
- Local-first Model Option

## 正式環境要求 / Production requirements

**繁體中文**  
正式環境建議額外加入 Enterprise SSO/OIDC、Authorization/RBAC、Tenant Isolation、Rate Limiting、TLS、Centralized Secret Management、Audit Logging、DLP、Upload Malware Scan、Network Segmentation、Model Allowlist、Egress Control 與 Data Retention Policy。

**English**  
Add enterprise SSO/OIDC, authorization/RBAC, tenant isolation, rate limiting, TLS, centralized secret management, audit logging, DLP, malware scanning for uploads, network segmentation, model allowlists, egress controls, and data-retention policies.

## Prompt Injection

**繁體中文**  
RAG 不會自動消除 Prompt Injection。Retrieved Documents 應視為 Untrusted Input；若後續加入 Agent / Tool Calling，Tool Permission 必須與 Model Output 分離控管。

**English**  
RAG does not eliminate prompt injection. Treat retrieved documents as untrusted input. If agents or tools are added later, restrict tool permissions independently of model output.
