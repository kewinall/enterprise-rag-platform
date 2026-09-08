from app.agent.orchestrator import merge_retrieval_results


def test_merge_retrieval_results_deduplicates_chunks():
    existing = [
        {"chunk_id": "a", "text": "first"},
        {"chunk_id": "b", "text": "second"},
    ]
    incoming = [
        {"chunk_id": "b", "text": "duplicate"},
        {"chunk_id": "c", "text": "third"},
    ]

    merged = merge_retrieval_results(existing, incoming)

    assert [item["chunk_id"] for item in merged] == ["a", "b", "c"]
    assert merged[1]["text"] == "second"
