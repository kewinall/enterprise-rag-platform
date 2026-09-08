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
Audit 設計刻意不保存 Request Body，避免 Question、Prompt、Answer 或 Document Content 被默認寫入稽核資料庫。

**English**  
The audit design intentionally excludes request bodies so questions, prompts, answers, and document content are not persisted by default.

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

Disable:

    CACHE_ENABLED=false

## Cache Semantics

以下欄位任一不同就會產生不同 Key / Any difference creates a separate cache key:

- Question
- Top-K
- Retrieval Mode
- Metadata Filters
- Model

**繁體中文**  
目前 Cache 不會自動因 Document Reindex 而全域 Invalidated，因此需要高一致性的正式環境可縮短 TTL、關閉 Cache，或在後續版本加入 Collection Revision / Document Revision 到 Cache Key。

**English**  
The cache is not globally invalidated on document reindex in v0.3. For strict consistency, reduce TTL, disable caching, or add collection/document revisioning to future cache keys.
