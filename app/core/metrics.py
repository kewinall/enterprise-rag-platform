from prometheus_client import Counter, Gauge, Histogram

AGENT_RUNS = Counter(
    "enterprise_rag_agent_runs_total",
    "Total agent runs by status.",
    ["status"],
)
AGENT_TOOL_CALLS = Counter(
    "enterprise_rag_agent_tool_calls_total",
    "Agent tool calls by tool and status.",
    ["tool", "status"],
)
AGENT_APPROVALS = Counter(
    "enterprise_rag_agent_approvals_total",
    "Agent approval decisions.",
    ["decision"],
)
AGENT_RATE_LIMITED = Counter(
    "enterprise_rag_agent_rate_limited_total",
    "Agent requests rejected by rate limiting.",
)
AGENT_BUDGET_EXCEEDED = Counter(
    "enterprise_rag_agent_budget_exceeded_total",
    "Agent runs stopped by token or cost budget.",
)
AGENT_LATENCY = Histogram(
    "enterprise_rag_agent_run_duration_seconds",
    "End-to-end agent runtime latency.",
)
AGENT_LLM_TOKENS = Counter(
    "enterprise_rag_agent_llm_tokens_total",
    "LLM tokens consumed by agent runs.",
    ["direction"],
)
AGENT_ESTIMATED_COST = Counter(
    "enterprise_rag_agent_estimated_cost_usd_total",
    "Estimated agent LLM cost in USD.",
)
AGENT_PENDING_JOBS = Gauge(
    "enterprise_rag_agent_jobs_pending",
    "Queued agent jobs visible to the worker.",
)
