from app.core.object_store import ObjectStore


def test_object_key_is_tenant_scoped_and_sanitized():
    store = ObjectStore()
    key = store.make_object_key(
        "tenant-a",
        "doc-id",
        "../../Quarterly Report (Final).pdf",
    )
    assert key == "tenant-a/doc-id/Quarterly_Report_Final_.pdf"
