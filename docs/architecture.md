# 架構 / Architecture

## v0.5 Architecture

**繁體中文**  
v0.5 在 v0.4 Enterprise RAG Platform 上增加 Agent Orchestration Layer。Identity / Tenant / RBAC 仍是最外層安全邊界，Agent Planner 不能直接取得 Infrastructure Credential，也不能自行新增 Tool。所有 Tool 都由 Server Registry 與 Permission Policy 定義。

**English**  
v0.5 adds an agent orchestration layer on top of the v0.4 enterprise RAG platform. Identity, tenant, and RBAC remain the outer security boundary. The planner never receives infrastructure credentials and cannot create arbitrary tools; all tools are defined by the server-side registry and permission policy.

## Agent Runtime Flow / Agent 執行流程

1. FastAPI Authentication 建立 Principal。  
   FastAPI authentication builds the principal.
2. Agent Planner 將 Question 分類、Rewrite，並提出 Tool Calls / Subqueries。  
   The planner classifies and rewrites the question and proposes tool calls/subqueries.
3. Tool Registry 驗證 Tool Name。  
   The tool registry validates the tool name.
4. Permission Policy 驗證 Role 與 Tenant Scope。  
   The permission policy enforces role and tenant scope.
5. Read-only Tools 可執行；破壞性 Tool 產生 Approval Request。  
   Read-only tools may execute; destructive tools generate approval requests.
6. Multi-hop Retrieval 執行 Subqueries。  
   Multi-hop retrieval executes subqueries.
7. Context Critic 判斷資訊是否足夠。  
   The context critic evaluates retrieval sufficiency.
8. 不足時執行 Corrective Retrieval。  
   Corrective retrieval runs when evidence is insufficient.
9. LLM 依 Context 生成 Answer。  
   The LLM generates an answer from collected evidence.
10. Answer Critic 評估 Groundedness / Relevance。  
    The answer critic evaluates groundedness and relevance.
11. 必要時 Revision 一次。  
    One revision may run when needed.
12. API 回傳 Answer、Citation、Plan、Review 與 Trace。  
    The API returns answer, citations, plan, review, and trace.

## Tool Boundary

Allowed tools:

- search_knowledge
- list_documents
- get_document_metadata
- delete_document

Not exposed:

- arbitrary shell
- arbitrary HTTP
- raw SQL
- filesystem write
- unrestricted Python/code execution
- cloud-administration credentials

## Approval Boundary

delete_document requires:

    admin role
        +
    same tenant
        +
    pending action
        +
    human approval
        +
    one-time consumption

Approval state is stored in Redis with an expiration TTL.

## Existing Platform Layers

Agent Layer still uses:

- OIDC / API Key Principal
- Tenant-scoped Qdrant
- Redis
- PostgreSQL Audit
- MinIO / S3
- LiteLLM
- OpenTelemetry
- Kubernetes / Helm
- Offline Deployment

## Production Direction

**繁體中文**  
後續若加入 MCP、Data Platform Tool 或 Infrastructure Tool，仍應透過相同 Tool Registry / Permission / Approval Pattern，而不是將任意 Tool Runtime 直接交給 LLM。

**English**  
Future MCP, data-platform, or infrastructure tools should use the same registry, permission, and approval pattern rather than exposing unrestricted tool runtimes directly to the LLM.
