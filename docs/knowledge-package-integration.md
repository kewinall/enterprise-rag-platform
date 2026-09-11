# Engineering Knowledge Package Integration

This integration consumes Knowledge Package Contract v1.0 produced by `kewinall/engineering-knowledge-base` without changing the RAG Platform's existing ingestion/retrieval ownership.

## Contract

Expected directory:

```text
knowledge/
├─ package.json
├─ manifest.jsonl
└─ segments.jsonl
```

The consumer validates:

- supported `schema_version`
- manifest / segment file SHA-256 declared by `package.json`
- document and segment counts
- unique `document_id` and `segment_id`
- segment content SHA-256
- valid source line ranges
- segment-to-manifest source path consistency
- citation `document_id`, `segment_id`, source path and line-range consistency
- per-document segment counts

## Provenance Preservation

The RAG storage layer keeps the source contract fields in Qdrant payloads:

- canonical `document_id`
- canonical `segment_id`
- `source_path`
- `line_start` / `line_end`
- `content_sha256`
- heading path
- access class
- quality score
- citation object

Qdrant point IDs remain UUID-compatible storage identifiers derived deterministically from `source_repository + segment_id`. The storage identifier never replaces the canonical segment ID.

## Validate Only

```bash
python scripts/ingest_knowledge_package.py \
  ../engineering-knowledge-base/dist/knowledge \
  --tenant-id engineering-knowledge \
  --validate-only
```

Or:

```bash
make validate-knowledge-package
```

## Ingest

Start the normal RAG dependencies, then:

```bash
make ingest-knowledge-package
```

Defaults can be overridden:

```bash
make ingest-knowledge-package \
  KNOWLEDGE_PACKAGE=/path/to/knowledge \
  KNOWLEDGE_TENANT=engineering-knowledge
```

## Retrieval Benchmark

The golden dataset remains source-owned by `engineering-knowledge-base`:

```bash
make benchmark-knowledge
```

This executes vector-only, lexical/BM25-only and hybrid retrieval against the same cases and writes:

```text
artifacts/knowledge-evaluation/retrieval-results.json
```

Metrics include Recall@K, MRR, average latency, P50 latency, P95 latency and failed cases.

## Citation Fidelity

```bash
make evaluate-knowledge-citations
```

The evaluator checks the persisted retrieval payload against the original citation/provenance contract and writes:

```text
artifacts/knowledge-evaluation/citation-results.json
```

`--fail-on-broken` is enabled by the Make target. The expected hard gate is zero broken citations.

## Full Evidence Run

```bash
make knowledge-evidence
```

Runtime evidence remains outside the Knowledge Source of Truth repository. This keeps canonical source/version control separate from environment-specific retrieval measurements.
