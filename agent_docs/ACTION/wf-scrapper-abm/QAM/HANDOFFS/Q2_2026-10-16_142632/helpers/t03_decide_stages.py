"""Q2 T-03 instrument: explicit DECIDE stages and selection on copied saved data.

G3 correction: run 1 of this helper misread the import output shape —
`decide import --out` creates a DIRECTORY sealed with inventory.json and
INVENTORY.md, and the export binding is the SHA-256 of the inventory.json
file itself (no sibling inventory review file; only export writes
plan.review.json). Row choice also now follows the real schema: HTML choices
must name kind=='document' rows; imported REST evidence rows carry
rest_items and export single-item scopes (paginate false). Whole-collection
bound semantics (rest_collection rows requiring --collection-max-pages) do
not arise from import and remain covered by the cited suite node. Rerun of
the invalidated T-03 measurement only; T-02 is unaffected.

On scratch COPIES of the saved first-selected collection (and selected-live-01
for REST-item semantics), run the public CLI stages import → list → select
(QA/example actor) → export with explicit paths. Verify separate outputs and
printed 'no collection executed' markers (no implicit next-stage
invocation); only explicitly included choices export; unspecified rows stay
undecided. Exercise unknown-ID and conflicting include/exclude CLI refusals.
Prove a decision bound to different exact inventory bytes (reformatting, then
reordering) refuses export. Verify a one-item REST choice does not expand to a
collection. Finally use `python -m recon_pipeline add --collection COPY
--plan EXPORT` offline and observe zero transport invocations. The exported
plan contains saved external URLs and is used for the offline add ONLY —
never collect/resume. Writes JSON to argv[1].
"""
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRATCH = Path("/tmp/opencode/q2-scratch-20261016")
SNAP = SCRATCH / "snapshot-scoped"
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
ACTOR = "Opy — Q2 QA example actor"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_map(root: Path) -> dict:
    return {str(p.relative_to(root)): sha(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def decide(args) -> dict:
    proc = subprocess.run([str(VENV), "-m", "recon_pipeline.decide", *args],
                          cwd=SNAP, capture_output=True, text=True)
    return {"argv": ["python", "-m", "recon_pipeline.decide", *args], "exit": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr}


def collect_cli(args) -> dict:
    proc = subprocess.run([str(VENV), "-m", "recon_pipeline", *args],
                          cwd=SNAP, capture_output=True, text=True)
    return {"argv": ["python", "-m", "recon_pipeline", *args], "exit": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr}


def main() -> int:
    work = SCRATCH / "t03"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    colls = SCRATCH / "t03-collections"
    if colls.exists():
        shutil.rmtree(colls)
    colls.mkdir(parents=True)
    result = {
        "instrument_correction": ("run 1 misread import output shape: --out is a sealed directory; "
                                  "binding is the inventory.json file SHA-256; corrected and rerun"),
        "acknowledgment": ("The exported plan contains saved external URLs; it is used for the "
                           "offline add stage only. collect/resume are never invoked with it "
                           "(T-03 prohibition recorded)."),
    }

    copy1 = colls / "first-selected-copy"
    shutil.copytree(SNAP / "outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505", copy1)
    src_map = tree_map(copy1)
    checklist = json.loads((copy1 / "checklist.json").read_bytes())
    page_urls = {it["url"] for it in checklist["items"]}

    inv_dir = work / "inventory"
    r1 = decide(["import", "--collection", str(copy1), "--out", str(inv_dir)])
    inv_file = inv_dir / "inventory.json"
    inventory = json.loads(inv_file.read_bytes()) if inv_file.is_file() else {"items": []}
    result["stage1_import"] = {
        "cli": r1,
        "out_is_directory": inv_dir.is_dir(),
        "sealed_files": sorted(p.name for p in inv_dir.rglob("*")),
        "inventory_id": inventory.get("inventory_id"),
        "items_count": len(inventory.get("items", [])),
        "items": inventory.get("items", []),
    }

    r2 = decide(["list", "--inventory", str(inv_file)])
    result["stage2_list"] = r2

    items = inventory.get("items", [])
    docs = [x for x in items if x.get("kind") == "document"]
    linked = [x for x in docs if x.get("url") not in page_urls]
    chosen_row = (linked or docs or [None])[0]
    result["stage3_selection_inputs"] = {
        "document_rows": len(docs),
        "linked_heading_rows_preferred": len(linked),
        "chosen_row": chosen_row,
    }
    chosen = chosen_row["id"] if chosen_row else None
    dec = work / "decision.json"
    if chosen:
        r3 = decide(["select", "--inventory", str(inv_file), "--out", str(dec),
                     "--by", ACTOR, "--example", "--include-html", chosen])
        result["stage3_select"] = r3
        decision = json.loads(dec.read_bytes()) if dec.is_file() else {}
        result["stage3_decision"] = decision
        result["stage3_only_explicit_choices"] = {
            "include_html_is_exactly_chosen": decision.get("include_html") == [chosen],
            "include_rest_empty": not decision.get("include_rest"),
            "exclude_empty": not decision.get("exclude"),
            "unspecified_rows_undecided_note": decision.get("note"),
            "inventory_binding_sha256": decision.get("inventory_file_sha256"),
            "inventory_file_sha256_actual": sha(inv_file.read_bytes()),
            "binding_matches_file": decision.get("inventory_file_sha256") == sha(inv_file.read_bytes()),
        }

    neg1 = decide(["select", "--inventory", str(inv_file), "--out", str(work / "neg-unknown.json"),
                   "--by", ACTOR, "--include-html", "nonexistent000000000000"])
    neg1["refused_visibly"] = neg1["exit"] == 2 and "DECIDE refused:" in neg1["stderr"]
    if chosen:
        neg2 = decide(["select", "--inventory", str(inv_file), "--out", str(work / "neg-conflict.json"),
                       "--by", ACTOR, "--include-html", chosen, "--exclude", chosen])
        neg2["refused_visibly"] = neg2["exit"] == 2 and "DECIDE refused:" in neg2["stderr"]
    else:
        neg2 = {"skipped": "no document row to conflict"}
    result["select_negatives"] = {"unknown_id": neg1, "conflicting_include_exclude": neg2}

    plan = work / "plan.json"
    r4 = decide(["export", "--inventory", str(inv_file), "--decision", str(dec), "--out", str(plan)])
    plan_data = json.loads(plan.read_bytes()) if plan.is_file() else {}
    plan_review_path = work / "plan.review.json"
    plan_review = json.loads(plan_review_path.read_bytes()) if plan_review_path.is_file() else None
    result["stage4_export"] = {
        "cli": r4,
        "plan": plan_data,
        "plan_review": plan_review,
        "selected_only": (chosen_row and plan_data.get("pages") == [chosen_row["url"]]) or None,
        "rest_absent_or_empty": not plan_data.get("rest"),
        "collection_executed_false": bool(plan_review and plan_review.get("collection_executed") is False),
        "recorded_by": plan_review.get("recorded_by") if plan_review else None,
        "no_implicit_next_stage_markers": (
            "no collection executed" in result["stage3_select"]["stdout"]
            and "no collection executed" in r4["stdout"]) if chosen else None,
    }

    original_bytes = inv_file.read_bytes()
    parsed = json.loads(original_bytes)
    inv_file.write_bytes(json.dumps(parsed, ensure_ascii=False, indent=1).encode())
    ref1 = decide(["export", "--inventory", str(inv_file), "--decision", str(dec),
                   "--out", str(work / "plan-reformatted-refusal.json")])
    ref1["refused_visibly"] = ref1["exit"] == 2 and "DECIDE refused:" in ref1["stderr"]
    inv_file.write_bytes(original_bytes)
    ref2 = {"skipped": "fewer than two items", "refused_visibly": None}
    if isinstance(parsed.get("items"), list) and len(parsed["items"]) > 1:
        reordered = dict(parsed)
        reordered["items"] = parsed["items"][1:] + parsed["items"][:1]
        inv_file.write_bytes(json.dumps(reordered, ensure_ascii=False, indent=2).encode())
        ref2 = decide(["export", "--inventory", str(inv_file), "--decision", str(dec),
                       "--out", str(work / "plan-reordered-refusal.json")])
        ref2["refused_visibly"] = ref2["exit"] == 2 and "DECIDE refused:" in ref2["stderr"]
        inv_file.write_bytes(original_bytes)
    result["binding_refusals"] = {"reformatted_inventory": ref1, "reordered_inventory": ref2}

    copy2 = colls / "selected-live-01-copy"
    shutil.copytree(SNAP / "outputs/collections/CyberizeGroup-selected-live-01", copy2)
    inv2_dir = work / "inventory-rest"
    inv2_file = inv2_dir / "inventory.json"
    r5 = decide(["import", "--collection", str(copy2), "--out", str(inv2_dir)])
    inv2 = json.loads(inv2_file.read_bytes()) if inv2_file.is_file() else {"items": []}
    rest_rows = [x for x in inv2.get("items", []) if x.get("rest_items")]
    rest_findings = {"import": r5, "items": inv2.get("items", []),
                     "rows_with_rest_items": len(rest_rows),
                     "collection_bound_citation": ("whole-REST-collection export requires an explicit "
                                                    "--collection-max-pages on rest_collection rows, which "
                                                    "recon (not import) creates; covered by "
                                                    "tests/test_decide.py::test_unknown_conflict_and_broad_collection_need_explicit_scope")}
    if rest_rows:
        rid = rest_rows[0]["id"]
        dec2 = work / "decision-rest.json"
        r6 = decide(["select", "--inventory", str(inv2_file), "--out", str(dec2),
                     "--by", ACTOR, "--include-rest", rid])
        plan2 = work / "plan-rest.json"
        r7 = decide(["export", "--inventory", str(inv2_file), "--decision", str(dec2), "--out", str(plan2)])
        plan2_data = json.loads(plan2.read_bytes()) if plan2.is_file() else {}
        entries = plan2_data.get("rest") or []
        rest_findings["single_item_choice"] = {
            "select": r6, "export": r7,
            "chosen_row_id": rid,
            "rest_scope": entries,
            "no_collection_expansion": all(not e.get("paginate") for e in entries),
            "single_item_endpoints_only": sorted(e["url"] for e in entries)
            == sorted(x["url"] for x in rest_rows[0]["rest_items"]),
        }
    else:
        rest_findings["cli_variant_skipped"] = ("no imported row carries rest_items; single-item REST "
                                                "scope covered by the suite citation above")
    result["rest_row_semantics"] = rest_findings

    copy3 = colls / "first-selected-add-copy"
    shutil.copytree(SNAP / "outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505", copy3)
    before = tree_map(copy3)
    t0 = time.monotonic()
    r10 = collect_cli(["add", "--collection", str(copy3), "--plan", str(plan)])
    elapsed = time.monotonic() - t0
    after = tree_map(copy3)
    added = sorted(k for k in after if k not in before)
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in before if after.get(k) != before[k])
    try:
        add_stdout = json.loads(r10["stdout"])
    except (json.JSONDecodeError, ValueError):
        add_stdout = r10["stdout"]
    result["stage5_offline_add"] = {
        "cli": r10,
        "stdout_json": add_stdout,
        "elapsed_s": round(elapsed, 2),
        "new_files": added, "removed_files": removed, "changed_files": changed,
        "attempt_bytes_unchanged": not any(k.startswith("attempts/") for k in added + changed),
        "checklist_updated_only_plus_lock": set(changed) <= {"checklist.json"} and set(added) <= {".writer.lock"},
        "queued_ids": add_stdout.get("queued_ids") if isinstance(add_stdout, dict) else None,
        "zero_transport_evidence": {
            "code_path": "collector.py main(): add branch prints queued_ids and returns before run_collection/BrowserTransport is constructed",
            "no_attempt_artifacts": not any(k.startswith("attempts/") for k in added),
            "fast_completion_no_browser": elapsed < 10,
        },
        "source_collection_copy_unchanged": tree_map(copy1) == src_map,
    }

    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    s1 = result["stage1_import"]
    print("import exit:", r1["exit"], "| out is dir:", s1["out_is_directory"],
          "| sealed:", s1["sealed_files"], "| items:", s1["items_count"])
    print("list exit:", r2["exit"])
    print("chosen row:", chosen, "| linked-heading preferred:", bool(linked))
    print("select exit:", result["stage3_select"]["exit"] if chosen else "SKIPPED",
          "| only explicit choices:", result.get("stage3_only_explicit_choices", {}).get("include_html_is_exactly_chosen"),
          "| binding matches file:", result.get("stage3_only_explicit_choices", {}).get("binding_matches_file"))
    print("select negatives: unknown id:", neg1["refused_visibly"],
          "| conflict:", neg2.get("refused_visibly"))
    print("export exit:", r4["exit"], "| selected only:", result["stage4_export"]["selected_only"],
          "| rest empty:", result["stage4_export"]["rest_absent_or_empty"],
          "| collection_executed False:", result["stage4_export"]["collection_executed_false"])
    print("reformat refusal:", ref1["refused_visibly"], "| reorder refusal:", ref2.get("refused_visisible" if False else "refused_visibly"))
    if rest_rows:
        print("REST single-item no expansion:", rest_findings["single_item_choice"]["no_collection_expansion"],
              "| endpoints only:", rest_findings["single_item_choice"]["single_item_endpoints_only"])
    else:
        print("REST CLI variant skipped; suite citation recorded")
    a = result["stage5_offline_add"]
    print("offline add exit:", r10["exit"], "| queued_ids:", a["queued_ids"],
          "| new:", a["new_files"], "| changed:", a["changed_files"],
          "| attempts untouched:", a["attempt_bytes_unchanged"], "| elapsed:", a["elapsed_s"], "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())