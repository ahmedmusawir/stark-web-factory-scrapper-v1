"""Q2 T-12 instrument: raw preservation + invalid-reference tamper negatives.

Runs the CANDIDATE Prepare CLI (snapshot copy) offline. Part 1: byte-map the
accepted source collection before/after a fresh Prepare into a NEW derived
directory; require zero source changes. Part 2: on separate scratch copies,
tamper one body byte / recorded body hash / escaping body_file reference
(hash-consistent canary) / symlinked body; record each CLI outcome and require
refusals to happen before any derived output exists. Canary hashes prove no
file outside the owned synthetic tree is touched. Writes JSON result to argv[1].
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

SNAP = Path("/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
SCRIPT = SNAP / "agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py"
COLL = SNAP / "outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505"
ANDRO = "attempts/76f31511d3acb8433bdb9d50/220f10a856624283ba03669128dffef9"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_map(root: Path) -> dict:
    return {
        str(p.relative_to(root)): sha(p.read_bytes())
        for p in sorted(root.rglob("*"))
        if p.is_file() and not p.is_symlink()
    }


def run_cli(collection: Path, out: Path) -> dict:
    proc = subprocess.run(
        [str(VENV), str(SCRIPT), "--collection", str(collection), "--out", str(out)],
        cwd=SNAP, capture_output=True, text=True,
    )
    return {
        "argv_tail": [SCRIPT.name, "--collection", str(collection), "--out", str(out)],
        "exit": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "out_created": out.exists(),
    }


def main() -> int:
    result = {}

    before = tree_map(COLL)
    out1 = SNAP / "outputs/prepared/qa-t12-derived"
    fresh = run_cli(COLL, out1)
    after = tree_map(COLL)
    changed = {k: {"before": before[k], "after": after.get(k)}
               for k in before if after.get(k) != before[k]}
    changed.update({k: "new_after" for k in after if k not in before})
    result["part1_source_preservation"] = {
        "cli": fresh,
        "source_file_count": len(before),
        "source_changes": changed,
        "zero_source_changes": not changed,
        "derived_files": sorted(str(p.relative_to(out1)) for p in out1.rglob("*") if p.is_file())
        if out1.exists() else [],
    }

    base = SNAP / "outputs/qa-t12-copies"
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)
    negatives = {}

    ca = base / "body-flip"
    shutil.copytree(COLL, ca)
    body = ca / ANDRO / "body"
    data = bytearray(body.read_bytes())
    data[100] ^= 0xFF
    body.write_bytes(bytes(data))
    negatives["body_byte_flip"] = run_cli(ca, base / "out-body-flip")

    cb = base / "metadata-hash-tamper"
    shutil.copytree(COLL, cb)
    rj = cb / ANDRO / "result.json"
    meta = json.loads(rj.read_bytes())
    meta["sha256"] = "0" * 64
    rj.write_bytes(json.dumps(meta, indent=2).encode())
    negatives["metadata_hash_tamper"] = run_cli(cb, base / "out-metadata")

    cc = base / "escaping-reference"
    shutil.copytree(COLL, cc)
    canary_bytes = b"<html><body><p>outside canary content</p></body></html>"
    canary = base / "canary-outside.html"
    canary.write_bytes(canary_bytes)
    rj2 = cc / ANDRO / "result.json"
    meta2 = json.loads(rj2.read_bytes())
    meta2["body_file"] = "../../../../canary-outside.html"
    meta2["sha256"] = sha(canary_bytes)
    meta2["bytes"] = len(canary_bytes)
    rj2.write_bytes(json.dumps(meta2, indent=2).encode())
    esc = run_cli(cc, base / "out-escaping")
    esc["canary_unchanged"] = canary.read_bytes() == canary_bytes
    negatives["escaping_reference_hash_consistent"] = esc

    cd = base / "symlink-body"
    shutil.copytree(COLL, cd)
    canary2 = base / "canary2-original-body-copy"
    shutil.copy2(COLL / ANDRO / "body", canary2)
    body2 = cd / ANDRO / "body"
    body2.unlink()
    body2.symlink_to(canary2)
    sym = run_cli(cd, base / "out-symlink")
    sym["canary2_unchanged"] = canary2.read_bytes() == (COLL / ANDRO / "body").read_bytes()
    negatives["symlinked_body_original_content"] = sym

    for name, case in negatives.items():
        case["expected_refusal_before_output"] = (
            case["exit"] == 2 and "Prepare refused" in case["stderr"] and not case["out_created"]
        )
    result["part2_tamper_negatives"] = negatives
    result["assessment"] = {
        "part1_zero_source_changes": result["part1_source_preservation"]["zero_source_changes"],
        "body_byte_flip_refused_before_output": negatives["body_byte_flip"]["expected_refusal_before_output"],
        "metadata_hash_tamper_refused_before_output": negatives["metadata_hash_tamper"]["expected_refusal_before_output"],
        "escaping_reference_behavior": "refused" if negatives["escaping_reference_hash_consistent"]["expected_refusal_before_output"] else "ACCEPTED-or-other — record as boundary observation",
        "symlink_behavior": "refused" if negatives["symlinked_body_original_content"]["expected_refusal_before_output"] else "followed/accepted — record as boundary observation",
        "outside_files_untouched": negatives["escaping_reference_hash_consistent"]["canary_unchanged"] and negatives["symlinked_body_original_content"]["canary2_unchanged"],
    }
    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("part1 zero source changes:", result["assessment"]["part1_zero_source_changes"])
    for name, case in negatives.items():
        print(name, "exit", case["exit"], "out_created", case["out_created"],
              "refusal:", "Prepare refused" in case["stderr"])
    print("assessment:", json.dumps(result["assessment"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())