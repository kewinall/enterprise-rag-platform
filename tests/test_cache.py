from app.core.cache import make_rag_cache_key


def test_cache_key_is_deterministic():
    first = make_rag_cache_key("question", 5, "hybrid", {"source": "a.md"}, "model")
    second = make_rag_cache_key("question", 5, "hybrid", {"source": "a.md"}, "model")
    assert first == second


def test_cache_key_changes_with_request():
    first = make_rag_cache_key("question", 5, "hybrid", None, "model")
    second = make_rag_cache_key("other question", 5, "hybrid", None, "model")
    assert first != second
