import json

from app.core.operational_feedback import OperationalFeedbackWriter


def test_writer_emits_privacy_safe_contract_events(tmp_path):
    path = tmp_path / "feedback.jsonl"
    writer = OperationalFeedbackWriter(
        path,
        consumer_name="enterprise-rag-platform",
        consumer_version="0.6.0",
        environment="test",
        evidence_kind="live_consumer",
    )

    query_id = writer.new_query_id()
    writer.emit_search(
        query_id=query_id,
        results=[
            {"document_id": "ekb.security.trivy.scan-container-image"},
            {"document_id": "ekb.security.trivy.scan-container-image"},
            {"document_id": "unknown"},
        ],
    )
    writer.emit_citation_click(
        query_id=query_id,
        document_id="ekb.security.trivy.scan-container-image",
        rank=1,
    )
    writer.emit_troubleshooting_reuse(
        document_id="ekb.security.trivy.scan-container-image",
        outcome="success",
    )
    writer.emit_lifecycle_feedback(
        document_id="ekb.security.trivy.scan-container-image",
        reason="outdated",
        severity="medium",
    )

    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert [event["event_type"] for event in events] == [
        "search",
        "citation_click",
        "troubleshooting_reuse",
        "lifecycle_feedback",
    ]
    assert events[0]["top_document_ids"] == ["ekb.security.trivy.scan-container-image"]
    assert events[0]["query_id"] == query_id
    assert events[0]["consumer"]["evidence_kind"] == "live_consumer"

    forbidden = {"query_text", "raw_query", "prompt", "username", "email", "ip_address"}
    assert all(not forbidden.intersection(event) for event in events)
