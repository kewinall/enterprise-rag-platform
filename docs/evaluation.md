# 評測 / Evaluation

## Retrieval Evaluation

**繁體中文**  
Retrieval Quality 應在調整 Chunking、Embedding、Top-K、Reranker 前先量測，避免只看主觀回答。

**English**  
Retrieval quality should be measured before changing chunking, embeddings, top-k, or rerankers.

Metrics:
- Recall@K
- MRR
- Average Retrieval Latency

執行 / Run:

    make benchmark

## RAGAS-style Answer Evaluation

**繁體中文**  
v0.3 新增 LLM-as-a-Judge Evaluator。此實作採用 RAGAS 常見概念，但不硬依賴 Ragas Python Package，降低 Framework API 版本變動與額外 Dependency 對主 Runtime 的影響。

**English**  
v0.3 adds an LLM-as-a-Judge evaluator using common RAGAS-style concepts without hard-depending on the Ragas Python package, reducing framework API churn and runtime dependency surface.

Metrics:

- **Faithfulness** — Answer Claims 是否由 Retrieved Context 支持 / whether answer claims are supported by retrieved context.
- **Answer Relevance** — Answer 是否回應原 Question / whether the answer addresses the question.
- **Context Relevance** — Retrieved Context 是否與 Question 相關 / whether contexts are relevant.
- **Answer Correctness** — 有 Reference 時比較 Answer / compares against a reference when provided.

API:

    POST /api/v1/evaluate/answer

CLI:

    make evaluate-answers

## Evaluator Model

**繁體中文**  
預設 Evaluator 使用與 RAG Generation 相同的 LLM Gateway / Model。可透過 EVALUATOR_LLM_BASE_URL、EVALUATOR_LLM_API_KEY、EVALUATOR_LLM_MODEL 指定獨立 Judge Model。

**English**  
By default, evaluation uses the same gateway/model as generation. EVALUATOR_LLM_BASE_URL, EVALUATOR_LLM_API_KEY, and EVALUATOR_LLM_MODEL can point to a separate judge model.

## Production Evaluation / 正式環境建議

後續可加入 / Recommended additions:

- Context Precision / Recall
- NDCG
- Citation Correctness
- Latency P50 / P95 / P99
- Token Usage / Cost
- Task Success Rate
- Human Review Sample
