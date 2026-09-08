import argparse
import asyncio
import json
from pathlib import Path

from app.evaluation.answer_eval import evaluate_answer
from app.rag.llm import generate_answer
from app.retrieval.hybrid import hybrid_search


async def run(dataset: Path, k: int, mode: str) -> dict:
    cases = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    rows = []

    for case in cases:
        results = hybrid_search(case["question"], final_top_k=k, mode=mode)
        contexts = [item["text"] for item in results]
        numbered_context = "\n\n".join(
            f"[{index}] {text}" for index, text in enumerate(contexts, start=1)
        )
        answer = await generate_answer(case["question"], numbered_context)
        scores = await evaluate_answer(
            question=case["question"],
            answer=answer,
            contexts=contexts,
            reference=case.get("reference"),
        )
        rows.append(
            {
                "question": case["question"],
                "answer": answer,
                "scores": scores,
            }
        )

    metric_names = [
        "faithfulness",
        "answer_relevance",
        "context_relevance",
        "answer_correctness",
    ]
    summary = {}
    for metric in metric_names:
        values = [
            row["scores"][metric]
            for row in rows
            if row["scores"].get(metric) is not None
        ]
        summary[metric] = round(sum(values) / len(values), 4) if values else None

    return {"mode": mode, "cases": len(rows), "summary": summary, "results": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--mode", choices=["vector", "hybrid"], default="hybrid")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.dataset, args.k, args.mode)), indent=2))
