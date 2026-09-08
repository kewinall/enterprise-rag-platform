import argparse
import json
from pathlib import Path

from app.evaluation.metrics import recall_at_k, reciprocal_rank
from app.retrieval.hybrid import hybrid_search


def evaluate(dataset: Path, k: int, mode: str) -> dict:
    cases = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    recalls = []
    reciprocal_ranks = []

    for case in cases:
        results = hybrid_search(case["question"], final_top_k=k, mode=mode)
        sources = [result["source"] for result in results]
        expected = case["expected_source"]
        recalls.append(recall_at_k(sources, expected, k))
        reciprocal_ranks.append(reciprocal_rank(sources, expected))

    total = len(cases) or 1
    return {
        "mode": mode,
        "cases": len(cases),
        f"recall@{k}": sum(recalls) / total,
        "mrr": sum(reciprocal_ranks) / total,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--mode", choices=["vector", "hybrid"], default="hybrid")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.dataset, args.k, args.mode), indent=2))
