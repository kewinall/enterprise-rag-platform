# Secret Management / 機密管理

## Principle / 原則

**繁體中文**  
Git Repository 只保存 .env.example 與 Secret Key Name，不保存真實 Password、Token、Cloud Credential。

**English**  
The repository stores only .env.example and secret key names, never real passwords, tokens, or cloud credentials.

## Docker Compose

Local Demo 使用 .env，且 .env 已被 .gitignore 排除。  
Local demos use .env, which is excluded by .gitignore.

## Kubernetes

Helm Chart 使用：

    secret.existingSecret: enterprise-rag-secrets

Deployment 透過 envFrom.secretRef 讀取，Chart 不自動產生帶明文 Secret 的 Manifest。

The deployment consumes an existing Kubernetes Secret through envFrom.secretRef; the chart does not generate plaintext secret manifests.

## External Secrets

範例 / Example:

    examples/kubernetes/external-secret.yaml

**繁體中文**  
可由 External Secrets Operator 對接 AWS Secrets Manager、Azure Key Vault、Google Secret Manager、HashiCorp Vault 等實際 Backend。

**English**  
External Secrets Operator can map secrets from AWS Secrets Manager, Azure Key Vault, Google Secret Manager, HashiCorp Vault, and similar backends.

## Production Rules / 正式環境規則

- Secret Rotation
- Least Privilege
- Short-lived Credential where possible
- Audit secret access
- Separate secret per environment
- Never reuse demo credentials
