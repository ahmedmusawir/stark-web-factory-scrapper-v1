# BIM-000 Lean Pre-Q - 2026-09-05

Independent QA execution by Cody. Recommendation only; SOL retains Gate Q. AC-54 is not graded.

## Specimen and mandatory runs

- PASS: branch `qa/web-factory-p1-bim000`; HEAD `9d40ca5a9303d0a93074bf1c8470ad877409dec8` exactly matches the pinned candidate. Initial working tree clean.
- PASS: `venv/bin/pytest -q` -> `13 passed in 2.62s`.
- PASS: `printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com` -> exit 0, 194 URLs written to repo-root `outputs/discovered_pages.json`.
- PASS: `venv/bin/python -m smart_crawler.crawler --limit 10` -> exit 0, 10 attempted, 10 successful, zero failed/blocked. It consumed the discovery file directly; no copy, rename, or trim occurred.
- PASS: regenerated `outputs/run_summary.json`, UTC `08:59:29` to `09:00:50`, contains the required metadata and 10 records with exactly `{url,status,ok,elapsed_s,error}`. All statuses 200, all ok true, all errors null. URL order equals discovery's first ten; all ten Markdown files exist and are nonempty.
- PASS: console status lines `[1/10]` through `[10/10]` all reported `200 ok`; nine logged pauses were `4.1, 3.7, 4.3, 2.8, 2.6, 3.8, 2.4, 2.4, 2.3` seconds. No unexpected 403/429. Generated artifacts remain gitignored; this report preserves the observed results.

## Requested ruling recommendations

- AC-10 - PASS WITH NOTE. A: from `/tmp`, `env -u PYTHONPATH <repo>/venv/bin/python -m discover_site.discover ...` fails with `ModuleNotFoundError: No module named 'discover_site'`. B: the same live discovery with `PYTHONPATH=<repo>` succeeds and writes 194 URLs to `<repo>/outputs/discovered_pages.json`; `/tmp/outputs` does not exist afterward. Source anchors through `Path(__file__).resolve().parents[1]`. Intended output-path requirement satisfied; no packaging change needed.
- AC-41 - PASS WITH NOTE. File absent; no implementation/import or README operational reference. Targeted source scans and tracked-file grep find only `CHANGELOG.md:11` outside protocol/history documents. That truthful deletion record is harmless, not an operational AC failure. Changelog untouched.
- AC-45 - PASS WITH NOTE. Independently compared Stage 1 (`600d181`) to HEAD: six references in the September 2 session and one in September 3 were repointed; all seven archived targets exist. Three anticipated named references existed. Stage 1 RECOVERY already referenced its current report, so the fourth was superseded. Current RECOVERY target exists; CLAUDE layout and table document `RESPONSES/OLD/`. Intent satisfied without manufacturing references.

## Failed criteria

- AC-21 - FAIL: `smart_crawler/crawler.py:243` returns for a valid empty JSON list before `write_summary` at line 270. Independent offline probe called real `main()` with `--input <temporary empty.json>` containing `[]`, redirecting only PAGE_DIR/SUMMARY_PATH to a temporary directory. Observed `No URLs found in file`, normal return, and `empty run writes summary: False`. Thus "written every run" is false; an existing summary would remain stale. Normal ten-page and blocked-stop summary coverage passes, but does not cover this case. This is an implementation gap, not a live-site issue.
- AC-52 - FAIL against literal wording: Stage 2 report explicitly records read-only `git status`, `git log`, `git diff --stat`, and `git branch --show-current` by Claudy, while the AC says no git command. The session also records git inspection. No independent evidence establishes unauthorized mutation, and git history alone cannot identify who invoked commands. Tony/SOL must adjudicate the documented process exception; code changes cannot undo it.

## Remaining AC coverage and scope

| Criteria | Result | Evidence/basis |
|---|---|---|
| AC-01,02,04,05,06 | PASS WITH NOTE | Stage 1 report records old 0.6.3, target/release/API review, no browser refresh required, six tests and pre-Stage-2 10/10 smoke. Historical runs not recreated. Independent `git diff ba05030 600d181 -- discover_site smart_crawler tests` is empty, supporting unchanged baseline code/tests. |
| AC-03 | PASS | Installed and direct/lock pin 0.9.3; sorted pip freeze equals lock; pip check: `No broken requirements found.` |
| AC-07 | PASS WITH NOTE | Historical baseline green; conditional stop rule not triggered per Stage 1 evidence. |
| AC-11,12,13 | PASS | Live direct handoff; input/limit tests; no retired filename in application, tests, README or RUN_NOTES. |
| AC-20,22,23 | PASS | Offline failure/no-file and consecutive-block/reset tests; additional 200 + success=False probe returns ok false and no markdown; ten live status lines. |
| AC-30,31,32,33 | PASS | Nine pauses; shared Session UA; actual installed BrowserConfig headers contain nonempty sec-ch-ua: Chromium/Google Chrome v140 and Not_A Brand v8. No application stealth, webdriver override, magic or simulate_user configuration. |
| AC-40,42,43,44 | PASS | Metadata banner and dynamic count; foreign-CWD import test; root paths; unused sys removed; neutral fixtures; two-command README flow and BIM-000 RUN_NOTES/CHANGELOG entries. |
| AC-46 | PASS WITH NOTE | .env.example unchanged from pre-module baseline; GEMINI_API_KEY placeholder preserved; python-dotenv remains 1.1.0. Stage 2 dependency diff empty. Stage 1 changed the transitive distribution to unclecode-litellm 1.81.13 as reported; installed Crawl4AI requires it, direct requirements do not, and Stark code imports neither LiteLLM nor Gemini. |
| AC-50,51,53 | PASS | Independent 13-test and live results above; both required engineering reports present and read, along with brief/spec/readiness report. |

Implementation drift: none outside BIM-000 scope found in baseline-to-candidate diff and application inspection. No Phase 1 intelligence, Gemini integration, Prepare work, raw-HTML capture, or stealth implementation added. AC-21 is an in-scope omission. No implementation fixes, commits, merges, or branch changes performed by QA.

Environmental issues - PASS WITH NOTE: initial sandbox discovery could not resolve DNS; rerun with approved external access succeeded. Pip emitted a non-writable cache warning but dependency validation passed. Live crawler logged image-load timeouts, consistent with retained wait_for_images; all pages still succeeded. No live-site failure reproduced.

## Recommendation to SOL

**REWORK REQUIRED** - address or explicitly adjudicate AC-21's every-run summary gap and resolve AC-52's documented process discrepancy. The mandatory smoke and three requested intent rulings otherwise pass. This is not SOL's final verdict.
