from app.retrieval.store import build_qdrant_filter


def test_qdrant_filter_builds_all_conditions():
    query_filter = build_qdrant_filter(
        {
            "document_id": "doc-1",
            "source": "handbook.md",
            "page": 2,
        }
    )

    assert query_filter is not None
    assert len(query_filter.must) == 3


def test_qdrant_filter_returns_none_for_empty_filter():
    assert build_qdrant_filter(None) is None
    assert build_qdrant_filter({}) is None
