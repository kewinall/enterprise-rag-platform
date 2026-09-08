import pytest

from app.core.budget import BudgetExceeded, BudgetTracker, estimate_tokens


def test_estimate_tokens_is_positive():
    assert estimate_tokens("hello") >= 1


def test_budget_tracker_blocks_projected_token_overflow():
    tracker = BudgetTracker(
        max_tokens=10,
        max_cost_usd=0,
        input_cost_per_1k=0,
        output_cost_per_1k=0,
    )
    with pytest.raises(BudgetExceeded):
        tracker.preflight(11)


def test_budget_snapshot_tracks_usage():
    tracker = BudgetTracker(
        max_tokens=100,
        max_cost_usd=1,
        input_cost_per_1k=0.01,
        output_cost_per_1k=0.02,
    )
    tracker.record(20, 10)
    snapshot = tracker.snapshot()
    assert snapshot["total_tokens"] == 30
    assert snapshot["llm_calls"] == 1
