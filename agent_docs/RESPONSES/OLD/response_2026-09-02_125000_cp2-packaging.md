# CP2 REPORT — requirements.txt conversion + venv install — 2026-09-02 12:50

**Branch:** phase-c1-cleanup. No git commands run.

## Files created
- `requirements.txt` — 6 exact pins carried from the retired poetry.lock:
  `crawl4ai==0.6.3 playwright==1.52.0 python-dotenv==1.1.0 beautifulsoup4==4.13.4 requests==2.32.3 pytest==8.3.5`
- `requirements-lock.txt` — `pip freeze` after the first green install: 94 lines (full transitive snapshot; reproducibility record)
- `.env.example` — `GEMINI_API_KEY=` (placeholder only)

## Files modified
- `.gitignore` — appended `outputs/*` + `!outputs/.gitkeep` (venv/ was already ignored at line 134). Verified with `git check-ignore`: `venv` ignored, `outputs/discovered_pages.json` ignored, `outputs/.gitkeep` NOT ignored.

## Environment (local, not committed)
```
python --version                       # 3.12.3 (pyenv, via .python-version)
python -m venv venv
venv/bin/pip install -r requirements.txt   # EXIT 0, 94 packages
venv/bin/pip freeze > requirements-lock.txt
venv/bin/playwright install chromium   # EXIT 0 → Chromium Headless Shell 136.0.7103.25 (build v1169), 101 MB
venv/bin/python -c "import crawl4ai, playwright, bs4, requests, dotenv"   # imports ok
```
Pins verified in freeze: `Crawl4AI==0.6.3` (capitalized dist name), `playwright==1.52.0`, `python-dotenv==1.1.0`, `beautifulsoup4==4.13.4`, `requests==2.32.3`, `pytest==8.3.5`. No version changed.

## ⚠️ One finding — transitive drift produced a warning (not an error)
`RequestsDependencyWarning: urllib3 (2.7.0) or chardet (7.6.0)/charset_normalizer (3.5.1) doesn't match a supported version!`

| Package | old poetry.lock | venv now | Pulled in by |
|---|---|---|---|
| chardet | 5.2.0 | **7.6.0** | Crawl4AI (unpinned) |
| urllib3 | 2.4.0 | 2.7.0 | requests |
| charset-normalizer | 3.4.2 | 3.5.1 | requests |

Cause: requests 2.32.3 asserts `chardet < 6`; chardet 7.6.0 trips it. Harmless (requests still imports and works; charset-normalizer is used instead), but it prints on every import.
**Options — your call, not doing either unilaterally:**
- (a) Add `chardet==5.2.0` to requirements.txt (restores the lock version; silences the warning; still "no version changes" in spirit) — my recommendation
- (b) Leave as-is; note it in RUN_NOTES

## Not done / deferred
- `crawl4ai-setup` not run — only if the CP3 crawl fails without it.
- pip itself is 24.0 (notice says 26.2.1 available) — not upgraded, not in scope.

## Suggested commit (text only)
```
git add requirements.txt requirements-lock.txt .env.example .gitignore
git commit -m "chore(c1): replace Poetry with pinned requirements.txt + venv workflow

- requirements.txt: 6 exact pins carried from poetry.lock (crawl4ai 0.6.3,
  playwright 1.52.0, python-dotenv 1.1.0, beautifulsoup4 4.13.4,
  requests 2.32.3, pytest 8.3.5) — no version changes
- requirements-lock.txt: pip freeze of the first green install
- .env.example: GEMINI_API_KEY placeholder
- .gitignore: keep outputs/ run artifacts local, track outputs/.gitkeep"
```

→ CP2 STOP. Awaiting confirm (+ chardet ruling) before CP3.

## Addendum 12:55 — chardet ruling (a) applied
- `requirements.txt` +1 line: `chardet==5.2.0`
- `venv/bin/pip install -r requirements.txt` → uninstalled chardet-7.6.0, installed chardet-5.2.0
- `requirements-lock.txt` refrozen; delta is exactly one line: `chardet==7.6.0` → `chardet==5.2.0` (still 94 lines)
- `python -W error -c "import requests"` → clean, no RequestsDependencyWarning
