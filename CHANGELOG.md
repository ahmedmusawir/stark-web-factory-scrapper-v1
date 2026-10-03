# CHANGELOG

Doc/playbook change log for this repo. `[CC]` = Claude Code, `[TS]` = Tony Stark manual edit. Newest first.

## 2026-10-02 — Cody — JARVIS rulings / BUILD_READBACK 1.2

- Applied prospective M-01–M-04 dispositions and E-13–E-19; canonical lock setup documented without changing dependencies/installing; complete/partial fixture bindings and integrity-first snapshots; shared CHK smoke; precise leak scanner boundary; C6 reader; authored/source boundary checks.
- Inspected actual product/tests/installed source read-only; BUILD_READBACK names APIs, unproven controls, exact certified-test rewrites, proposed live bounds and source-to-commit QA evidence binding. Updated QA/QAM/entries/recovery consistently.
- No product/test changes, product tests, installs, live requests, independent QA, Git mutations or deletion. AWAITING BUILD_READBACK REVIEW AND TONY'S BUILD APPROVAL.

## 2026-10-02 — Cody — ABM 1.1 / QAM documentation amendment

- JARVIS Architect amendment under Tony’s delegated authority: browser-session discovery/REST, complementary sources, five-second completion pacing, no retries/switching, first intentional refusal stop, scoped redirects/media and demonstrated image-wait settings.
- Corrected response-byte versus derivative provenance, route accounting, valid-partial handling and mailto embed count. Preserved 48 ACs/24 groups and historical carry-ins; added E-05–E-12 with current provenance, not old Director approvals.
- Added module/QAM entries, independent Q1/Lead decision/Q2 workflow and instruction-driven handoffs; Tony cleanup accepted before final Gate Q; updated recovery/records/QA plan. Open architectural decisions remain in ABM_AMENDMENT_1_1.md.
- Documentation only: no product/test/dependency edits, tests, live requests, installs, Git mutations or deletion. No BUILD_READBACK/C1. Awaiting JARVIS review.

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

## 2026-09-06 — [CC] Claude Code — bim001 Raw HTML Capture

- **bim000 test amendments (AC-71), listed as made:**
  - (a) `tests/test_crawler.py::sandbox` fixture — additionally redirects `crawler.RUN_ROOT` to `tmp_path`. (chunk 4)
  - (b) `tests/test_crawler.py::test_empty_input_writes_truthful_summary_without_crawling` — argv gains `--project TestProj`; assertions unchanged. (chunk 1)
  - (c) `tests/test_crawler.py::_result()` stub — optional `html=None` parameter; attribute set only when provided, absent by default. (chunk 3)
- **Chunk 1:** `smart_crawler/crawler.py` — `--project` flag (optional to argparse, validated in `main()` before any input read, mkdir or browser; missing/invalid → stderr usage + exit 2); `read_urls()` split out of `load_urls()` (behavior preserved); `RUN_ROOT` constant; `make_run_id()`. 7 new tests (`test_ac01…`, `ac02`, `ac03_04_05`, `ac06`, `ac08`, `ac11`, `ac63`).
- **Chunk 2:** `smart_crawler/crawler.py` — `RunFolder` class (`create` with same-second wait, `log`, `allocate_slug` -2/-3, `save_html` byte-for-byte + never-overwrite, `record_page` 11 keys, `write_manifest` 23 keys, `write_absences`), `build_absences()`, `input_hosts()`. Not yet wired into `main()`. 8 new tests (ac10, 21, 23, 30, 31, 34, 40, 50).
- **Chunk 3:** `smart_crawler/crawler.py` — `crawl_page` returns transport keys `html` (guarded `getattr`) and `fetched` alongside `markdown`; `crawl_all(urls, crawler, run=None)` pops all three before the record reaches `run_summary.json`, and when a `RunFolder` is given calls new `record_capture()` (outcome ladder blocked > failed > unsupported > captured; write failure → `failed`, reason `write failed: …`; stage-log line per page; `stop rule` log line). `save_markdown`, `write_summary`, run-config literals untouched. 7 new tests (ac20, 22, 24, 25, 26, 27, 28).
- **Chunk 4:** `smart_crawler/crawler.py` — `main()` wired: validate → `read_urls` (all) → slice by `--limit` → `RunFolder.create()` on every path past validation → `run start` log → crawl (or empty-input branch) → `close_run()` writes `run_summary.json` (unchanged contract), `manifest.json` (counts, hosts, command, resolved input path, `stopped_early`), `absences.json` (`limit` / `stop_rule` skips), `run end` log; exit 2 on early stop after the manifest is written. `run()` threads the RunFolder. Banner shows project, run_id and run folder. 12 new tests (ac07, 13, 14, 32, 33, 35, 36, 37, 41, 42, 43, 51).
- **Chunk 5 (hardening, no behavior change):** 5 source/contract tests — `test_ac10_run_folder_layout_end_to_end`, `test_ac12_no_mkdir_at_module_level` (AST: nothing called at import), `test_ac60_run_summary_contract_unchanged_via_main`, `test_ac61_62_bim000_code_and_config_literals_unchanged`, `test_ac63_exit_codes_complete`. Import-usage sweep: every import used; `load_urls` retained as bim000 API (used by tests). One test-helper fix (`_one_url_input` mkdir exist_ok).
- **Chunk 6 (docs):** `README.md` — Run section rewritten: `--project` required, canonical command `python -m smart_crawler.crawler --project CyberizeGroup --limit 10`, run-folder layout, outcomes, exit codes; Layout/Tests updated. `RUN_NOTES.md` — bim001 section: canonical command, what a run leaves behind, two-file state (manifest.json = run record from bim001 onward; run_summary.json = frozen bim000 contract kept for compatibility), negative CLI checks, pins.
- **Summary of bim001 (for the reader who skips the chunks):** `--project` flag (validated at runtime, exit 2 with corrective usage) · run folder `outputs/<project>/runs/<run_id>/` created in `main()` only · raw HTML capture `html/<slug>.html`, byte-for-byte, `-2`/`-3` collision suffix · `manifest.json` (23 keys, 11 per page) · `absences.json` (blocked / failed / unsupported / skipped with `limit` / `stop_rule`) · stage log `stage_log.txt` · permitted bim000 test amendments (a) sandbox `RUN_ROOT`, (b) test 8 argv `--project`, (c) stub optional `html` · 40 new `test_acNN_*` tests, suite 54 passed · **no pin changes** (`requirements-lock.txt` byte-identical).
- **QA repair (2026-09-06, qa/web-factory-p1-bim001):** AC-32 — `input_hosts` now records URL hostnames (`urlparse(u).hostname`, `None` skipped) rather than netloc values with ports. AC-71 — `FakeCrawler.arun` restored byte-for-byte to `main`; exception simulation moved to bim001-only `RaisingFakeCrawler` subclass (not a bim000 amendment); `test_ac25` uses it; `test_ac32` extended with an explicit-port URL.
- **Close-out (2026-09-07):** certified candidate `eee039a`; SOL Gate Q PASS 2026-09-07; certification package `7517049`; four errata (AC-20, AC-35, AC-90, AC-92) recorded in `agent_docs/ACTION/web-factory-p1-bim001/QA/QA_ERRATA_BIM001_2026-09-06.md`; retrospective `agent_docs/ACTION/web-factory-p1-bim001/BIM001_RETROSPECTIVE.md`.
- **Reason:** web-factory-p1-bim001 brief; plan `agent_docs/RESPONSES/BIM001_plan_2026-09-06.md` approved 2026-09-06.

## 2026-09-05 — [CC] Claude Code — bim000 QA close (Gate Q PASS)

- **Updated:** `smart_crawler/crawler.py` — AC-21 fix: empty `[]` input now writes `run_summary.json` (pages=[]) instead of returning early (dcfb1ea).
- **Updated:** `tests/test_crawler.py` — regression test for the empty-input run; suite 14 passed.
- **Added:** `agent_docs/ACTION/web-factory-p1-bim000/BIM000_RETROSPECTIVE.md`, `agent_docs/RESPONSES/QA_GATEQ_VERDICT_web-factory-p1-bim000_2026-09-05.md` — close-out records.
- **Updated:** `RECOVERY.md`, `RUN_NOTES.md`, `agent_docs/SESSIONS/session_2026-09-05.md` — CLOSED state, certified SHA `81099ee`.
- **Reason:** Cody PRE-Q found AC-21; SOL ruled surgical rework; Cody retest PASS; SOL Gate Q PASS on `qa/web-factory-p1-bim000` @ 81099ee.

## 2026-10-02_135008Z — Cody Engineer / ABM launch

- Recorded Director GO and JARVIS E-20/E-21 prospectively in current module/QA/QAM entry documents, journal and recovery. Preserve prior records and dirty work. Product implementation begins under approved BUILD_READBACK; QA pending.

## 2026-10-02 — Cody / C1 raw v2

- Implemented raw v2 and validator; R8/E-01 retire shared Markdown/summary outputs without touching old files. E-05 first-refusal/no-retry five-second policy; E-09 all-route accounting.
- 29 authorized existing-test rewrites are individually documented with errata; exact names in agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/build/2026-10-02_135008Z/C1-rewrites.json; 19 unrelated certified functions retain behavior. C2 transport rewrites pending. Static independent validator positives/negatives added. 63 engineering tests passed; QA NOT RUN.

## 2026-10-02 — Cody / C2 browser discovery

- Replaced requests discovery with explicit owned Chromium reads; canonical identity and typed discovery outcomes. E-06/E-05 authorize remaining five certified transport/query rewrites; all 34 readback-enumerated rewrites now recorded.
- Implemented E-20 correlated Chromium redirect transition and E-21 cf-mitigated allowlist/detector cases. Initial real browser proof passed; full C3 controls pending. 72 engineering tests green; QA NOT RUN.

## 2026-10-02 — Cody / C3–C4

- Implemented browser admission, correlated redirect completion, shared pacing, explicit challenge/refusal stops, background separation, caps and partial finalization. Real Chromium loopback tests plus SIGINT/raw-limit tests.
- Implemented REST archived responses and indexed exact-value derivatives, pagination/route mapping/optional absences; no root enumeration/field filtering/client fallback. Declared fixture facts and typed raw validation checks. 101 engineering tests pass; independent QA NOT RUN.

## Web Recon ABM 1.2 — C5/C6 engineering implementation (2026-10-02)

- Added received-media inventory and scoped browser HEAD (E-07), with off-scope retrieval explicitly untested.
- Added bounded Capture orchestration, owned Chromium process watchdog, partial finalization, source/runtime identity and the minimal C6 read-only reader (E-17).
- Retained Director-authored screenshot bytes with hashes; the tool writes only the slot README (E-07).
- Added complete F-09, corrupt F-10 and valid two-loss F-12 readers, real-worker budget/interrupt proofs and fact-bound snapshot comparisons (E-14).
- Shared Markdown/run_summary remain retired (R8/E-01); existing history is preserved. No Prepare construction or independent QA completion claimed at this milestone.

## 2026-10-02 — Cody engineering checkpoint

C1–C6 Capture/minimal raw reader implemented with 131 passing engineering tests and paired fixture comparison. CHK live failed on a same-URL incidental stylesheet classified as intentional; one dispatch, partial evidence retained. No Prepare/E2/QA completion claim. RECOVERY, ledger and QAM record BLOCKED; exact source and defect packaged for review.
