from collections.abc import Sequence


def recall_at_k(
    ranked_sources: Sequence[str],
    expected_source: str,
    k: int,
) -> float:
    return float(expected_source in ranked_sources[:k])


def reciprocal_rank(
    ranked_sources: Sequence[str],
    expected_source: str,
) -> float:
    try:
        rank = ranked_sources.index(expected_source) + 1
    except ValueError:
        return 0.0
    return 1.0 / rank
