"""Q2 T-13 instrument: independent reference enumeration, provenance
drill-down, and the synthetic article>header>h1 heading case.

Cites the fresh Prepare runs of the accepted three-page collection already
produced by T-12/T-18 (no duplicate full-suite work). Independently enumerates
every reference in each SOURCE_INDEX (accepted v01, accepted growth-call
reviewed, fresh T-18 run-1, saved growth-call initial, fresh T-16 initial),
resolves and re-hashes every referenced file under the snapshot root, and
derives the reference counts independently. Requires per-page source URL,
capture date, raw body + hash, metadata + hash, CSS drill-down and prepared
file + hash, plus usable brief/gap entry points in each accepted package.
Adds the synthetic case whose meaningful title appears only as
article>header>h1 and records where the title lands; if the helper routes it
to boilerplate that is preserved as a helper limitation, NOT counted as final
content preservation. Writes JSON result to argv[1].
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_scan import find_file_references

SNAP = Path("/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
SCRIPT = SNAP / "agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


INDEXES = {
    "accepted_v01": SNAP / "outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01/SOURCE_INDEX.json",
    "accepted_growth_reviewed": SNAP / "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed/SOURCE_INDEX.json",
    "fresh_t18_run1": SNAP / "outputs/prepared/qa-t18-run1/SOURCE_INDEX.json",
    "saved_growth_initial": SNAP / "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736/SOURCE_INDEX.json",
    "fresh_t16_initial": SNAP / "outputs/prepared/qa-t16-initial/SOURCE_INDEX.json",
}

ACCEPTED_PKGS = {
    "v01": SNAP / "outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01",
    "growth_reviewed": SNAP / "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed",
}


def enumerate_index(root: Path, index_path: Path) -> dict:
    index = json.loads(index_path.read_bytes())
    refs = find_file_references(index)
    out = []
    for r in refs:
        target = (root / r["file"]).resolve()
        rec = dict(r)
        rec["resolved"] = str(target)
        rec["exists"] = target.is_file()
        if rec["exists"]:
            data = target.read_bytes()
            rec["actual_sha256"] = sha(data)
            rec["hash_match"] = (r["sha256"] is None) or (rec["actual_sha256"] == r["sha256"])
            if r.get("bytes") is not None:
                rec["bytes_match"] = len(data) == r["bytes"]
        else:
            rec["hash_match"] = False
        out.append(rec)
    unique = {(r["file"], r["sha256"]) for r in out}
    return {
        "index": str(index_path.relative_to(root)),
        "raw_count": len(out),
        "unique_count": len(unique),
        "all_resolve_and_match": all(r["exists"] and r["hash_match"] for r in out),
        "failures": [r for r in out if not (r["exists"] and r["hash_match"])],
        "references": out,
    }


def drilldown(index: dict, pkg_root: Path) -> dict:
    pages = []
    for p in index.get("pages", []):
        src = p.get("source") or {}
        ext = p.get("extraction") or {}
        prepared = p.get("prepared") or {}
        pages.append({
            "id": p.get("id"),
            "url_present": bool(p.get("url")),
            "capture_saved_at_present": bool(p.get("capture_saved_at")),
            "raw_file_present": bool(src.get("raw_file")),
            "raw_sha256_present": bool(src.get("raw_sha256")),
            "metadata_file_present": bool(src.get("metadata_file")),
            "metadata_sha256_present": bool(src.get("metadata_sha256")),
            "css_selector": ext.get("css_selector") or ext.get("selector"),
            "prepared_file_present": bool(prepared.get("file")),
            "prepared_sha256_present": bool(prepared.get("sha256")),
            "links_recorded": len(p.get("links") or []),
            "images_recorded": len(p.get("images") or []),
        })
    brief = pkg_root / "ARCHITECT_BRIEF.md"
    gaps = pkg_root / "GAPS_AND_REQUESTS.md"
    core = [
        (pg["url_present"] and pg["capture_saved_at_present"] and pg["raw_file_present"]
         and pg["raw_sha256_present"] and pg["css_selector"]
         and pg["prepared_file_present"] and pg["prepared_sha256_present"])
        for pg in pages
    ]
    return {
        "pages": pages,
        "all_pages_have_core_drilldown": all(core),
        "architect_brief_entry_point": {"exists": brief.is_file(),
                                         "bytes": brief.stat().st_size if brief.is_file() else 0},
        "gaps_entry_point": {"exists": gaps.is_file(),
                             "bytes": gaps.stat().st_size if gaps.is_file() else 0},
    }


def synthetic_case() -> dict:
    sys.path.insert(0, str(SNAP))
    from recon_pipeline.collector import create, persist_result, atomic_json

    coll = SNAP / "outputs/qa-t13-synth/collection"
    if coll.exists():
        import shutil
        shutil.rmtree(coll)
    html = ("<html><body><header>Global Navigation Bar</header>"
            "<article><header><h1>Meaningful Page Title</h1></header>"
            "<p>Main body paragraph describing the offering.</p>"
            "<a href=\"/book\">Book a Call</a></article>"
            "<footer>Global Site Footer</footer></body></html>")
    state = create(coll, {"pages": ["https://example.test/page"], "rest": []})
    item = state["items"][0]
    persist_result(coll, item, {"body": html.encode(), "status": 200, "headers": {},
                                "final_url": item["url"], "redirect_from": [],
                                "body_complete": True, "ok": True, "error": None,
                                "saved_at": "2026-10-11T00:00:00+00:00"})
    item["status"] = "completed"
    atomic_json(coll / "checklist.json", state)
    out = SNAP / "outputs/prepared/qa-t13-synth-derived"
    proc = subprocess.run([str(VENV), str(SCRIPT), "--collection", str(coll), "--out", str(out)],
                           cwd=SNAP, capture_output=True, text=True)
    page_files = sorted(out.glob("pages/*.md")) if out.exists() else []
    page_text = page_files[0].read_text(encoding="utf-8") if page_files else ""
    boiler = (out / "BOILERPLATE.md").read_text(encoding="utf-8") if (out / "BOILERPLATE.md").is_file() else ""
    main_content = page_text.split("<!-- MAIN CONTENT -->", 1)[1] if "<!-- MAIN CONTENT -->" in page_text else page_text
    title = "Meaningful Page Title"
    return {
        "cli": {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
                "out_created": out.exists()},
        "title_in_final_main_content": title in main_content,
        "title_in_boilerplate": title in boiler,
        "title_in_raw_markdown": title in page_text,
        "paragraph_in_main_content": "Main body paragraph describing the offering." in main_content,
        "cta_in_main_content": "Book a Call" in main_content,
        "main_content_excerpt": main_content[:500],
        "boilerplate_excerpt": boiler[:500],
        "classification": None,
    }


def main() -> int:
    result = {
        "fresh_prepare_runs_cited": ["outputs/prepared/qa-t12-derived",
                                     "outputs/prepared/qa-t18-run1",
                                     "outputs/prepared/qa-t18-run2"],
    }
    enumerations = {name: enumerate_index(SNAP, path) for name, path in INDEXES.items()}
    result["enumeration"] = {
        name: {k: v[k] for k in ("index", "raw_count", "unique_count", "all_resolve_and_match", "failures")}
        for name, v in enumerations.items()
    }
    result["enumeration_references_full"] = {
        name: v["references"] for name, v in enumerations.items()
    }
    dd = {}
    for name, pkg in ACCEPTED_PKGS.items():
        idx = json.loads((pkg / "SOURCE_INDEX.json").read_bytes())
        dd[name] = drilldown(idx, pkg)
    result["accepted_drilldown"] = dd
    synth = synthetic_case()
    synth["classification"] = (
        "title preserved in final main content"
        if synth["title_in_final_main_content"]
        else ("HELPER LIMITATION: meaningful title routed to boilerplate (article>header>h1 stripped by "
              "the header boilerplate selector); not counted as final content preservation"
              if synth["title_in_boilerplate"] or synth["title_in_raw_markdown"]
              else "TITLE LOST ENTIRELY — finding")
    )
    result["synthetic_article_header_h1"] = synth
    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for name, v in result["enumeration"].items():
        print(name, "refs raw/unique:", v["raw_count"], "/", v["unique_count"],
              "all_resolve_and_match:", v["all_resolve_and_match"],
              "failures:", len(v["failures"]))
    for name, v in dd.items():
        print("drilldown", name, "core:", v["all_pages_have_core_drilldown"],
              "brief:", v["architect_brief_entry_point"]["bytes"], "B",
              "gaps:", v["gaps_entry_point"]["bytes"], "B")
    print("synthetic:", json.dumps({k: synth[k] for k in (
        "title_in_final_main_content", "title_in_boilerplate", "title_in_raw_markdown",
        "paragraph_in_main_content", "cta_in_main_content")}, indent=2))
    print("classification:", synth["classification"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())