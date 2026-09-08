# 安全 / Security

## Scope / 定位

**繁體中文**  
本 Repository 是 Enterprise AI Security Reference Implementation，不是完整 IAM / DLP / SIEM / Secret Platform。

**English**  
This repository is an enterprise AI security reference implementation, not a complete IAM, DLP, SIEM, or secret-management platform.

## Existing Platform Controls

- OIDC JWT Validation
- Viewer / Editor / Admin RBAC
- Server-enforced Tenant Isolation
- MinIO / S3 Tenant Boundary
- PostgreSQL Audit
- Redis Tenant Cache Revision
- OpenTelemetry Data Minimization
- Existing Secret Reference / External Secrets Example
- Non-root Kubernetes Runtime
- NetworkPolicy
- pip-audit
- Trivy

## Agent Tool Security

**繁體中文**  
Agent Planner 不具備直接 Tool Execution 權限。Planner Output 只是「提案」，Server Tool Registry 仍會重新驗證 Tool Name、Role、Tenant 與 Approval Policy。

**English**  
The planner does not receive direct tool-execution authority. Planner output is only a proposal; the server-side tool registry re-validates tool name, role, tenant, and approval policy.

Allowed tools:

| Tool | Required Role | Human Approval |
|---|---|---|
| search_knowledge | viewer | No |
| list_documents | viewer | No |
| get_document_metadata | viewer | No |
| delete_document | admin | Yes |

Not exposed:

- arbitrary shell
- arbitrary HTTP
- raw SQL
- arbitrary filesystem write
- unrestricted Python/code execution
- cloud administration credentials

## Human Approval Gate

**繁體中文**
- Destructive Tool 必須先通過 Admin Role。
- Approval Request 綁定 Tenant。
- Approval 有 TTL。
- Approve / Reject 都會再次檢查 Tenant 與 Required Role。
- Approval Request 採單次消耗。

**English**
- Destructive tools first require the Admin role.
- Approval requests are tenant-bound.
- Approvals expire through TTL.
- Approve/reject operations re-check tenant and required role.
- Approval requests are single-consumption.

## Planner / Critic Failure

**繁體中文**  
Planner 或 Critic 回傳無法解析的 JSON 時，不會放寬 Tool Policy。Planner 失敗會降級成 tenant-scoped search；Critic 失敗則跳過該 Critic Step。

**English**  
Invalid planner or critic JSON never relaxes tool policy. Planner failure degrades to tenant-scoped search, while critic failure skips only the failed critic step.

## Prompt Injection

Prompt Injection 檢查仍會在 Standard RAG 與 Agentic RAG Endpoint 前執行。  
Prompt-injection screening remains active before both Standard RAG and Agentic RAG endpoints.

**繁體中文**  
此 Heuristic 不是完整防護。正式環境仍應加入 Tool Input Validation、Content Sanitization、Model Guardrails、Adversarial Evaluation、Egress Control 與 Least-Privilege Tool Credential。

**English**  
The heuristic is not a complete defense. Production environments should add tool-input validation, content sanitization, model guardrails, adversarial evaluation, egress controls, and least-privilege tool credentials.

## Production Requirements

- Enterprise SSO / Conditional Access
- Rate Limiting / WAF
- DLP / Malware Scan
- Managed KMS
- Data Retention / Deletion Workflow
- Model Allowlist
- Egress Proxy / Private Endpoint
- Signed Images / SBOM Attestation
- SIEM Integration
- Dedicated Agent Approval Audit
- Tool-level Rate Limit / Budget
