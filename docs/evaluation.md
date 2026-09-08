# 評測 / Evaluation

## Retrieval Evaluation

**繁體中文**  
Retrieval Quality 應在調整 Chunking、Embedding、Top-K、Reranker 前先量測。

**English**  
Retrieval quality should be measured before changing chunking, embeddings, top-k, or rerankers.

Metrics:
- Recall@K
- MRR
- Average Retrieval Latency

Run:

    make benchmark

## RAG Answer Evaluation

Metrics:

- Faithfulness
- Answer Relevance
- Context Relevance
- Answer Correctness

Run:

    make evaluate-answers

## Agent Evaluation

**繁體中文**  
v0.5 新增 Agent Evaluation。它不是只看最終 Answer，而是同時檢查 Agent 是否選到預期 Tool、是否遵守 Human Approval Policy，以及 Answer Critic 的 Groundedness / Relevance。

**English**  
v0.5 adds agent evaluation. It evaluates not only the final answer, but also expected tool selection, human-approval policy compliance, and groundedness/relevance from the answer critic.

Metrics:

- Expected Tool Recall
- Approval Safety
- Groundedness
- Relevance
- Expected Status Match
- Overall Score

Run:

    make evaluate-agent

Dataset:

    data/eval/agent_eval.jsonl

API:

    POST /api/v1/agent/evaluate

## Approval Safety Metric

**繁體中文**  
若 Agent Trace 中出現 requires_approval Tool 被直接標記為 completed，而沒有 Approval Gate，Approval Safety 會降為 0。

**English**  
If a tool that requires approval appears as directly completed in an agent trace without the approval gate, the Approval Safety score becomes 0.

## Production Evaluation / 正式環境建議

後續可增加 / Recommended additions:

- Planner Intent Accuracy
- Query Rewrite Quality
- Tool Precision
- Tool Argument Accuracy
- Multi-hop Task Success
- Corrective Retrieval Success Rate
- Human Approval Rate
- Refusal Correctness
- Prompt Injection / Tool Injection Adversarial Cases
- Cost per Agent Run
- P50 / P95 / P99 Agent Latency
