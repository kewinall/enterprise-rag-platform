import hashlib
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
kb = root.parent / "engineering-knowledge-base"
out = kb / "artifacts/knowledge-evaluation"
expected = {
    s["segment_id"]: s
    for s in map(
        json.loads, (kb / "dist/knowledge/segments.jsonl").read_text(encoding="utf-8").splitlines()
    )
}
points = []
offset = None
while True:
    body = {
        "limit": 256,
        "with_payload": True,
        "with_vector": False,
        "filter": {"must": [{"key": "tenant_id", "match": {"value": "engineering-knowledge"}}]},
    }
    if offset is not None:
        body["offset"] = offset
    req = urllib.request.Request(
        "http://localhost:6333/collections/engineering_kb_v051/points/scroll",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    result = json.load(urllib.request.urlopen(req))["result"]
    points += result["points"]
    offset = result["next_page_offset"]
    if offset is None:
        break
failures = []
seen = set()
for point in points:
    p = point["payload"]
    sid = p.get("segment_id")
    seen.add(sid)
    s = expected.get(sid)
    if not s:
        failures.append({"segment_id": sid, "reason": "unexpected segment"})
        continue
    for key in [
        "document_id",
        "source_path",
        "line_start",
        "line_end",
        "content_sha256",
        "citation",
    ]:
        if p.get(key) != s[key]:
            failures.append({"segment_id": sid, "reason": key + " differs from package"})
    canonical = "\n".join(
        (kb / s["source_path"])
        .read_text(encoding="utf-8")
        .splitlines()[s["line_start"] - 1 : s["line_end"]]
    ).strip()
    if (
        canonical != p["text"]
        or hashlib.sha256(p["text"].encode()).hexdigest() != s["content_sha256"]
    ):
        failures.append({"segment_id": sid, "reason": "canonical text or hash mismatch"})
for sid in expected.keys() - seen:
    failures.append({"segment_id": sid, "reason": "missing segment"})
report = json.loads((out / "citation-results.json").read_text(encoding="utf-8"))
report["canonical_verification"] = {
    "expected_segments": len(expected),
    "stored_points": len(points),
    "unique_segments": len(seen),
    "failures": failures,
    "passed": not failures and len(points) == len(expected) == len(seen),
}
(out / "citation-results.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report["canonical_verification"]["passed"] else 1)
