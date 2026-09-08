# 安全 / Security

## Scope / 定位

**繁體中文**  
本 Repository 是 Enterprise AI Security Reference Implementation，不是完整 IAM / DLP / SIEM / Secret Platform。

**English**  
This repository is an enterprise AI security reference implementation, not a complete IAM, DLP, SIEM, or secret-management platform.

## Authentication

- API Key Mode：只用於 Local Demo / local demo only
- OIDC Mode：JWT Signature + Issuer + Audience Validation
- JWKS Client Cache
- Role Claim Mapping
- Tenant Claim Mapping

## RBAC

- viewer: Query / Search / List / Download
- editor: viewer + Ingest / Reindex
- admin: editor + Delete

## Tenant Isolation

**繁體中文**
- Tenant 由 Principal 取得。
- Client Filter 無法指定 tenant_id。
- Document ID、Qdrant、Cache、CRUD 都 Tenant-scoped。
- Cache Revision 也依 Tenant 分離。

**English**
- Tenant identity comes from the authenticated principal.
- Client filters cannot specify tenant_id.
- Document IDs, Qdrant data, cache, and CRUD are tenant-scoped.
- Cache revisions are separated per tenant.

## Object Storage

- S3-compatible Storage
- Tenant-scoped Object Key
- Presigned Download URL
- Client 不取得 Storage Credential / clients do not receive storage credentials
- Production 建議 Encryption / KMS / Private Endpoint / Versioning

## Audit Privacy

PostgreSQL Audit 預設不保存 / does not store by default:

- Question
- Prompt
- Answer
- Document Content
- Request Body

只記錄 Operational Metadata。  
Only operational metadata is recorded.

## Telemetry Privacy

OpenTelemetry Span 不保存 Prompt / Context / Answer 本文。  
OpenTelemetry spans do not store prompt, context, or answer bodies.

## Secret Management

Helm Chart 使用 Existing Secret Reference。  
The Helm chart consumes an existing secret reference.

External Secrets example:

    examples/kubernetes/external-secret.yaml

詳見 / See: docs/secrets.md

## Container / Kubernetes Hardening

- Non-root User
- Drop Linux Capabilities
- No Privilege Escalation
- Read-only Root Filesystem
- Writable /tmp EmptyDir only
- Liveness / Readiness Probe
- NetworkPolicy
- PDB
- HPA Resource Boundaries

## CI Security

- pip-audit
- Trivy Filesystem Scan

## Production Requirements

仍建議加入 / still recommended:

- Enterprise SSO / Conditional Access
- mTLS where required
- Rate Limiting / WAF
- Malware Scan
- DLP
- Managed KMS
- Data Retention / Deletion Workflow
- Model Allowlist
- Egress Proxy / Private Endpoint
- Signed Images / SBOM Attestation
- SIEM Integration
