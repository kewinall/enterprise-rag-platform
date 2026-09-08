from app.ingestion.chunking import create_document_id, split_text


def test_document_id_is_tenant_scoped():
    tenant_a = create_document_id("handbook.md", "tenant-a")
    tenant_b = create_document_id("handbook.md", "tenant-b")
    assert tenant_a != tenant_b


def test_chunks_preserve_tenant_id():
    chunks = split_text(
        "enterprise data",
        "demo.txt",
        chunk_size=100,
        overlap=10,
        tenant_id="tenant-a",
    )
    assert len(chunks) == 1
    assert chunks[0].tenant_id == "tenant-a"
