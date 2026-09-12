# Windows runtime evidence baseline

This companion runner measures an existing Knowledge Package on Windows host Python,
with Qdrant 1.19.0 in WSL. It does not start the complete RAG stack.
Private knowledge and results stay in the sibling knowledge repository.

## Preparation

Use sibling checkouts named `engineering-knowledge-base` and `enterprise-rag-platform`.
In the KB, run the metadata, registry, internal-link and evaluation validators, then
export and validate `dist/knowledge` using the KB Makefile or equivalent Python commands.
Use `--revision <KB commit>` when exporting a new package. Preserve the frozen input
snapshot when reproducing a previously accepted baseline.

In the RAG checkout, create `.venv-baseline`, install CPU PyTorch from
`https://download.pytorch.org/whl/cpu`, then install `-e ".[dev]"`.
For the accepted environment, use the dependency versions recorded with its evidence.
Use the Windows system trust store for pip if your network uses a trusted local CA;
do not disable TLS verification. The Windows runner exports public system CA
certificates into the local venv for model-download verification.

Start Qdrant in WSL, only if the named container does not already exist:

```sh
docker run -d --name engineering-kb-v051-qdrant \
  -p 127.0.0.1:6333:6333 qdrant/qdrant:v1.19.0
```

If Windows localhost requests incur IPv6 fallback delays, run this foreground
loopback-only helper in a separate terminal; stop it with Ctrl+C after use:

```powershell
.\.venv-baseline\Scripts\python.exe scripts/baseline_localhost_relay.py
```

## Run

```powershell
.\.venv-baseline\Scripts\python.exe scripts/run_runtime_baseline.py
```

The runner fixes localhost:6333, collection `engineering_kb_v051`, MiniLM-L6-v2,
CPU threads=1, reranker=false, vector/lexical candidates=10, final k=5,
three warm-up queries and three measured runs. The collection must be dedicated
to this package; canonical verification rejects missing or extra segments.
Archive existing evidence before running; the runner refuses to overwrite it.
Never reuse a production collection.

Outputs are written to the sibling KB `artifacts/knowledge-evaluation/`.
Failures return nonzero and keep stage logs and metadata. A completed run includes
consumer validation, ingestion, retrieval, citation checks and comparison against
canonical source text, line ranges, hashes and complete segment membership.
Record the model snapshot revision, container image digest, input hashes and any
network helper used before accepting the run as a regression reference.

Recall@5 retains the existing any-expected-source hit-rate definition. MRR is
truncated at five returned chunks, without document deduplication. Latency includes
Qdrant operations; lexical and hybrid modes scroll the corpus and rebuild BM25
for every query. The reported latency is environment-specific, not a production SLA.
