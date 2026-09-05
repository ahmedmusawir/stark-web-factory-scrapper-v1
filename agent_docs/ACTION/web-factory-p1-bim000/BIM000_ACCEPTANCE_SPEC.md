# web-factory-p1-bim000 — ACCEPTANCE SPEC

> **Module:** `web-factory-p1-bim000` · **Version:** 1.0 · **Date:** 2026-09-05
> Seeded before implementation. SOL grades against this list. Every AC has a check any seat can run. EVIDENCE means a file, a command output, or a diff line.

---

## Stage 1 — Controlled upgrade

| AC | Statement | Check |
|---|---|---|
| AC-01 | Installed Crawl4AI before upgrade is recorded (expected 0.6.3). | `pip show crawl4ai` output pasted in the Stage 1 report. |
| AC-02 | Target version chosen from a current stable release, with the reason and the changelog items reviewed listed in the Stage 1 report. | Report names version, source URL, and each breaking change touching our APIs, or states none. |
| AC-03 | `requirements.txt` pins the new version exactly (`crawl4ai==X.Y.Z`). `requirements-lock.txt` regenerated. `pip freeze` == lock. `pip check` clean. | Diff + command outputs. |
| AC-04 | Playwright browsers refreshed only if required by the new pin; whether it was done is stated. | Report line. |
| AC-05 | Existing 6 tests pass on the new pin, unchanged. | `pytest -q` summary line. |
| AC-06 | Capped 10-page smoke on cyberizegroup.com succeeds on the new pin with the crawler otherwise unchanged (pre-Stage-2 code). | Crawl log, 10/10. |
| AC-07 | If AC-05 or AC-06 fails, or migration exceeds the reviewed surface, Claudy stops and files a finding. No Stage 2 work exists. | Finding doc present, no Stage 2 diff. |

## Stage 2 — Handoff contract (F3)

| AC | Statement | Check |
|---|---|---|
| AC-10 | `python -m discover_site.discover <url>` writes `outputs/discovered_pages.json` at repo root regardless of CWD. | Run from `/tmp`, file lands in repo `outputs/`. |
| AC-11 | `python -m smart_crawler.crawler` reads `outputs/discovered_pages.json` by default. No copy or rename needed. | Two commands back to back, no manual step. |
| AC-12 | `--input PATH` overrides the input file; `--limit N` crawls only the first N. | Offline test + smoke uses `--limit 10`. |
| AC-13 | The string `discovered_pages_final` appears nowhere in code, tests, README, or RUN_NOTES. | `grep -r discovered_pages_final . --exclude-dir=venv --exclude-dir=.git --exclude-dir=agent_docs` → 0. |

## Stage 2 — Status validation

| AC | Statement | Check |
|---|---|---|
| AC-20 | A response with `status_code >= 400` or `success=False` is a failed page. No `.md` is written for it. | Offline test with stubbed 403 and 500 results. |
| AC-21 | `outputs/run_summary.json` is written every run: list of `{url, status, ok, elapsed_s, error}` plus `started_at`, `finished_at`, `crawl4ai_version`, `pause_range_s`. | File present after smoke; 10 entries; all `status: 200`. |
| AC-22 | 403 and 429 are recorded with `error: "blocked"`. Run stops after three consecutive blocked pages and says so. | Offline test with stubbed sequence. |
| AC-23 | Console prints status for every page, success or not. | Smoke log shows 10 status lines. |

## Stage 2 — Pacing and identity

| AC | Statement | Check |
|---|---|---|
| AC-30 | A random pause of 2–5 s runs between pages and each pause value is logged. | Smoke log shows 9 pause lines with values in range. |
| AC-31 | Crawler UA is a complete current Chrome-shaped string (contains `Chrome/` and `Safari/537.36`). Resulting `sec-ch-ua` is non-empty on the installed Crawl4AI. | Test asserts UA tokens; Stage 2 report shows the client-hint value. |
| AC-32 | Discovery uses a `requests.Session` with the same UA on all sitemap calls. No `python-requests` UA leaves the tool. | Offline test on `sitemap_utils`. |
| AC-33 | No stealth mode, no `navigator.webdriver` override, no `magic`/`simulate_user`. | grep + config diff. |

## Stage 2 — Truth, retirement, hygiene, docs

| AC | Statement | Check |
|---|---|---|
| AC-40 | No hardcoded version strings. Banner reports `crawl4ai.__version__` (or package metadata). No "707", no "AI-cleaned". | grep `v0\.[67]\.x`, `707`, `AI-cleaned` → 0 in source. |
| AC-41 | `discover_site/smart_discover.py` deleted. No import, no README mention. | File absent; grep `smart_discover` → 0 outside `agent_docs/`. |
| AC-42 | `crawler.py` root-anchors `outputs/`; no `mkdir` at import time. Importing `smart_crawler.crawler` from `/tmp` creates no directory. | Offline test. |
| AC-43 | `import sys` removed from `discover.py`. Test fixtures use `example.com`. | Diff. |
| AC-44 | README run section shows the two-command flow only. RUN_NOTES has a bim000 section. `CHANGELOG.md` exists with a bim000 entry. | Files. |
| AC-45 | Four stale `RESPONSES/` references repointed to `RESPONSES/OLD/`. `CLAUDE.md` layout table has an `OLD/` row. | Diff lines. |
| AC-46 | `.env.example`, `python-dotenv` pin, and `litellm` transitive untouched. | Diff shows no change. |

## Regression and close

| AC | Statement | Check |
|---|---|---|
| AC-50 | All tests pass: original 6 plus new ones. Count stated. | `pytest -q` summary. |
| AC-51 | Final 10-page smoke on cyberizegroup.com: 10/10, `run_summary.json` all 200, pauses logged, no manual step. | Log + file. |
| AC-52 | No git command was run by Claudy. | Session log statement + `git log` unchanged until Director commits. |
| AC-53 | Stage 1 and Stage 2 reports filed under `agent_docs/RESPONSES/`. | Files present. |
| AC-54 | SOL verdict: PASS. Director merges. | Verdict doc. |
