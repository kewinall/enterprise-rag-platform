import pytest

from app.ingestion.chunking import create_document_id, split_sections, split_text
from app.ingestion.parsers import ParsedSection


def test_split_text_is_deterministic():
    text = "A" * 250
    first = split_text(text, "demo.txt", chunk_size=100, overlap=20)
    second = split_text(text, "demo.txt", chunk_size=100, overlap=20)
    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]
    assert len(first) == 3


def test_split_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        split_text("hello", "demo.txt", chunk_size=10, overlap=10)


def test_split_sections_preserves_metadata():
    document_id = create_document_id("handbook.md")
    chunks = split_sections(
        sections=[
            ParsedSection(
                text="Security controls and least privilege.",
                page=3,
                section="Security",
                content_type="text/markdown",
            )
        ],
        source="handbook.md",
        document_id=document_id,
        chunk_size=100,
        overlap=10,
    )

    assert len(chunks) == 1
    assert chunks[0].document_id == document_id
    assert chunks[0].page == 3
    assert chunks[0].section == "Security"
    assert chunks[0].content_type == "text/markdown"
