# Agent Governance / Agent 治理

## Token Budget

    AGENT_BUDGET_MAX_TOKENS=12000

每次 LLM Call 會優先使用 Provider usage；若 Provider 未回 usage，使用字元估算。  
Each LLM call uses provider usage when available and falls back to character-based token estimation.

## Cost Budget

    AGENT_BUDGET_MAX_COST_USD=0.25
    AGENT_INPUT_COST_PER_1K=0
    AGENT_OUTPUT_COST_PER_1K=0

**繁體中文**  
預設 Cost Rate 為 0，因 Local Ollama Demo 沒有 Token Billing。使用 Cloud Model 時應設定實際 Rate，Cost Budget 才會發揮作用。

**English**  
Cost rates default to zero because the local Ollama demo has no token billing. Configure real rates for cloud models to enforce the cost budget.

## Rate Limit

    AGENT_RATE_LIMIT_PER_MINUTE=30

Scope:

    tenant_id + subject

Redis 不可用時 Demo 會 fail-open，正式環境應搭配 API Gateway / WAF Rate Limit。  
The demo fails open if Redis is unavailable; production should also enforce limits at the API gateway/WAF layer.

## Data Platform Tools

Read-only:

- get_platform_status
- get_recent_audit_events

這些 Tool 僅回傳 Tenant-scoped、低敏 operational metadata。  
These tools return tenant-scoped, low-sensitivity operational metadata only.

## Adversarial Evaluation

Run:

    make evaluate-adversarial

Checks include:

- Ignore previous instructions
- Reveal hidden/system instructions
- Unknown shell tool injection
- Tool Allowlist enforcement
