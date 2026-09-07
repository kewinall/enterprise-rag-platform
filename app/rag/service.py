from app.core.config import get_settings
from app.rag.llm import generate_answer
from app.retrieval.hybrid import hybrid_search


async def answer_question(question: str, top_k: int | None = None) -> dict:
    settings = get_settings()
    limit = top_k or settings.final_top_k
    results = hybrid_search(question, final_top_k=limit)

    context_parts = []
    citations = []
    for idx, item in enumerate(results, start=1):
        context_parts.append(f"[{idx}] Source: {item['source']}\n{item['text']}")
        citations.append(
            {"id": idx, "source": item["source"], "chunk_id": item["chunk_id"]}
        )

    answer = await generate_answer(question, "\n\n".join(context_parts))
    return {
        "answer": answer,
        "citations": citations,
        "retrieval": {"candidates": len(results), "used": len(results), "mode": "hybrid"},
    }
