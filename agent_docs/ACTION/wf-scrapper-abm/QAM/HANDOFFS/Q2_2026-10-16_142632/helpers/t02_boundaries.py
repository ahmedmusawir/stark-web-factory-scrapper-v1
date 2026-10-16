"""Q2 T-02 instrument: collector input/output boundary refusals via the public CLI.

Fresh synthetic directories under QA scratch. For each documented bad-plan
class, run `python -m recon_pipeline collect --collection <new-dir>
--plan <file>` and require documented refusal exit 2, a 'Collector refused:'
message, and NO created collection directory (validation precedes mkdir per
collector.py create/plan_items). A positive control exercises plan validation
through the API with no directory side effect. Existing-collection refusal
with byte preservation, add-with-changed-pagination-scope refusal, the T-17
paginated-refresh refusal and the unknown-refresh-ID refusal run on
API-created collections (create() is local mkdir+checklist only; no
transport). Traversal/symlink/escaping negatives are cited from T-12;
existing-output/inside-collection refusals and DECIDE rejections are cited
from the T-22 regression. Writes JSON to argv[1].
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRATCH = Path("/tmp/opencode/q2-scratch-20261016")
SNAP = SCRATCH / "snapshot-scoped"
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_map(root: Path) -> dict:
    return {str(p.relative_to(root)): sha(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def run_cli(args) -> dict:
    proc = subprocess.run([str(VENV), "-m", "recon_pipeline", *args],
                          cwd=SNAP, capture_output=True, text=True)
    return {"argv": ["python", "-m", "recon_pipeline", *args], "exit": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr}


CASES = [
    ("non_http_scheme", {"pages": ["ftp://127.0.0.1/x"]}),
    ("missing_hostname", {"pages": ["http:///no-host"]}),
    ("credential_bearing_url", {"pages": ["http://user:secret@127.0.0.1/x"]}),
    ("fragment_in_url", {"pages": ["http://127.0.0.1/x#section"]}),
    ("rest_root_enumeration", {"rest": [{"url": "http://127.0.0.1:9876/wp-json"}]}),
    ("pagination_without_max_pages",
     {"rest": [{"url": "http://127.0.0.1:9876/wp-json/wp/v2/posts", "paginate": True}]}),
    ("pagination_starting_at_page_2",
     {"rest": [{"url": "http://127.0.0.1:9876/wp-json/wp/v2/posts?page=2", "paginate": True, "max_pages": 2}]}),
    ("unknown_plan_key", {"pages": ["http://127.0.0.1/x"], "bogus": 1}),
    ("unknown_rest_key", {"rest": [{"url": "http://127.0.0.1:9876/wp-json/wp/v2/posts", "per_page": 5}]}),
    ("empty_plan", {}),
    ("paginate_not_boolean",
     {"rest": [{"url": "http://127.0.0.1:9876/wp-json/wp/v2/posts", "paginate": "yes", "max_pages": 2}]}),
    ("max_pages_below_one", {"rest": [{"url": "http://127.0.0.1:9876/wp-json/wp/v2/posts", "max_pages": 0}]}),
    ("rest_not_array", {"pages": ["http://127.0.0.1/a"], "rest": "http://127.0.0.1/b"}),
]


def main() -> int:
    result = {"citations": {
        "existing_output_and_inside_collection_refusals": [
            "agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py::test_preserves_existing_packages_and_input[existing]",
            "agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py::test_preserves_existing_packages_and_input[inside]",
        ],
        "traversal_symlink_escaping_negatives":
            "T-12 (t12_result.json part2): body_byte_flip, metadata_hash_tamper, "
            "escaping_reference_hash_consistent, symlinked_body_original_content — all refused "
            "exit 2 before derived output; canaries outside the owned tree untouched",
        "decide_rejections": [
            "tests/test_decide.py::test_unknown_conflict_and_broad_collection_need_explicit_scope",
            "tests/test_offline_inventory.py::test_unknown_id_is_rejected_without_output[include]",
            "tests/test_offline_inventory.py::test_unknown_id_is_rejected_without_output[exclude]",
            "tests/test_offline_inventory.py::test_conflicting_or_empty_choices_are_rejected",
        ],
    }}
    base = SCRATCH / "t02-cases"
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)

    rows = {}
    for name, plan in CASES:
        case_dir = base / name
        plan_path = base / (name + ".json")
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        r = run_cli(["collect", "--collection", str(case_dir), "--plan", str(plan_path)])
        r["refused_visibly"] = r["exit"] == 2 and "Collector refused:" in r["stderr"]
        r["collection_dir_not_created"] = not case_dir.exists()
        rows[name] = r
    result["plan_refusals"] = rows
    result["all_plan_refusals_pass"] = all(
        r["refused_visibly"] and r["collection_dir_not_created"] for r in rows.values())

    sys.path.insert(0, str(SNAP))
    from recon_pipeline.collector import plan_items, create

    valid = {"pages": ["http://127.0.0.1:9876/qa-control-a"], "rest": []}
    items = plan_items(valid)
    result["positive_control_plan_items"] = {
        "items": items,
        "no_directory_side_effect": all(not (base / n).exists() for n, _ in CASES),
    }

    valid_path = base / "valid.json"
    valid_path.write_text(json.dumps(valid), encoding="utf-8")
    existing = base / "existing-collection"
    create(existing, valid)
    before = tree_map(existing)
    r2 = run_cli(["collect", "--collection", str(existing), "--plan", str(valid_path)])
    after = tree_map(existing)
    r2["refused_visibly"] = r2["exit"] == 2 and "Collector refused:" in r2["stderr"]
    r2["bytes_unchanged"] = before == after
    result["existing_collection_refusal"] = r2

    paginated = {"pages": [], "rest": [{"url": "http://127.0.0.1:9876/wp-json/wp/v2/posts",
                                        "paginate": True, "max_pages": 2}]}
    coll = base / "paginated-collection"
    create(coll, paginated)
    before = tree_map(coll)
    changed = {"pages": [], "rest": [{"url": "http://127.0.0.1:9876/wp-json/wp/v2/posts",
                                       "paginate": True, "max_pages": 3}]}
    changed_path = base / "changed-scope.json"
    changed_path.write_text(json.dumps(changed), encoding="utf-8")
    r3 = run_cli(["add", "--collection", str(coll), "--plan", str(changed_path)])
    after = tree_map(coll)
    r3["refused_visibly"] = r3["exit"] == 2 and "Collector refused:" in r3["stderr"]
    r3["bytes_unchanged_except_writer_lock"] = (
        {k: v for k, v in before.items() if k != ".writer.lock"}
        == {k: v for k, v in after.items() if k != ".writer.lock"}
        and set(after) - set(before) <= {".writer.lock"}
    )
    result["add_changed_pagination_scope_refusal"] = r3

    item_id = json.loads((coll / "checklist.json").read_bytes())["items"][0]["id"]
    r4 = run_cli(["refresh", "--collection", str(coll), "--id", item_id])
    after = tree_map(coll)
    r4["refused_visibly"] = (
        r4["exit"] == 2
        and "refresh a paginated collection into a NEW collection" in r4["stderr"]
    )
    r4["bytes_unchanged_except_writer_lock"] = (
        {k: v for k, v in before.items() if k != ".writer.lock"}
        == {k: v for k, v in after.items() if k != ".writer.lock"}
        and set(after) - set(before) <= {".writer.lock"}
    )
    result["t17_paginated_refresh_refusal"] = r4

    r5 = run_cli(["refresh", "--collection", str(coll), "--id", "nonexistent000000000000"])
    r5["refused_visibly"] = r5["exit"] == 2 and "unknown refresh ID" in r5["stderr"]
    result["unknown_refresh_id_refusal"] = r5

    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("plan refusal cases:", sum(1 for r in rows.values() if r["refused_visibly"] and r["collection_dir_not_created"]),
          "/", len(rows), "pass; all:", result["all_plan_refusals_pass"])
    for name in ("non_http_scheme", "credential_bearing_url", "rest_root_enumeration",
                 "pagination_without_max_pages", "pagination_starting_at_page_2",
                 "unknown_plan_key", "empty_plan"):
        print(" ", name, "→ exit", rows[name]["exit"], "|", rows[name]["stderr"].strip()[:90])
    print("positive control items:", len(items), "| no dir side effect:",
          result["positive_control_plan_items"]["no_directory_side_effect"])
    print("existing-collection refusal:", r2["refused_visibly"], "| bytes unchanged:", r2["bytes_unchanged"])
    print("add changed-scope refusal:", r3["refused_visibly"], "| bytes preserved:",
          r3["bytes_unchanged_except_writer_lock"])
    print("paginated refresh refusal:", r4["refused_visibly"], "| bytes preserved:",
          r4["bytes_unchanged_except_writer_lock"])
    print("unknown refresh ID refusal:", r5["refused_visibly"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())