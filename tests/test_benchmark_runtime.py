import json

import pytest

from scripts import benchmark_retrieval as b


class FakeFeedbackWriter:
    def __init__(self):
        self.events = []

    def emit_search(self, *, query_id, results, explicit_feedback=None):
        self.events.append(
            {
                "query_id": query_id,
                "results": results,
                "explicit_feedback": explicit_feedback,
            }
        )
        return "evt-test"


def test_warmup_excluded_and_repeated_metrics(tmp_path, monkeypatch):
    dataset = tmp_path / "cases.jsonl"
    dataset.write_text(
        json.dumps({"case_id": "a", "question": "q", "expected_sources": ["a"]}) + "\n"
    )
    calls = []

    def search(*args, **kwargs):
        calls.append(kwargs)
        return [
            {"source": "x", "document_id": "ekb.test.x"},
            {"source": "a", "document_id": "ekb.test.a"},
        ]

    monkeypatch.setattr(b, "hybrid_search", search)
    times = iter([0, 0.010, 1, 1.020, 2, 2.030])
    monkeypatch.setattr(b, "perf_counter", lambda: next(times))
    writer = FakeFeedbackWriter()
    r = b.benchmark_mode(
        dataset,
        5,
        "vector",
        "tenant",
        warmup=2,
        runs=3,
        feedback_writer=writer,
    )
    assert len(calls) == 5
    assert all(c["filters"] == {"tenant_id": "tenant"} for c in calls)
    assert len(r["observations"]) == 3
    assert r["recall@5"] == 1 and r["mrr"] == 0.5
    assert r["avg_latency_ms"] == 20 and r["p50_latency_ms"] == 20
    assert r["p95_latency_ms"] == 30
    assert [o["run"] for o in r["observations"]] == [1, 2, 3]
    assert [event["query_id"] for event in writer.events] == [
        "benchmark-vector-a-run-1",
        "benchmark-vector-a-run-2",
        "benchmark-vector-a-run-3",
    ]


def test_empty_dataset_rejected(tmp_path):
    dataset = tmp_path / "empty.jsonl"
    dataset.write_text("")
    with pytest.raises(ValueError):
        b.benchmark_mode(dataset, 5, "vector")
