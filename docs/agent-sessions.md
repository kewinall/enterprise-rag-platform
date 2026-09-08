# Agent Session、Checkpoint、Memory 與 Async Job

## Session / 工作階段

**繁體中文**  
Session 是 Agent 持久化的邊界。Session 綁定 tenant_id，並保存建立者、標題與更新時間。

**English**  
A session is the persistence boundary for agent state. It is tenant-scoped and stores creator, title, and timestamps.

Create:

    POST /api/v1/agent/sessions

## Checkpoint

每次帶 session_id 的 Agent Run 都保存結果 Checkpoint。  
Every agent run with a session_id stores a result checkpoint.

    GET /api/v1/agent/sessions/{session_id}/checkpoint

Checkpoint 用於 Debug / Resume Reference，不直接保存 Infrastructure Credential。  
Checkpoints are for debugging/resume reference and never store infrastructure credentials.

## Governed Memory / 受治理記憶

**繁體中文**
- Memory 只由使用者透過 API/UI 明確寫入。
- Agent 不會自行永久記住對話。
- 每筆 Memory 有 expires_at。
- Retention 受到 Server Maximum 限制。
- Memory 只在同 Tenant Session 中載入。

**English**
- Memory is written only through explicit user API/UI actions.
- The agent does not autonomously persist conversation memory.
- Every memory item has expires_at.
- Retention is capped by server policy.
- Memory loads only within the same tenant session.

Default:

    AGENT_MEMORY_DEFAULT_RETENTION_DAYS=7
    AGENT_MEMORY_MAX_RETENTION_DAYS=30

## Async Jobs

Create:

    POST /api/v1/agent/jobs

Status:

    GET /api/v1/agent/jobs/{job_id}

States:

    queued -> running -> completed
                     -> failed

**繁體中文**  
Job Queue 使用 PostgreSQL FOR UPDATE SKIP LOCKED，因此多個 API Replica 可共同取 Job 而不重複執行。

**English**  
The job queue uses PostgreSQL FOR UPDATE SKIP LOCKED so multiple replicas can claim jobs without duplicate execution.
