# 故障排除 / Troubleshooting

## Readiness

    curl http://localhost:8000/ready

回傳 Dependencies / returns dependencies:

- qdrant
- redis
- postgres
- object_store

## OIDC Token 401

確認 / Check:

- AUTH_MODE=oidc
- OIDC_ISSUER 與 Token iss 相同 / matches token iss
- OIDC_AUDIENCE 存在於 aud / exists in aud
- OIDC_JWKS_URL API Container 可連線 / reachable from API container
- Token 尚未過期 / token not expired

Keycloak logs:

    docker compose logs keycloak

## 403 Role Required

查看 Principal:

    GET /api/v1/me

確認 Token Role Claim 包含 viewer、editor 或 admin。  
Confirm the role claim contains viewer, editor, or admin.

## Tenant 看不到文件 / Tenant cannot see documents

**繁體中文**  
v0.4 只會查詢與 Principal tenant_id 相同的 Chunk。v0.3 升級後的 Legacy Chunk 沒有 tenant_id，需要重新 Ingest。

**English**  
v0.4 only retrieves chunks matching the principal tenant_id. Legacy v0.3 chunks have no tenant_id and must be re-ingested.

## Object Store unavailable

MinIO:

    docker compose logs minio

確認 / Check:

    S3_ENDPOINT_URL
    S3_BUCKET
    S3_ACCESS_KEY_ID
    S3_SECRET_ACCESS_KEY

Console:

    http://localhost:9001

## Download 404

確認該 Document 由 v0.4 重新 Ingest，且 Qdrant Metadata 有 object_key。  
Ensure the document was re-ingested under v0.4 and its Qdrant metadata contains object_key.

## Redis Cache

    docker compose exec redis redis-cli ping

Expected:

    PONG

文件變更後 Tenant Revision 會增加，因此舊 Cache 不再 Hit。  
Document mutations increment the tenant revision, so old cache entries stop matching.

## PostgreSQL Audit

    docker compose exec postgres pg_isready -U rag -d rag

Recent events:

    docker compose exec postgres psql -U rag -d rag       -c "select id,event_time,method,path,status_code,duration_ms from rag_audit_event order by id desc limit 10;"

## LiteLLM / Ollama

    docker compose logs litellm
    docker compose exec ollama ollama list

Pull model:

    docker compose exec ollama ollama pull llama3.2:3b

## Helm Validation

    helm lint charts/enterprise-rag
    helm template test charts/enterprise-rag

## Offline Bundle

Verify checksum:

    bash scripts/offline/verify-bundle.sh ./offline-bundle
