"""Q2 T-21 agent-stage binder: records the agent-authored brief and gaps into
the package index (mirroring the accepted v01 agent_authored entry shape:
file / sha256 / author / role), then re-runs the independent reference
scanner over the updated index so every reference — including the two new
agent_authored entries — resolves under the snapshot root with matching
hashes. Writes JSON to argv[1]. The authored files themselves were written by
the agent (Opy, Q2 QA) from the prepared package facts, not by this helper.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_scan import find_file_references

SNAP = Path("/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
PKG = SNAP / "outputs/prepared/qa-t21-prepared"
AUTHOR = "Opy — Q2 QA (independent)"
ROLE = "Q2 T-21 whole-flow agent stage; authored from the prepared package facts"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    index_path = PKG / "SOURCE_INDEX.json"
    index = json.loads(index_path.read_bytes())
    entries = []
    for name in ("ARCHITECT_BRIEF.md", "GAPS_AND_REQUESTS.md"):
        path = PKG / name
        entries.append({
            "file": str(path.relative_to(SNAP)),
            "sha256": sha(path.read_bytes()),
            "author": AUTHOR,
            "role": ROLE,
        })
    index["agent_authored"] = entries
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    updated = json.loads(index_path.read_bytes())
    refs = find_file_references(updated)
    rows = []
    for r in refs:
        target = (SNAP / r["file"]).resolve()
        ok = target.is_file() and (r["sha256"] is None
                                   or sha(target.read_bytes()) == r["sha256"])
        rows.append({"file": r["file"], "resolves_with_matching_hash": ok})
    result = {
        "agent_authored_entries": entries,
        "authored_bytes": {e["file"].rsplit("/", 1)[1]:
                           (SNAP / e["file"]).stat().st_size for e in entries},
        "reference_count_after_authoring": len(rows),
        "all_references_resolve_and_match": all(x["resolves_with_matching_hash"]
                                                for x in rows),
        "references": rows,
        "brief_excerpt": (PKG / "ARCHITECT_BRIEF.md").read_text(encoding="utf-8")[:400],
        "gaps_excerpt": (PKG / "GAPS_AND_REQUESTS.md").read_text(encoding="utf-8")[:400],
    }
    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("agent_authored entries:", len(entries))
    for e in entries:
        print(" ", e["file"].rsplit("/", 1)[1], e["sha256"][:16] + "…",
              (SNAP / e["file"]).stat().st_size, "bytes")
    print("references after authoring:", len(rows),
          "| all resolve + hash-match:", result["all_references_resolve_and_match"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())