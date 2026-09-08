install:
	python -m pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload

lint:
	ruff check app tests scripts

test:
	pytest -q

evaluate:
	python scripts/evaluate_retrieval.py --dataset data/eval/retrieval_eval.jsonl --k 5

benchmark:
	python scripts/benchmark_retrieval.py --dataset data/eval/retrieval_eval.jsonl --k 5

evaluate-answers:
	python scripts/evaluate_answers.py --dataset data/eval/answer_eval.jsonl --k 5 --mode hybrid
