# Operational Feedback Integration

Enterprise RAG Platform v0.6.1 implements the Engineering Knowledge Base v0.8 operational-feedback contract without turning the RAG runtime into the knowledge-governance source of truth.

## Boundary

The runtime owns interaction capture and privacy filtering. `engineering-knowledge-base` owns stable document validation, aggregation, observation thresholds, and feedback-to-knowledge governance.

The local JSONL writer is a reference export path for development, controlled evidence, and small single-process deployments. Production deployments may forward the same contract to a durable telemetry pipeline instead of relying on container-local storage.

## Privacy

Operational feedback never exports raw search text, prompts, usernames, email addresses, IP addresses, or authenticated subject identifiers.

Search events contain:

- a random pseudonymous `query_id`;
- result count and outcome;
- stable `document_id` values for returned knowledge;
- consumer version/environment/provenance metadata.

## Enable live export

The writer is disabled by default.

```env
OPERATIONAL_FEEDBACK_ENABLED=true
OPERATIONAL_FEEDBACK_PATH=/var/lib/enterprise-rag/operational-feedback.jsonl
OPERATIONAL_FEEDBACK_CONSUMER_NAME=enterprise-rag-platform
```

When enabled, `POST /api/v1/search` returns a `query_id` and records a privacy-safe search event.

## Explicit feedback endpoints

Citation engagement:

```http
POST /api/v1/feedback/citation-click
```

```json
{
  "query_id": "q-...",
  "document_id": "ekb.security.trivy.scan-container-image",
  "rank": 1
}
```

Troubleshooting reuse:

```http
POST /api/v1/feedback/troubleshooting-reuse
```

```json
{
  "document_id": "ekb.kubernetes.crashloopbackoff.troubleshooting",
  "outcome": "success"
}
```

Lifecycle feedback:

```http
POST /api/v1/feedback/lifecycle
```

```json
{
  "document_id": "ekb.security.rhel-backport-cve-verification",
  "reason": "version_mismatch",
  "severity": "medium"
}
```

The API verifies that the referenced document exists in the caller's tenant before recording document-linked feedback.

## Controlled-runtime export

`benchmark_retrieval.py` can export actual retrieval observations using the same event contract:

```bash
python scripts/benchmark_retrieval.py \
  --dataset /path/to/retrieval-golden.jsonl \
  --tenant-id knowledge-base \
  --runs 1 \
  --operational-feedback-output dist/operational-feedback.jsonl
```

These events use:

```json
{
  "consumer": {
    "name": "enterprise-rag-platform-benchmark",
    "version": "0.6.1",
    "environment": "controlled-runtime",
    "evidence_kind": "controlled_runtime"
  }
}
```

This proves the consumer telemetry integration against real retrieval execution, but it must not be described as production human usage. Live API events use `evidence_kind=live_consumer`.

## Knowledge Base validation

Exported events can be validated by the source repository:

```bash
python scripts/validate_operational_feedback.py \
  --input /path/to/operational-feedback.jsonl

python scripts/generate_operational_feedback_report.py \
  --input /path/to/operational-feedback.jsonl \
  --output dist/usage-feedback
```

A controlled-runtime `OBSERVED` result is evidence that the integration works and that sample thresholds can be evaluated. It is not a production adoption or user-success claim.
