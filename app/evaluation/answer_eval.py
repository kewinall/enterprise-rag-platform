import json

from app.core.config import get_settings
from app.core.telemetry import get_tracer
from app.rag.llm import chat_completion

tracer = get_tracer(__name__)


def parse_evaluation_payload(raw: str) -> dict:
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Evaluator did not return a JSON object")

    payload = json.loads(raw[start : end + 1])
    result = {}
    for name in (
        "faithfulness",
        "answer_relevance",
        "context_relevance",
        "answer_correctness",
    ):
        value = payload.get(name)
        if value is None:
            result[name] = None
            continue
        score = float(value)
        result[name] = max(0.0, min(1.0, score))

    result["reason"] = str(payload.get("reason", "")).strip()
    return result


async def evaluate_answer(
    question: str,
    answer: str,
    contexts: list[str],
    reference: str | None = None,
) -> dict:
    settings = get_settings()
    evaluator_base_url = settings.evaluator_llm_base_url or settings.llm_base_url
    evaluator_api_key = settings.evaluator_llm_api_key or settings.llm_api_key
    evaluator_model = settings.evaluator_llm_model or settings.llm_model

    context_text = "\n\n".join(
        f"[{index}] {context}" for index, context in enumerate(contexts, start=1)
    )
    reference_text = reference or "(not provided)"

    system = (
        "You are a strict RAG evaluator. Return JSON only. Score each metric from 0 to 1. "
        "faithfulness measures whether answer claims are supported by retrieved contexts. "
        "answer_relevance measures whether the answer addresses the question. "
        "context_relevance measures whether the retrieved contexts are relevant to the question. "
        "answer_correctness compares the answer with the reference when a reference is provided; "
        "otherwise use null. Include a concise reason."
    )
    user = (
        f"Question:\n{question}\n\n"
        f"Answer:\n{answer}\n\n"
        f"Retrieved contexts:\n{context_text}\n\n"
        f"Reference answer:\n{reference_text}\n\n"
        "Return exactly these keys: faithfulness, answer_relevance, context_relevance, "
        "answer_correctness, reason."
    )

    with tracer.start_as_current_span("rag.evaluate_answer") as span:
        span.set_attribute("rag.evaluation.context_count", len(contexts))
        raw = await chat_completion(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            model=evaluator_model,
            base_url=evaluator_base_url,
            api_key=evaluator_api_key,
            temperature=0.0,
        )
        return parse_evaluation_payload(raw)
