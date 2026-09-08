from app.agent.json_utils import extract_json_object
from app.agent.models import AgentPlan, ToolCall
from app.core.config import get_settings
from app.core.telemetry import get_tracer
from app.rag.llm import chat_completion

tracer = get_tracer(__name__)

ALLOWED_TOOL_NAMES = {
    "search_knowledge",
    "list_documents",
    "get_document_metadata",
    "delete_document",
}


def parse_plan(raw: str) -> AgentPlan:
    payload = extract_json_object(raw)

    rewritten_query = str(payload.get("rewritten_query", "")).strip()
    if not rewritten_query:
        raise ValueError("Planner response must include rewritten_query")

    subqueries = tuple(
        str(item).strip()
        for item in payload.get("subqueries", [])
        if str(item).strip()
    )

    tool_calls = []
    for item in payload.get("tool_calls", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if name not in ALLOWED_TOOL_NAMES:
            continue
        arguments = item.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}
        tool_calls.append(ToolCall(name=name, arguments=arguments))

    return AgentPlan(
        intent=str(payload.get("intent", "knowledge_query")).strip() or "knowledge_query",
        rewritten_query=rewritten_query,
        subqueries=subqueries,
        tool_calls=tuple(tool_calls),
        answer_strategy=str(payload.get("answer_strategy", "")).strip(),
    )


async def plan_query(question: str) -> AgentPlan:
    settings = get_settings()
    system = (
        "You are the planner for an enterprise RAG agent. Return JSON only. "
        "You may choose tools only from: search_knowledge, list_documents, "
        "get_document_metadata, delete_document. "
        "search_knowledge arguments: query, top_k, mode. "
        "list_documents takes no arguments. "
        "get_document_metadata arguments: document_id. "
        "delete_document arguments: document_id and always requires human approval. "
        "For normal questions, include at least one search_knowledge tool call. "
        "Use subqueries only when the question requires multi-hop retrieval. "
        "Never invent a document_id."
    )
    user = (
        f"Question:\n{question}\n\n"
        "Return keys: intent, rewritten_query, subqueries, tool_calls, answer_strategy. "
        f"Use at most {settings.agent_max_subqueries} subqueries and "
        f"{settings.agent_max_tool_calls} tool calls."
    )
    with tracer.start_as_current_span("agent.plan"):
        raw = await chat_completion(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
        )
        plan = parse_plan(raw)

    return AgentPlan(
        intent=plan.intent,
        rewritten_query=plan.rewritten_query,
        subqueries=plan.subqueries[: settings.agent_max_subqueries],
        tool_calls=plan.tool_calls[: settings.agent_max_tool_calls],
        answer_strategy=plan.answer_strategy,
    )
