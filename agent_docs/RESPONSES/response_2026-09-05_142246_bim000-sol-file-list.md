# Response — bim000: Files for SOL

Repo: `~/python/stark-web-factory-scrapper-v1`, branch `web-factory-p1-bim000`. All paths relative to repo root. All verified present on disk.

## 1. What SOL grades against

| File | Purpose |
|---|---|
| `agent_docs/ACTION/web-factory-p1-bim000/BIM000_ACCEPTANCE_SPEC.md` | The AC list (AC-01…AC-54). Frozen. |
| `agent_docs/ACTION/web-factory-p1-bim000/BIM000_BRIEF.md` | Scope (§3) and out-of-scope (§4), for context on rulings. |

## 2. Claudy's evidence reports (read these two)

| File | Covers |
|---|---|
| `agent_docs/RESPONSES/response_2026-09-05_123610_bim000-stage1-upgrade.md` | AC-01 … AC-07 (crawl4ai upgrade, committed 600d181) |
| `agent_docs/RESPONSES/response_2026-09-05_131346_bim000-stage2-complete.md` | AC-10 … AC-53 (stage prep, committed f124cb0) |
| `agent_docs/RESPONSES/response_2026-09-05_141959_bim000-sol-readiness.md` | Four caveats SOL will hit (AC-10, AC-41, AC-45, gitignored artifacts) |

## 3. Code and docs the ACs point at

| File | ACs |
|---|---|
| `requirements.txt`, `requirements-lock.txt` | AC-03, AC-46 |
| `smart_crawler/crawler.py` | AC-11, 12, 20–23, 30, 31, 33, 40, 42 |
| `discover_site/sitemap_utils.py` | AC-31, 32 (USER_AGENT, SESSION) |
| `discover_site/discover.py` | AC-10, 32, 43 |
| `tests/test_crawler.py`, `tests/test_discover.py`, `tests/test_sitemap_utils.py` | AC-12, 20, 22, 30–32, 42, 43, 50 |
| `README.md`, `RUN_NOTES.md`, `CHANGELOG.md` | AC-13, 41, 44 |
| `CLAUDE.md` (root, lines 306 and 314) | AC-45 |
| `agent_docs/SESSIONS/session_2026-09-02.md`, `session_2026-09-03.md` | AC-45 |
| `agent_docs/SESSIONS/session_2026-09-05.md` | AC-52 (git-zero statement, checkpoints A–G) |

## 4. Run artifacts (gitignored — exist on this VM only)

| File | ACs |
|---|---|
| `outputs/run_summary.json` | AC-21, AC-51 |
| `outputs/pages/*.md` (10 files) | AC-51 |
| `outputs/discovered_pages.json` (194 URLs) | AC-10, AC-11 |

To regenerate from a clean checkout: `printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com` then `venv/bin/python -m smart_crawler.crawler --limit 10` (about 90 s).

## 5. Commands SOL can run directly

```
venv/bin/pytest -q                                                   # AC-05, AC-50 → 13 passed
venv/bin/pip show crawl4ai | grep Version                            # AC-01/03 → 0.9.3
grep -r discovered_pages_final . --exclude-dir=venv --exclude-dir=.git --exclude-dir=agent_docs   # AC-13 → 0
grep -r smart_discover . --exclude-dir=venv --exclude-dir=.git --exclude-dir=agent_docs           # AC-41 → 1 (CHANGELOG line; ruling)
grep -rnE 'enable_stealth|use_undetected|override_navigator|magic|simulate_user' discover_site smart_crawler   # AC-33 → 0
grep -rnE 'v0\.[67]\.x|707|AI-cleaned' discover_site smart_crawler   # AC-40 → 0
```
