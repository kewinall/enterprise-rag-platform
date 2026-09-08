from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.core.config import get_settings
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.lexical import bm25_rank
from app.retrieval.store import PayloadFilter, get_vector_store


@lru_cache
def get_reranker() -> CrossEncoder | None:
    settings = get_settings()
    if not settings.enable_reranker:
        return None
    return CrossEncoder(settings.reranker_model)


def hybrid_search(
    query: str,
    final_top_k: int | None = None,
    filters: PayloadFilter | None = None,
    mode: str = "hybrid",
) -> list[dict]:
    settings = get_settings()
    store = get_vector_store()
    limit = final_top_k or settings.final_top_k

    if mode == "vector":
        return store.search(query, limit=limit, filters=filters)
    if mode != "hybrid":
        raise ValueError(f"Unsupported retrieval mode: {mode}")

    vector_results = store.search(
        query,
        limit=settings.vector_top_k,
        filters=filters,
    )
    corpus = store.list_chunks(filters=filters)
    lexical_results = bm25_rank(query, corpus, limit=settings.lexical_top_k)

    vector_ids = [item["chunk_id"] for item in vector_results]
    lexical_ids = [item["chunk_id"] for item in lexical_results]
    fused = reciprocal_rank_fusion([vector_ids, lexical_ids])

    by_id = {item["chunk_id"]: item for item in corpus}
    by_id.update({item["chunk_id"]: item for item in vector_results})

    candidates = []
    for chunk_id, fusion_score in fused:
        if chunk_id in by_id:
            candidates.append({**by_id[chunk_id], "fusion_score": fusion_score})

    reranker = get_reranker()
    if reranker and candidates:
        pairs = [(query, item["text"]) for item in candidates]
        rerank_scores = reranker.predict(pairs)
        for item, score in zip(candidates, rerank_scores, strict=True):
            item["rerank_score"] = float(score)
        candidates.sort(key=lambda item: item["rerank_score"], reverse=True)

    return candidates[:limit]
