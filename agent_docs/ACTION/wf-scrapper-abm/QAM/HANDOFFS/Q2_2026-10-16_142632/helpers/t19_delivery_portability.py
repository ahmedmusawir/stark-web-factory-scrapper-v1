"""Q2 T-19 instrument: delivery-tree portability and confinement.

Builds a new delivery tree under owned scratch from verified files only:
both accepted prepared packages, the saved initial growth-call package, the
three source collections, every file reference independently enumerated from
the package indexes (the documented figure is not the oracle), and the
Prepare helper copied at its normal relative script location. Re-verifies
every copied byte against the snapshot, re-scans the delivered indexes so
every reference resolves inside the tree with matching hashes, checks the
per-page drill-down and brief/gap entry points, runs the COPIED helper with
inputs under the delivery root (both collections, NEW derived directories),
and requires an external-root collection to refuse visibly. Records external
link/image references as data without fetching. Writes JSON to argv[1].
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_scan import find_file_references

SNAP = Path("/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
DELIVERY = Path("/tmp/opencode/q2-scratch-20261016/delivery-t19")
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
HELPER_REL = "agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py"
ACCEPTED_PKGS = [
    "outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01",
    "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed",
]
INITIAL_PKGS = [
    "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736",
]
COLLECTIONS = [
    "outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505",
    "outputs/collections/CyberizeGroup-growth-call-follow-up-2026-10-13_223736",
    "outputs/collections/CyberizeGroup-selected-live-01",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_helper(helper: Path, cwd: Path, collection: Path, out: Path) -> dict:
    proc = subprocess.run(
        [str(VENV), str(helper), "--collection", str(collection), "--out", str(out)],
        cwd=cwd, capture_output=True, text=True,
    )
    return {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
            "out_created": out.exists()}


def main() -> int:
    result = {}
    refs = []
    for pkg in ACCEPTED_PKGS + INITIAL_PKGS:
        idx = json.loads((SNAP / pkg / "SOURCE_INDEX.json").read_bytes())
        refs.extend(find_file_references(idx))
    files = sorted({r["file"] for r in refs})
    result["independently_enumerated_reference_files"] = files
    result["independent_reference_count"] = len(files)

    if DELIVERY.exists():
        shutil.rmtree(DELIVERY)
    copied_dirs = []
    for d in ACCEPTED_PKGS + INITIAL_PKGS + COLLECTIONS:
        (DELIVERY / d).parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SNAP / d, DELIVERY / d)
        copied_dirs.append(d)
    (DELIVERY / HELPER_REL).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SNAP / HELPER_REL, DELIVERY / HELPER_REL)
    extras, missing = [], []
    for f in files:
        dst = DELIVERY / f
        if dst.exists():
            continue
        src = SNAP / f
        if not src.is_file():
            missing.append(f)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        extras.append(f)
    result["copied_dirs"] = copied_dirs
    result["copied_extra_reference_files"] = extras
    result["references_missing_in_snapshot"] = missing

    verify = {}
    all_bytes_match = True
    for p in sorted(DELIVERY.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(DELIVERY))
            src = SNAP / rel
            s = sha(src.read_bytes()) if src.is_file() else "ABSENT_IN_SNAPSHOT"
            d = sha(p.read_bytes())
            verify[rel] = {"snapshot_sha256": s, "delivery_sha256": d, "match": s == d}
            if s != d:
                all_bytes_match = False
    result["delivery_file_count"] = len(verify)
    result["all_delivery_bytes_match_snapshot"] = all_bytes_match
    result["delivery_verification"] = verify

    delivered_scan = {}
    for pkg in ACCEPTED_PKGS:
        idx_path = DELIVERY / pkg / "SOURCE_INDEX.json"
        idx = json.loads(idx_path.read_bytes())
        refs_d = find_file_references(idx)
        rows = []
        for r in refs_d:
            target = (DELIVERY / r["file"]).resolve()
            ok = target.is_file() and (
                r["sha256"] is None or sha(target.read_bytes()) == r["sha256"]
            ) and str(target).startswith(str(DELIVERY.resolve()))
            rows.append({"file": r["file"], "resolves_in_tree": ok})
        delivered_scan[pkg] = {
            "raw_count": len(rows),
            "unique_count": len({r["file"] for r in rows}),
            "all_resolve_in_tree": all(r["resolves_in_tree"] for r in rows),
            "failures": [r for r in rows if not r["resolves_in_tree"]],
        }
    result["delivered_index_resolution"] = delivered_scan

    helper = DELIVERY / HELPER_REL
    runs = {
        "first_selected_in_delivery": run_helper(
            helper, DELIVERY,
            DELIVERY / COLLECTIONS[0],
            DELIVERY / "outputs/prepared/qa-t19-derived-first-selected"),
        "growth_call_in_delivery": run_helper(
            helper, DELIVERY,
            DELIVERY / COLLECTIONS[1],
            DELIVERY / "outputs/prepared/qa-t19-derived-growth-call"),
    }
    external = run_helper(
        helper, DELIVERY,
        SNAP / COLLECTIONS[0],
        DELIVERY / "outputs/prepared/qa-t19-external-root")
    external["expected_visible_refusal"] = (
        external["exit"] == 2 and "Prepare refused" in external["stderr"]
        and not external["out_created"]
    )
    runs["external_root_negative"] = external
    result["copied_helper_runs"] = runs

    dd = {}
    for pkg in ACCEPTED_PKGS:
        idx = json.loads((DELIVERY / pkg / "SOURCE_INDEX.json").read_bytes())
        pages = []
        for p in idx.get("pages", []):
            src = p.get("source") or {}
            ext = p.get("extraction") or {}
            pages.append({
                "url_present": bool(p.get("url")),
                "capture_saved_at_present": bool(p.get("capture_saved_at")),
                "raw_file_present": bool(src.get("raw_file")),
                "raw_sha256_present": bool(src.get("raw_sha256")),
                "metadata_file_present": bool(src.get("metadata_file")),
                "css_selector": ext.get("css_selector") or ext.get("selector"),
                "prepared_file_present": bool((p.get("prepared") or {}).get("file")),
                "links_recorded": len(p.get("links") or []),
                "images_recorded": len(p.get("images") or []),
            })
        brief = DELIVERY / pkg / "ARCHITECT_BRIEF.md"
        gaps = DELIVERY / pkg / "GAPS_AND_REQUESTS.md"
        dd[pkg] = {
            "pages": pages,
            "all_pages_core_drilldown": all(
                pg["url_present"] and pg["capture_saved_at_present"]
                and pg["raw_file_present"] and pg["raw_sha256_present"]
                and pg["css_selector"] and pg["prepared_file_present"] for pg in pages),
            "brief_entry_point": {"exists": brief.is_file(),
                                  "bytes": brief.stat().st_size if brief.is_file() else 0},
            "gaps_entry_point": {"exists": gaps.is_file(),
                                 "bytes": gaps.stat().st_size if gaps.is_file() else 0},
        }
    result["delivered_drilldown"] = dd

    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("independently enumerated reference files:", result["independent_reference_count"])
    print("missing in snapshot:", missing)
    print("delivery files:", result["delivery_file_count"],
          "all bytes match snapshot:", all_bytes_match)
    for pkg, v in delivered_scan.items():
        print("delivered scan", pkg, "all_resolve_in_tree:", v["all_resolve_in_tree"],
              "count:", v["unique_count"])
    for name, r in runs.items():
        print(name, "exit:", r["exit"], "out_created:", r["out_created"],
              ("visible_refusal:" + str(r["expected_visible_refusal"]))
              if name == "external_root_negative" else "")
    for pkg, v in dd.items():
        print("drilldown", pkg, "core:", v["all_pages_core_drilldown"],
              "brief bytes:", v["brief_entry_point"]["bytes"],
              "gaps bytes:", v["gaps_entry_point"]["bytes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())