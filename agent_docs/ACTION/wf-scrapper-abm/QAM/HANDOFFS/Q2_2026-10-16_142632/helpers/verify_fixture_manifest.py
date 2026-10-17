"""Q2 G2 helper: verify the 34 manifest reference files under a given root.

Checks existence, byte size and SHA-256 of every fixture-manifest reference file
against the reviewed ORIGINAL_Q1 manifest. Read-only for the target root; writes
only its JSON result given as argv[2]. Usage:
  verify_fixture_manifest.py <repo_root> <result_json>
"""
import hashlib
import json
import sys
from pathlib import Path

MANIFEST = Path(
    "/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/"
    "wf-scrapper-abm/QAM/HANDOFFS/WebFactory_Q1_Lead_Review_2026-10-15/"
    "ORIGINAL_Q1/governing/fixture-manifest.json"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2])
    manifest = json.loads(MANIFEST.read_bytes().decode("utf-8"))
    results = []
    for ref in manifest["references"]:
        path = root / ref["file"]
        entry = {
            "file": ref["file"],
            "expected_sha256": ref["sha256"],
            "expected_bytes": ref["bytes"],
        }
        if not path.is_file():
            entry["status"] = "MISSING"
        else:
            data = path.read_bytes()
            actual = sha256_bytes(data)
            entry.update(
                actual_bytes=len(data),
                actual_sha256=actual,
                status="MATCH"
                if (len(data) == ref["bytes"] and actual == ref["sha256"])
                else "MISMATCH",
            )
        results.append(entry)
    ok = all(r["status"] == "MATCH" for r in results)
    summary = {
        "root": str(root),
        "manifest": str(MANIFEST),
        "reference_count": len(results),
        "match": sum(1 for r in results if r["status"] == "MATCH"),
        "missing": [r["file"] for r in results if r["status"] == "MISSING"],
        "mismatch": [r["file"] for r in results if r["status"] == "MISMATCH"],
        "all_match": ok,
        "files": results,
    }
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("root:", root)
    print("references:", summary["reference_count"], "match:", summary["match"])
    print("missing:", summary["missing"] or "none")
    print("mismatch:", summary["mismatch"] or "none")
    print("ALL_MATCH", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())