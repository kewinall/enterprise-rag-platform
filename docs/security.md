# 安全 / Security

## Core Controls

- OIDC JWT Validation
- Viewer / Editor / Admin RBAC
- Server-enforced Tenant Isolation
- Tool Allowlist
- Human Approval for destructive tools
- MinIO / S3 tenant boundary
- Secret externalization
- Non-root Kubernetes runtime
- pip-audit / Trivy

## Durable State

**繁體中文**
- Session / Checkpoint / Job / Memory 都包含 tenant_id。
- Memory 只由使用者明確寫入，不自動永久保存聊天內容。
- Memory 有 expires_at 與 Server-side retention cap。
- Restart recovery 只重新排程未完成 Job，不會改變 Role/Tenant。

**English**
- Session, checkpoint, job, and memory records contain tenant_id.
- Memory is explicitly written by users and does not automatically persist conversation history.
- Memory has expires_at and a server-side retention cap.
- Restart recovery only requeues unfinished jobs; it does not change role or tenant identity.

## MCP Security

MCP tools/list only exposes tools permitted to the authenticated principal.  
MCP tools/call reuses execute_tool, therefore Tenant/RBAC/Approval remain enforced.

Unsupported unrestricted capabilities remain absent:
- shell
- raw SQL
- arbitrary HTTP
- eval/exec
- secret read
- cloud admin

## Budget / Rate

Token budget is always enforceable. Cost budget requires configured model rates.  
Rate limit scope is tenant_id + subject.

Redis failure is fail-open in this reference demo; production should also enforce gateway/WAF rate limiting.

## Adversarial Evaluation

Prompt-injection heuristics and unknown-tool filtering are regression-tested in CI.

## Remaining Production Controls

- DLP / Malware scanning
- SIEM integration
- signed images / SBOM attestation
- dedicated approval audit
- per-tool quota
- distributed rate limiting at gateway
- full red-team program
