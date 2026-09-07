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
