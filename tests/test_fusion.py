from app.retrieval.fusion import reciprocal_rank_fusion


def test_rrf_rewards_items_seen_in_multiple_rankings():
    result = reciprocal_rank_fusion([["a", "b"], ["b", "c"]])
    assert result[0][0] == "b"
