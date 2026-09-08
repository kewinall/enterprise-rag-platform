from app.evaluation.metrics import recall_at_k, reciprocal_rank


def test_recall_at_k():
    ranked = ["a.md", "b.md", "c.md"]
    assert recall_at_k(ranked, "b.md", 2) == 1.0
    assert recall_at_k(ranked, "c.md", 2) == 0.0


def test_reciprocal_rank():
    ranked = ["a.md", "b.md", "c.md"]
    assert reciprocal_rank(ranked, "b.md") == 0.5
    assert reciprocal_rank(ranked, "missing.md") == 0.0
