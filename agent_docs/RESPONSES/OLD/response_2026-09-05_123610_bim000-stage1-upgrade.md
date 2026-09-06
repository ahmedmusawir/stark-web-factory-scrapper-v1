# Response — bim000 Stage 1 (CP1): Controlled crawl4ai upgrade — REPORT

**Module:** web-factory-p1-bim000 · Stage 1 · **Result: GREEN.** Stop rule not triggered. No Stage 2 work exists.
**Branch:** `web-factory-phase1-a` (read-only check). **Git commands run by Claudy:** none (`git status`, `git diff --stat`, `git show`-free; read-only only).
**Plan:** `agent_docs/RESPONSES/response_2026-09-05_122244_bim000-cp1-plan.md` (approved 12:31, "go" = fresh venv + observer).
**Executed:** 12:31–12:35, 2026-09-05. Scratchpad logs: `pip_install_cp1.log`, `pytest_cp1.txt`, `discover_cp1.log`, `crawl_cp1.log`, `requirements*.pre-cp1` (pre-change copies), `crawl_observer.py`.

Labels: **EVIDENCE** (command output / file / diff) · **INFERENCE** (conclusion, basis stated) · **GAP** (expected, not obtained).

---

## AC-01 — Installed version before upgrade recorded

EVIDENCE — `venv/bin/pip show crawl4ai` (12:14, before any change):
```
Name: Crawl4AI
Version: 0.6.3
Summary: 🚀🤖 Crawl4AI: Open-source LLM Friendly Web Crawler & scraper
Home-page: https://github.com/unclecode/crawl4ai
Requires: aiofiles, aiohttp, aiosqlite, beautifulsoup4, brotli, chardet, click, colorama, cssselect, fake-useragent, httpx, humanize, litellm, lxml, nltk, numpy, pillow, playwright, psutil, pydantic, pyOpenSSL, pyperclip, python-dotenv, rank-bm25, requests, rich, snowballstemmer, tf-playwright-stealth, xxhash
```
Companion: playwright 1.52.0, Python 3.12.3, pre-change lock = 94 lines (copy kept at scratchpad `requirements-lock.txt.pre-cp1`).

## AC-02 — Target version, reason, changelog items reviewed

EVIDENCE — `venv/bin/pip index versions crawl4ai` → `LATEST: 0.9.3`; PyPI JSON: 0.9.3 uploaded 2026-08-31, not yanked, `requires_python >=3.10`.
**Target: `crawl4ai==0.9.3`.** Reason: current stable; security release ("no new features and no breaking changes" — CHANGELOG §0.9.3); the two breaking-change releases in the span (0.8.0, 0.9.0) are scoped to the Docker API server ("The pip library is unaffected" — CHANGELOG §0.9.0). No intermediate version offers a smaller library delta.
Sources read: `https://raw.githubusercontent.com/unclecode/crawl4ai/main/CHANGELOG.md` (sections 0.9.3, 0.9.0, 0.8.9–0.8.7, 0.8.0, 0.7.3, 0.7.x, 0.6.2, 0.6.1); `https://pypi.org/pypi/crawl4ai/0.9.3/json`; source at tag `v0.9.3`: `__init__.py`, `async_configs.py`, `async_webcrawler.py`, `async_crawler_strategy.py`, `browser_manager.py`, `browser_adapter.py`, `models.py`, `antibot_detector.py`.

Breaking changes touching our APIs — **none.** Per API:
| API | 0.9.3 | Evidence |
|---|---|---|
| `AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode` exports | unchanged | `__init__.py:4,6,117,155,160,161` |
| `BrowserConfig(headless, user_agent)` | unchanged; new `enable_stealth=False` | `async_configs.py:850-858` |
| `CrawlerRunConfig(cache_mode, page_timeout, delay_before_return_html, wait_for_images)` | unchanged; new `max_retries=0`, `fallback_fetch_function=None` | `async_configs.py:1656,1668,1671,1672,1744-1745` |
| `arun()` return | `CrawlResultContainer` with `__getattr__` → first result; `.success/.markdown/.status_code/.html` resolve as before | `models.py:291-316`; CHANGELOG 0.8.9 #1898 |
| `result.status_code`, `result.html`, `result.markdown`, `result.success` | present | `async_crawler_strategy.py:766`; `models.py` |
| `CacheMode.BYPASS` | unchanged | `__init__.py:155` |

Behavior changes (non-breaking) that reach our unchanged code:
1. **Anti-bot detector in `arun()`** (`async_webcrawler.py:55,405,512,611-630`; `antibot_detector.py`): 429 → blocked; 403/503 with HTML → blocked; vendor block-page signatures (tier 1) any size; generic terms (tier 2) only <10 KB + error status; structural check (tier 3) only <50 KB HTML. Blocked → `success=False`, `error_message="Blocked by anti-bot protection: …"`. `max_retries` default 0 → no retries. INFERENCE: closes run-002's soft-403 blind spot via the library; our `crawler.py:65-71` failure branch now fires on 403/429.
2. **Stealth stack replaced, still off by default:** `tf-playwright-stealth` → `playwright-stealth` (only via `StealthAdapter` when `enable_stealth=True`, `browser_manager.py:771-773`); `patchright` imported only under `if use_undetected:` (`browser_manager.py:625,711,831`); default adapter `PlaywrightAdapter` (`async_crawler_strategy.py:95`). "No stealth" ruling holds unchanged.
3. `sec-ch-ua` derivation unchanged (`async_configs.py:945-946`) → AC-31 (Stage 2) still applies.

## AC-03 — Exact pin, lock regenerated, freeze == lock, pip check clean

EVIDENCE — `git diff --stat`: `requirements.txt | 4 ++--` (pin line + header comment), `requirements-lock.txt` regenerated.
`requirements.txt` now:
```
# Exact pins. Carried over from the retired poetry.lock (2026-09-02); crawl4ai bumped 0.6.3 -> 0.9.3 in bim000 Stage 1 (2026-09-05). Do not bump without a ruling.
crawl4ai==0.9.3
playwright==1.52.0
python-dotenv==1.1.0
beautifulsoup4==4.13.4
requests==2.32.3
pytest==8.3.5
chardet==5.2.0
```
Install method (approved): `mv venv venv.bak` → `python -m venv venv` → `venv/bin/pip install -r requirements.txt` → exit 0 (12:31:42–12:32:43, 61 s). Why fresh: `unclecode-litellm` replaces `litellm` in the same package dir; in-place install would overlay and leave orphans (`litellm`, `openai`, `tf-playwright-stealth`).
EVIDENCE — `venv/bin/pip freeze > requirements-lock.txt` → **98 lines** (was 94). `venv/bin/pip check` → `No broken requirements found.` `diff <(pip freeze|sort) <(sort requirements-lock.txt)` → identical (**freeze == lock**). `pip show crawl4ai` → **0.9.3**; `pip show playwright` → **1.52.0**.
Lock delta vs pre-CP1 (EVIDENCE, `diff` of sorted locks): **added** alphashape 1.3.1, click-log 0.4.0, h2 4.4.1, hpack 4.2.0, hyperframe 6.1.0, httpx2 2.12.0, httpcore2 2.12.0, lark 1.3.1, networkx 3.6.1, patchright 1.62.3, playwright-stealth 2.0.3, rtree 1.4.1, scipy 1.18.1, shapely 2.1.2, trimesh 5.1.0, truststore 0.10.4, unclecode-litellm 1.81.13 · **removed** litellm 1.99.0, tf-playwright-stealth 1.2.0, boto3/botocore/s3transfer/jmespath, colorama, distro, fake-http-header, pydantic-settings, pyperclip, python-dateutil, six · **floated** (unpinned transitives re-resolved in the fresh venv): lxml 5.4.0→6.1.3, pillow 10.4.0→12.3.0, openai 2.54.0→3.8.0, anyio 4.14.2→4.15.0, huggingface_hub 1.29.0→1.30.0, importlib_metadata 8.9.0→9.0.1, tokenizers 0.23.1→0.23.2. INFERENCE: the floats are a consequence of the fresh-venv choice (the dry-run against the old venv would have kept them); all are transitive, none imported by our code, and the regression + smoke below ran on exactly this set. All seven direct pins unchanged except crawl4ai.

## AC-04 — Playwright browsers refreshed only if required; stated

EVIDENCE — playwright stayed at 1.52.0 (pinned). `venv/bin/playwright install --dry-run chromium` → `browser: chromium version 136.0.7103.25 / Install location: ~/.cache/ms-playwright/chromium-1169` and `chromium-headless-shell … chromium_headless_shell-1169`; both directories already present (`ls ~/.cache/ms-playwright` → `chromium-1169 chromium_headless_shell-1169 …`). **No browser install was performed; none was required.** `patchright` is installed as a package but never invoked by default (AC-02 item 2), so no `patchright install` either.

## AC-05 — Existing 6 tests pass on the new pin, unchanged

EVIDENCE — `venv/bin/pytest -q` (fresh venv, crawl4ai 0.9.3, no test file changed):
```
......                                                                   [100%]
6 passed in 0.22s
```
Pre-check: `venv/bin/python -c "from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode"` → `crawl4ai 0.9.3 imports OK`.

## AC-06 — Capped 10-page smoke on cyberizegroup.com, crawler unchanged

EVIDENCE — Discovery: `printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com` — 12:33:18, exit 0, 7.4 s, sitemap index + 3 children, **194 URLs**, 0× 403/429 (`discover_cp1.log`).
EVIDENCE — Trim (last manual use, per CP1 step 7): run-002 one-liner → `outputs/discovered_pages_final.json`, 10 URLs (same first 10 as run-002).
EVIDENCE — Crawl: `printf 'y\n' | venv/bin/python <scratchpad>/crawl_observer.py` (wraps `AsyncWebCrawler.arun`; imports `smart_crawler.crawler` **unchanged** — `git status` shows no `.py` modified) — 12:33:26–12:34:33, exit 0, **67.5 s wall**. `[INIT].... → Crawl4AI 0.9.3`.
```
[OBSERVER] status=200 success=True fit_md=0 raw_md=12277 elapsed=8.9s url=https://cyberizegroup.com/blog/
[OBSERVER] status=200 success=True fit_md=0 raw_md=14257 elapsed=6.5s url=https://cyberizegroup.com/web-design-process/
[OBSERVER] status=200 success=True fit_md=0 raw_md=26568 elapsed=6.8s url=https://cyberizegroup.com/what-to-look-for-in-ppc-agency/
[OBSERVER] status=200 success=True fit_md=0 raw_md=7561  elapsed=5.9s url=https://cyberizegroup.com/our-covid-19-plan/
[OBSERVER] status=200 success=True fit_md=0 raw_md=18835 elapsed=6.2s url=https://cyberizegroup.com/5-foundational-principles-for-online-success/
[OBSERVER] status=200 success=True fit_md=0 raw_md=24609 elapsed=6.4s url=https://cyberizegroup.com/5-mistakes-real-estate-agents-make/
[OBSERVER] status=200 success=True fit_md=0 raw_md=6217  elapsed=5.6s url=https://cyberizegroup.com/covid-19-safety-tips-for-the-2020-pandemic/
[OBSERVER] status=200 success=True fit_md=0 raw_md=26697 elapsed=6.4s url=https://cyberizegroup.com/on-page-seo-audit/
[OBSERVER] status=200 success=True fit_md=0 raw_md=24756 elapsed=6.5s url=https://cyberizegroup.com/what-to-expect-from-a-ppc-agency/
[OBSERVER] status=200 success=True fit_md=0 raw_md=29644 elapsed=6.3s url=https://cyberizegroup.com/ppc-agency-checklist/
✅ Successful: 10   ❌ Failed: 0   Success rate: 100.0%   Average per file: 18.8 KB
```
**10/10, all HTTP 200, no 403/429, no ANTIBOT log lines, no anti-bot veto (all `success=True`).** `fit_markdown` empty on 10/10 → `raw_markdown` fallback, identical to run-002 (F1 deferred, expected). 10 `.md` files written 12:33:36–12:34:33, 6,216–29,691 bytes (run-002: 6,208–29,382; INFERENCE: byte drift = dynamic content, same as run-002 vs C1).
INFERENCE — pages ran 5.6–6.8 s each vs 6.3–7.2 s on 0.6.3 (mean 6.3 s vs 6.6 s): within noise; no performance regression.

## AC-07 — Stop rule

Not triggered: AC-05 = 6 passed, AC-06 = 10/10, migration surface = zero code changes (no argument renames needed). **No Stage 2 work exists**: `git status` shows only `requirements.txt`, `requirements-lock.txt`, and protocol files (`agent_docs/`, `RECOVERY.md`) changed; every `.py`, README, RUN_NOTES, `.env.example`, `CLAUDE.md` untouched. Revert path remains available: `venv.bak/` (old 0.6.3 venv, gitignored) + scratchpad copies of both requirements files.

## Notes for the Director / SOL

- **`venv.bak/`** (~old venv, gitignored via `.gitignore:137`) is left in place for revert safety. Delete once CP1 is accepted: `rm -rf venv.bak`.
- **`unclecode-litellm`** is described on PyPI as a "pre-compromise fork of litellm". INFERENCE: upstream litellm had a supply-chain incident after 1.81.x; the old venv carried litellm 1.99.0. The fresh venv no longer has upstream litellm at all. Our code never imports either (ruling R-A). Awareness only.
- For Stage 2 AC-20/22: on 0.9.3 the library already flips `success=False` for 403/429/503 and sets `error_message` — our status validation can rely on both `status_code` and `success` as the spec says.
- `outputs/discovered_pages_final.json` exists from this smoke; Stage 2 deletes the convention.

```
🔔 GIT REMINDER — uncommitted CP1 work on web-factory-phase1-a:
  requirements.txt, requirements-lock.txt (the Stage 1 diff)
  agent_docs/RESPONSES/response_2026-09-05_122244_bim000-cp1-plan.md
  agent_docs/RESPONSES/response_2026-09-05_123610_bim000-stage1-upgrade.md
  agent_docs/SESSIONS/session_2026-09-05.md, RECOVERY.md
  (+ carried: 09-04 recon, session logs, handoff/plan responses, your OLD/ move)
→ Your call. I will not run it.
```

🛑 Stage 1 complete. Awaiting Director: CP1 green → CP2 handoff.
