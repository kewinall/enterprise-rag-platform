from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.ingestion.chunking import Chunk

SUPPORTED_SCHEMA_VERSION = "1.0"


class KnowledgePackageError(ValueError):
    """Raised when an exported knowledge package violates its contract."""


@dataclass(frozen=True)
class KnowledgePackage:
    root: Path
    package: dict
    manifest_by_id: dict[str, dict]
    segments: list[dict]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise KnowledgePackageError(f"{path.name}:{line_number}: invalid JSON") from exc
        if not isinstance(record, dict):
            raise KnowledgePackageError(f"{path.name}:{line_number}: expected JSON object")
        records.append(record)
    return records


def load_knowledge_package(root: Path) -> KnowledgePackage:
    root = Path(root)
    package_path = root / "package.json"
    if not package_path.is_file():
        raise KnowledgePackageError("package.json is missing")

    package = json.loads(package_path.read_text(encoding="utf-8"))
    schema_version = str(package.get("schema_version", ""))
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise KnowledgePackageError(
            f"unsupported schema_version {schema_version!r}; expected {SUPPORTED_SCHEMA_VERSION!r}"
        )

    files = package.get("files") or {}
    manifest_meta = files.get("manifest") or {}
    segments_meta = files.get("segments") or {}
    manifest_path = root / str(manifest_meta.get("path", "manifest.jsonl"))
    segments_path = root / str(segments_meta.get("path", "segments.jsonl"))

    for path, meta in ((manifest_path, manifest_meta), (segments_path, segments_meta)):
        if not path.is_file():
            raise KnowledgePackageError(f"{path.name} is missing")
        expected_sha = str(meta.get("sha256", ""))
        actual_sha = _sha256_file(path)
        if expected_sha and actual_sha != expected_sha:
            raise KnowledgePackageError(f"{path.name}: sha256 mismatch")

    manifest = _read_jsonl(manifest_path)
    segments = _read_jsonl(segments_path)
    if len(manifest) != int(package.get("document_count", -1)):
        raise KnowledgePackageError("document_count does not match manifest.jsonl")
    if len(segments) != int(package.get("segment_count", -1)):
        raise KnowledgePackageError("segment_count does not match segments.jsonl")

    manifest_by_id: dict[str, dict] = {}
    expected_segment_counts: dict[str, int] = {}
    for record in manifest:
        document_id = str(record.get("document_id", ""))
        if not document_id:
            raise KnowledgePackageError("manifest record is missing document_id")
        if document_id in manifest_by_id:
            raise KnowledgePackageError(f"duplicate document_id: {document_id}")
        if str(record.get("schema_version", "")) != schema_version:
            raise KnowledgePackageError(f"{document_id}: schema_version mismatch")
        manifest_by_id[document_id] = record
        expected_segment_counts[document_id] = int(record.get("segment_count", 0))

    actual_segment_counts = {document_id: 0 for document_id in manifest_by_id}
    seen_segment_ids: set[str] = set()
    for segment in segments:
        segment_id = str(segment.get("segment_id", ""))
        document_id = str(segment.get("document_id", ""))
        if not segment_id:
            raise KnowledgePackageError("segment record is missing segment_id")
        if segment_id in seen_segment_ids:
            raise KnowledgePackageError(f"duplicate segment_id: {segment_id}")
        seen_segment_ids.add(segment_id)
        if document_id not in manifest_by_id:
            raise KnowledgePackageError(f"{segment_id}: unknown document_id {document_id!r}")
        if str(segment.get("schema_version", "")) != schema_version:
            raise KnowledgePackageError(f"{segment_id}: schema_version mismatch")

        content = str(segment.get("content", ""))
        if _sha256_text(content) != str(segment.get("content_sha256", "")):
            raise KnowledgePackageError(f"{segment_id}: content_sha256 mismatch")

        line_start = int(segment.get("line_start", 0))
        line_end = int(segment.get("line_end", 0))
        if line_start <= 0 or line_end < line_start:
            raise KnowledgePackageError(f"{segment_id}: invalid source line range")

        source_path = str(segment.get("source_path", ""))
        manifest_source_path = str(manifest_by_id[document_id].get("source_path", ""))
        if source_path != manifest_source_path:
            raise KnowledgePackageError(f"{segment_id}: source_path does not match manifest")

        citation = segment.get("citation") or {}
        required_citation = {
            "document_id": document_id,
            "segment_id": segment_id,
            "source_path": source_path,
            "line_start": line_start,
            "line_end": line_end,
        }
        for key, expected in required_citation.items():
            if citation.get(key) != expected:
                raise KnowledgePackageError(f"{segment_id}: citation {key} mismatch")

        actual_segment_counts[document_id] += 1

    for document_id, expected in expected_segment_counts.items():
        if actual_segment_counts[document_id] != expected:
            raise KnowledgePackageError(
                f"{document_id}: segment_count mismatch "
                f"({actual_segment_counts[document_id]} != {expected})"
            )

    return KnowledgePackage(
        root=root,
        package=package,
        manifest_by_id=manifest_by_id,
        segments=segments,
    )


def package_to_chunks(
    knowledge_package: KnowledgePackage,
    tenant_id: str = "engineering-knowledge",
) -> list[Chunk]:
    chunks: list[Chunk] = []
    source_repository = str(knowledge_package.package.get("source_repository", "knowledge-package"))

    for segment in knowledge_package.segments:
        document_id = str(segment["document_id"])
        segment_id = str(segment["segment_id"])
        source_path = str(segment["source_path"])
        metadata = segment.get("metadata") or {}
        manifest = knowledge_package.manifest_by_id[document_id]
        quality = manifest.get("quality") or {}
        heading_path = [str(value) for value in (segment.get("heading_path") or [])]
        citation = dict(segment.get("citation") or {})
        qdrant_id = str(uuid5(NAMESPACE_URL, f"{source_repository}:{segment_id}"))

        chunks.append(
            Chunk(
                chunk_id=qdrant_id,
                document_id=document_id,
                tenant_id=tenant_id,
                source=source_path,
                object_key=None,
                text=str(segment["content"]),
                ordinal=int(segment.get("ordinal", 0)),
                page=None,
                section=heading_path[-1] if heading_path else None,
                content_type="text/markdown",
                segment_id=segment_id,
                source_path=source_path,
                line_start=int(segment["line_start"]),
                line_end=int(segment["line_end"]),
                content_sha256=str(segment["content_sha256"]),
                heading_path=heading_path,
                access_class=str(metadata.get("access_class", manifest.get("access_class", "private"))),
                quality_score=float(quality.get("score", 0.0)),
                citation=citation,
            )
        )

    return chunks
