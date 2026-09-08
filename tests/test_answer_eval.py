import pytest

from app.evaluation.answer_eval import parse_evaluation_payload


def test_parse_evaluation_payload():
    payload = parse_evaluation_payload(
        '{"faithfulness":0.9,"answer_relevance":0.8,'
        '"context_relevance":0.7,"answer_correctness":null,"reason":"grounded"}'
    )
    assert payload["faithfulness"] == 0.9
    assert payload["answer_correctness"] is None
    assert payload["reason"] == "grounded"


def test_parse_evaluation_payload_clamps_scores():
    payload = parse_evaluation_payload(
        '{"faithfulness":1.4,"answer_relevance":-0.2,'
        '"context_relevance":0.5,"answer_correctness":0.5,"reason":"test"}'
    )
    assert payload["faithfulness"] == 1.0
    assert payload["answer_relevance"] == 0.0


def test_parse_evaluation_payload_requires_json():
    with pytest.raises(ValueError):
        parse_evaluation_payload("not-json")
