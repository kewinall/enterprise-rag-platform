import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import traceback
from pathlib import Path

root = Path(__file__).resolve().parents[1]
kb = root.parent / "engineering-knowledge-base"
out = kb / "artifacts/knowledge-evaluation"
out.mkdir(parents=True, exist_ok=True)
if (out / "baseline-metadata.json").exists():
    raise SystemExit("Evidence already exists; archive it before a new run.")


def save(name, value):
    (out / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


os.environ.update(
    QDRANT_URL="http://localhost:6333",
    QDRANT_COLLECTION="engineering_kb_v051",
    EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2",
    ENABLE_RERANKER="false",
    VECTOR_TOP_K="10",
    LEXICAL_TOP_K="10",
    FINAL_TOP_K="5",
    PYTHONIOENCODING="utf-8",
    CUDA_VISIBLE_DEVICES="",
    OMP_NUM_THREADS="1",
    MKL_NUM_THREADS="1",
)
meta = {
    "status": "running",
    "timestamp_utc": datetime.datetime.now(datetime.UTC).isoformat(),
    "python": sys.version,
    "platform": platform.platform(),
    "processor": platform.processor(),
    "cpu_count": os.cpu_count(),
    "settings": {
        k: os.environ[k]
        for k in [
            "QDRANT_URL",
            "QDRANT_COLLECTION",
            "EMBEDDING_MODEL",
            "ENABLE_RERANKER",
            "VECTOR_TOP_K",
            "LEXICAL_TOP_K",
            "FINAL_TOP_K",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
        ]
    },
    "warmup": 3,
    "runs": 3,
    "repositories": {
        p.name: {
            "sha": git(p, "rev-parse", "HEAD"),
            "branch": git(p, "branch", "--show-current"),
            "status": git(p, "status", "--short"),
            "version": (p / "VERSION").read_text().strip() if (p / "VERSION").exists() else "0.6.0",
        }
        for p in [kb, root]
    },
    "input_sha256": {
        str(p.relative_to(kb)): sha(p)
        for p in [
            *sorted((kb / "dist/knowledge").glob("*")),
            kb / "evaluation/retrieval-golden.jsonl",
        ]
    },
    "benchmark_sha256": sha(root / "scripts/benchmark_retrieval.py"),
    "stages": {},
}
save("baseline-metadata.json", meta)
for name in ["retrieval-results.json", "citation-results.json", "failed-cases.json"]:
    save(name, {"status": "not_run", "results": None})


def run(name, args, cwd=root):
    proc = subprocess.run(
        [sys.executable, *args],
        check=False,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (out / (name + ".log")).write_text(proc.stdout, encoding="utf-8")
    meta["stages"][name] = proc.returncode
    save("baseline-metadata.json", meta)
    if proc.returncode:
        raise RuntimeError(name + " failed; see " + name + ".log")


try:
    import ssl
    import urllib.request

    import torch

    meta["torch"] = {
        "version": torch.__version__,
        "cuda": torch.version.cuda,
        "threads": torch.get_num_threads(),
    }
    meta["qdrant"] = json.load(urllib.request.urlopen("http://localhost:6333/"))
    # Export the Windows CA trust bundle so child processes preserve TLS verification.
    certs = ssl.enum_certificates("ROOT") + ssl.enum_certificates("CA")
    bundle = root / ".venv-baseline/runtime-ca.pem"
    bundle.write_text(
        "".join(ssl.DER_cert_to_PEM_cert(cert) for cert, enc, trust in certs if enc == "x509_asn"),
        encoding="ascii",
    )
    os.environ["SSL_CERT_FILE"] = str(bundle)
    os.environ["REQUESTS_CA_BUNDLE"] = str(bundle)
    run(
        "consumer-validation",
        ["scripts/ingest_knowledge_package.py", str(kb / "dist/knowledge"), "--validate-only"],
    )
    run("ingest", ["scripts/ingest_knowledge_package.py", str(kb / "dist/knowledge")])
    run(
        "retrieval",
        [
            "scripts/benchmark_retrieval.py",
            "--dataset",
            str(kb / "evaluation/retrieval-golden.jsonl"),
            "--tenant-id",
            "engineering-knowledge",
            "--k",
            "5",
            "--warmup",
            "3",
            "--runs",
            "3",
            "--output",
            str(out / "retrieval-results.json"),
        ],
    )
    run(
        "citation",
        [
            "scripts/evaluate_citation_fidelity.py",
            "--tenant-id",
            "engineering-knowledge",
            "--fail-on-broken",
            "--output",
            str(out / "citation-results.json"),
        ],
    )
    run("canonical-verification", ["scripts/verify_baseline_canonical.py"])
    report = json.loads((out / "retrieval-results.json").read_text(encoding="utf-8"))
    cases = [
        json.loads(x)
        for x in (kb / "evaluation/retrieval-golden.jsonl").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    failures = []
    for case in cases:
        missed = {
            mode: any(x["case_id"] == case["case_id"] for x in report[mode]["failures"])
            for mode in ["vector", "lexical", "hybrid"]
        }
        if any(missed.values()):
            category = (
                "all_modes_miss"
                if all(missed.values())
                else "fusion_miss"
                if missed["hybrid"]
                else "vector_only_miss"
                if missed["vector"] and not missed["lexical"]
                else "lexical_only_miss"
                if missed["lexical"] and not missed["vector"]
                else "fusion_rescue"
            )
            failures.append({**case, "category": category, "missed": missed})
    save(
        "failed-cases.json",
        {
            "status": "completed",
            "classification_note": "Observed mode outcomes, not causal diagnosis; a miss in any measured run is counted.",
            "cases": failures,
        },
    )
    meta["status"] = "completed"
except Exception as exc:  # noqa: BLE001 - retain evidence and return nonzero for any runtime failure
    meta["status"] = "blocked"
    meta["blocker"] = str(exc)
    (out / "error.log").write_text(traceback.format_exc(), encoding="utf-8")
finally:
    subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        check=True,
        stdout=(out / "requirements-runtime.txt").open("w", encoding="utf-8"),
    )
    save("baseline-metadata.json", meta)
    lines = [
        "# v0.5.1 Runtime Evidence Baseline",
        "",
        f"Status: {meta['status']}",
        "",
        "KB source version remains 0.5.0; v0.5.1 labels this experiment, not a released version.",
        "",
        "Metrics preserve existing semantics: Recall@5 is any-expected-source hit rate; MRR is truncated at 5 returned chunks, without document deduplication. Warm-up excluded; 50 cases x 3 runs per mode. Latency includes Qdrant requests and, for BM25/Hybrid, corpus scrolling and rebuilding BM25.",
        "",
    ]
    if meta["status"] == "completed":
        lines += ["|Mode|Recall@5|MRR@5|Avg ms|P50 ms|P95 ms|", "|---|---:|---:|---:|---:|---:|"]
        for mode in ["vector", "lexical", "hybrid"]:
            r = report[mode]
            lines.append(
                "|"
                + mode
                + "|"
                + "|".join(
                    str(r[k])
                    for k in [
                        "recall@5",
                        "mrr",
                        "avg_latency_ms",
                        "p50_latency_ms",
                        "p95_latency_ms",
                    ]
                )
                + "|"
            )
        from collections import Counter

        lines += [
            "",
            str(Counter(x["category"] for x in failures)),
            "",
            "Citation result: " + (out / "citation-results.json").read_text(encoding="utf-8"),
            "",
            "Citation evaluator checks payload consistency; canonical-verification separately checks exact source text, hashes and complete segment membership. No production threshold has been asserted.",
        ]
    else:
        lines += [
            "Blocked: " + meta.get("blocker", "unknown"),
            "",
            "No measured metrics are claimed. Not suitable for freezing as baseline.",
        ]
    (out / "baseline-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(meta["status"], meta.get("blocker", ""), flush=True)


if meta["status"] != "completed":
    raise SystemExit(1)
