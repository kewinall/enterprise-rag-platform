from app.agent.json_utils import extract_json_object
from app.agent.models import AnswerReview, ContextReview
from app.core.telemetry import get_tracer
from app.rag.llm import chat_completion

tracer = get_tracer(__name__)


def parse_context_review(raw: str) -> ContextReview:
    payload = extract_json_object(raw)
    return ContextReview(
        sufficient=bool(payload.get("sufficient", False)),
        reason=str(payload.get("reason", "")).strip(),
        follow_up_query=(
            str(payload.get("follow_up_query", "")).strip() or None
        ),
    )


def parse_answer_review(raw: str) -> AnswerReview:
    payload = extract_json_object(raw)
    groundedness = max(0.0, min(1.0, float(payload.get("groundedness", 0.0))))
    relevance = max(0.0, min(1.0, float(payload.get("relevance", 0.0))))
    return AnswerReview(
        passed=bool(payload.get("passed", False)),
        groundedness=groundedness,
        relevance=relevance,
        reason=str(payload.get("reason", "")).strip(),
        revision_instruction=(
            str(payload.get("revision_instruction", "")).strip() or None
        ),
    )


async def review_context(
    question: str,
    contexts: list[str],
) -> ContextReview:
    system = (
        "You are a retrieval critic. Return JSON only. Decide whether the retrieved "
        "contexts are sufficient to answer the question without guessing. If insufficient, "
        "provide one focused follow_up_query. Return keys: sufficient, reason, follow_up_query."
    )
    context_text = "\n\n".join(
        f"[{index}] {text}" for index, text in enumerate(contexts, start=1)
    )
    with tracer.start_as_current_span("agent.context_critic"):
        raw = await chat_completion(
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"Question:\n{question}\n\nContexts:\n{context_text}",
                },
            ],
            temperature=0.0,
        )
    return parse_context_review(raw)


async def review_answer(
    question: str,
    answer: str,
    contexts: list[str],
) -> AnswerReview:
    system = (
        "You are an answer critic for enterprise RAG. Return JSON only. "
        "Evaluate whether the answer is grounded in the supplied context and relevant "
        "to the question. Scores range from 0 to 1. Return keys: passed, groundedness, "
        "relevance, reason, revision_instruction. passed should normally require both "
        "scores to be at least 0.75."
    )
    context_text = "\n\n".join(
        f"[{index}] {text}" for index, text in enumerate(contexts, start=1)
    )
    with tracer.start_as_current_span("agent.answer_critic"):
        raw = await chat_completion(
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\nAnswer:\n{answer}\n\n"
                        f"Contexts:\n{context_text}"
                    ),
                },
            ],
            temperature=0.0,
        )
    return parse_answer_review(raw)
