from collections.abc import Sequence

import httpx

from app.core.config import get_settings
from app.core.telemetry import get_tracer

tracer = get_tracer(__name__)


async def chat_completion(
    messages: Sequence[dict[str, str]],
    *,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
) -> str:
    settings = get_settings()
    resolved_model = model or settings.llm_model
    resolved_base_url = base_url or settings.llm_base_url
    resolved_api_key = api_key or settings.llm_api_key
    resolved_temperature = (
        settings.llm_temperature if temperature is None else temperature
    )

    payload = {
        "model": resolved_model,
        "temperature": resolved_temperature,
        "messages": list(messages),
    }
    headers = {"Authorization": f"Bearer {resolved_api_key}"}

    with tracer.start_as_current_span("llm.chat_completion") as span:
        span.set_attribute("gen_ai.request.model", resolved_model)
        span.set_attribute("gen_ai.operation.name", "chat")
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{resolved_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            span.set_attribute("http.response.status_code", response.status_code)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


async def generate_answer(question: str, context: str) -> str:
    system = (
        "You are an enterprise RAG assistant. Answer only from the supplied context. "
        "If the context is insufficient, say so. Cite sources using [1], [2], etc."
    )
    return await chat_completion(
        [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nContext:\n{context}",
            },
        ]
    )
