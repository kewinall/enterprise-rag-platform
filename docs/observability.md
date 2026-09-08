# 可觀測性 / Observability

## OpenTelemetry

**繁體中文**  
平台使用 OpenTelemetry Manual Instrumentation。設定 OTEL_EXPORTER_OTLP_TRACES_ENDPOINT 後會使用 OTLP HTTP Export；未設定時使用 Console Exporter。

**English**  
The platform uses manual OpenTelemetry instrumentation. When OTEL_EXPORTER_OTLP_TRACES_ENDPOINT is configured, traces are exported over OTLP HTTP; otherwise the console exporter is used.

## RAG Spans

- http.request
- rag.retrieve
- rag.answer_question
- llm.chat_completion
- rag.evaluate_answer

## Agent Spans

v0.5 adds:

- agent.run
- agent.plan
- agent.context_critic
- agent.answer_critic

Agent Tool Execution 仍可從 agent.run Trace 與 API Response Trace 交叉確認。  
Agent tool execution can be correlated through the agent.run trace and the API response trace.

## Data Minimization / 資料最小化

**繁體中文**  
Span 記錄 Operational Metadata，例如 Model、Retrieval Mode、Top-K、Tenant ID、Result Count、HTTP Status。Question、Prompt、Context、Answer Body 不寫入 Span Attribute。

**English**  
Spans record operational metadata such as model, retrieval mode, top-k, tenant ID, result count, and HTTP status. Questions, prompts, contexts, and answer bodies are not written to span attributes.

## Local Collector

    docker compose logs -f otel-collector

## Production Backend

可替換 / Can be replaced with:

- Grafana Tempo
- Jaeger
- OpenTelemetry-compatible APM
- Enterprise observability platform

## Recommended Agent Dashboard

後續建議 / Recommended:

- Agent Runs
- Planner Latency
- Tool Calls per Run
- Approval Required Rate
- Approval Reject Rate
- Corrective Retrieval Rate
- Revision Rate
- Groundedness / Relevance Distribution
- Token / Cost per Agent Run
