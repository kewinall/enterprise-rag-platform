from app.evaluation.adversarial import evaluate_adversarial_cases


def test_adversarial_suite_passes_reference_cases():
    result = evaluate_adversarial_cases()
    assert result["pass_rate"] == 1.0
