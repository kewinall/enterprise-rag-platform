# 故障排除 / Troubleshooting

## Agent State unavailable

Readiness:

    GET /ready

Check:

    agent_state=ready

PostgreSQL must be reachable and able to create agent_session, agent_checkpoint, agent_job, and agent_memory.

## Async Job remains queued

Check:
- AGENT_ASYNC_JOBS_ENABLED=true
- PostgreSQL connectivity
- application worker is running
- LiteLLM / Qdrant dependencies

After restart, jobs left in running state are requeued automatically.

## Session 404

Confirm the session_id belongs to the current tenant.

## Memory not used

Check:
- request session_id
- use_memory=true
- memory has not expired
- memory belongs to the same tenant/session

## Budget exceeded

Response status:

    budget_exceeded

Check:

    AGENT_BUDGET_MAX_TOKENS
    AGENT_BUDGET_MAX_COST_USD
    AGENT_INPUT_COST_PER_1K
    AGENT_OUTPUT_COST_PER_1K

Cost rates default to zero for the local demo.

## HTTP 429 Agent rate limit

Check:

    AGENT_RATE_LIMIT_PER_MINUTE

Scope is tenant + subject. Retry after the returned retry_after_seconds.

## MCP error

Supported subset:
- server/discover
- initialize
- tools/list
- tools/call

Unsupported methods return JSON-RPC method-not-found.

## Dashboard has no data

Ensure Prometheus scrapes:

    /metrics

Then import:

    observability/grafana-agent-dashboard.json

## Existing v0.5 checks

OIDC, Tenant, MinIO/S3, Redis, Qdrant, LiteLLM, Approval and Helm troubleshooting remain applicable.
