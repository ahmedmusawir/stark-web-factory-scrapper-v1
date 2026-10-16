"""Q2 T-16 instrument: Growth Call embed honesty.

Runs the CANDIDATE Prepare CLI offline on a snapshot copy of the saved Growth
Call collection into a NEW derived directory (initial output preserved).
Independently inspects the raw parent HTML with BeautifulSoup (no fetch, no
script execution, no form submission): parent form/label counts, booking iframe
source, native-main content boundary, unavailable child content. Compares the
fresh initial output against both the saved initial package and the reviewed
package. Writes JSON result to argv[1].
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

SNAP = Path("/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
SCRIPT = SNAP / "agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py"
GC_COLL = SNAP / "outputs/collections/CyberizeGroup-growth-call-follow-up-2026-10-13_223736"
INITIAL_SAVED = SNAP / "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736"
REVIEWED = SNAP / "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    result = {}
    copy = SNAP / "outputs/qa-t16/collection-copy"
    if copy.exists():
        shutil.rmtree(copy)
    copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(GC_COLL, copy)
    out = SNAP / "outputs/prepared/qa-t16-initial"
    proc = subprocess.run(
        [str(VENV), str(SCRIPT), "--collection", str(copy), "--out", str(out)],
        cwd=SNAP, capture_output=True, text=True,
    )
    result["fresh_initial_cli"] = {"exit": proc.returncode, "stdout": proc.stdout,
                                    "stderr": proc.stderr, "out_created": out.exists()}

    body = copy / "attempts/1919308e975782c911a6d794/7ec2e8ca209e4388ad37785247758eb2/body"
    soup = BeautifulSoup(body.read_bytes().decode("utf-8"), "html.parser")
    forms = soup.select("form")
    labels = [lbl.get_text(" ", strip=True) for lbl in soup.select("label")]
    iframes = [{"src": fr.get("src"), "title": fr.get("title")} for fr in soup.select("iframe")]
    main_node = soup.select_one(".tcb-post-content #tve_editor")
    main_text = main_node.get_text(" ", strip=True) if main_node else None
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    meta_desc = soup.select_one('meta[name="description"]')
    result["raw_parent_inspection"] = {
        "body_sha256": sha(body.read_bytes()),
        "form_count": len(forms),
        "form_actions": [f.get("action") for f in forms],
        "label_texts": labels,
        "iframes": iframes,
        "native_main_boundary": ".tcb-post-content #tve_editor",
        "native_main_text": main_text,
        "native_main_text_empty": main_text == "",
        "page_title": title,
        "meta_description": meta_desc.get("content") if meta_desc else None,
        "booking_iframe_in_main_subtree": bool(main_node and main_node.find("iframe")) if main_node else None,
    }

    page_rel = "pages/1919308e975782c911a6d794.md"
    fresh_page = (out / page_rel).read_bytes() if (out / page_rel).is_file() else None
    saved_initial_page = (INITIAL_SAVED / page_rel).read_bytes()
    reviewed_page = (REVIEWED / page_rel).read_bytes()
    result["initial_page_comparison"] = {
        "fresh_bytes": len(fresh_page) if fresh_page else None,
        "saved_initial_bytes": len(saved_initial_page),
        "reviewed_bytes": len(reviewed_page),
        "fresh_equals_saved_initial": fresh_page == saved_initial_page,
        "fresh_page_sha256": sha(fresh_page) if fresh_page else None,
        "saved_initial_sha256": sha(saved_initial_page),
        "reviewed_sha256": sha(reviewed_page),
        "fresh_initial_near_empty": fresh_page == saved_initial_page and len(saved_initial_page) < 300,
    }
    for name, pkg in (("fresh", out), ("saved_initial", INITIAL_SAVED), ("reviewed", REVIEWED)):
        bp = pkg / "BOILERPLATE.md"
        result.setdefault("boilerplate_comparison", {})[name] = {
            "sha256": sha(bp.read_bytes()) if bp.is_file() else None
        }

    embeds = json.loads((REVIEWED / "EMBEDS_AND_FORM_LABELS.json").read_bytes())
    result["reviewed_embeds_file"] = embeds
    rindex = json.loads((REVIEWED / "SOURCE_INDEX.json").read_bytes())
    page0 = rindex["pages"][0]
    result["reviewed_package_checks"] = {
        "main_text_empty_flag": page0["extraction"].get("main_text_empty"),
        "gaps": page0["gaps"],
        "preparation_outcome": rindex.get("preparation_outcome"),
        "classification_basis": page0.get("classification_basis"),
        "page_presentation_label": page0["prepared"].get("presentation"),
        "embeds_file_present": (REVIEWED / "EMBEDS_AND_FORM_LABELS.json").is_file(),
        "child_content_marked_unknown": any("UNKNOWN" in (rindex.get("preparation_outcome") or "", )
                                            for _ in [0]) or "UNKNOWN" in rindex.get("preparation_outcome", ""),
        "initial_extraction_note": rindex.get("initial_extraction"),
    }
    gaps_md = (REVIEWED / "GAPS_AND_REQUESTS.md").read_text()
    result["reviewed_gaps_mentions_unknown"] = {
        "contains_UNKNOWN": "UNKNOWN" in gaps_md,
        "contains_PARTIAL": "PARTIAL" in gaps_md,
    }
    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("fresh initial exit:", result["fresh_initial_cli"]["exit"])
    print("raw parent: forms", result["raw_parent_inspection"]["form_count"],
          "| labels", len(result["raw_parent_inspection"]["label_texts"]),
          "| iframes", result["raw_parent_inspection"]["iframes"])
    print("native main text empty:", result["raw_parent_inspection"]["native_main_text_empty"])
    print("initial page comparison:", {k: v for k, v in result["initial_page_comparison"].items()
                                        if k in ("fresh_bytes", "saved_initial_bytes", "reviewed_bytes", "fresh_equals_saved_initial")})
    print("reviewed preparation_outcome:", result["reviewed_package_checks"]["preparation_outcome"])
    print("reviewed gaps mention UNKNOWN/PARTIAL:", result["reviewed_gaps_mentions_unknown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())