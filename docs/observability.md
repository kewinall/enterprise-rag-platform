# 可觀測性 / Observability

## OpenTelemetry

Existing spans:
- http.request
- rag.retrieve
- rag.answer_question
- llm.chat_completion
- agent.run
- agent.plan
- agent.context_critic
- agent.answer_critic

Prompt / Context / Answer bodies are not written into span attributes.

## Prometheus Agent Metrics

v0.6 adds:

- enterprise_rag_agent_runs_total
- enterprise_rag_agent_tool_calls_total
- enterprise_rag_agent_approvals_total
- enterprise_rag_agent_rate_limited_total
- enterprise_rag_agent_budget_exceeded_total
- enterprise_rag_agent_run_duration_seconds
- enterprise_rag_agent_llm_tokens_total
- enterprise_rag_agent_estimated_cost_usd_total
- enterprise_rag_agent_jobs_pending

Endpoint:

    /metrics

## Grafana Dashboard

Import:

    observability/grafana-agent-dashboard.json

Panels:

- Agent Runs
- Rate Limited
- Budget Exceeded
- Estimated LLM Cost
- Runs by Status
- Tool Calls
- Agent P95 Latency
- LLM Tokens

## Production

Prometheus can scrape the API metrics endpoint; Grafana may use the included dashboard as a starting point. OpenTelemetry traces can be exported to Tempo, Jaeger, or another compatible backend.
