# 架構 / Architecture

## v0.6 Architecture

**繁體中文**  
v0.6 在 Agent Orchestration 外新增 Durable State 與 Governance Plane。FastAPI 不再只處理單次 Request；Session、Checkpoint、Async Job 與 Memory 都保存於 PostgreSQL，Rate Limit 使用 Redis，LLM 呼叫受到同一 Request-scoped Budget Tracker 管控。

**English**  
v0.6 adds durable state and governance planes around agent orchestration. FastAPI is no longer limited to single-request execution: sessions, checkpoints, async jobs, and memory are stored in PostgreSQL, rate limiting uses Redis, and LLM calls share a request-scoped budget tracker.

## Runtime

    Authentication
        |
        v
    Rate Limit
        |
        v
    Managed Agent Runtime
      |      |       |
      |      |       +--> Budget Tracker
      |      +----------> Session Memory
      +-----------------> Agent State Machine
                             |
                             v
                         Tool Registry
                          /        \
                   read-only      destructive
                      |               |
                      |          Human Approval
                      v
                 Data / RAG Tools
                      |
                      v
                 Result + Checkpoint

## Durable State

PostgreSQL tables:

- agent_session
- agent_checkpoint
- agent_job
- agent_memory

Running jobs are reset to queued during startup recovery.

## Async Worker

Worker claims jobs with:

    FOR UPDATE SKIP LOCKED

This permits multiple replicas to claim distinct jobs safely.

## MCP Boundary

MCP Tool Adapter maps tools/list and tools/call to the exact same Tool Registry. It does not create a parallel authorization path.

## Governance

- Tenant scope
- Role policy
- Human approval
- Memory expiry
- Token budget
- Estimated cost budget
- Rate limit
- Prompt/tool injection evaluation
- Prometheus metrics
