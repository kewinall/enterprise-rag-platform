# Audit 與 Cache / Audit and Cache

## PostgreSQL Audit

Table:

    rag_audit_event

欄位 / Columns:

- id
- event_time
- request_id
- method
- path
- status_code
- duration_ms
- metadata

**繁體中文**  
Audit 設計刻意不保存 Request Body，避免 Question、Prompt、Answer 或 Document Content 被默認寫入稽核資料庫。v0.4 會在低敏 Metadata 中加入 subject、tenant_id 與 auth_mode，方便做租戶層級稽核。

**English**  
The audit design intentionally excludes request bodies so questions, prompts, answers, and document content are not persisted by default. v0.4 adds subject, tenant_id, and auth_mode to low-sensitivity metadata for tenant-aware auditing.

Disable:

    AUDIT_ENABLED=false

## Redis Answer Cache

**繁體中文**  
Cache 用來降低重複 Question 的 Retrieval / Generation Cost。Key 使用 SHA-256 Hash，不直接以 Question 作為 Redis Key。

**English**  
The cache reduces retrieval/generation cost for repeated requests. Keys use SHA-256 and do not expose the raw question in the Redis key.

設定 / Configuration:

    CACHE_ENABLED=true
    REDIS_URL=redis://redis:6379/0
    CACHE_TTL_SECONDS=300

## Cache Semantics

以下任一欄位不同都會產生不同 Key / Any difference creates a separate cache key:

- tenant_id
- tenant_revision
- Question
- Top-K
- Retrieval Mode
- Metadata Filters
- Model

## Tenant Revision Invalidation

**繁體中文**  
v0.4 在 Redis 維護每個 Tenant 的 revision。Ingest、Reindex、Delete 成功後會 bump revision。下一次 Query 會使用新的 revision 形成 Cache Key，因此舊答案即使尚未 TTL Expire，也不再被命中。

**English**  
v0.4 maintains a per-tenant revision in Redis. Successful ingest, reindex, and delete operations bump the revision. New queries use the updated revision in their cache keys, so stale answers are no longer reused even if the old cache entry has not expired.

Redis Key:

    rag:tenant-revision:{tenant_id}

Disable:

    CACHE_ENABLED=false
