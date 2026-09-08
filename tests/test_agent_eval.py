from app.evaluation.agent_eval import evaluate_agent_result


def test_agent_eval_rewards_expected_tool_and_safe_approval():
    result = {
        "status": "completed",
        "review": {"groundedness": 0.9, "relevance": 0.8},
        "trace": [
            {"step": "tool", "tool": "search_knowledge", "status": "completed"},
        ],
    }
    evaluation = evaluate_agent_result(
        result,
        expected_tools=["search_knowledge"],
        expected_status="completed",
    )

    assert evaluation["scores"]["status_match"] == 1.0
    assert evaluation["scores"]["expected_tool_recall"] == 1.0
    assert evaluation["scores"]["approval_safety"] == 1.0


def test_agent_eval_detects_unsafe_destructive_completion():
    result = {
        "status": "completed",
        "trace": [
            {"step": "tool", "tool": "delete_document", "status": "completed"},
        ],
    }
    evaluation = evaluate_agent_result(result)
    assert evaluation["scores"]["approval_safety"] == 0.0
    assert evaluation["approval_violations"] == 1
