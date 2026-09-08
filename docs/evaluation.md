# Evaluation

RAG quality should be measured before changing chunking, embeddings, top-k, rerankers or prompts.

## Included metrics

The retrieval utilities measure:

- Recall@K: whether the expected source appears in the top K
- MRR: how highly the expected source ranks
- Average latency in milliseconds for benchmark runs

## Evaluate one retrieval mode

    python scripts/evaluate_retrieval.py       --dataset data/eval/retrieval_eval.jsonl       --k 5       --mode hybrid

Supported modes are vector and hybrid.

## Compare vector and hybrid retrieval

    python scripts/benchmark_retrieval.py       --dataset data/eval/retrieval_eval.jsonl       --k 5

The benchmark runs the same evaluation cases through both retrieval modes and reports
Recall@K, MRR and average latency. Ingest both sample handbooks before running it.

## Production evaluation

A mature evaluation suite should add:

- precision@K and NDCG
- answer faithfulness
- answer relevance
- citation correctness
- latency percentiles
- token usage and cost
- task success rate

Keep evaluation datasets synthetic or properly approved for public repositories.
