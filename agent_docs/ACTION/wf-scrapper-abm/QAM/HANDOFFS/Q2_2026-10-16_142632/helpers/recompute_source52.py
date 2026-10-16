"""Q2 G1 helper: recompute the source52 identity from candidate blobs, HEAD blobs and worktree.

Method per LEAD-01 section 0: SHA-256 of UTF-8
json.dumps(path_to_sha256, sort_keys=True, separators=(',', ':')), no trailing
newline, over exactly the 52 inventoried paths. Read-only for the repository;
writes only its own JSON result file given as argv[1].
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1")
INVENTORY = REPO / (
    "agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/"
    "WebFactory_Q1_Lead_Review_2026-10-15/ORIGINAL_Q1/governing/source-inventory.json"
)
CANDIDATE = "8fbcff289fde5149be0c0631b08e8a5fbcb3faa4"
EXECUTION_HEAD = "e1972ff3a80bf67a321461a743d0097e97cd069a"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source52(path_to_sha: dict) -> str:
    payload = json.dumps(path_to_sha, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    inventory = json.loads(INVENTORY.read_bytes().decode("utf-8"))
    recorded = inventory["files"]
    out_path = Path(sys.argv[1])

    def blob(commit: str, path: str) -> bytes:
        proc = subprocess.run(
            ["git", "-C", str(REPO), "show", f"{commit}:{path}"],
            check=True,
            capture_output=True,
        )
        return proc.stdout

    sources = {
        "candidate_blobs": {p: sha256_bytes(blob(CANDIDATE, p)) for p in recorded},
        "execution_head_blobs": {p: sha256_bytes(blob(EXECUTION_HEAD, p)) for p in recorded},
        "worktree_files": {p: sha256_bytes((REPO / p).read_bytes()) for p in recorded},
    }
    results = {}
    for name, mapping in sources.items():
        results[name] = {
            "source52": source52(mapping),
            "file_count": len(mapping),
            "per_file_mismatch_vs_inventory": {
                p: {"inventory": recorded[p], "actual": h}
                for p, h in mapping.items()
                if recorded[p] != h
            },
        }
    expected = inventory["sha256"]
    results["expected_source52"] = expected
    results["all_sources_match_expected"] = all(
        results[name]["source52"] == expected for name in sources
    )
    results["all_three_sources_identical"] = len({results[n]["source52"] for n in sources}) == 1
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    for name in sources:
        print(name, results[name]["source52"], "per-file mismatches:", len(results[name]["per_file_mismatch_vs_inventory"]))
    print("expected", expected)
    print("ALL_MATCH", results["all_sources_match_expected"])
    return 0 if results["all_sources_match_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())