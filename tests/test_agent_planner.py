import pytest

from app.agent.planner import parse_plan


def test_parse_plan_filters_unknown_tools():
    plan = parse_plan(
        """{
          "intent":"knowledge_query",
          "rewritten_query":"security policy",
          "subqueries":["access control"],
          "tool_calls":[
            {"name":"search_knowledge","arguments":{"query":"security"}},
            {"name":"run_shell","arguments":{"command":"rm -rf /"}}
          ],
          "answer_strategy":"grounded summary"
        }"""
    )

    assert plan.rewritten_query == "security policy"
    assert [call.name for call in plan.tool_calls] == ["search_knowledge"]


def test_parse_plan_requires_rewritten_query():
    with pytest.raises(ValueError):
        parse_plan('{"intent":"knowledge_query","rewritten_query":""}')
