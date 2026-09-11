KNOWLEDGE_PACKAGE ?= ../engineering-knowledge-base/dist/knowledge
KNOWLEDGE_EVAL ?= ../engineering-knowledge-base/evaluation/retrieval-golden.jsonl
KNOWLEDGE_TENANT ?= engineering-knowledge
KNOWLEDGE_EVIDENCE ?= artifacts/knowledge-evaluation

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

evaluate-agent:
	python scripts/evaluate_agent.py --dataset data/eval/agent_eval.jsonl --top-k 5 --mode hybrid

evaluate-adversarial:
	python scripts/evaluate_adversarial.py

validate-knowledge-package:
	python scripts/ingest_knowledge_package.py $(KNOWLEDGE_PACKAGE) --tenant-id $(KNOWLEDGE_TENANT) --validate-only

ingest-knowledge-package:
	python scripts/ingest_knowledge_package.py $(KNOWLEDGE_PACKAGE) --tenant-id $(KNOWLEDGE_TENANT)

benchmark-knowledge:
	python scripts/benchmark_retrieval.py --dataset $(KNOWLEDGE_EVAL) --tenant-id $(KNOWLEDGE_TENANT) --k 5 --output $(KNOWLEDGE_EVIDENCE)/retrieval-results.json

evaluate-knowledge-citations:
	python scripts/evaluate_citation_fidelity.py --tenant-id $(KNOWLEDGE_TENANT) --fail-on-broken --output $(KNOWLEDGE_EVIDENCE)/citation-results.json

knowledge-evidence: benchmark-knowledge evaluate-knowledge-citations
