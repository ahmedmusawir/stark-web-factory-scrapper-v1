"""Q2 G0 helper: verify the installed Lead-review folder equals the approved ZIP bytes.

Checks: ZIP SHA-256 against the Director-released value, member-name safety (no
absolute or parent-escaping paths), member count including FILE_INDEX.json, and
byte-for-byte comparison of every member against the installed repository folder.
Read-only for the repository; writes only its own JSON result file given as argv[1].
"""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

ZIP_PATH = Path("/home/moose/Downloads/WebFactory_Q1_Lead_Review_2026-10-15.zip")
EXPECTED_ZIP_SHA256 = "62d6da2cb44c20aa6694920f6b15184c9c5d3cb5e4825686afe35c6d6f9e8475"
INSTALLED = Path(
    "/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/"
    "wf-scrapper-abm/QAM/HANDOFFS/WebFactory_Q1_Lead_Review_2026-10-15"
)
FOLDER_PREFIX = "WebFactory_Q1_Lead_Review_2026-10-15/"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    out_path = Path(sys.argv[1])
    zip_bytes = ZIP_PATH.read_bytes()
    result = {
        "zip": {
            "path": str(ZIP_PATH),
            "bytes": len(zip_bytes),
            "sha256": sha256_bytes(zip_bytes),
            "matches_director_release": sha256_bytes(zip_bytes) == EXPECTED_ZIP_SHA256,
        }
    }
    installed_files = {
        str(p.relative_to(INSTALLED)): p for p in INSTALLED.rglob("*") if p.is_file()
    }
    comparisons = {}
    with ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        result["member_count"] = len(names)
        result["unsafe_members"] = [
            n for n in names
            if n.startswith("/") or n.startswith("\\") or ".." in Path(n).parts
        ]
        index_name = next(n for n in names if Path(n).name == "FILE_INDEX.json")
        result["file_index_member"] = json.loads(zf.read(index_name))
        for name in names:
            member_bytes = zf.read(name)
            rel = name
            if rel not in installed_files and rel.startswith(FOLDER_PREFIX):
                rel = rel[len(FOLDER_PREFIX):]
            installed = installed_files.get(rel)
            if installed is None:
                comparisons[name] = {"status": "NO_INSTALLED_COUNTERPART"}
                continue
            installed_bytes = installed.read_bytes()
            comparisons[name] = {
                "status": "MATCH" if member_bytes == installed_bytes else "DIFFERS",
                "bytes": len(installed_bytes),
                "sha256": sha256_bytes(installed_bytes),
            }
    member_rels = set()
    for n in names:
        member_rels.add(n[len(FOLDER_PREFIX):] if n.startswith(FOLDER_PREFIX) else n)
    uncovered = sorted(set(installed_files) - member_rels)
    result["installed_file_count"] = len(installed_files)
    result["installed_files_not_covered_by_zip_members"] = uncovered
    result["member_comparison"] = comparisons
    result["all_members_match_installed"] = (
        not result["unsafe_members"]
        and all(c["status"] == "MATCH" for c in comparisons.values())
        and not uncovered
        and result["zip"]["matches_director_release"]
    )
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    bad = [n for n, c in comparisons.items() if c["status"] != "MATCH"]
    print("zip sha matches director release:", result["zip"]["matches_director_release"])
    print("members:", result["member_count"], "| installed files:", len(installed_files))
    print("unsafe members:", result["unsafe_members"] or "none")
    print("non-matching members:", bad or "none")
    print("installed files not covered:", uncovered or "none")
    print("ALL_MATCH", result["all_members_match_installed"])
    return 0 if result["all_members_match_installed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())