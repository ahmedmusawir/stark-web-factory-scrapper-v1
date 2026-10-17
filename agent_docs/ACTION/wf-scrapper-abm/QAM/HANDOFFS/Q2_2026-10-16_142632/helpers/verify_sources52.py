"""Q2 G1 helper: verify the 52 inventoried source files under a given root.

Recomputes per-file SHA-256 against the reviewed source inventory and the
aggregate source52 (SHA-256 of UTF-8 json.dumps(mapping, sort_keys=True,
separators=(',', ':')), no trailing newline). Read-only; writes only its JSON
result given as argv[2]. Usage:
  verify_sources52.py <root> <result_json>
"""
import hashlib
import json
import sys
from pathlib import Path

INVENTORY = Path(
    "/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/"
    "wf-scrapper-abm/QAM/HANDOFFS/WebFactory_Q1_Lead_Review_2026-10-15/"
    "ORIGINAL_Q1/governing/source-inventory.json"
)


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2])
    inv = json.loads(INVENTORY.read_bytes().decode("utf-8"))
    files = {}
    bad = []
    for path, expected in inv["files"].items():
        f = root / path
        if not f.is_file():
            bad.append({"file": path, "problem": "MISSING"})
            continue
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        files[path] = actual
        if actual != expected:
            bad.append({"file": path, "expected": expected, "actual": actual})
    digest = hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    result = {
        "root": str(root),
        "source52": digest,
        "expected_source52": inv["sha256"],
        "source52_ok": digest == inv["sha256"],
        "per_file_mismatches": bad,
        "file_count": len(files),
    }
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("root:", root)
    print("source52:", digest)
    print("expected:", inv["sha256"])
    print("per-file mismatches:", bad or "none")
    print("SOURCE52_OK:", result["source52_ok"] and not bad)
    return 0 if result["source52_ok"] and not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())