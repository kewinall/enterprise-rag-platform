import re

from rank_bm25 import BM25Okapi

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/+\-]*|[\u3400-\u4dbf\u4e00-\u9fff]+")
_CJK_PATTERN = re.compile(r"^[\u3400-\u4dbf\u4e00-\u9fff]+$")


def _cjk_bigrams(value: str) -> list[str]:
    if len(value) < 2:
        return [value]
    return [value[index : index + 2] for index in range(len(value) - 1)]


def tokenize(text: str) -> list[str]:
    """Tokenize ASCII terms and CJK text without requiring an external segmenter."""
    tokens: list[str] = []
    for match in _TOKEN_PATTERN.finditer(text):
        value = match.group(0)
        if _CJK_PATTERN.fullmatch(value):
            tokens.extend(_cjk_bigrams(value))
        else:
            tokens.append(value.lower())
    return tokens


def bm25_rank(query: str, documents: list[dict], limit: int) -> list[dict]:
    if not documents:
        return []
    corpus = [tokenize(doc["text"]) for doc in documents]
    model = BM25Okapi(corpus)
    scores = model.get_scores(tokenize(query))
    ranked = sorted(zip(documents, scores, strict=True), key=lambda x: x[1], reverse=True)
    return [{**doc, "score": float(score)} for doc, score in ranked[:limit]]
