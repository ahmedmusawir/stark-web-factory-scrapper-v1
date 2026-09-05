# PLAN (AMENDED) — PHASE C1: Cleanup + Functional Baseline — 2026-09-02 12:25

**Status:** PENDING_APPROVAL (amended per Operator rulings; supersedes response_2026-09-02_121500)

## Rulings applied
- GIT: I run zero git commands. 4 commits → 4 CHECKPOINTS; at each I stop, report exact file changes + suggested commit message, wait for confirm.
- PACKAGING: Poetry retired, not installed. pyproject.toml + poetry.lock deleted. requirements.txt with exact pins from lock. pyenv 3.12.3 + `python -m venv venv` + pip. `pip freeze > requirements-lock.txt` after first green install.
- IDENTITY PURGE: grep across surviving py/md/toml/txt/cfg → zero hits; README rewritten as Stark Web Recon stub.
- TESTS: `tests/` with 2-3 pure-logic pytest smoke tests, no network, no env.

## Pins extracted from poetry.lock (verified 12:20)
```
crawl4ai==0.6.3
playwright==1.52.0
python-dotenv==1.1.0
beautifulsoup4==4.13.4
requests==2.32.3
pytest==8.3.5
```
Tooling verified: pyenv 3.12.3 active via .python-version; `python3 -m venv` OK; pip 24.0.

## ⚠️ One confusion to rule on — identity grep scope
Pre-deletion grep of survivors shows hits in files that carry the words legitimately:
- `CLAUDE.md` — factory doctrine ("RAG | Google File Search API", "Google File Search API Patterns" section). Tony's file.
- `agent_docs/RECON/*`, `agent_docs/SESSIONS/*`, `agent_docs/RESPONSES/*` — audit trail that *describes* the GHL cargo being removed. Scrubbing it falsifies history.
- `agent_docs/SKILLS/stark-recon-skill-v1.1/**` — the recon skill's own examples/templates.
Also: bare `rag` matches `fragment`, `average`, `storage`, `drag` → grep must use `\brag\b`.

**My assumption (override at green light):** purge grep = `grep -rniE "ghl|gohighlevel|genai|filesearch|file search|chatbot|\brag\b" --include=*.py --include=*.md --include=*.toml --include=*.txt --include=*.cfg . --exclude-dir=agent_docs --exclude-dir=venv --exclude=CLAUDE.md` → zero hits. agent_docs/ and CLAUDE.md are exempt as protocol/audit files. Everything else — code, README, .env.example, RUN_NOTES, tests — must be clean. Known straggler already found in a KEEP file: `crawler.py:197` ("Better RAG quality") → scrub.

## 📋 CHECKPOINT PLAN

**CP1 — Deletions + purge proof** (no git; I delete with `rm`, you commit)
- Delete: `smart_crawler/summary_generator_ghl.py`, `utils/` (14 files), `ghl_chatbot_streamlit.py`, `ghl_chatbot_streamlit-1.py`, `ghl_store_name.txt`, `docs/` (4), `CLAUDE TRAINING GUIDES/` (14), `outputs/**` (1,428 files) → create `outputs/.gitkeep`
- Delete: `pyproject.toml`, `poetry.lock` (pins already extracted above)
- Run purge grep; report hits remaining in KEEP code (expected: crawler.py:197,248; smart_discover.py:201,237 — fixed in CP3, or scrubbed here if you prefer CP1 fully clean → I'll scrub the string-only ones here: crawler.py 197/248, smart_discover.py 201; line 237 is a logic change → CP3)
- Report: file list + suggested commit message → wait

**CP2 — requirements.txt + venv install green**
- Create `requirements.txt` (6 pins above; pytest included — single file, no dev split unless you want `requirements-dev.txt`)
- `python -m venv venv` (pyenv 3.12.3) → `venv/bin/pip install -r requirements.txt`
- `venv/bin/playwright install chromium` (browser download only); `crawl4ai-setup` only if a crawl fails without it
- `venv/bin/pip freeze > requirements-lock.txt`
- `.gitignore` already ignores `venv/`; add `outputs/*` + `!outputs/.gitkeep`
- Add `.env.example` (`GEMINI_API_KEY=`)
- Report: install output summary, freeze line count, files → wait

**CP3 — Code fixes + tests green + live runs**
- `discover_site/__init__.py`, `smart_crawler/__init__.py` (empty)
- `discover_site/discover.py`: `from discover_site.sitemap_utils import fetch_sitemap_urls`; output path anchored to repo root via `Path(__file__).resolve().parents[1] / "outputs"`, mkdir
- `smart_crawler/crawler.py`: docstring (`v0.7.x`→`v0.6.x`, run line → `python -m smart_crawler.crawler`); remove summary_generator next-step hint; "Better RAG quality" line scrubbed
- `discover_site/smart_discover.py`: usage example URL → generic; line 237 prefix derived from `base_url`; `/docs/` filter untouched
- `tests/test_sitemap_utils.py` (parse flat sitemap + sitemap-index from XML strings via `ET`, using a mocked `requests.get`) and `tests/test_discover.py` (`is_valid_link`, `normalize_link` — pure functions, no network). 2 files, ~3-5 asserts. No pytest config needed once `utils/test_*.py` is gone.
- `venv/bin/pytest` from root → green
- Live: `printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com/` (fallback option 2 if no sitemap.xml) → `outputs/discovered_pages.json`; one-liner → first 5 URLs → `outputs/discovered_pages_final.json`; `printf 'y\n' | venv/bin/python -m smart_crawler.crawler` → ≤5 md in `outputs/pages/`
- Report: diffs, pytest output, run outputs → wait

**CP4 — README + RUN_NOTES + session state**
- `README.md` rewritten: one-paragraph Stark Web Recon description; setup (pyenv/venv/pip); run discovery + crawl
- `RUN_NOTES.md`: exact commands, produced files, purge-grep proof, pin provenance (lock → requirements)
- Session file COMPLETE entry, RECOVERY.md
- Report → wait for final confirm

## FILES I WILL NOT TOUCH
`CLAUDE.md`, `.python-version`, `agent_docs/RECON/*`, `agent_docs/SKILLS/*`, `discover_site/sitemap_utils.py` (only tested, not edited), crawler.py logic (cwd BASE_DIR, input filename, interactive confirm, "707 URLs" message)

## ASSUMPTIONS
1. Identity-grep exemptions as stated above (agent_docs/, CLAUDE.md).
2. Single `requirements.txt` including pytest (no dev split).
3. Baseline artifacts not committed (`outputs/*` ignored, `.gitkeep` tracked).
4. Branch `phase-c1-cleanup` is yours to create; I work in whatever branch is checked out and never verify by mutating.

## RISKS
- No `/sitemap.xml` on cyberizegroup.com → homepage-link fallback, documented.
- crawl4ai 0.6.3 browser deps may need `crawl4ai-setup` (network).
- pip resolution of transitive deps is unpinned until `requirements-lock.txt` is captured — that file becomes the reproducibility record.

→ Awaiting green light.
