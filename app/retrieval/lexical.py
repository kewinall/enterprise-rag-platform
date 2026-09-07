from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in text.split() if token.strip()]


def bm25_rank(query: str, documents: list[dict], limit: int) -> list[dict]:
    if not documents:
        return []
    corpus = [tokenize(doc["text"]) for doc in documents]
    model = BM25Okapi(corpus)
    scores = model.get_scores(tokenize(query))
    ranked = sorted(zip(documents, scores, strict=True), key=lambda x: x[1], reverse=True)
    return [{**doc, "score": float(score)} for doc, score in ranked[:limit]]
