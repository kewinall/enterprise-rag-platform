# Evaluation

RAG quality should be measured before changing chunking, embeddings, top-k, rerankers or prompts.

The included CLI measures:
- Recall@K: whether the expected source appears in the top K
- MRR: how highly the expected source ranks

A mature evaluation suite should add:
- precision@K
- NDCG
- answer faithfulness
- answer relevance
- citation correctness
- latency percentiles
- token usage
- cost per request
- task success rate

Keep evaluation datasets synthetic or properly approved for public repositories.
