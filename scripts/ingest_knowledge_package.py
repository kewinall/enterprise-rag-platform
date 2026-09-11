import argparse
import json
from pathlib import Path

from app.ingestion.knowledge_package import load_knowledge_package, package_to_chunks
from app.retrieval.store import get_vector_store


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and ingest an Engineering Knowledge Base package into Qdrant."
    )
    parser.add_argument("package", type=Path, help="Directory containing package.json and JSONL files")
    parser.add_argument("--tenant-id", default="engineering-knowledge")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the package and print a summary without writing to Qdrant",
    )
    args = parser.parse_args()

    knowledge_package = load_knowledge_package(args.package)
    chunks = package_to_chunks(knowledge_package, tenant_id=args.tenant_id)

    summary = {
        "schema_version": knowledge_package.package["schema_version"],
        "knowledge_base_version": knowledge_package.package.get("knowledge_base_version"),
        "source_repository": knowledge_package.package.get("source_repository"),
        "source_revision": knowledge_package.package.get("source_revision"),
        "documents": len(knowledge_package.manifest_by_id),
        "segments": len(chunks),
        "tenant_id": args.tenant_id,
        "mode": "validate-only" if args.validate_only else "ingest",
    }

    if not args.validate_only:
        get_vector_store().upsert(chunks)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
