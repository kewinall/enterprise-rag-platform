import argparse
import json
import math
from pathlib import Path
from time import perf_counter

from app.evaluation.metrics import recall_at_k, reciprocal_rank
from app.retrieval.hybrid import hybrid_search


def _expected_sources(case: dict) -> list[str]:
    values = case.get("expected_sources")
    if values:
        return [str(value) for value in values]
    value = case.get("expected_source")
    if value:
        return [str(value)]
    raise ValueError(f"case {case.get('case_id', '<unknown>')} has no expected source")


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(percentile * len(ordered)) - 1))
    return ordered[index]


def benchmark_mode(dataset: Path, k: int, mode: str, tenant_id: str | None = None) -> dict:
    cases = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines() if line.strip()]
    recalls = []
    reciprocal_ranks = []
    latencies_ms = []
    failures = []
    filters = {"tenant_id": tenant_id} if tenant_id else None

    for case in cases:
        started = perf_counter()
        results = hybrid_search(case["question"], final_top_k=k, mode=mode, filters=filters)
        latencies_ms.append((perf_counter() - started) * 1000)

        sources = [result["source"] for result in results]
        expected = _expected_sources(case)
        recall = max(recall_at_k(sources, source, k) for source in expected)
        rr = max(reciprocal_rank(sources, source) for source in expected)
        recalls.append(recall)
        reciprocal_ranks.append(rr)
        if recall == 0:
            failures.append(
                {
                    "case_id": case.get("case_id"),
                    "question": case["question"],
                    "expected_sources": expected,
                    "returned_sources": sources,
                }
            )

    total = len(cases) or 1
    return {
        "mode": mode,
        "cases": len(cases),
        f"recall@{k}": round(sum(recalls) / total, 4),
        "mrr": round(sum(reciprocal_ranks) / total, 4),
        "avg_latency_ms": round(sum(latencies_ms) / total, 2),
        "p50_latency_ms": round(_percentile(latencies_ms, 0.50), 2),
        "p95_latency_ms": round(_percentile(latencies_ms, 0.95), 2),
        "failures": failures,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--tenant-id", default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    report = {
        "dataset": str(args.dataset),
        "top_k": args.k,
        "tenant_id": args.tenant_id,
        "vector": benchmark_mode(args.dataset, args.k, "vector", args.tenant_id),
        "lexical": benchmark_mode(args.dataset, args.k, "lexical", args.tenant_id),
        "hybrid": benchmark_mode(args.dataset, args.k, "hybrid", args.tenant_id),
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
