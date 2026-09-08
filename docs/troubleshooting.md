# 故障排除 / Troubleshooting

## Agentic RAG Disabled

確認 / Check:

    AGENT_ENABLED=true

Endpoint:

    POST /api/v1/agent/query

## Planner 回傳 degraded / Planner degraded

**繁體中文**  
如果 Planner 回傳非 JSON，Agent Trace 會顯示 plan status=degraded，並安全降級為 search_knowledge。

**English**  
If the planner returns invalid JSON, the trace shows plan status=degraded and safely falls back to search_knowledge.

確認 LiteLLM / Ollama:

    docker compose logs litellm
    docker compose exec ollama ollama list

## Critic degraded

Context / Answer Critic 若無法解析 JSON，Trace 會顯示 degraded。  
If critic JSON cannot be parsed, the trace records degraded status.

這不會放寬 Tool Permission。  
This does not relax tool permissions.

## Approval Request 建立失敗

Approval Workflow 需要 Redis:

    docker compose exec redis redis-cli ping

Expected:

    PONG

確認 / Check:

    AGENT_APPROVAL_TTL_SECONDS=600

## Approval 404

可能原因 / Possible reasons:

- TTL 已過期 / expired
- 已被 Approve / Reject / consumed
- action_id 錯誤 / incorrect action ID

## Approval 403

確認 / Check:

- Principal Tenant 與 Approval Tenant 相同
- Principal 具有 Required Role
- delete_document 需要 admin

## Agent Tool 被 rejected

查看 / Inspect:

    GET /api/v1/agent/tools

Agent Trace 會包含 Tool、status=rejected 與 reason。  
The agent trace includes the tool, rejected status, and reason.

## Multi-hop 沒執行 / Multi-hop did not run

Planner 只有在需要拆解問題時才輸出 subqueries，且受到：

    AGENT_MAX_SUBQUERIES
    AGENT_MAX_STEPS

限制。  
The planner emits subqueries only when needed and remains bounded by those settings.

## Readiness

    curl http://localhost:8000/ready

Dependencies:

- qdrant
- redis
- postgres
- object_store

## OIDC / Tenant / Object Store

既有 v0.4 Troubleshooting 原則仍適用。  
Existing v0.4 troubleshooting guidance still applies.

- Verify OIDC issuer/audience/JWKS.
- Verify /api/v1/me roles and tenant.
- Verify MinIO endpoint and credentials.
- Re-ingest legacy chunks that do not contain tenant_id.

## Helm Validation

    helm lint charts/enterprise-rag
    helm template test charts/enterprise-rag

## Offline Bundle

    bash scripts/offline/verify-bundle.sh ./offline-bundle
