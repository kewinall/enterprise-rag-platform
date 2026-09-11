from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from app.ingestion.parsers import ParsedSection


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    tenant_id: str
    source: str
    object_key: str | None
    text: str
    ordinal: int
    page: int | None
    section: str | None
    content_type: str
    segment_id: str | None = None
    source_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    content_sha256: str | None = None
    heading_path: list[str] | None = None
    access_class: str | None = None
    quality_score: float | None = None
    citation: dict | None = None


def create_document_id(source: str, tenant_id: str = "default") -> str:
    normalized_source = source.strip() or "upload"
    normalized_tenant = tenant_id.strip() or "default"
    return str(uuid5(NAMESPACE_URL, f"{normalized_tenant}:{normalized_source}"))


def split_sections(
    sections: list[ParsedSection],
    source: str,
    document_id: str,
    chunk_size: int,
    overlap: int,
    tenant_id: str = "default",
    object_key: str | None = None,
) -> list[Chunk]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be > 0 and 0 <= overlap < chunk_size")

    chunks: list[Chunk] = []
    ordinal = 0

    for section in sections:
        cleaned = " ".join(section.text.split())
        if not cleaned:
            continue

        start = 0
        while start < len(cleaned):
            end = min(len(cleaned), start + chunk_size)
            piece = cleaned[start:end]
            chunk_id = str(
                uuid5(
                    NAMESPACE_URL,
                    (
                        f"{tenant_id}:{document_id}:{ordinal}:{section.page}:"
                        f"{section.section}:{piece}"
                    ),
                )
            )
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    tenant_id=tenant_id,
                    source=source,
                    object_key=object_key,
                    text=piece,
                    ordinal=ordinal,
                    page=section.page,
                    section=section.section,
                    content_type=section.content_type,
                )
            )
            ordinal += 1
            if end == len(cleaned):
                break
            start = end - overlap

    return chunks


def split_text(
    text: str,
    source: str,
    chunk_size: int,
    overlap: int,
    document_id: str | None = None,
    tenant_id: str = "default",
    object_key: str | None = None,
) -> list[Chunk]:
    resolved_document_id = document_id or create_document_id(source, tenant_id)
    return split_sections(
        sections=[ParsedSection(text=text)],
        source=source,
        document_id=resolved_document_id,
        chunk_size=chunk_size,
        overlap=overlap,
        tenant_id=tenant_id,
        object_key=object_key,
    )
