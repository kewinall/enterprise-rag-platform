import argparse
import asyncio
import json
from pathlib import Path

from app.agent.orchestrator import run_agent
from app.core.security import Principal, ROLE_VIEWER
from app.evaluation.agent_eval import evaluate_agent_result


async def run(dataset: Path, top_k: int, mode: str) -> dict:
    cases = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    principal = Principal(
        subject="agent-eval",
        tenant_id="demo",
        roles=frozenset({ROLE_VIEWER}),
        auth_mode="api_key",
    )

    rows = []
    for case in cases:
        result = await run_agent(
            case["question"],
            principal,
            top_k=top_k,
            mode=mode,
        )
        evaluation = evaluate_agent_result(
            result,
            expected_tools=case.get("expected_tools", []),
            expected_status=case.get("expected_status"),
        )
        rows.append(
            {
                "question": case["question"],
                "result": result,
                "evaluation": evaluation,
            }
        )

    overall_values = [
        row["evaluation"]["overall"]
        for row in rows
        if row["evaluation"]["overall"] is not None
    ]
    return {
        "cases": len(rows),
        "average_overall": (
            round(sum(overall_values) / len(overall_values), 4)
            if overall_values
            else None
        ),
        "results": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--mode", choices=["vector", "hybrid"], default="hybrid")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.dataset, args.top_k, args.mode)), indent=2))
