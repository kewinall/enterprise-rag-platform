import json
import sys

from app.evaluation.adversarial import evaluate_adversarial_cases


if __name__ == "__main__":
    result = evaluate_adversarial_cases()
    print(json.dumps(result, indent=2))
    if result["pass_rate"] < 1.0:
        sys.exit(1)
