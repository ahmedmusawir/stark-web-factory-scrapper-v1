"""Q2 T-06 + T-14 offline instrument: label/inventory identity against raw source.

T-06: verifies the bound corrected review (Tony's recorded decision binding)
through the product's own seal digest, then rechecks EVERY row title against
the anchor text at its cited locator (a[href][N], zero-based document order)
in the saved blog body (evidence/0001.body, 591,675 B, source-recorded SHA).
A row's title may come from any one of its cited anchors; sibling locators
that reference image links (''), ellipsis continuations ('...') or generic
CTAs ('Read Post') are retained by the product while the guard declines them
as titles — non-matching anchor texts are recorded and classified here. The
rows whose matching anchors sit inside h2 elements are the nine actual saved
h2 texts — also derived directly from the raw h2 elements (article h2s
contain an article link; the section h2 'Additional Blog Posts' does not);
counts are derived here, never taken from any Engineer record. The later
selected-live-01 blog capture (592,886 B, internally verified against its own
result.json SHA) is an independent cross-check of the same nine texts.
Generic label variants are then exercised through the snapshot's own
candidate() guard: 'Read more →' (U+2192), 'Read more ›' (U+203A),
'READ MORE…', punctuation-only, whitespace-only, against an informative
control, plus the October 11 contract sequence — a weak label must not
replace an earlier informative title and locators must be retained. Per O6,
acceptance of the arrow variant as a title is recorded as a FINDING against
current behavior, not a waiver.

T-14: the same version's inventory.json and INVENTORY.md must agree on
every row number, ID, title, kind and URL, with all selections UNDECIDED.
INVENTORY.md titles are display()-HTML-escaped ('&' rendered as '&amp;');
they are compared after html.unescape, and the escaping is recorded.

G3 instrument corrections (run 1 preserved as *.run1):
(a) the hand-typed EXPECT_VERSION constant had dropped one character
(63 vs 64 chars, first divergence at index 38) — display-invisible under
eyeball verification; expected bindings are now derived at runtime from the
recorded decision file (outputs/selections/.../tony-decision.json) and the
row-recorded source SHA instead of being retyped;
(b) run 1 required every cited locator's anchor text to equal the title —
over-strict, since the product retains locators whose labels the guard
declines; matching is now per-row (any cited informative anchor);
(c) run 1 compared INVENTORY.md titles without reversing display()'s
HTML escaping.

Zero external requests; offline files only. Writes JSON to argv[1].
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, "/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
from recon_pipeline import decide as dmod  # noqa: E402

REAL = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1")
REV = REAL / "agent_docs/RESPONSES/OLD/response_2026-10-11_001956_label-cleanup-tony-choices_review"
DECISION = (REAL / "outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505"
            "/tony-decision.json")
BLOG2 = (REAL / "outputs/collections/CyberizeGroup-selected-live-01/attempts/"
         "1123c12ff8bf603a484f7a3c/ab86d5ab12c24022b45f08578f2bde5d")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(BeautifulSoup(str(text), "html.parser").get_text(" ", strip=True).split())


def guard_ignorable(text) -> bool:
    if not text:
        return True
    if not any(c.isalnum() for c in text):
        return True
    return text.casefold().rstrip(" .…›»>") in dmod.GENERIC_LINK_LABELS


def fresh_inv() -> dict:
    return {"schema": dmod.SCHEMA, "origin": "http://127.0.0.1/", "mode": "qa",
            "created_at": "", "context": {}, "items": [], "requests": [], "gaps": [],
            "wordpress": {"status": "not_attempted", "collections": []},
            "stop_reason": None, "cleanup_error": None}


def main() -> int:
    result = {}

    # --- binding verification (expected values from the recorded decision) ----
    inv_bytes = (REV / "inventory.json").read_bytes()
    inv = json.loads(inv_bytes)
    rows = inv["items"]
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    digest_input = {k: v for k, v in inv.items() if k != "inventory_id"}
    result["binding"] = {
        "decision_file": str(DECISION),
        "expected_from_decision_file": {
            "inventory_id": decision.get("inventory_id"),
            "inventory_file_sha256": decision.get("inventory_file_sha256")},
        "file_sha256": sha(inv_bytes),
        "file_sha_matches_decision": sha(inv_bytes) == decision.get("inventory_file_sha256"),
        "inventory_id": inv.get("inventory_id"),
        "digest_matches_version": (dmod.digest(digest_input) == inv.get("inventory_id")
                                   == decision.get("inventory_id")),
        "rows": len(rows),
        "titled_rows": sum(1 for x in rows if x.get("title")),
        "ellipsis_titles": sum(1 for x in rows if x.get("title") and "…" in x["title"]),
        "generic_cta_titles": sum(1 for x in rows
                                  if x.get("title") and guard_ignorable(norm(x["title"]))),
    }

    # --- raw-source recheck ------------------------------------------------------
    ev_bytes = (REV / "evidence" / "0001.body").read_bytes()
    recorded_ev_sha = next(s["sha256"] for row in rows for s in row.get("sources", [])
                           if s.get("file") == "evidence/0001.body" and s.get("sha256"))
    soup = BeautifulSoup(ev_bytes, "html.parser")
    anchors = soup.find_all("a", href=True)
    in_h2 = [a.find_parent("h2") is not None for a in anchors]
    by_row = {}
    locator_matches = 0
    adjacent_artifacts = 0
    guard_ignored, other_texts = [], []
    rows_with_match = 0
    for row in rows:
        title = norm(row.get("title") or "")
        entries = []
        row_matched = False
        for s in row.get("sources", []):
            if s.get("file") != "evidence/0001.body":
                continue
            m = re.match(r"^a\[href\]\[(\d+)\]$", s.get("locator", ""))
            if not m:
                continue
            n = int(m.group(1))
            t0 = norm(anchors[n].get_text(" ", strip=True)) if n < len(anchors) else None
            t1 = norm(anchors[n - 1].get_text(" ", strip=True)) if 0 < n <= len(anchors) else None
            m0 = bool(title and t0 is not None and t0 == title)
            if m0:
                locator_matches += 1
                row_matched = True
                entries.append({"locator": s["locator"], "anchor_text": t0,
                                "matches_title": True, "anchor_in_h2": in_h2[n]})
            else:
                if title and t1 == title:
                    adjacent_artifacts += 1
                if guard_ignorable(t0):
                    guard_ignored.append({"row": row["row"], "locator": s["locator"],
                                          "anchor_text": t0})
                else:
                    other_texts.append({"row": row["row"], "locator": s["locator"],
                                        "anchor_text": t0, "title": title,
                                        "anchor_href": anchors[n].get("href") if n < len(anchors) else None})
                entries.append({"locator": s["locator"], "anchor_text": t0,
                                "matches_title": False,
                                "anchor_in_h2": in_h2[n] if n < len(in_h2) else None})
        if row_matched:
            rows_with_match += 1
        by_row[row["row"]] = {"id": row["id"], "url": row["url"], "title": row.get("title"),
                              "row_matched": row_matched, "sources": entries}
    titled = sum(1 for r in by_row.values() if r["title"])
    unexplained = []
    for e in other_texts:
        row_url = (by_row.get(e["row"], {}).get("url") or "")
        if not (e.get("anchor_href") in ("#", "") or e.get("anchor_href") == row_url):
            unexplained.append(e)
    h2_rows = sorted([r for r in by_row.values()
                      if any(e["matches_title"] and e["anchor_in_h2"] for e in r["sources"])],
                     key=lambda r: r["id"])
    nine_texts = [r["title"] for r in h2_rows]
    h2_elements = soup.find_all("h2")
    article_h2_texts = sorted(norm(h.get_text(" ", strip=True))
                             for h in h2_elements if h.find("a", href=True))
    section_h2_texts = [norm(h.get_text(" ", strip=True))
                        for h in h2_elements if not h.find("a", href=True)]

    blog2_bytes = (BLOG2 / "body").read_bytes()
    blog2_meta = json.loads((BLOG2 / "result.json").read_text(encoding="utf-8"))
    soup2 = BeautifulSoup(blog2_bytes, "html.parser")
    h2_texts_2 = sorted(norm(h.get_text(" ", strip=True))
                        for h in soup2.find_all("h2") if h.find("a", href=True))
    cross_ok = article_h2_texts == h2_texts_2 == sorted(t for t in nine_texts if t)

    result["raw_source_recheck"] = {
        "evidence_sha256": sha(ev_bytes),
        "recorded_evidence_sha": recorded_ev_sha,
        "evidence_sha_matches_row_record": sha(ev_bytes) == recorded_ev_sha,
        "evidence_bytes": len(ev_bytes),
        "anchors_in_evidence": len(anchors),
        "anchors_inside_h2": sum(1 for x in in_h2 if x),
        "locator_convention": "zero_based_document_order",
        "locators_examined": sum(len(r["sources"]) for r in by_row.values()),
        "matching_locators": locator_matches,
        "adjacent_locators_matching_title": adjacent_artifacts,
        "rows_with_matching_locator": rows_with_match,
        "titled_rows": titled,
        "every_titled_row_matches_raw": rows_with_match == titled and titled > 0,
        "guard_ignored_anchor_texts_sample": guard_ignored[:12],
        "guard_ignored_count": len(guard_ignored),
        "other_anchor_texts": other_texts,
        "unexplained_informative_anchor_texts": unexplained,
        "other_anchor_note": ("non-matching informative cited texts are recorded; same-URL citations "
                              "(fragment-only '#' or row-URL hrefs) are adjudicated as expected "
                              "locator retention, not title contradictions"),
        "h2_anchored_rows_derived": len(h2_rows),
        "nine_h2_texts_derived": nine_texts,
        "raw_article_h2_texts": article_h2_texts,
        "raw_section_h2_texts": section_h2_texts,
        "article_h2_count_derived": len(article_h2_texts),
        "nine_exact_match_raw": sorted(t for t in nine_texts if t) == article_h2_texts,
        "blog2_internal_sha_ok": sha(blog2_bytes) == blog2_meta.get("sha256"),
        "blog2_bytes": len(blog2_bytes),
        "blog2_article_h2_texts": h2_texts_2,
        "cross_capture_nine_match": cross_ok,
    }

    # --- generic label guard offline cases (through the snapshot's own code) ---
    url = "http://127.0.0.1/fixture-doc"
    cases = ["Read more \u2192", "Read more \u203a", "READ MORE\u2026",
             "?!...", "   ", "\u2192\u2192",
             "How to Regain Consistency with Facebook Ads After the Andromeda Update"]
    guard = []
    for label in cases:
        iv = fresh_inv()
        dmod.candidate(iv, url, "synthetic:h2", title=label)
        row = iv["items"][0]
        guard.append({"label": label, "accepted_title": row["title"],
                      "ignored_as_title": row["title"] is None,
                      "locator_retained": len(row["sources"]) == 1})
    seq = fresh_inv()
    dmod.candidate(seq, url, "synthetic:first", title="Informative Title Kept")
    dmod.candidate(seq, url, "synthetic:h2", title="Read more \u203a")
    row_kept = seq["items"][0]
    seq2 = fresh_inv()
    dmod.candidate(seq2, url, "synthetic:first", title="Informative Title Kept")
    dmod.candidate(seq2, url, "synthetic:h2", title="Read more \u2192")
    row_arrow = seq2["items"][0]
    result["label_guard_cases"] = {
        "cases": guard,
        "informative_then_stripped_variant": {
            "final_title": row_kept["title"],
            "informative_preserved": row_kept["title"] == "Informative Title Kept",
            "sources_count": len(row_kept["sources"]),
        },
        "informative_then_arrow_variant": {
            "final_title": row_arrow["title"],
            "informative_replaced_by_arrow": row_arrow["title"] == "Read more \u2192",
            "sources_count": len(row_arrow["sources"]),
        },
        "expected_ignored_all_pass": all(
            c["ignored_as_title"] for c in guard
            if c["label"] in ("Read more \u203a", "READ MORE\u2026", "?!...", "   ", "\u2192\u2192")),
        "informative_accepted": next(
            c for c in guard if c["label"].startswith("How to Regain"))["accepted_title"] is not None,
        "arrow_variant_accepted_as_title": next(
            c for c in guard if c["label"] == "Read more \u2192")["accepted_title"] is not None,
        "o6_note": ("Per O6 the arrow variant must not supply or replace a candidate title; "
                    "acceptance is a FINDING against current behavior, not a waiver"),
    }

    # --- T-14: inventory JSON / INVENTORY.md twin agreement ----------------------
    md = (REV / "INVENTORY.md").read_text(encoding="utf-8")
    md_rows = {}
    current = None
    escaped_titles = 0
    for line in md.splitlines():
        m = re.match(r"^(\d+)\. \*\*(.+?)\*\* — `([^`]+)` — (\w+)$", line)
        if m:
            current = {"row": int(m.group(1)), "title": m.group(2), "id": m.group(3),
                       "kind": m.group(4)}
            md_rows[current["row"]] = current
            if "&amp;" in current["title"] or "&lt;" in current["title"]:
                escaped_titles += 1
            continue
        m2 = re.match(r"^\s+- URL: (.+)$", line)
        if m2 and current is not None:
            current["url"] = m2.group(1)
    twin = []
    for row in rows:
        mdr = md_rows.get(row["row"])
        json_title = row["title"] if row["title"] is not None else "[title unknown]"
        twin.append({
            "row": row["row"], "id": row["id"],
            "id_agrees": bool(mdr) and mdr["id"] == row["id"],
            "kind_agrees": bool(mdr) and mdr["kind"] == row["kind"],
            "title_agrees": bool(mdr) and html.unescape(mdr["title"]) == json_title,
            "url_agrees": bool(mdr) and mdr.get("url") == row["url"],
            "selection": row.get("selection"),
        })
    result["t14_twin"] = {
        "json_rows": len(rows), "md_rows": len(md_rows),
        "row_numbers_contiguous": sorted(md_rows) == list(range(1, len(rows) + 1)),
        "all_fields_agree": all(t["id_agrees"] and t["kind_agrees"] and t["title_agrees"]
                                and t["url_agrees"] for t in twin),
        "all_undecided": all(t["selection"] == "UNDECIDED" for t in twin),
        "md_escapes_html_in_titles": escaped_titles,
        "unescape_note": ("INVENTORY.md renders titles through display(), which HTML-escapes "
                          "'&' as '&amp;'; JSON holds raw text — compared after html.unescape"),
        "rows": twin,
    }

    b = result["binding"]
    r = result["raw_source_recheck"]
    g = result["label_guard_cases"]
    t14 = result["t14_twin"]
    result["assessment"] = {
        "binding_verified": b["file_sha_matches_decision"] and b["digest_matches_version"],
        "titles_recheck_pass": (r["evidence_sha_matches_row_record"]
                                and r["every_titled_row_matches_raw"]
                                and not r["unexplained_informative_anchor_texts"]
                                and r["locators_examined"] >= 36),
        "nine_derived_from_raw": r["h2_anchored_rows_derived"],
        "article_h2_count_derived": r["article_h2_count_derived"],
        "nine_exact_match_raw": r["nine_exact_match_raw"],
        "nine_exact_match_cross_capture": r["cross_capture_nine_match"],
        "no_ellipsis_or_generic_titles": b["ellipsis_titles"] == 0 and b["generic_cta_titles"] == 0,
        "guard_stripped_variants_pass": (g["expected_ignored_all_pass"] and g["informative_accepted"]
                                         and g["informative_then_stripped_variant"]["informative_preserved"]
                                         and g["informative_then_stripped_variant"]["sources_count"] == 2),
        "arrow_variant_finding": g["arrow_variant_accepted_as_title"]
                                 or g["informative_then_arrow_variant"]["informative_replaced_by_arrow"],
        "t14_twin_pass": t14["all_fields_agree"] and t14["all_undecided"]
                         and t14["json_rows"] == t14["md_rows"] and t14["row_numbers_contiguous"],
    }
    result["g3_corrections"] = [
        {"instrument": "t06_t14_labels.py run 1 (preserved as *.run1)",
         "cause": ("hand-typed EXPECT_VERSION dropped one character (63 vs 64 chars, first "
                   "divergence at index 38); display-invisible under eyeball verification"),
         "fix": ("expected bindings derived at runtime from the recorded decision file; "
                 "evidence SHA taken from the row-recorded value")},
        {"instrument": "t06_t14_labels.py run 1 per-row matching",
         "cause": ("required every cited locator's anchor text to equal the row title; the "
                   "product legitimately retains locators whose labels the guard declines"),
         "fix": ("per-row any-matching-anchor semantics; non-matching anchor texts classified "
                 "(guard-ignored vs other)")},
        {"instrument": "t06_t14_labels.py run 1 twin comparison",
         "cause": "INVENTORY.md titles are display()-HTML-escaped; raw comparison disagreed on 3 '&' titles",
         "fix": "html.unescape before comparison; escaping recorded"},
        {"instrument": "t06_t14_labels.py run 3 assessment",
         "cause": ("the other-anchor category treated any informative non-matching cited text as a "
                   "failure; row 6's a[href][3] is a fragment-only '#' nav dropdown toggle ('Services') "
                   "that resolves to the page's own URL — a retained same-URL citation, while the "
                   "title 'Blog' is confirmed from two other cited anchors"),
         "fix": ("other entries now record the anchor href; fragment-only or row-URL hrefs are "
                 "adjudicated programmatically as explained same-URL citations; only unexplained "
                 "informative texts fail the recheck")},
    ]

    out = Path(sys.argv[1])
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    a = result["assessment"]
    print("binding verified:", a["binding_verified"], "| rows:", b["rows"],
          "| titled:", b["titled_rows"], "| ellipsis titles:", b["ellipsis_titles"],
          "| generic titles:", b["generic_cta_titles"])
    print("locators examined:", r["locators_examined"], "| rows with matching anchor:",
          r["rows_with_matching_locator"], "/", r["titled_rows"],
          "| guard-ignored anchor texts:", r["guard_ignored_count"],
          "| other non-matching texts:", len(r["other_anchor_texts"]))
    print("nine h2 rows derived:", r["h2_anchored_rows_derived"],
          "| raw article h2 count:", r["article_h2_count_derived"],
          "| exact match raw:", r["nine_exact_match_raw"],
          "| cross-capture:", r["cross_capture_nine_match"])
    print("guard: stripped variants pass:", a["guard_stripped_variants_pass"],
          "| ARROW VARIANT ACCEPTED (O6 finding):", a["arrow_variant_finding"])
    print("t14 twin:", a["t14_twin_pass"], "| json rows:", t14["json_rows"],
          "| md rows:", t14["md_rows"], "| escaped md titles:", t14["md_escapes_html_in_titles"])
    print("assessment:", json.dumps(a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())