from time import perf_counter
from typing import Any

from app.agent.approval import create_approval_request
from app.agent.critic import review_answer, review_context
from app.agent.models import AgentPlan, ToolCall
from app.agent.planner import plan_query
from app.agent.state import get_agent_state_store
from app.agent.tools import (
    ToolApprovalRequired,
    ToolPermissionError,
    execute_tool,
)
from app.core.budget import BudgetExceeded, BudgetTracker, budget_scope
from app.core.config import get_settings
from app.core.metrics import (
    AGENT_BUDGET_EXCEEDED,
    AGENT_ESTIMATED_COST,
    AGENT_LATENCY,
    AGENT_LLM_TOKENS,
    AGENT_RUNS,
    AGENT_TOOL_CALLS,
)
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
    if tool_name == "get_platform_status":
        return [
            (
                f"Platform status: documents={result.get('documents')}, "
                f"chunks={result.get('chunks')}, "
                f"content_types={result.get('content_types')}"
            )
        ]
    if tool_name == "get_recent_audit_events":
        return [
            (
                f"Audit event: {item.get('method')} {item.get('path')} "
                f"status={item.get('status_code')} duration_ms={item.get('duration_ms')}"
            )
            for item in result.get("events", [])
        ]
    return []


def _citations(results: list[dict]) -> list[dict]:
    return [
        {
            "id": index,
            "document_id": item.get("document_id"),
            "source": item.get("source"),
            "chunk_id": item.get("chunk_id"),
            "page": item.get("page"),
            "section": item.get("section"),
        }
        for index, item in enumerate(results, start=1)
    ]


async def _revise_answer(
    question: str,
    answer: str,
    context_text: str,
    instruction: str,
) -> str:
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


async def _run_agent_core(
    question: str,
    principal: Principal,
    *,
    top_k: int,
    mode: str,
    seed_contexts: list[str] | None = None,
) -> dict:
    settings = get_settings()
    trace: list[dict[str, Any]] = []
    retrieval_results: list[dict] = []
    contexts: list[str] = list(seed_contexts or [])
    approvals: list[dict] = []
    steps = 0

    if seed_contexts:
        trace.append({"step": "memory", "status": "loaded", "items": len(seed_contexts)})

    with tracer.start_as_current_span("agent.run") as span:
        span.set_attribute("agent.tenant_id", principal.tenant_id)
        span.set_attribute("agent.max_steps", settings.agent_max_steps)

        try:
            plan = await plan_query(question)
        except (TypeError, ValueError) as exc:
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

        tool_calls = list(plan.tool_calls) or [
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
                result = await execute_tool(principal, call.name, arguments)
            except ToolApprovalRequired:
                approval = await create_approval_request(
                    principal,
                    call.name,
                    arguments,
                )
                approvals.append(approval)
                AGENT_TOOL_CALLS.labels(call.name, "approval_required").inc()
                trace.append(
                    {
                        "step": "tool",
                        "tool": call.name,
                        "status": "approval_required",
                        "action_id": approval["action_id"],
                    }
                )
            except (ToolPermissionError, ValueError, LookupError, KeyError) as exc:
                AGENT_TOOL_CALLS.labels(call.name, "rejected").inc()
                trace.append(
                    {
                        "step": "tool",
                        "tool": call.name,
                        "status": "rejected",
                        "reason": str(exc),
                    }
                )
            else:
                AGENT_TOOL_CALLS.labels(call.name, "completed").inc()
                trace.append(
                    {"step": "tool", "tool": call.name, "status": "completed"}
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
            AGENT_TOOL_CALLS.labels("search_knowledge", "completed").inc()
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
            except (TypeError, ValueError) as exc:
                trace.append(
                    {"step": "context_critic", "status": "degraded", "reason": str(exc)}
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
            AGENT_TOOL_CALLS.labels("search_knowledge", "completed").inc()
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

        retrieved_texts = [
            item["text"] for item in retrieval_results if item.get("text")
        ]
        retrieved_set = set(retrieved_texts)
        auxiliary_contexts = [item for item in contexts if item not in retrieved_set]
        context_parts = []
        if auxiliary_contexts:
            context_parts.append(
                "Auxiliary context (not citation-indexed):\n"
                + "\n".join(f"- {item}" for item in auxiliary_contexts)
            )
        if retrieved_texts:
            context_parts.append(
                "Citable retrieved evidence:\n"
                + "\n\n".join(
                    f"[{index}] {text}"
                    for index, text in enumerate(retrieved_texts, start=1)
                )
            )
        generation_context = "\n\n".join(context_parts)
        answer = await generate_answer(question, generation_context)
        trace.append({"step": "generate", "status": "completed"})
        steps += 1

        answer_review = None
        if steps < settings.agent_max_steps:
            try:
                answer_review = await review_answer(question, answer, contexts)
            except (TypeError, ValueError) as exc:
                trace.append(
                    {"step": "answer_critic", "status": "degraded", "reason": str(exc)}
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
                generation_context,
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


async def run_agent(
    question: str,
    principal: Principal,
    *,
    top_k: int = 5,
    mode: str = "hybrid",
    session_id: str | None = None,
    use_memory: bool = True,
) -> dict:
    settings = get_settings()
    if not settings.agent_enabled:
        raise RuntimeError("Agentic RAG is disabled")

    started = perf_counter()
    tracker = BudgetTracker(
        max_tokens=settings.agent_budget_max_tokens,
        max_cost_usd=settings.agent_budget_max_cost_usd,
        input_cost_per_1k=settings.agent_input_cost_per_1k,
        output_cost_per_1k=settings.agent_output_cost_per_1k,
    )
    state_store = get_agent_state_store()
    seed_contexts: list[str] = []

    if session_id is not None:
        session = await state_store.get_session(session_id, principal.tenant_id)
        if session is None:
            raise LookupError("Agent session not found")
        if use_memory:
            memories = await state_store.list_memory(session_id, principal.tenant_id)
            seed_contexts = [
                f"User-approved session memory [{item['memory_key']}]: {item['memory_value']}"
                for item in memories
            ]

    try:
        with budget_scope(tracker):
            result = await _run_agent_core(
                question,
                principal,
                top_k=top_k,
                mode=mode,
                seed_contexts=seed_contexts,
            )
    except BudgetExceeded as exc:
        AGENT_BUDGET_EXCEEDED.inc()
        result = {
            "status": "budget_exceeded",
            "answer": None,
            "citations": [],
            "trace": [{"step": "budget", "status": "exceeded", "reason": str(exc)}],
        }

    budget = tracker.snapshot()
    result["budget"] = budget
    result["session_id"] = session_id

    if session_id is not None:
        checkpoint = await state_store.save_checkpoint(
            session_id,
            principal.tenant_id,
            {
                "question": question,
                "result": result,
            },
        )
        result["checkpoint_id"] = checkpoint["checkpoint_id"]

    AGENT_RUNS.labels(str(result.get("status", "unknown"))).inc()
    AGENT_LLM_TOKENS.labels("prompt").inc(budget["prompt_tokens"])
    AGENT_LLM_TOKENS.labels("completion").inc(budget["completion_tokens"])
    AGENT_ESTIMATED_COST.inc(budget["estimated_cost_usd"])
    AGENT_LATENCY.observe(perf_counter() - started)
    return result
