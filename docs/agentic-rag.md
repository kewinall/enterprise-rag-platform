# Agentic RAG / Agentic RAG 設計

## 目的 / Purpose

**繁體中文**  
Standard RAG 對單次 Retrieval 很有效，但複雜問題可能需要拆解、重新查詢、判斷 Context 是否足夠，再決定是否修正答案。v0.5 以可測試 State Machine 實作這些 Agentic 行為。

**English**  
Standard RAG works well for single-pass retrieval, but complex questions may require decomposition, query refinement, context sufficiency checks, and answer revision. v0.5 implements these behaviors as a testable state machine.

## State Machine

    Plan
      |
      v
    Tool Calls
      |
      v
    Multi-hop Retrieval
      |
      v
    Context Critic
      |
      +--> Corrective Retrieval
      |
      v
    Generate
      |
      v
    Answer Critic
      |
      +--> Revision
      |
      v
    Final Answer

## Query Planner

Planner Output:

- intent
- rewritten_query
- subqueries
- tool_calls
- answer_strategy

**繁體中文**  
Planner 只能從 Server Allowlist 選 Tool；未知 Tool 會在 parse 階段被丟棄。

**English**  
The planner may select tools only from the server allowlist. Unknown tools are discarded during parsing.

## Multi-hop Retrieval

**繁體中文**  
若問題需要多段證據，Planner 可以產生最多 AGENT_MAX_SUBQUERIES 個 Subquery。每個 Subquery 仍使用相同 Tenant Scope 與 Retrieval Mode。

**English**  
For questions requiring multiple evidence paths, the planner may emit up to AGENT_MAX_SUBQUERIES subqueries. Every subquery still uses the same tenant scope and retrieval mode.

## Corrective Retrieval

Context Critic returns:

- sufficient
- reason
- follow_up_query

若 insufficient 且仍有 Step Budget，Agent 執行一次 Focused Follow-up Search。  
If evidence is insufficient and step budget remains, the agent performs one focused follow-up search.

## Answer Critic

Metrics:

- groundedness
- relevance
- passed
- revision_instruction

若 Critic 不通過且 AGENT_ENABLE_ANSWER_REVISION=true，Agent 最多修訂一次。  
If the critic fails and answer revision is enabled, the agent performs at most one revision.

## Safe Degradation

**繁體中文**  
Planner JSON 無法解析時會 fallback 到 tenant-scoped search。Critic JSON 無法解析時只跳過該 Critic，不會放寬 Tool Policy。

**English**  
Invalid planner JSON falls back to tenant-scoped search. Invalid critic JSON skips only that critic step and never relaxes tool policy.

## Trace

API Response 包含 Trace，可看到：

- plan
- tool completed / rejected / approval_required
- multi_hop_retrieval
- context_critic
- corrective_retrieval
- generate
- answer_critic
- revision

這讓 Agent Behavior 可以被 Debug、Audit 與 Evaluation。  
This makes agent behavior debuggable, auditable, and evaluable.
