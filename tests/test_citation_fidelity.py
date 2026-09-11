from app.evaluation.citation_fidelity import evaluate_citation_fidelity


def test_citation_fidelity_accepts_matching_provenance() -> None:
    chunk = {
        "chunk_id": "chunk-1",
        "document_id": "ekb.test.doc",
        "segment_id": "ekb.test.doc.seg.0001.abc",
        "source": "docs/test.md",
        "source_path": "docs/test.md",
        "line_start": 10,
        "line_end": 15,
        "content_sha256": "abc123",
        "citation": {
            "document_id": "ekb.test.doc",
            "segment_id": "ekb.test.doc.seg.0001.abc",
            "source_path": "docs/test.md",
            "line_start": 10,
            "line_end": 15,
        },
    }

    report = evaluate_citation_fidelity([chunk])

    assert report["citation_validity"] == 1.0
    assert report["broken_citations"] == 0


def test_citation_fidelity_reports_broken_source_range() -> None:
    chunk = {
        "chunk_id": "chunk-1",
        "document_id": "ekb.test.doc",
        "segment_id": "ekb.test.doc.seg.0001.abc",
        "source": "docs/test.md",
        "source_path": "docs/test.md",
        "line_start": 15,
        "line_end": 10,
        "content_sha256": "abc123",
        "citation": {
            "document_id": "ekb.test.doc",
            "segment_id": "ekb.test.doc.seg.0001.abc",
            "source_path": "docs/test.md",
            "line_start": 15,
            "line_end": 10,
        },
    }

    report = evaluate_citation_fidelity([chunk])

    assert report["broken_citations"] == 1
    assert "invalid source line range" in report["failures"][0]["reasons"]
