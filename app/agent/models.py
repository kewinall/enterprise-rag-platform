from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentPlan:
    intent: str
    rewritten_query: str
    subqueries: tuple[str, ...] = ()
    tool_calls: tuple[ToolCall, ...] = ()
    answer_strategy: str = ""


@dataclass(frozen=True)
class ContextReview:
    sufficient: bool
    reason: str
    follow_up_query: str | None = None


@dataclass(frozen=True)
class AnswerReview:
    passed: bool
    groundedness: float
    relevance: float
    reason: str
    revision_instruction: str | None = None
