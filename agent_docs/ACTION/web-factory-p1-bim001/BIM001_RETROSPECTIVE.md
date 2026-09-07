# BIM001 Retrospective — web-factory-p1-bim001 (Raw HTML Capture)

> Closed 2026-09-07. SOL Gate Q: PASS (as stated by the Director). Certified candidate `eee039a` on `qa/web-factory-p1-bim001`; certification package committed at `7517049`. Written by Claudy (Engineer) at close-out. Facts only, with pointers; lesson candidates live in the doctrine journal (`QA/INPUTS/WEB_FACTORY_P1_DOCTRINE_JOURNAL.md`) and are not repeated here.

## What worked
- **Plan Mode with red flags up front.** The P1 plan (`agent_docs/RESPONSES/BIM001_plan_2026-09-06.md` §I) named four spec items that could not be met literally before any code existed; the Director ruled on them (I-1…I-4) and three of the four became the recorded errata rather than mid-build surprises.
- **Six commit-sized chunks, each green.** 14 → 54 tests, one pytest line per chunk, Director staging between chunks (`BIM001_chunk1…6_2026-09-06.md`). bim000's 14 tests never moved; the three permitted amendments (a/b/c) were listed in CHANGELOG as they were made.
- **Manifest as truth, run folder as package root.** `outputs/<project>/runs/<run_id>/{html/, manifest.json, absences.json, stage_log.txt}` came out of the smoke exactly as the spec drew it; `run_summary.json` stayed byte-for-byte the bim000 contract (`BIM001_complete_2026-09-06.md` §7; `QA/QA_LIVE_BIM001_2026-09-07_1017.md` §8).
- **Independent QA that executes instead of reads.** Cody's offline stage (`QA/QA_OFFLINE_EXECUTION_BIM001_2026-09-06_1508.md`) reproduced every claim with stubs and found both literal fails; the retest (`QA/QA_RETEST_BIM001_2026-09-06_1553.md`) re-proved the repair from source and JUnit, not from my report.
- **Two live smokes, both 10/10.** Engineer P3 run `2026-09-06T07-30-16Z` (100.6 s) and SOL-authorized QA run `2026-09-07T04-10-56Z` (85.9 s): all 200, all captured, all files start `<!DOCTYPE`, 184 `skipped/limit` absences, byte sizes equal to manifest.

## What fought back
- **Two literal fails on candidate `657e25e`, one rework cycle, repaired in `eee039a`** (`QA/ENGINEERING_REPAIR_BIM001_2026-09-06_1528.md`):
  - **AC-32 netloc vs hostname.** `input_hosts` used `urlparse().netloc`, which keeps ports; the spec says hostnames. Repair: `urlparse().hostname`, `None` skipped, sorted unique. Consequence worth knowing: `hostname` lower-cases the host.
  - **AC-71 helper edit.** I added exception-raising to bim000's `FakeCrawler.arun` — useful, but outside the closed a/b/c list. Repair: `FakeCrawler` restored byte-for-byte to `main`; exception simulation moved to a bim001-only `RaisingFakeCrawler` subclass; only `test_ac25` uses it.
- **Four errata, recorded by QA without touching the frozen spec** (`QA/QA_ERRATA_BIM001_2026-09-06.md`): **AC-20** ("present" HTML means non-empty; `html == ""` stays `unsupported / no html in result`, no zero-byte files) · **AC-35** (`md_file` records the markdown file bim000 actually wrote, `pages/<base-slug>.md`; the literal `pages/<slug>.md` applies to non-colliding URLs) · **AC-90** (`RECOVERY.md` is allowed process documentation on the surface) · **AC-92** (`importlib.metadata.version("playwright")` is allowed metadata inspection; the grep counts one source hit).
- **Volume.** Captured HTML runs 380–600 KB per page (avg ≈ 433 KB across both smokes). A full 194-page CyberizeGroup run is therefore roughly 85–90 MB of HTML per run folder, before bim002/bim003 add their streams. `outputs/` is gitignored; the QA lane holds a byte-identical snapshot of one run.
- **`Some images failed to load within timeout` on stderr** on most pages, both smokes (`wait_for_images=True` retained by ruling R5). Cosmetic today; every page still captured. Preserved as an observation, not a defect.
- **Report-naming drift.** bim001 reports are `BIM001_<stage>_<date>.md`; bim000 used `response_<ts>_<slug>.md`. Both conventions now coexist in `agent_docs/RESPONSES/`. One rule should win before bim002.
- **A cited file moved.** The module `CLAUDE.md` §2.5 and P1 cite `agent_docs/RECON/READ_pre-bim001_2026-09-06.md`; the Director's archive pass moved it to `agent_docs/RECON/OLD/`. The frozen contract cannot be edited, so the pointer stays stale by design; noted here and in the completion report.
- **Interpreter slip in P3.** The prompt's literal `python -m …` resolved to the bare pyenv interpreter (no crawl4ai) and failed on import in 0.2 s, no network; re-run with `venv/bin/python`. Same lesson as bim000's `sys.path` slip: name the interpreter.

## Numbers
Candidates `657e25e` → `eee039a`; cert package `7517049` · tests 14 → 54 (40 new `test_acNN_*`; 14 bim000 untouched, 47 baseline asserts preserved) · literal fails 2, rework cycles 1, errata 4 (AC-20/35/90/92), open blockers 0 · live smokes 2 × 10/10, 0 blocked/failed/unsupported · per-page HTML 378,922–600,508 bytes · pins unchanged (crawl4ai 0.9.3, playwright 1.52.0), lock byte-identical · SOL final counts as stated by the Director: 48 PASS / 4 PASS WITH NOTE / 0 FAIL.

## Carry into bim002
- **`--project NAME` is required for every crawl from now on.** No default, no inference; missing or invalid exits 2 with the corrective usage.
- **`manifest.json` is the run truth; the run folder `outputs/<project>/runs/<run_id>/` is the package root** that bim002 adds its stream into (REST + SEO). Do not create a second root.
- **`run_summary.json` stays frozen** (bim000 contract: same path, five top-level keys, five per-page keys) until bim004 retires it.
- **`input_hosts` is lower-cased** (`urlparse().hostname` semantics). Compare against lower-cased hosts, not raw input text.
- **`RECOVERY.md` is on the allowed surface** (AC-90 erratum); future specs should list it.
- **Test 8 argv carries `--project TestProj`** (permitted amendment b); any new test that drives `main()` must pass `--project`.
- **`RaisingFakeCrawler` exists** in `tests/test_crawler.py` for exception-path tests; do not touch `FakeCrawler`.
- **Block-page bodies are not captured** (assumption A2): 403/429 → `blocked`, nothing saved. Capturing block-page evidence is a candidate for a later module.
- **"Empty html" vs "absent html" share one reason string** (`no html in result`, AC-20 interpretation). Parked; split the reasons only if a consumer needs the distinction.
- Also inherited unchanged: `wait_for_images=True` and `fit_markdown` (F1) remain deferred decisions; per-run HTML volume is ~90 MB for a full CyberizeGroup crawl.
