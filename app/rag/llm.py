import httpx

from app.core.config import get_settings


async def generate_answer(question: str, context: str) -> str:
    settings = get_settings()
    system = (
        "You are an enterprise RAG assistant. Answer only from the supplied context. "
        "If the context is insufficient, say so. Cite sources using [1], [2], etc."
    )
    payload = {
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Question:\n{question}\n\nContext:\n{context}"},
        ],
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
