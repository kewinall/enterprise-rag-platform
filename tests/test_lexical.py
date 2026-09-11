from app.retrieval.lexical import bm25_rank, tokenize


def test_tokenize_preserves_ascii_and_cjk_bigrams() -> None:
    tokens = tokenize("Pod 出現 ImagePullBackOff，應如何排查？")

    assert "pod" in tokens
    assert "imagepullbackoff" in tokens
    assert "出現" in tokens
    assert "如何" in tokens
    assert "排查" in tokens


def test_bm25_rank_supports_traditional_chinese_queries() -> None:
    documents = [
        {
            "chunk_id": "k8s",
            "text": "Kubernetes Pod 映像拉取失敗與 ImagePullBackOff 排查流程",
        },
        {
            "chunk_id": "db",
            "text": "PostgreSQL 資料庫備份與還原操作流程",
        },
    ]

    results = bm25_rank("映像拉取失敗", documents, limit=2)

    assert results[0]["chunk_id"] == "k8s"
