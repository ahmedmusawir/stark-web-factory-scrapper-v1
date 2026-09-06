# CHANGELOG

Doc/playbook change log for this repo. `[CC]` = Claude Code, `[TS]` = Tony Stark manual edit. Newest first.

## 2026-09-05 — [CC] Claude Code — bim000 Stage prep + controlled upgrade

- **Updated:** `requirements.txt`, `requirements-lock.txt` — crawl4ai 0.6.3 → 0.9.3 (exact pin; lock regenerated, 98 lines). Stage 1, committed 600d181.
- **Updated:** `smart_crawler/crawler.py` — `--input PATH` / `--limit N` (reads `outputs/discovered_pages.json` by default, no prompt); status validation (≥400 or `success=False` = failed, no file; 403/429 = `blocked`; 3 consecutive → stop, exit 2); per-page status lines; `outputs/run_summary.json`; random 2–5 s pause between pages; complete Chrome UA; paths anchored to repo root, no import-time mkdir; truthful banner (version from package metadata, count from `len(urls)`).
- **Updated:** `discover_site/sitemap_utils.py` — `USER_AGENT` constant + shared `requests.Session` used for every discovery call.
- **Updated:** `discover_site/discover.py` — uses the shared session; unused `import sys` removed.
- **Removed:** `discover_site/smart_discover.py` — retired (Docusaurus-only, unused, nothing imported it).
- **Updated:** `tests/test_discover.py`, `tests/test_sitemap_utils.py` — fixtures use `example.com`; sitemap stub targets `SESSION.get`.
- **Added:** `tests/test_crawler.py` — 7 offline tests (status handling, blocked-stop, pacing, flags, session UA, import side effects). Suite: 13 passed.
- **Updated:** `README.md` — two-command run section; references to the retired sidebar discoverer and the separate "final" input file removed; layout updated.
- **Updated:** `RUN_NOTES.md` — bim000 section (Stage 1 + Stage 2 commands).
- **Updated:** `CLAUDE.md` — Protocol Directory Layout: `agent_docs/RESPONSES/OLD/` row (archived responses, Director-managed).
- **Updated:** `agent_docs/SESSIONS/session_2026-09-02.md`, `session_2026-09-03.md` — stale `RESPONSES/` paths repointed to `RESPONSES/OLD/`.
- **Added:** `CHANGELOG.md` — this file.
- **Reason:** web-factory-p1-bim000 brief §3 (F3 handoff fix, status validation, pacing, identity, F4 truth, R-B retire, paths, hygiene, docs).

## 2026-09-06 — [CC] Claude Code — bim001 Raw HTML Capture (in progress)

- **bim000 test amendments (AC-71), listed as made:**
  - (b) `tests/test_crawler.py::test_empty_input_writes_truthful_summary_without_crawling` — argv gains `--project TestProj`; assertions unchanged. (chunk 1)
- **Chunk 1:** `smart_crawler/crawler.py` — `--project` flag (optional to argparse, validated in `main()` before any input read, mkdir or browser; missing/invalid → stderr usage + exit 2); `read_urls()` split out of `load_urls()` (behavior preserved); `RUN_ROOT` constant; `make_run_id()`. 7 new tests (`test_ac01…`, `ac02`, `ac03_04_05`, `ac06`, `ac08`, `ac11`, `ac63`).
- **Chunk 2:** `smart_crawler/crawler.py` — `RunFolder` class (`create` with same-second wait, `log`, `allocate_slug` -2/-3, `save_html` byte-for-byte + never-overwrite, `record_page` 11 keys, `write_manifest` 23 keys, `write_absences`), `build_absences()`, `input_hosts()`. Not yet wired into `main()`. 8 new tests (ac10, 21, 23, 30, 31, 34, 40, 50).
- **Reason:** web-factory-p1-bim001 brief; plan `agent_docs/RESPONSES/BIM001_plan_2026-09-06.md` approved 2026-09-06. No pin changes.

## 2026-09-05 — [CC] Claude Code — bim000 QA close (Gate Q PASS)

- **Updated:** `smart_crawler/crawler.py` — AC-21 fix: empty `[]` input now writes `run_summary.json` (pages=[]) instead of returning early (dcfb1ea).
- **Updated:** `tests/test_crawler.py` — regression test for the empty-input run; suite 14 passed.
- **Added:** `agent_docs/ACTION/web-factory-p1-bim000/BIM000_RETROSPECTIVE.md`, `agent_docs/RESPONSES/QA_GATEQ_VERDICT_web-factory-p1-bim000_2026-09-05.md` — close-out records.
- **Updated:** `RECOVERY.md`, `RUN_NOTES.md`, `agent_docs/SESSIONS/session_2026-09-05.md` — CLOSED state, certified SHA `81099ee`.
- **Reason:** Cody PRE-Q found AC-21; SOL ruled surgical rework; Cody retest PASS; SOL Gate Q PASS on `qa/web-factory-p1-bim000` @ 81099ee.
