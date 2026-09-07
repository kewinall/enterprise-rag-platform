from dataclasses import dataclass
from hashlib import sha256


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
        digest = sha256(f"{source}:{ordinal}:{piece}".encode()).hexdigest()[:24]
        chunks.append(Chunk(chunk_id=digest, source=source, text=piece, ordinal=ordinal))
        if end == len(cleaned):
            break
        start = end - overlap
        ordinal += 1

    return chunks
