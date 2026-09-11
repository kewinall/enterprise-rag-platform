import hashlib
import json
from pathlib import Path

import pytest

from app.ingestion.knowledge_package import (
    KnowledgePackageError,
    load_knowledge_package,
    package_to_chunks,
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_package(root: Path, *, tamper_content_hash: bool = False) -> None:
    root.mkdir(parents=True, exist_ok=True)
    document_id = "ekb.kubernetes.imagepullbackoff.troubleshooting"
    source_path = "docs/kubernetes/imagepullbackoff-troubleshooting.md"
    content = "# Troubleshooting\n\nCheck Pod events and registry authentication."
    content_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if tamper_content_hash:
        content_sha = "0" * 64
    segment_id = f"{document_id}.seg.0001.{content_sha[:12]}"
    citation = {
        "document_id": document_id,
        "segment_id": segment_id,
        "source_path": source_path,
        "heading": "Troubleshooting",
        "anchor": "troubleshooting",
        "line_start": 10,
        "line_end": 12,
    }
    manifest = {
        "schema_version": "1.0",
        "document_id": document_id,
        "source_path": source_path,
        "access_class": "private",
        "segment_count": 1,
        "quality": {"score": 0.9, "label": "high"},
    }
    segment = {
        "schema_version": "1.0",
        "segment_id": segment_id,
        "document_id": document_id,
        "source_path": source_path,
        "ordinal": 1,
        "heading_path": ["Troubleshooting"],
        "line_start": 10,
        "line_end": 12,
        "content": content,
        "content_sha256": content_sha,
        "metadata": {"access_class": "private"},
        "citation": citation,
    }

    manifest_bytes = (json.dumps(manifest, sort_keys=True) + "\n").encode("utf-8")
    segments_bytes = (json.dumps(segment, sort_keys=True) + "\n").encode("utf-8")
    (root / "manifest.jsonl").write_bytes(manifest_bytes)
    (root / "segments.jsonl").write_bytes(segments_bytes)
    package = {
        "schema_version": "1.0",
        "knowledge_base_version": "v0.5.0",
        "source_repository": "kewinall/engineering-knowledge-base",
        "source_revision": "test",
        "document_count": 1,
        "segment_count": 1,
        "files": {
            "manifest": {
                "path": "manifest.jsonl",
                "sha256": _sha256_bytes(manifest_bytes),
            },
            "segments": {
                "path": "segments.jsonl",
                "sha256": _sha256_bytes(segments_bytes),
            },
        },
    }
    (root / "package.json").write_text(json.dumps(package), encoding="utf-8")


def test_load_and_convert_knowledge_package(tmp_path: Path) -> None:
    package_dir = tmp_path / "knowledge"
    _write_package(package_dir)

    knowledge_package = load_knowledge_package(package_dir)
    chunks = package_to_chunks(knowledge_package, tenant_id="engineering")

    assert len(knowledge_package.manifest_by_id) == 1
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.document_id == "ekb.kubernetes.imagepullbackoff.troubleshooting"
    assert chunk.tenant_id == "engineering"
    assert chunk.source == "docs/kubernetes/imagepullbackoff-troubleshooting.md"
    assert chunk.segment_id is not None
    assert chunk.line_start == 10
    assert chunk.line_end == 12
    assert chunk.content_sha256 is not None
    assert chunk.citation is not None
    assert chunk.citation["source_path"] == chunk.source


def test_rejects_tampered_segment_content(tmp_path: Path) -> None:
    package_dir = tmp_path / "knowledge"
    _write_package(package_dir, tamper_content_hash=True)

    with pytest.raises(KnowledgePackageError, match="content_sha256 mismatch"):
        load_knowledge_package(package_dir)
