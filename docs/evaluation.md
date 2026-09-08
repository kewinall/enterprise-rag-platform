# 評測 / Evaluation

## 為什麼需要 Evaluation / Why evaluation matters

**繁體中文**  
在調整 Chunking、Embedding、Top-K、Reranker 或 Prompt 前，應先以固定 Evaluation Dataset 量測品質，避免只憑主觀回答判斷 RAG 是否改善。

**English**  
RAG quality should be measured with a stable evaluation dataset before changing chunking, embeddings, top-k, rerankers, or prompts.

## 已提供的 Metrics / Included metrics

- Recall@K — Expected Source 是否出現在 Top K / whether the expected source appears in the top K.
- MRR — Expected Source 排名越前分數越高 / how highly the expected source ranks.
- Average Latency — 平均 Retrieval Latency（ms）/ average retrieval latency in milliseconds.

## 評估單一 Retrieval Mode / Evaluate one retrieval mode

    python scripts/evaluate_retrieval.py \
      --dataset data/eval/retrieval_eval.jsonl \
      --k 5 \
      --mode hybrid

支援 / Supported: vector, hybrid.

## 比較 Vector 與 Hybrid / Compare vector and hybrid retrieval

    python scripts/benchmark_retrieval.py \
      --dataset data/eval/retrieval_eval.jsonl \
      --k 5

**繁體中文**  
Benchmark 使用相同 Evaluation Cases 分別跑 Vector 與 Hybrid，輸出 Recall@K、MRR 與 Average Latency。執行前請先匯入兩份 Synthetic Handbook。

**English**  
The benchmark runs the same evaluation cases through both retrieval modes and reports Recall@K, MRR, and average latency. Ingest both sample handbooks before running it.

## Production Evaluation / 正式環境建議

建議後續加入 / Recommended additions:

- Precision@K / NDCG
- Answer Faithfulness
- Answer Relevance
- Citation Correctness
- Latency Percentile
- Token Usage / Cost
- Task Success Rate

**繁體中文**：公開 Repository 的 Evaluation Dataset 應使用 Synthetic Data 或經核准可公開資料。  
**English**: Keep evaluation datasets synthetic or properly approved for public repositories.
