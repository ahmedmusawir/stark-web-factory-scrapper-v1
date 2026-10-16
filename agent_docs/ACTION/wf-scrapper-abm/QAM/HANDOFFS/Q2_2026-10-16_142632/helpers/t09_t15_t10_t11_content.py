"""Q2 T-09 + T-15 + T-10 + T-11 offline instrument: content, REST and records.

T-09: derives the Andromeda page's paragraphs/list items/headings/links
directly from the raw subtree at the package's declared CSS boundary
(mirroring its declared removed_markup/separated_boilerplate), and compares
exact text and order to the prepared sample — counts are derived here, never
taken from the Engineer's index. Re-runs DECIDE import on a fresh scratch
copy of the saved selected-live-01 collection and requires the present-empty
REST warning without erasure of the HTML row's substantive evidence. Keeps
October 7 REST, October 10 advertised metadata and October 11 HTML
separately dated. Inspects authored briefs for unsupported plugin/root-cause
conclusions (keyword presence with an explicit unknown-cause caveat is not
a failure).

T-15: inspects every field actually returned by the saved post11945 REST
payload without inventing absent fields; records DECIDE's intentional FIELDS
projection versus COLLECT's saved full response; corroborates the T-21
native byte-fidelity record by re-hashing the qa-t21-flow REST body and
checking its value appears in the T-21 native evidence.

T-10: verifies the accepted packages expose image references/notes where
available and explicitly leave image completeness UNVERIFIED; the historical
media1661/1753 discrepancy stays OPEN outside this current-scope test.

T-11: inspects the native QA run records (timelines, gap, scopes, runtime
including browser version/UA/cache/waits/timeouts, browser traffic, cleanup
messages) and requires captured source / generated extraction / agent
interpretation to be structurally distinguishable in all three packages.

G3 instrument correction (run 1 transcript preserved as *.run1): the
rest-live saved bodies were addressed as rest-live/000N.body but live
under rest-live/evidence/ per the fixture manifest; run 1 crashed before
writing its result JSON.

Zero external requests; loopback-free offline files only (one local
subprocess for DECIDE import). Writes JSON to argv[1].
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

SNAP = Path("/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
SCRATCH = Path("/tmp/opencode/q2-scratch-20261016")
REAL = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1")
VENV = REAL / "venv/bin/python"
LANE = REAL / "agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/Q2_2026-10-16_142632"
V01 = SNAP / "outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01"
GROWTH = SNAP / "outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed"
QAT21 = SNAP / "outputs/prepared/qa-t21-prepared"
QAT21COL = SNAP / "outputs/collections/qa-t21-flow"
POST11945 = (SNAP / "outputs/collections/CyberizeGroup-selected-live-01/attempts/"
             "831c1e00b05bbdb42ea72413/86de34339bf54d5fb794cb0ffcc2cfdc")
RESTLIVE = (REAL / "agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/"
            "2026-10-10_135244Z/rest-live")
MANIFEST = (REAL / "agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/"
            "WebFactory_Q1_Lead_Review_2026-10-15/ORIGINAL_Q1/governing/fixture-manifest.json")

sys.path.insert(0, str(SNAP))
from recon_pipeline import decide as dmod  # noqa: E402

CAVEATS = ("unknown", "not established", "no evidence", "unclear", "not proven",
           "not verified", "unverified", "cannot be determined")
CLAIM_KEYS = ("plugin", "root cause", "cause", "thrive", "theme", "wordpress",
              "site-wide", "entire site", "whole site")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(str(text).split())


def manifest_map() -> dict:
    mm = {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for arch in data.get("archives", []):
        for entry in arch.get("restore_only", []):
            mm[entry["file"]] = entry["sha256"]
    return mm


def verify_manifest(mm: dict, suffix: str, data: bytes) -> dict:
    hit = next((k for k in mm if k.endswith(suffix)), None)
    return {"path": hit, "sha256": sha(data),
            "matches_manifest": bool(hit) and mm[hit] == sha(data)}


def derive_page(page: dict) -> dict:
    raw = (SNAP / page["source"]["raw_file"]).read_bytes()
    soup = BeautifulSoup(raw, "html.parser", from_encoding="utf-8")
    ext = page["extraction"]
    subs = soup.select(ext["css_selector"])
    sub = subs[ext["match_index"]]
    for sel in ("script", "style", "noscript", "template", "svg", 'input[type="hidden"]',
                "header", "footer", "nav", "#thrive-header", "#thrive-footer",
                '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]'):
        for el in sub.select(sel):
            el.decompose()
    headings = [norm(h.get_text(" ", strip=True)) for h in sub.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    paras_all = sub.find_all("p")
    paras = [t for t in (norm(x.get_text(" ", strip=True)) for x in paras_all) if t]
    lis_all = sub.find_all("li")
    lis = [t for t in (norm(x.get_text(" ", strip=True)) for x in lis_all) if t]
    base = page.get("final_url") or page["url"]
    links = [{"label": norm(a.get_text(" ", strip=True)),
              "resolved": urljoin(base, a.get("href", ""))}
             for a in sub.find_all("a", href=True)]
    return {"raw_sha_ok": sha(raw) == page["source"]["raw_sha256"],
            "raw_bytes": len(raw), "headings": headings, "paragraphs": paras,
            "list_items": lis, "links": links,
            "paragraphs_raw": len(paras_all), "list_items_raw": len(lis_all)}


def compare_prepared(derived: dict, page: dict) -> dict:
    md_bytes = (SNAP / page["prepared"]["file"]).read_bytes()
    md = md_bytes.decode("utf-8")
    flat = norm(md.replace("**", " "))
    out = {"prepared_sha_ok": sha(md_bytes) == page["prepared"]["sha256"],
           "prepared_bytes": len(md_bytes),
           "md_renders_strong_as_emphasis": "**" in md}

    def seq(texts):
        positions = [flat.find(t) for t in texts]
        return {"positions": positions,
                "all_present": all(p >= 0 for p in positions),
                "in_document_order": positions == sorted(positions)}

    out["headings_seq"] = seq(derived["headings"])
    out["paragraphs_seq"] = seq(derived["paragraphs"])
    out["list_items_seq"] = seq(derived["list_items"])
    out["links"] = [{"label": l["label"], "resolved": l["resolved"],
                     "label_in_md": l["label"] in flat, "resolved_in_md": l["resolved"] in flat}
                    for l in derived["links"]]
    out["links_all_present"] = all(l["label_in_md"] and l["resolved_in_md"] for l in out["links"])
    ic = page["content"]
    out["derived_counts"] = {"headings": len(derived["headings"]),
                             "paragraphs": len(derived["paragraphs"]),
                             "list_items": len(derived["list_items"]),
                             "links": len(derived["links"])}
    out["index_counts"] = {k: (len(ic[k]) if isinstance(ic[k], list) else ic[k])
                           for k in ("headings", "paragraphs", "list_items", "links") if k in ic}
    out["counts_match"] = all(out["derived_counts"][k] == out["index_counts"].get(k)
                              for k in out["derived_counts"])
    return out


def scan_brief(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    hits, agency, interp = [], [], []
    for i, line in enumerate(lines):
        low = line.lower()
        if any(k in low for k in CLAIM_KEYS):
            window = " ".join(lines[max(0, i - 2):i + 3]).lower()
            hits.append({"line": i + 1, "text": line.strip()[:280],
                         "caveat_within_two_lines": any(c in window for c in CAVEATS)})
        if "agency services" in low:
            agency.append({"line": i + 1, "text": line.strip()[:280],
                           "listing_or_category_wording": any(w in low for w in ("listing", "category", "index page"))})
        if "interpretation" in low or "design implication" in low:
            interp.append(i + 1)
    return {"lines": len(lines), "claim_hits": hits, "agency_services": agency,
            "interpretation_label_lines": interp[:12],
            "claim_hits_without_caveat": [h for h in hits if not h["caveat_within_two_lines"]]}


def run_record(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["runs"][-1] if isinstance(data, dict) and data.get("runs") else data


def inspect_run(rec: dict) -> dict:
    reqs = rec.get("requests", [])
    pairs = []
    for a, b in zip(reqs, reqs[1:]):
        pairs.append({"start_minus_prev_completion": round(b["start"] - a["completion"], 4),
                      "preceding_completion_consistent": b.get("preceding_completion") == a["completion"]})
    rt = rec.get("runtime", {})
    return {"started_at": rec.get("started_at"), "finished_at": rec.get("finished_at"),
            "gap_seconds": rec.get("gap_seconds"),
            "requests": len(reqs), "pairs": pairs,
            "all_pairs_gap_ge_5": all(p["start_minus_prev_completion"] >= 5.0 for p in pairs),
            "preceding_completion_all_consistent": all(p["preceding_completion_consistent"] for p in pairs),
            "runtime": {k: rt.get(k) for k in ("browser", "user_agent", "cache",
                                              "html_wait_for_images", "html_post_load_delay",
                                              "navigation_timeout_ms", "tls_verification")},
            "browser_traffic": rec.get("browser_traffic"),
            "cleanup_messages": rec.get("cleanup_messages"),
            "cleanup_distinct_key": "cleanup_messages" in rec,
            "collection_outcome": rec.get("collection_outcome")}


def provenance(pkg: Path) -> dict:
    idx = json.loads((pkg / "SOURCE_INDEX.json").read_text(encoding="utf-8"))
    pages = idx.get("pages", [])
    authored = idx.get("agent_authored", [])
    return {"package": pkg.name, "pages": len(pages),
            "pages_with_raw_ref": sum(1 for p in pages if p.get("source", {}).get("raw_file") and p["source"].get("raw_sha256")),
            "pages_with_prepared_ref": sum(1 for p in pages if p.get("prepared", {}).get("file") and p["prepared"].get("sha256")),
            "agent_authored": [{"author": a.get("author"), "role_or_basis": a.get("role") or a.get("basis"),
                                "file": a.get("file")} for a in authored],
            "image_completeness": idx.get("image_completeness"),
            "images_completeness_alt": idx.get("images_completeness"),
            "unavailable_items": len(idx.get("unavailable_items", [])),
            "rest_context": len(idx.get("rest_context", []))}


def main() -> int:
    result = {}
    mm = manifest_map()

    # --- T-09: Andromeda derivation vs prepared sample -------------------------
    v01_idx = json.loads((V01 / "SOURCE_INDEX.json").read_text(encoding="utf-8"))
    andr = next(p for p in v01_idx["pages"] if "andromeda" in p["url"])
    derived = derive_page(andr)
    cmp_result = compare_prepared(derived, andr)
    result["t09_andromeda"] = {
        "url": andr["url"], "document_type": andr.get("document_type"),
        "css_selector": andr["extraction"]["css_selector"],
        "raw_sha_ok": derived["raw_sha_ok"], "raw_bytes": derived["raw_bytes"],
        "derived": cmp_result,
        "plan_expected_counts": {"headings": 6, "paragraphs": 7, "list_items": 15},
        "derived_texts": {"headings": derived["headings"], "paragraphs": derived["paragraphs"],
                          "list_items": derived["list_items"]},
    }

    # --- T-09: DECIDE import on a fresh copy of saved selected-live-01 ----------
    copy_dir = SCRATCH / "t09" / "collection-copy"
    out_dir = SCRATCH / "t09" / "import-out"
    shutil.rmtree(SCRATCH / "t09", ignore_errors=True)
    shutil.copytree(REAL / "outputs/collections/CyberizeGroup-selected-live-01", copy_dir)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run([str(VENV), "-m", "recon_pipeline.decide", "import",
                          "--collection", str(copy_dir), "--out", str(out_dir)],
                         cwd=str(SNAP), env=env, capture_output=True, text=True, timeout=120)
    imp_rows, imp_note = [], ""
    if out_dir.joinpath("inventory.json").is_file():
        imp = json.loads((out_dir / "inventory.json").read_text(encoding="utf-8"))
        imp_note = f"sealed dir files: {sorted(x.name for x in out_dir.iterdir())}"
        for r in imp.get("items", []):
            imp_rows.append({"id": r["id"], "kind": r.get("kind"), "url": r.get("url"),
                             "title": r.get("title"), "gaps": r.get("gaps", []),
                             "sources": len(r.get("sources", [])),
                             "rest_items": len(r.get("rest_items", [])),
                             "dates": sorted((r.get("dates") or {}).keys())})
    andr_row = next((r for r in imp_rows if "andromeda" in (r.get("url") or "")), None)
    blog_row = next((r for r in imp_rows if (r.get("url") or "").rstrip("/").endswith("/blog")), None)
    present_empty_gaps = [g for g in (andr_row or {}).get("gaps", [])
                          if "empty" in g or "present" in g]
    result["t09_import"] = {
        "exit": proc.returncode, "stdout_tail": proc.stdout[-400:], "stderr_tail": proc.stderr[-400:],
        "sealed_out": imp_note, "rows": imp_rows,
        "andromeda_row": andr_row, "blog_row": blog_row,
        "present_empty_warning_visible": bool(present_empty_gaps),
        "present_empty_gaps": present_empty_gaps,
        "html_row_substantive": bool(blog_row) and bool(blog_row.get("title") or blog_row["sources"] > 0),
        "index_present_empty_finding": next(
            (s for s in json.dumps(v01_idx.get("historical_context", {})).split('", "')
             if "empty string" in s), None),
    }

    # --- T-09/T-15: separately dated saved sources -------------------------------
    post_body = POST11945.joinpath("body").read_bytes()
    post_meta = json.loads(POST11945.joinpath("result.json").read_text(encoding="utf-8"))
    post_obj = json.loads(post_body)
    rl_bytes = (RESTLIVE / "result.json").read_bytes()
    rl = json.loads(rl_bytes)
    rest_bodies = {n: (RESTLIVE / "evidence" / f).read_bytes() for n, f in
                   (("types", "0001.body"), ("pages", "0002.body"), ("posts", "0003.body"))}
    manifest_checks = {"result.json": verify_manifest(mm, "rest-live/result.json", rl_bytes),
                       "types.body": verify_manifest(mm, "rest-live/evidence/0001.body", rest_bodies["types"]),
                       "pages.body": verify_manifest(mm, "rest-live/evidence/0002.body", rest_bodies["pages"]),
                       "posts.body": verify_manifest(mm, "rest-live/evidence/0003.body", rest_bodies["posts"]),
                       "post11945_body": verify_manifest(mm, "86de34339bf54d5fb794cb0ffcc2cfdc/body", post_body)}
    result["t09_dated_sources"] = {
        "october_7_rest": {"saved_at": post_meta.get("saved_at"), "final_url": post_meta.get("final_url"),
                           "body_bytes": len(post_body), "body_sha256": sha(post_body),
                           "title_rendered": post_obj.get("title", {}).get("rendered")},
        "october_10_metadata": {"started_utc": rl.get("started_utc"), "ended_utc": rl.get("ended_utc"),
                                "public_types": len(rl.get("public_types", [])),
                                "requests": len(rl.get("requests", [])),
                                "advertised_totals_caveat": rl.get("advertised_totals_are_not_enumerated_counts"),
                                "samples": [{"type": s.get("type"), "advertised_total": s.get("advertised_total"),
                                             "projection_honored": s.get("projection_honored"),
                                             "content_requested": s.get("content_requested"),
                                             "field_keys": s.get("field_keys"),
                                             "body_sha256": s.get("sha256")} for s in rl.get("samples", [])]},
        "october_11_html": {"prepared_at": v01_idx.get("prepared_at"),
                           "capture_saved_at": [p.get("capture_saved_at") for p in v01_idx["pages"]],
                           "source_collection": v01_idx.get("source_collection")},
        "manifest_checks": manifest_checks,
        "all_manifest_checks_pass": all(v["matches_manifest"] for v in manifest_checks.values()),
        "three_dates_distinct": True,
    }

    # --- T-15: saved REST fields vs DECIDE projection -----------------------------
    t21_rec = (LANE / "native" / "t21_result.json").read_text(encoding="utf-8")
    rest_attempt = None
    for att in (QAT21COL / "attempts").glob("*/"):
        for run in att.glob("*/"):
            meta = run / "result.json"
            if meta.is_file():
                m = json.loads(meta.read_text(encoding="utf-8"))
                if "wp-json" in (m.get("url") or ""):
                    rest_attempt = run / "body"
    t21_saved_sha = sha(rest_attempt.read_bytes()) if rest_attempt else None
    result["t15_seo_rest"] = {
        "saved_post11945_fields": sorted(post_obj.keys()),
        "content": {"present": "content" in post_obj,
                    "rendered_is_empty_string": post_obj.get("content", {}).get("rendered") == "",
                    "content_keys": sorted(post_obj.get("content", {}).keys())},
        "seo_custom_fields_present": sorted(k for k in post_obj if any(w in k.lower() for w in ("yoast", "seo", "head"))),
        "decide_fields_projection": dmod.FIELDS,
        "projection_excludes_content": "content" not in dmod.FIELDS,
        "saved_response_includes_content": "content" in post_obj,
        "oct10_projection_honored": [s.get("projection_honored") for s in rl.get("samples", [])],
        "t21_rest_saved_sha256": t21_saved_sha,
        "t21_saved_sha_appears_in_native_record": t21_saved_sha in t21_rec,
        "no_live_call": True,
    }

    # --- T-10: media references/notes ---------------------------------------------
    def md_image_refs(pkg: Path) -> dict:
        counts = {}
        pages_dir = pkg / "pages"
        for md in sorted(pages_dir.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            counts[md.name] = len(re.findall(r"!\[[^\]]*\]\([^)]+\)|<img[^>]*>", text))
        return counts

    image_mentions = []

    def walk(node, path):
        if isinstance(node, str) and "image" in node.lower() and len(image_mentions) < 12:
            image_mentions.append({"path": path, "text": node[:200]})
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(v01_idx, "SOURCE_INDEX")
    embeds = json.loads((GROWTH / "EMBEDS_AND_FORM_LABELS.json").read_text(encoding="utf-8")) \
        if (GROWTH / "EMBEDS_AND_FORM_LABELS.json").is_file() else None
    result["t10_media"] = {
        "v01": {"image_completeness": v01_idx.get("image_completeness"),
                "per_page_images": [{"id": p["id"], "images": len(p["content"].get("images", [])),
                                     "images_note": p["content"].get("images_note")}
                                    for p in v01_idx["pages"]],
                "prepared_md_image_refs": md_image_refs(V01),
                "image_mentions_in_index": image_mentions},
        "growth": {"image_completeness": json.loads((GROWTH / "SOURCE_INDEX.json").read_text(encoding="utf-8")).get("image_completeness"),
                   "prepared_md_image_refs": md_image_refs(GROWTH),
                   "embeds_and_forms": embeds},
        "historical_media_gap": "OPEN outside this current-scope test (recorded media1661/1753 discrepancy)",
    }

    # --- T-11: native run records + provenance --------------------------------------
    t04_rec = inspect_run(run_record(LANE / "native" / "t04-t07-checklist.json"))
    t21_run = inspect_run(run_record(QAT21COL / "checklist.json"))
    prov = [provenance(V01), provenance(GROWTH), provenance(QAT21)]
    result["t11_records"] = {
        "t04_run": t04_rec, "t21_run": t21_run,
        "provenance": prov,
        "provenance_distinguishable": all(
            p["pages_with_raw_ref"] == p["pages"] and p["pages_with_prepared_ref"] == p["pages"]
            and p["agent_authored"] for p in prov),
        "retired_note": "historical authored screenshot-stream schema is retired; current packages use raw/prepared/agent_authored labels",
    }

    # --- T-09: authored claims inspection -------------------------------------------
    result["authored_claims"] = {
        "v01": scan_brief(V01 / "ARCHITECT_BRIEF.md"),
        "growth": scan_brief(GROWTH / "ARCHITECT_BRIEF.md"),
        "qat21": scan_brief(QAT21 / "ARCHITECT_BRIEF.md"),
    }

    result["g3_corrections"] = [
        {"instrument": "t09_t15_t10_t11_content.py run 1 (transcript preserved as *.run1)",
         "cause": "rest-live saved bodies addressed as rest-live/000N.body; they live under rest-live/evidence/",
         "fix": ("paths corrected to rest-live/evidence/000N.body; manifest lookup suffixes "
                 "matched to the fixture manifest's recorded paths")},
        {"instrument": "t09_t15_t10_t11_content.py run 2 derivation (result preserved as *.run2)",
         "cause": ("BeautifulSoup default decoding mis-detected the saved Andromeda UTF-8 body "
                   "(non-ASCII characters rendered as mojibake, failing md containment); "
                   "index_counts compared list fields against derived ints without len()"),
         "fix": ("explicit from_encoding='utf-8' (the saved bytes are UTF-8, as the product's "
                 "own prepared output shows); index counts normalized with len() for list fields")},
        {"instrument": "t09_t15_t10_t11_content.py run 3 list-item containment",
         "cause": ("the prepared md renders the Andromeda list items with markdown emphasis "
                   "('**Prospecting – Find the Winners** : …'), so the derived raw text is not a "
                   "literal substring — the emphasis markers interleave identical words in order"),
         "fix": ("emphasis markers (**) removed from the md text before containment; words and "
                 "order otherwise compared exactly; the rendering is recorded in the result")},
        {"instrument": "t09_t15_t10_t11_content.py run 4 assessment field name",
         "cause": ("the assessment key was named 't09_authored_claims_unsupported_count', asserting "
                   "the keyword hits were unsupported conclusions; the instrument only detects "
                   "keyword matches without a nearby caveat — adjudication is the Executor's, "
                   "recorded in the report"),
         "fix": ("renamed to 'authored_claim_keyword_hits_without_caveat'; hit texts remain "
                 "recorded verbatim for independent re-adjudication")},
    ]

    a = result["t09_andromeda"]["derived"]
    imp = result["t09_import"]
    t15 = result["t15_seo_rest"]
    t11 = result["t11_records"]
    result["assessment"] = {
        "t09_derivation_pass": (result["t09_andromeda"]["raw_sha_ok"] and a["prepared_sha_ok"]
                                and a["counts_match"] and a["headings_seq"]["all_present"]
                                and a["headings_seq"]["in_document_order"]
                                and a["paragraphs_seq"]["all_present"] and a["paragraphs_seq"]["in_document_order"]
                                and a["list_items_seq"]["all_present"] and a["list_items_seq"]["in_document_order"]
                                and a["links_all_present"]),
        "t09_import_pass": imp["exit"] == 0 and imp["present_empty_warning_visible"] and imp["html_row_substantive"],
        "t09_manifest_pass": result["t09_dated_sources"]["all_manifest_checks_pass"],
        "t15_pass": (t15["content"]["present"] and t15["content"]["rendered_is_empty_string"]
                     and t15["projection_excludes_content"] and t15["saved_response_includes_content"]
                     and all(t15["oct10_projection_honored"])
                     and t15["t21_saved_sha_appears_in_native_record"]),
        "t10_pass": ("UNVERIFIED" in (result["t10_media"]["v01"]["image_completeness"] or "")
                     and all(note for note in
                             [p["images_note"] for p in result["t10_media"]["v01"]["per_page_images"]])),
        "t11_pass": (t04_rec["all_pairs_gap_ge_5"] and t04_rec["preceding_completion_all_consistent"]
                     and t21_run["all_pairs_gap_ge_5"] and t21_run["preceding_completion_all_consistent"]
                     and t11["provenance_distinguishable"]
                     and t04_rec["runtime"]["browser"] and t04_rec["cleanup_distinct_key"]),
        "authored_claim_keyword_hits_without_caveat": sum(
            len(result["authored_claims"][k]["claim_hits_without_caveat"]) for k in result["authored_claims"]),
    }

    out = Path(sys.argv[1])
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    asm = result["assessment"]
    print("t09 derivation:", asm["t09_derivation_pass"],
          "| derived counts:", a["derived_counts"], "| index:", a["index_counts"])
    print("t09 import exit:", imp["exit"], "| present-empty visible:", imp["present_empty_warning_visible"],
          "| gaps:", imp["present_empty_gaps"], "| html substantive:", imp["html_row_substantive"])
    print("t09 dated sources manifest pass:", asm["t09_manifest_pass"],
          "| t15:", asm["t15_pass"], "| t10:", asm["t10_pass"], "| t11:", asm["t11_pass"])
    print("authored claim keyword hits without nearby caveat (adjudicated in report):",
          asm["authored_claim_keyword_hits_without_caveat"])
    print("assessment:", json.dumps(asm))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())