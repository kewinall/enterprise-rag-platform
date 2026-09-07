# Security

This repository is a reference implementation, not a complete enterprise security control plane.

## Included controls

- API key gate
- upload-size limit
- no committed secrets
- non-root API container
- prompt-injection heuristic
- dependency audit workflow
- Trivy filesystem scan
- local-first model option

## Production requirements

Add enterprise SSO/OIDC, authorization/RBAC, tenant isolation, rate limiting, TLS, centralized secret management, audit logging, DLP, malware scanning for uploads, network segmentation, model allowlists, egress controls and data-retention policies.

RAG does not eliminate prompt injection. Treat retrieved documents as untrusted input and restrict any agent/tool permissions independently of model output.
