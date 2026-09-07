from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    text: str
    ordinal: int


def split_text(text: str, source: str, chunk_size: int, overlap: int) -> list[Chunk]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be > 0 and 0 <= overlap < chunk_size")

    chunks: list[Chunk] = []
    start = 0
    ordinal = 0

    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        piece = cleaned[start:end]
        chunk_id = str(uuid5(NAMESPACE_URL, f"{source}:{ordinal}:{piece}"))
        chunks.append(Chunk(chunk_id=chunk_id, source=source, text=piece, ordinal=ordinal))
        if end == len(cleaned):
            break
        start = end - overlap
        ordinal += 1

    return chunks
