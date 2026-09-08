import json

from app.evaluation.adversarial import evaluate_adversarial_cases


if __name__ == "__main__":
    print(json.dumps(evaluate_adversarial_cases(), indent=2))
