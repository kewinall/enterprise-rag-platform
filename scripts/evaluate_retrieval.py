import argparse
import json
from pathlib import Path

from app.retrieval.store import get_vector_store


def evaluate(dataset: Path, k: int) -> dict:
    cases = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    hits = 0
    reciprocal_ranks = []

    for case in cases:
        results = get_vector_store().search(case["question"], limit=k)
        ids = [result["source"] for result in results]
        expected = case["expected_source"]
        if expected in ids:
            hits += 1
            reciprocal_ranks.append(1 / (ids.index(expected) + 1))
        else:
            reciprocal_ranks.append(0)

    total = len(cases) or 1
    return {
        "cases": len(cases),
        f"recall@{k}": hits / total,
        "mrr": sum(reciprocal_ranks) / total,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.dataset, args.k), indent=2))
