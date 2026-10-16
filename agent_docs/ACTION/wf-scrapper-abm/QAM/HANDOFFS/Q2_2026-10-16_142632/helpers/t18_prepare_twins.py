"""Q2 T-18 instrument: Prepare repeatability twins.

Runs the CANDIDATE Prepare CLI twice on the same accepted source collection
into two distinct NEW derived directories. Requires byte-identical page and
boilerplate content, and compares SOURCE_INDEX.json field-by-field with a
normalization allowlist declared BEFORE comparison: run timestamp
(prepared_at), output location fields (pages[].prepared.file,
boilerplate.file). Any other difference remains a visible finding. The full
raw diff is retained in the JSON result (argv[1]). Also cross-compares run-1
page/boilerplate bytes against the accepted v01 package pages (repeatability
across runs and against the accepted package, recorded as an observation).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SNAP = Path("/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
SCRIPT = SNAP / "agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py"
COLL = SNAP / "outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505"
V01 = SNAP / "outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_cli(out: Path) -> dict:
    proc = subprocess.run(
        [str(VENV), str(SCRIPT), "--collection", str(COLL), "--out", str(out)],
        cwd=SNAP, capture_output=True, text=True,
    )
    return {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def flatten(obj, prefix="$"):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def main() -> int:
    run1 = SNAP / "outputs/prepared/qa-t18-run1"
    run2 = SNAP / "outputs/prepared/qa-t18-run2"
    cli1, cli2 = run_cli(run1), run_cli(run2)
    result = {"cli_run1": cli1, "cli_run2": cli2}

    def content_files(root: Path) -> dict:
        return {str(p.relative_to(root)): p.read_bytes()
                for p in sorted(root.rglob("*")) if p.is_file()
                and p.name != "SOURCE_INDEX.json"}

    c1, c2 = content_files(run1), content_files(run2)
    content_identical = c1 == c2
    result["content_files_identical"] = content_identical
    result["content_diff"] = {
        k: {"run1_sha256": sha(c1[k]) if k in c1 else None,
            "run2_sha256": sha(c2[k]) if k in c2 else None}
        for k in sorted(set(c1) | set(c2)) if c1.get(k) != c2.get(k)
    } or "none"

    i1 = json.loads((run1 / "SOURCE_INDEX.json").read_bytes())
    i2 = json.loads((run2 / "SOURCE_INDEX.json").read_bytes())
    f1, f2 = flatten(i1), flatten(i2)
    raw_diff = {
        k: {"run1": f1.get(k), "run2": f2.get(k)}
        for k in sorted(set(f1) | set(f2)) if f1.get(k) != f2.get(k)
    }
    allowlist = {"$.prepared_at", "$.boilerplate.file"} | {
        f"$.pages[{i}].prepared.file" for i in range(len(i1["pages"]))
    }
    result["normalization_allowlist"] = sorted(allowlist)
    result["source_index_raw_diff"] = raw_diff
    result["index_diff_outside_allowlist"] = {
        k: v for k, v in raw_diff.items() if k not in allowlist
    } or "none"
    result["index_normalized_identical"] = not result["index_diff_outside_allowlist"]

    v01_pages = {str(p.relative_to(V01)): p.read_bytes()
                 for p in sorted(V01.rglob("pages/*")) if p.is_file()}
    cross = {}
    for rel, expected in v01_pages.items():
        actual = (run1 / rel).read_bytes() if (run1 / rel).is_file() else None
        cross[rel] = {"identical": actual == expected,
                      "run1_sha256": sha(actual) if actual else None,
                      "v01_sha256": sha(expected)}
    boi = (V01 / "BOILERPLATE.md").read_bytes()
    cross["BOILERPLATE.md"] = {"identical": (run1 / "BOILERPLATE.md").read_bytes() == boi,
                               "v01_sha256": sha(boi)}
    result["run1_vs_accepted_v01_package"] = cross

    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("both CLI runs exit 0:", cli1["exit"] == 0 and cli2["exit"] == 0)
    print("content files identical:", content_identical)
    print("index diff paths:", list(raw_diff))
    print("index diff outside allowlist:", result["index_diff_outside_allowlist"])
    print("cross vs accepted v01:", {k: v["identical"] for k, v in cross.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())