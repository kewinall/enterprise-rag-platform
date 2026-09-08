from typing import Any

from app.agent.approval import create_approval_request
from app.agent.critic import review_answer, review_context
from app.agent.models import AgentPlan, ToolCall
from app.agent.planner import plan_query
from app.agent.tools import (
    ToolApprovalRequired,
    ToolPermissionError,
    execute_tool,
)
from app.core.config import get_settings
from app.core.security import Principal
from app.core.telemetry import get_tracer
from app.rag.llm import chat_completion, generate_answer

tracer = get_tracer(__name__)


def merge_retrieval_results(
    existing: list[dict],
    incoming: list[dict],
) -> list[dict]:
    by_id = {item["chunk_id"]: item for item in existing if item.get("chunk_id")}
    for item in incoming:
        chunk_id = item.get("chunk_id")
        if chunk_id and chunk_id not in by_id:
            by_id[chunk_id] = item
    return list(by_id.values())


def _tool_contexts(result: dict) -> list[str]:
    tool_name = result.get("tool")
    if tool_name == "search_knowledge":
        return [item["text"] for item in result.get("results", []) if item.get("text")]
    if tool_name == "list_documents":
        return [
            (
                f"Document: {item.get('source')} "
                f"(document_id={item.get('document_id')}, chunks={item.get('chunks')})"
            )
            for item in result.get("documents", [])
        ]
    if tool_name == "get_document_metadata":
        item = result.get("document") or {}
        return [
            (
                f"Document metadata: source={item.get('source')}, "
                f"document_id={item.get('document_id')}, chunks={item.get('chunks')}, "
                f"content_type={item.get('content_type')}"
            )
        ]
    return []


def _citations(results: list[dict]) -> list[dict]:
    citations = []
    for index, item in enumerate(results, start=1):
        citations.append(
            {
                "id": index,
                "document_id": item.get("document_id"),
                "source": item.get("source"),
                "chunk_id": item.get("chunk_id"),
                "page": item.get("page"),
                "section": item.get("section"),
            }
        )
    return citations


async def _revise_answer(
    question: str,
    answer: str,
    contexts: list[str],
    instruction: str,
) -> str:
    context_text = "\n\n".join(
        f"[{index}] {text}" for index, text in enumerate(contexts, start=1)
    )
    system = (
        "You revise enterprise RAG answers. Use only the supplied contexts. "
        "Do not add unsupported facts. Preserve source citations such as [1]."
    )
    return await chat_completion(
        [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\nCurrent answer:\n{answer}\n\n"
                    f"Critic instruction:\n{instruction}\n\nContexts:\n{context_text}"
                ),
            },
        ],
        temperature=0.0,
    )


async def run_agent(
    question: str,
    principal: Principal,
    *,
    top_k: int = 5,
    mode: str = "hybrid",
) -> dict:
    settings = get_settings()
    if not settings.agent_enabled:
        raise RuntimeError("Agentic RAG is disabled")

    trace: list[dict[str, Any]] = []
    retrieval_results: list[dict] = []
    contexts: list[str] = []
    approvals: list[dict] = []
    steps = 0

    with tracer.start_as_current_span("agent.run") as span:
        span.set_attribute("agent.tenant_id", principal.tenant_id)
        span.set_attribute("agent.max_steps", settings.agent_max_steps)

        try:
            plan = await plan_query(question)
        except ValueError as exc:
            plan = AgentPlan(
                intent="knowledge_query",
                rewritten_query=question,
                tool_calls=(
                    ToolCall(
                        name="search_knowledge",
                        arguments={"query": question, "top_k": top_k, "mode": mode},
                    ),
                ),
                answer_strategy="fallback grounded retrieval",
            )
            trace.append(
                {
                    "step": "plan",
                    "status": "degraded",
                    "reason": str(exc),
                    "fallback": "search_knowledge",
                }
            )
        else:
            trace.append(
                {
                    "step": "plan",
                    "status": "completed",
                    "intent": plan.intent,
                    "rewritten_query": plan.rewritten_query,
                    "subqueries": list(plan.subqueries),
                    "tool_calls": [
                        {"name": call.name, "arguments": call.arguments}
                        for call in plan.tool_calls
                    ],
                }
            )
        steps += 1

        tool_calls = list(plan.tool_calls)
        if not tool_calls:
            tool_calls = [
                ToolCall(
                    name="search_knowledge",
                    arguments={
                        "query": plan.rewritten_query,
                        "top_k": top_k,
                        "mode": mode,
                    },
                )
            ]

        for call in tool_calls[: settings.agent_max_tool_calls]:
            if steps >= settings.agent_max_steps:
                break
            arguments = dict(call.arguments)
            if call.name == "search_knowledge":
                arguments.setdefault("query", plan.rewritten_query)
                arguments.setdefault("top_k", top_k)
                arguments.setdefault("mode", mode)

            try:
                result = await execute_tool(
                    principal,
                    call.name,
                    arguments,
                )
            except ToolApprovalRequired:
                approval = await create_approval_request(
                    principal,
                    call.name,
                    arguments,
                )
                approvals.append(approval)
                trace.append(
                    {
                        "step": "tool",
                        "tool": call.name,
                        "status": "approval_required",
                        "action_id": approval["action_id"],
                    }
                )
            except (ToolPermissionError, ValueError, LookupError, KeyError) as exc:
                trace.append(
                    {
                        "step": "tool",
                        "tool": call.name,
                        "status": "rejected",
                        "reason": str(exc),
                    }
                )
            else:
                trace.append(
                    {
                        "step": "tool",
                        "tool": call.name,
                        "status": "completed",
                    }
                )
                contexts.extend(_tool_contexts(result))
                if call.name == "search_knowledge":
                    retrieval_results = merge_retrieval_results(
                        retrieval_results,
                        result.get("results", []),
                    )
            steps += 1

        if approvals:
            span.set_attribute("agent.approval_required", True)
            return {
                "status": "awaiting_approval",
                "answer": None,
                "approvals": approvals,
                "plan": {
                    "intent": plan.intent,
                    "rewritten_query": plan.rewritten_query,
                    "answer_strategy": plan.answer_strategy,
                },
                "trace": trace,
            }

        for subquery in plan.subqueries:
            if steps >= settings.agent_max_steps:
                break
            result = await execute_tool(
                principal,
                "search_knowledge",
                {"query": subquery, "top_k": top_k, "mode": mode},
            )
            contexts.extend(_tool_contexts(result))
            retrieval_results = merge_retrieval_results(
                retrieval_results,
                result.get("results", []),
            )
            trace.append(
                {
                    "step": "multi_hop_retrieval",
                    "query": subquery,
                    "results": len(result.get("results", [])),
                }
            )
            steps += 1

        context_review = None
        if contexts and steps < settings.agent_max_steps:
            try:
                context_review = await review_context(question, contexts)
            except ValueError as exc:
                trace.append(
                    {
                        "step": "context_critic",
                        "status": "degraded",
                        "reason": str(exc),
                    }
                )
            else:
                trace.append(
                    {
                        "step": "context_critic",
                        "status": "completed",
                        "sufficient": context_review.sufficient,
                        "reason": context_review.reason,
                        "follow_up_query": context_review.follow_up_query,
                    }
                )
            steps += 1

        if (
            context_review is not None
            and not context_review.sufficient
            and context_review.follow_up_query
            and steps < settings.agent_max_steps
        ):
            result = await execute_tool(
                principal,
                "search_knowledge",
                {
                    "query": context_review.follow_up_query,
                    "top_k": top_k,
                    "mode": mode,
                },
            )
            contexts.extend(_tool_contexts(result))
            retrieval_results = merge_retrieval_results(
                retrieval_results,
                result.get("results", []),
            )
            trace.append(
                {
                    "step": "corrective_retrieval",
                    "query": context_review.follow_up_query,
                    "results": len(result.get("results", [])),
                }
            )
            steps += 1

        if not contexts:
            return {
                "status": "completed",
                "answer": (
                    "No tenant-scoped evidence was found for this request. "
                    "The agent did not generate an unsupported answer."
                ),
                "citations": [],
                "plan": {
                    "intent": plan.intent,
                    "rewritten_query": plan.rewritten_query,
                    "answer_strategy": plan.answer_strategy,
                },
                "review": None,
                "trace": trace,
            }

        numbered_context = "\n\n".join(
            f"[{index}] {text}" for index, text in enumerate(contexts, start=1)
        )
        answer = await generate_answer(question, numbered_context)
        trace.append({"step": "generate", "status": "completed"})

        answer_review = None
        if steps < settings.agent_max_steps:
            try:
                answer_review = await review_answer(question, answer, contexts)
            except ValueError as exc:
                trace.append(
                    {
                        "step": "answer_critic",
                        "status": "degraded",
                        "reason": str(exc),
                    }
                )
            else:
                trace.append(
                    {
                        "step": "answer_critic",
                        "status": "completed",
                        "passed": answer_review.passed,
                        "groundedness": answer_review.groundedness,
                        "relevance": answer_review.relevance,
                        "reason": answer_review.reason,
                    }
                )
            steps += 1

        if (
            answer_review is not None
            and not answer_review.passed
            and answer_review.revision_instruction
            and settings.agent_enable_answer_revision
            and steps < settings.agent_max_steps
        ):
            answer = await _revise_answer(
                question,
                answer,
                contexts,
                answer_review.revision_instruction,
            )
            trace.append({"step": "revision", "status": "completed"})
            steps += 1

        span.set_attribute("agent.steps", steps)
        span.set_attribute("agent.retrieval_results", len(retrieval_results))

        return {
            "status": "completed",
            "answer": answer,
            "citations": _citations(retrieval_results[:top_k]),
            "plan": {
                "intent": plan.intent,
                "rewritten_query": plan.rewritten_query,
                "subqueries": list(plan.subqueries),
                "answer_strategy": plan.answer_strategy,
            },
            "review": (
                {
                    "passed": answer_review.passed,
                    "groundedness": answer_review.groundedness,
                    "relevance": answer_review.relevance,
                    "reason": answer_review.reason,
                }
                if answer_review is not None
                else None
            ),
            "trace": trace,
        }
