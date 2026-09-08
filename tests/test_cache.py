from app.core.cache import make_rag_cache_key


def test_cache_key_is_deterministic():
    first = make_rag_cache_key("question", 5, "hybrid", {"source": "a.md"}, "model")
    second = make_rag_cache_key("question", 5, "hybrid", {"source": "a.md"}, "model")
    assert first == second


def test_cache_key_changes_with_request():
    first = make_rag_cache_key("question", 5, "hybrid", None, "model")
    second = make_rag_cache_key("other question", 5, "hybrid", None, "model")
    assert first != second


def test_cache_key_is_tenant_scoped():
    tenant_a = make_rag_cache_key(
        "question",
        5,
        "hybrid",
        None,
        "model",
        tenant_id="tenant-a",
    )
    tenant_b = make_rag_cache_key(
        "question",
        5,
        "hybrid",
        None,
        "model",
        tenant_id="tenant-b",
    )
    assert tenant_a != tenant_b


def test_cache_key_changes_when_tenant_revision_changes():
    old = make_rag_cache_key(
        "question",
        5,
        "hybrid",
        None,
        "model",
        tenant_id="tenant-a",
        tenant_revision=1,
    )
    new = make_rag_cache_key(
        "question",
        5,
        "hybrid",
        None,
        "model",
        tenant_id="tenant-a",
        tenant_revision=2,
    )
    assert old != new
