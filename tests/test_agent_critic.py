from app.agent.critic import parse_answer_review, parse_context_review


def test_context_review_parsing():
    review = parse_context_review(
        '{"sufficient":false,"reason":"missing recovery details",'
        '"follow_up_query":"backup recovery procedure"}'
    )
    assert not review.sufficient
    assert review.follow_up_query == "backup recovery procedure"


def test_answer_review_clamps_scores():
    review = parse_answer_review(
        '{"passed":false,"groundedness":1.2,"relevance":-0.4,'
        '"reason":"test","revision_instruction":"use evidence"}'
    )
    assert review.groundedness == 1.0
    assert review.relevance == 0.0
