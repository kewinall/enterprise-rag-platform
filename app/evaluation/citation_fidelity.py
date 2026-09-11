from __future__ import annotations


def evaluate_citation_fidelity(chunks: list[dict]) -> dict:
    total = len(chunks)
    valid = 0
    failures: list[dict] = []

    for chunk in chunks:
        reasons: list[str] = []
        citation = chunk.get("citation") or {}
        required = {
            "document_id": chunk.get("document_id"),
            "segment_id": chunk.get("segment_id"),
            "source_path": chunk.get("source_path") or chunk.get("source"),
            "line_start": chunk.get("line_start"),
            "line_end": chunk.get("line_end"),
        }

        for key, expected in required.items():
            if expected in (None, ""):
                reasons.append(f"missing payload {key}")
            elif citation.get(key) != expected:
                reasons.append(f"citation {key} mismatch")

        line_start = chunk.get("line_start")
        line_end = chunk.get("line_end")
        if isinstance(line_start, int) and isinstance(line_end, int) and line_end < line_start:
            reasons.append("invalid source line range")
        if not chunk.get("content_sha256"):
            reasons.append("missing content_sha256")

        if reasons:
            failures.append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "segment_id": chunk.get("segment_id"),
                    "reasons": reasons,
                }
            )
        else:
            valid += 1

    denominator = total or 1
    return {
        "chunks": total,
        "valid_citations": valid,
        "broken_citations": total - valid,
        "citation_validity": round(valid / denominator, 4),
        "broken_citation_rate": round((total - valid) / denominator, 4),
        "failures": failures,
    }
