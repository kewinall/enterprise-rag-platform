import pytest

from app.ingestion.chunking import split_text


def test_split_text_is_deterministic():
    text = "A" * 250
    first = split_text(text, "demo.txt", chunk_size=100, overlap=20)
    second = split_text(text, "demo.txt", chunk_size=100, overlap=20)
    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]
    assert len(first) == 3


def test_split_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        split_text("hello", "demo.txt", chunk_size=10, overlap=10)
