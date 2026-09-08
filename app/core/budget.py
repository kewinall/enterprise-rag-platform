from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass


class BudgetExceeded(RuntimeError):
    pass


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


@dataclass
class BudgetTracker:
    max_tokens: int
    max_cost_usd: float
    input_cost_per_1k: float
    output_cost_per_1k: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    llm_calls: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @property
    def estimated_cost_usd(self) -> float:
        return (
            self.prompt_tokens / 1000 * self.input_cost_per_1k
            + self.completion_tokens / 1000 * self.output_cost_per_1k
        )

    def preflight(self, prompt_tokens: int) -> None:
        if self.max_tokens > 0 and self.total_tokens + prompt_tokens > self.max_tokens:
            raise BudgetExceeded("Agent token budget would be exceeded")
        projected = self.estimated_cost_usd + prompt_tokens / 1000 * self.input_cost_per_1k
        if self.max_cost_usd > 0 and projected > self.max_cost_usd:
            raise BudgetExceeded("Agent cost budget would be exceeded")

    def record(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.llm_calls += 1
        if self.max_tokens > 0 and self.total_tokens > self.max_tokens:
            raise BudgetExceeded("Agent token budget exceeded")
        if self.max_cost_usd > 0 and self.estimated_cost_usd > self.max_cost_usd:
            raise BudgetExceeded("Agent cost budget exceeded")

    def snapshot(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "llm_calls": self.llm_calls,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
            "max_tokens": self.max_tokens,
            "max_cost_usd": self.max_cost_usd,
        }


_budget_tracker: ContextVar[BudgetTracker | None] = ContextVar(
    "agent_budget_tracker",
    default=None,
)


@contextmanager
def budget_scope(tracker: BudgetTracker):
    token = _budget_tracker.set(tracker)
    try:
        yield tracker
    finally:
        _budget_tracker.reset(token)


def get_current_budget_tracker() -> BudgetTracker | None:
    return _budget_tracker.get()
