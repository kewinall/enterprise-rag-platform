from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from app.ingestion.parsers import ParsedSection


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    source: str
    text: str
    ordinal: int
    page: int | None
    section: str | None
    content_type: str


def create_document_id(source: str) -> str:
    normalized = source.strip() or "upload"
    return str(uuid5(NAMESPACE_URL, normalized))


def split_sections(
    sections: list[ParsedSection],
    source: str,
    document_id: str,
    chunk_size: int,
    overlap: int,
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
                        f"{document_id}:{ordinal}:{section.page}:"
                        f"{section.section}:{piece}"
                    ),
                )
            )
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    source=source,
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
) -> list[Chunk]:
    resolved_document_id = document_id or create_document_id(source)
    return split_sections(
        sections=[ParsedSection(text=text)],
        source=source,
        document_id=resolved_document_id,
        chunk_size=chunk_size,
        overlap=overlap,
    )
