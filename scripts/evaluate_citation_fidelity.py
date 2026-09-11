import argparse
import json
from pathlib import Path

from app.evaluation.citation_fidelity import evaluate_citation_fidelity
from app.retrieval.store import get_vector_store


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate citation/provenance fidelity for ingested knowledge chunks."
    )
    parser.add_argument("--tenant-id", default="engineering-knowledge")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Return exit code 1 when any citation is broken",
    )
    args = parser.parse_args()

    chunks = get_vector_store().list_chunks(filters={"tenant_id": args.tenant_id})
    report = {
        "tenant_id": args.tenant_id,
        **evaluate_citation_fidelity(chunks),
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

    if args.fail_on_broken and report["broken_citations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
