# 可觀測性 / Observability

## OpenTelemetry

**繁體中文**  
v0.3 使用 OpenTelemetry SDK Manual Instrumentation。若設定 OTEL_EXPORTER_OTLP_TRACES_ENDPOINT，Trace 會透過 OTLP HTTP Export；若未設定 Endpoint 則使用 Console Exporter。

**English**  
v0.3 uses manual OpenTelemetry SDK instrumentation. When OTEL_EXPORTER_OTLP_TRACES_ENDPOINT is configured, traces are exported over OTLP HTTP; otherwise the console exporter is used.

## Spans

- http.request
- rag.retrieve
- rag.answer_question
- llm.chat_completion
- rag.evaluate_answer

## Data Minimization / 資料最小化

**繁體中文**  
Span 只記錄 Model Name、Retrieval Mode、Top-K、Result Count、HTTP Status 等 Operational Metadata，不記錄 Question、Prompt、Retrieved Context 或 Answer Text。

**English**  
Spans record operational metadata such as model name, retrieval mode, top-k, result counts, and HTTP status. They do not record questions, prompts, retrieved context, or answer text.

## Local Collector

Docker Compose 內含 OTel Collector，使用 Debug Exporter：

    docker compose logs -f otel-collector

**繁體中文**  
正式環境可將 Exporter 改為 Grafana Tempo、Jaeger 或支援 OTLP 的 APM Platform。

**English**  
Production deployments can replace the debug exporter with Grafana Tempo, Jaeger, or another OTLP-compatible APM platform.
