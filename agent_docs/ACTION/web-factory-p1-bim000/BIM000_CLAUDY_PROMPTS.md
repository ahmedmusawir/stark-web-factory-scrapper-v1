# web-factory-p1-bim000 — CLAUDY PROMPTS

> Two prompts. CP1 is the upgrade. CP2 is the cleanup. CP2 is not handed over until CP1 is green and the Director says so.
> Both run in Plan Mode. Claudy plans, Director approves, Claudy executes. Zero git. Zero cloud.

---

## CP1 — Stage 1: Controlled Crawl4AI upgrade

```
You are Claudy, Engineer seat, Stark Web Factory Phase 1, module web-factory-p1-bim000, Stage 1.

Repo: ~/python/stark-web-factory-scrapper-v1. Branch is already checked out by the Director.
Read first: web-factory-p1-bim000/BIM000_BRIEF.md and BIM000_ACCEPTANCE_SPEC.md (AC-01 to AC-07).

PLAN MODE. Present the plan and stop for approval before any install or edit.

Task: upgrade crawl4ai as an isolated, pinned, regression-gated step. Nothing else changes in this stage.

Allowed: pip installs into ./venv, playwright browser install if the new pin requires it, network to pypi.org and github.com for version and changelog lookup, edits to requirements.txt and requirements-lock.txt only. Read-only elsewhere.
Forbidden: git commands, edits to any .py file, any change beyond the two requirements files.

Steps:
1. Record installed version: venv/bin/pip show crawl4ai.
2. Find the current stable release: venv/bin/pip index versions crawl4ai. State the target and why.
3. Read the release notes / changelog between installed and target. List every breaking change that touches: AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, arun, CacheMode, result.status_code, result.html, result.markdown, result.success. If none, say none, with the source you read.
4. Stop and present the plan. Wait for approval.
5. After approval: set crawl4ai==<target> in requirements.txt, pip install -r requirements.txt, regenerate requirements-lock.txt from pip freeze, run pip check. Install Playwright browsers only if crawl4ai or playwright now requires a new build; state whether you did.
6. Regression: venv/bin/pytest -q. Paste the summary line. Must be 6 passed.
7. Smoke: from repo root, printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com, then trim to first 10 the same way as run-002, then printf 'y\n' | venv/bin/python -m smart_crawler.crawler. Must be 10/10. This is the LAST time the manual trim is used.
8. STOP RULE: if step 6 or 7 fails, or step 3 reveals migration work beyond config/argument renames, do not force it. Revert the two requirements files, reinstall the old pin, write the finding, and stop.
9. Write agent_docs/RESPONSES/response_<timestamp>_bim000-stage1-upgrade.md covering AC-01 to AC-07 with evidence. Print the path and stop.
```

---

## CP2 — Stage 2: Stage prep (handed over only after CP1 is green)

```
You are Claudy, Engineer seat, Stark Web Factory Phase 1, module web-factory-p1-bim000, Stage 2.

Repo: ~/python/stark-web-factory-scrapper-v1. Same branch. Stage 1 is green; crawl4ai is on its new pin. Do not touch the pins.
Read first: web-factory-p1-bim000/BIM000_BRIEF.md §3 Stage 2 and BIM000_ACCEPTANCE_SPEC.md AC-10 to AC-54.

PLAN MODE. Present the plan, list every file you will touch, and stop for approval.

Forbidden: git commands, installs, changes to requirements*, .env.example, agent_docs/RESPONSES/OLD/ contents, anything under agent_docs/SKILLS/.

Work, in this order, one commit-sized chunk each (the Director commits, you do not):

A. Handoff contract (F3).
   - discover.py already root-anchors outputs/discovered_pages.json. Keep it.
   - crawler.py: argparse. --input PATH (default: <repo_root>/outputs/discovered_pages.json). --limit N (default: all). Remove the y/n interactive prompt; add --yes for compatibility if you prefer, but the default must run without input.
   - Delete every reference to discovered_pages_final in code, tests, README, RUN_NOTES.

B. Status validation.
   - After each arun: read result.status_code and result.success. status >= 400 or not success → failed. Do not write a .md for failed pages.
   - 403 and 429 → error "blocked". Stop the run after 3 consecutive blocked pages with a clear message.
   - Print status for every page.
   - Write outputs/run_summary.json: {started_at, finished_at, crawl4ai_version, pause_range_s, pages: [{url, status, ok, elapsed_s, error}]}.

C. Pacing and identity.
   - random.uniform(2, 5) pause between pages, logged with its value. Not before the first page.
   - Crawler UA: a complete current Chrome-shaped string with Chrome/ and Safari/537.36 tokens. After the change, print the sec-ch-ua value the installed crawl4ai derives from it and include it in the report.
   - sitemap_utils.py and discover.py: use one requests.Session with the same UA header for every call.
   - No stealth, no navigator override, no magic, no simulate_user.

D. Truth (F4) and retirement (R-B).
   - Banner and docstrings: version from importlib.metadata.version("crawl4ai"); URL count from len(urls); remove "AI-cleaned" and "v0.6.x/v0.7.x" and "707".
   - Confirm nothing imports discover_site.smart_discover. Then delete the file. Remove its README paragraph.

E. Paths and hygiene.
   - crawler.py: anchor outputs/ to repo root via Path(__file__).resolve().parents[1]. Move mkdir into main().
   - Remove unused import sys from discover.py. Replace cyberizegroup.com with example.com in test fixtures.

F. Tests (offline, stub crawl4ai results; no network in tests).
   - 403 and 500 results produce no file and appear in run_summary as failed / blocked.
   - Three consecutive 429s stop the run.
   - --limit 3 crawls 3. --input honors a custom path.
   - Session UA is set on sitemap calls.
   - Importing smart_crawler.crawler from a temp CWD creates no directory.
   - Run venv/bin/pytest -q. All green. State the count.

G. Docs.
   - README: two-command run section only. RUN_NOTES: add "bim000" section. Create CHANGELOG.md with a bim000 entry.
   - Repoint the four stale references to agent_docs/RESPONSES/OLD/: RECOVERY.md:5, agent_docs/SESSIONS/session_2026-09-03.md:30, session_2026-09-02.md:41 and :47.
   - CLAUDE.md Protocol Directory Layout table: add one row, agent_docs/RESPONSES/OLD/ — archived responses, Director-managed.

H. Final smoke, from repo root, no manual step:
   printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com
   venv/bin/python -m smart_crawler.crawler --limit 10
   Must be 10/10, run_summary.json all 200, 9 pause lines logged.

I. Write agent_docs/RESPONSES/response_<timestamp>_bim000-stage2-prep.md mapping every AC-10 to AC-53 to its evidence. Print the path. Stop.
```
