from app.core.config import get_settings
from app.rag.llm import generate_answer
from app.retrieval.hybrid import hybrid_search
from app.retrieval.store import PayloadFilter


async def answer_question(
    question: str,
    top_k: int | None = None,
    filters: PayloadFilter | None = None,
    mode: str = "hybrid",
) -> dict:
    settings = get_settings()
    limit = top_k or settings.final_top_k
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
    return {
        "answer": answer,
        "citations": citations,
        "retrieval": {
            "candidates": len(results),
            "used": len(results),
            "mode": mode,
            "filters": filters or {},
        },
    }
