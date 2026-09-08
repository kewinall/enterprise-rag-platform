# Kubernetes / Helm

## Helm Chart

Chart:

    charts/enterprise-rag

安裝 / Install:

    helm upgrade --install rag ./charts/enterprise-rag

## Included Resources / 已包含資源

- Deployment
- Service
- Optional Ingress
- ConfigMap
- Existing Secret Reference
- HorizontalPodAutoscaler
- PodDisruptionBudget
- NetworkPolicy
- Liveness / Readiness Probe
- Non-root Container Security Context
- Read-only Root Filesystem + writable /tmp EmptyDir

## External Dependencies

**繁體中文**  
Chart 預設只部署 RAG API，Qdrant、Redis、PostgreSQL、LiteLLM、Object Storage、OTel Collector 與 OIDC Provider 由 values.yaml 指向既有 Service。這種設計比較符合正式環境使用 Managed Service 或共享 Platform Service 的模式。

**English**  
The chart deploys the RAG API only. Qdrant, Redis, PostgreSQL, LiteLLM, object storage, the OTel Collector, and the OIDC provider are configured as external services through values.yaml. This matches production environments that use managed or shared platform services.

## Secret

預設 Secret Name:

    enterprise-rag-secrets

建議至少提供 / Recommended keys:

- LLM_API_KEY
- POSTGRES_DSN
- S3_ACCESS_KEY_ID
- S3_SECRET_ACCESS_KEY

External Secrets 範例 / example:

    examples/kubernetes/external-secret.yaml

## Validation

CI 會執行 / CI runs:

    helm lint charts/enterprise-rag
    helm template ci charts/enterprise-rag

## NetworkPolicy

**繁體中文**  
預設限制 Pod Ingress/Egress。Cluster-internal Service 可透過 Namespace Selector 存取；若正式依賴在 Cluster 外，需在 allowedEgressCIDRs 加入核准 CIDR，並依組織規範調整 DNS / Proxy / Private Endpoint。

**English**  
The default policy restricts pod ingress and egress. Cluster-internal services are reachable through namespace selection; approved external services require allowedEgressCIDRs and environment-specific DNS/proxy/private-endpoint rules.
