import argparse
import json
from pathlib import Path
from time import perf_counter

from app.evaluation.metrics import recall_at_k, reciprocal_rank
from app.retrieval.hybrid import hybrid_search


def benchmark_mode(dataset: Path, k: int, mode: str) -> dict:
    cases = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    recalls = []
    reciprocal_ranks = []
    latencies_ms = []

    for case in cases:
        started = perf_counter()
        results = hybrid_search(case["question"], final_top_k=k, mode=mode)
        latencies_ms.append((perf_counter() - started) * 1000)

        sources = [result["source"] for result in results]
        expected = case["expected_source"]
        recalls.append(recall_at_k(sources, expected, k))
        reciprocal_ranks.append(reciprocal_rank(sources, expected))

    total = len(cases) or 1
    return {
        "mode": mode,
        "cases": len(cases),
        f"recall@{k}": round(sum(recalls) / total, 4),
        "mrr": round(sum(reciprocal_ranks) / total, 4),
        "avg_latency_ms": round(sum(latencies_ms) / total, 2),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    report = {
        "vector": benchmark_mode(args.dataset, args.k, "vector"),
        "hybrid": benchmark_mode(args.dataset, args.k, "hybrid"),
    }
    print(json.dumps(report, indent=2))
