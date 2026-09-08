from app.core.cache import get_cache_store, make_rag_cache_key
from app.core.config import get_settings
from app.core.telemetry import get_tracer
from app.rag.llm import generate_answer
from app.retrieval.hybrid import hybrid_search
from app.retrieval.store import PayloadFilter

tracer = get_tracer(__name__)


async def answer_question(
    question: str,
    top_k: int | None = None,
    filters: PayloadFilter | None = None,
    mode: str = "hybrid",
    use_cache: bool = True,
) -> dict:
    settings = get_settings()
    limit = top_k or settings.final_top_k
    cache = get_cache_store()
    cache_key = make_rag_cache_key(
        question=question,
        top_k=limit,
        mode=mode,
        filters=filters,
        model=settings.llm_model,
    )

    if use_cache:
        cached = await cache.get_json(cache_key)
        if cached is not None:
            cached["cache"] = {"hit": True, "ttl_seconds": settings.cache_ttl_seconds}
            return cached

    with tracer.start_as_current_span("rag.answer_question") as span:
        span.set_attribute("rag.retrieval.mode", mode)
        span.set_attribute("rag.retrieval.top_k", limit)
        results = hybrid_search(
            question,
            final_top_k=limit,
            filters=filters,
            mode=mode,
        )

        context_parts = []
        citations = []
        for idx, item in enumerate(results, start=1):
            location = [item["source"]]
            if item.get("page") is not None:
                location.append(f"page {item['page']}")
            if item.get("section"):
                location.append(f"section {item['section']}")
            context_parts.append(f"[{idx}] Source: {', '.join(location)}\n{item['text']}")
            citations.append(
                {
                    "id": idx,
                    "document_id": item["document_id"],
                    "source": item["source"],
                    "chunk_id": item["chunk_id"],
                    "page": item.get("page"),
                    "section": item.get("section"),
                }
            )

        answer = await generate_answer(question, "\n\n".join(context_parts))
        response = {
            "answer": answer,
            "citations": citations,
            "retrieval": {
                "candidates": len(results),
                "used": len(results),
                "mode": mode,
                "filters": filters or {},
            },
            "cache": {"hit": False, "ttl_seconds": settings.cache_ttl_seconds},
        }
        span.set_attribute("rag.retrieval.result_count", len(results))

    if use_cache:
        await cache.set_json(cache_key, response, settings.cache_ttl_seconds)
    return response
