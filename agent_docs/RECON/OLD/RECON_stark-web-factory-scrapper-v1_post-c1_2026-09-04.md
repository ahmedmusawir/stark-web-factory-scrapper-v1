# RECON REPORT — stark-web-factory-scrapper-v1 (post-C1, pre-C2) — 2026-09-04

> Produced by `stark-recon` v1.1 (skill at `agent_docs/SKILLS/stark-recon-skill-v1.1/`).
> Read-only recon of the repo; zero source mutations, zero git mutations (only `git status`, `git branch`, `git log`, `git ls-files`).
> **Python repo** — per Operator ruling this run follows the 2026-09-02 baseline recon's translation: the mission's Next.js-specific sections (auth store, Tailwind tokens, Supabase, nav/auth-state, tsconfig) are marked **N/A** and replaced with their Python-stack equivalents. Where any doc and disk disagree, disk wins.
> Supersedes `RECON_crawl4ai-exp-project-v1_baseline_2026-09-02.md` (pre-C1; stale per AP-8).
> Snapshot: `main` @ d047503, working tree NOT clean (see D0.8). Launch CWD: `/home/moose/python/stark-web-factory-scrapper-v1`.

---

## Section 0 — Day-0 Ground-Truth Sweep (highest-value drift)

**D0.1 — Packaging doctrine vs disk: NOW CONSISTENT. — EVIDENCE**
CLAUDE.md:760 claims "requirements.txt + venv + pip (no Poetry/pyproject.toml)". Disk: `requirements.txt` (7 exact pins), `requirements-lock.txt` (94 lines), `venv/` present, no `pyproject.toml`, no `poetry.lock`. The baseline recon's #1 drift (Poetry) was resolved by C1 CP2. `venv/bin/pip freeze | sort` is byte-identical to sorted `requirements-lock.txt`; `pip check` → "No broken requirements found."

**D0.2 — Every README/RUN_NOTES-named file exists. — EVIDENCE**
`ls` confirmed all: `discover_site/{__init__,discover,sitemap_utils,smart_discover}.py`, `smart_crawler/{__init__,crawler}.py`, `tests/{test_discover,test_sitemap_utils}.py`, `pytest.ini`, `requirements.txt`, `requirements-lock.txt`, `.env.example`, `.python-version` (=3.12.3), `outputs/.gitkeep`, `RUN_NOTES.md`, `RECOVERY.md`, `CLAUDE.md`. No handbook lies in the README layout block (README.md:57-64).

**D0.3 — Forbidden-zone grep (Python equivalents). — EVIDENCE**
- `os.getenv` / `os.environ` / `load_dotenv` across all `.py` outside venv → **0 hits**. The baseline's 13 direct `os.getenv` call sites are gone (deleted with the chatbot/utils code). Failure-mode #20 is trivially satisfied because nothing reads env at all.
- Donor-identity purge grep (RUN_NOTES.md §5 pattern: ghl/gohighlevel/genai/filesearch/chatbot/rag) over `*.py *.md *.toml *.txt *.cfg *.ini *.example`, excluding `agent_docs/`, `venv/`, `.git/`, `CLAUDE.md` → **0 hits**. Purge held.
- `TODO|FIXME|XXX|placeholder|lorem` → 0 hits.

**D0.4 — Test runner. — EVIDENCE**
`pytest.ini`: `testpaths = tests`, `pythonpath = .`. `venv/bin/pytest --collect-only -q` → 6 tests, all in `tests/`. `venv/bin/pytest -q` → **6 passed in 0.22s** (fresh run this session, not a historical count). No `utils/test_*.py` collection hazard remains (utils/ deleted).

**D0.5 — Env ground truth. — EVIDENCE + GAP**
`.env.example` now exists (C1 added it) and contains exactly one line: `GEMINI_API_KEY=`. **But no code reads it** (D0.3: zero `os.getenv`/`dotenv` calls; `python-dotenv` is pinned in `requirements.txt:4` and imported nowhere). The example file and the dotenv dependency are residue of the deleted summarizer/chatbot, or forward-staging for C2. README.md:14 says "fill in values as later phases require them" — INFERENCE: intentional forward-staging. QUESTION for Tony: is `GEMINI_API_KEY` the intended C2 secret, or should the example be emptied until C2 defines its env?

**D0.6 — Entry-point inventory ("route table" equivalent). — EVIDENCE**
Runnable surfaces on disk, all module-form only:
| Entry | Reads | Writes |
|---|---|---|
| `python -m discover_site.discover <url>` (interactive 1/2/q) | network | `<REPO_ROOT>/outputs/discovered_pages.json` (root-anchored via `Path(__file__)`, discover.py:13-14) |
| `python -m discover_site.smart_discover <url>` | network (Playwright) | `outputs/discovered_pages_final.json` (**CWD-relative**, smart_discover.py:23) |
| `python -m smart_crawler.crawler` (interactive y/n) | `outputs/discovered_pages_final.json` (**CWD-relative** via `Path.cwd()`, crawler.py:24-28) | `outputs/pages/*.md` |
README.md:25 claim "Running the scripts by file path does not work" — VERIFIED: `venv/bin/python discover_site/discover.py --help` → `ModuleNotFoundError: No module named 'discover_site'`.

**D0.7 — Protocol files CLAUDE.md mandates. — GAP (unchanged since baseline)**
`CHANGELOG.md` → missing. `agent_docs/KIP_REGISTRY.md` → missing (CLAUDE.md:285,301,313,531 all reference it). `agent_docs/SKILLS/README.md` → 0 bytes. `agent_docs/ACTION/` → empty dir. Carried forward from the baseline recon's Surprise #8; C1 did not address it (out of C1 scope).

**D0.8 — Working tree is NOT clean; protocol artifacts moved mid-session. — EVIDENCE**
`git status --short` shows 6 `D` + 6 `??`: every `agent_docs/RESPONSES/response_2026-09-02_*.md` has been moved into a new `agent_docs/RESPONSES/OLD/` subfolder. Directory mtime `2026-09-04 15:37:41 +0600` — i.e. during this session, after session start (git status was clean at 15:36). Not done by Claudy. Consequences:
- `RECOVERY.md:5`, `session_2026-09-03.md:30`, `session_2026-09-02.md:41,47` all point at the OLD paths → **4 stale path references** now.
- `OLD/` is not a location in CLAUDE.md's Protocol Directory Layout table ("Every protocol artifact has exactly one home").
- The move is uncommitted → this is the KIP-2026-08-11 loss class live again.
QUESTION for Tony: is `RESPONSES/OLD/` a new archival convention (then CLAUDE.md's layout table + the 4 references need updating), or a scratch move?

---

## Section 1 — Stack Versions

All EVIDENCE from `requirements.txt` + `venv/bin/pip show` (both agree):
- Python **3.12.3** (`.python-version`, tracked in git; `venv/bin/python --version` matches)
- crawl4ai **0.6.3** · playwright **1.52.0** · beautifulsoup4 **4.13.4** · requests **2.32.3** · python-dotenv **1.1.0** · chardet **5.2.0** (transitive, pinned deliberately per RUN_NOTES §1) · pytest **8.3.5**
- Packaging: pip + venv, `requirements.txt` top-level pins, `requirements-lock.txt` full freeze (94 lines, == live venv).
- Playwright browsers on disk (`~/.cache/ms-playwright`): `chromium-1169`, `chromium_headless_shell-1169` (the ones playwright 1.52 uses), plus `chromium_headless_shell-1194` and `ffmpeg-1011` (from another project on this machine — INFERENCE; harmless).
- **Heavyweight transitive deps pulled in by crawl4ai 0.6.3** (in lock): `litellm==1.99.0`, `openai==2.54.0`, `nltk==3.10.3`, `numpy==2.5.2`, `lxml==5.4.0`, `rank-bm25==0.2.2`, `tf-playwright-stealth==1.2.0`, `fake-useragent==2.2.0`. None imported by our code. INFERENCE: not a problem, but the Architect should know an LLM client stack is already installed if C2 wants one — and that these are pinned by crawl4ai, not by us.
- **Absent:** FastAPI, Uvicorn, Supabase, Streamlit, google-genai, LangGraph, ADK, Next.js. CLAUDE.md's "Primary Stack" table (CLAUDE.md:752-765) remains factory-wide doctrine, not this repo's stack — same drift as baseline Section 1, still true.
- `pip-audit` not installed → no vulnerability audit run (N/A for `npm audit`). GAP, low priority.

## Section 2 — Structure vs Doc Claims

- Actual tree (tracked, 19 files outside `agent_docs/`): `discover_site/` (4 files), `smart_crawler/` (2), `tests/` (2), `outputs/.gitkeep`, root docs/config (`CLAUDE.md README.md RECOVERY.md RUN_NOTES.md pytest.ini requirements*.txt .env.example .gitignore .python-version`). `agent_docs/` has 18 tracked files (RECON, RESPONSES, SESSIONS, SKILLS). EVIDENCE: `git ls-files`.
- README.md:57-64 layout block matches disk exactly. EVIDENCE.
- CLAUDE.md preference folders `/types /services /api /components /app /reference` → all absent. GAP (same as baseline). For a 3-module script repo this is INFERENCE-appropriate; flag only if C2 introduces Pydantic models or external API calls (then `/types` and `reference/` become mandatory per CLAUDE.md:727,793).
- **Path-anchoring inconsistency across the 3 modules — EVIDENCE:** `discover.py:13` anchors output to the repo root via `Path(__file__).resolve().parents[1]` (C1 fix; works from any CWD). `crawler.py:24` uses `Path.cwd()`; `smart_discover.py:23` uses a bare relative `Path("outputs/...")`. Both of the latter silently write to `./outputs/` wherever you happen to be. README.md:25 covers this by mandating repo-root CWD, so it is documented, not broken. INFERENCE: C1 fixed only the module it had to; the other two were left as-is per scope discipline.
- **Import-time side effects — EVIDENCE:** `smart_discover.py:24` and `crawler.py:27` both `mkdir` at module import. Harmless today (pytest doesn't import them), but any future test that imports `smart_crawler.crawler` will create `outputs/pages/` in the test CWD.
- `discover.py:1` `import sys` is unused (0 `sys.` usages). EVIDENCE. Trivial.
- Local branches `phase-c1-cleanup` and `repo-cleanup-1` still exist (session_2026-09-03 said "Tony's to prune"). EVIDENCE: `git branch`.

## Section 3 — Auth Pattern

N/A (no web auth, no users). Secrets model: **none in use**. `.env.example` stages `GEMINI_API_KEY` but no code consumes it (D0.5). `.env` is gitignored (`.gitignore` "Environments" block). The baseline's committed File Search store id (`ghl_store_name.txt`) is gone — EVIDENCE: `find` → absent; identity grep clean.

## Section 4 — Design Reality

N/A. No UI of any kind remains (both Streamlit apps deleted in C1). CLAUDE.md:762 Streamlit-via-FastAPI rule has nothing to apply to. Console output uses emoji-heavy `print()` throughout `crawler.py`/`smart_discover.py`; `discover.py` uses `[INFO]/[WARNING]/[ERROR]` prefixes — two logging styles, no `logging` module anywhere (CLAUDE.md:783 `logging_service` rule: not implemented, same as baseline; INFERENCE: acceptable for scripts, flag if C2 adds a service layer).

## Section 5 — Database

N/A. No database. State = flat files under `outputs/` (gitignored except `.gitkeep`). Current contents: `outputs/pages/` holds the **5 crawled `.md` from the 2026-09-02 baseline run** (mtimes 14:38-14:39). **`outputs/discovered_pages.json` and `discovered_pages_final.json` are NOT present** — EVIDENCE: `ls outputs/*.json` → none. RUN_NOTES §3-4 describe them as produced; they have since been removed (INFERENCE: cleaned locally after CP4, or never survived the branch merge since gitignored). Consequence: `python -m smart_crawler.crawler` today exits 1 with "File not found … Run discovery first!" (crawler.py:135-138) until discovery is re-run. Not a defect; a reproduction note for the Architect.

## Section 6 — Skills / Security / Env

- Skills: `agent_docs/SKILLS/stark-recon-skill-v1.1/` complete (8 files). `agent_docs/SKILLS/README.md` still **0 bytes**. No `.claude/skills/` dir at root. EVIDENCE.
- `agent_docs/ACTION/` empty; `agent_docs/RECON/` has the baseline report + this one. EVIDENCE.
- Launch CWD: `/home/moose/python/stark-web-factory-scrapper-v1` (repo root) — required, since crawler/smart_discover are CWD-relative (Section 2).
- Required env vars: **none** (D0.5). `.env.example` stages `GEMINI_API_KEY` for a future phase.
- Security audit: none (`pip-audit` absent, no `agent_docs/security/`). GAP, low priority for a local CLI tool.
- Root pointer files: `CLAUDE.md` (v3.1 factory doctrine) present; no `AGENTS.md`/`GEMINI.md`/`PROJECT_POINTER.md`. The baseline's `CLAUDE TRAINING GUIDES/` + `MISSION_BRIEF.md` conflict is **resolved by deletion** — EVIDENCE: dir absent.

## Section 8 — Demo / Tutorial Scaffolding & Version Residue

- Third-party demo APIs: 0. Cross-project residue by identity grep: 0 (D0.3).
- **Stale banner/comment strings in `crawler.py` — EVIDENCE** (carried finding #3, verified still present): line 3 `"Crawl4AI v0.6.x"`, line 47 `"v0.7.x patterns"`, line 190 `"UPGRADED BATCH CRAWLER - v0.7.x"` (installed is 0.6.3), line 218 `"~30-40 minutes for 707 URLs"` (hardcoded count from the donor project's doc-site crawl; actual URL count is `len(urls)`, available one line up). Strings only, zero functional impact.
- **`smart_discover.py` carries donor-shaped assumptions — EVIDENCE:** line 51 waits for `.theme-doc-sidebar-menu` (Docusaurus), line 162 filters to URLs containing `/docs/`, line 166 drops `/category/`, line 237 assumes a `/docs/` prefix for pattern analysis. This module only works on Docusaurus-style doc sites. README.md:45 says so ("alternative discoverer for JavaScript sidebar-navigation doc sites… not used in the baseline run"). INFERENCE: it is a kept-but-unexercised tool; whether C2 wants a generic JS discoverer is a scoping question. QUESTION: keep, generalize, or retire in C2?
- **Test fixtures hardcode a real client domain — EVIDENCE:** `tests/test_discover.py:4` and `tests/test_sitemap_utils.py:6-8,26-43` use `cyberizegroup.com` (the C1 baseline target). Tests are fully offline (requests stubbed), so no network dependency. INFERENCE: cosmetic; `example.com` would be neutral. Not a donor-identity hit (the purge grep pattern does not include it, correctly).
- `docs/`, `utils/`, both Streamlit apps, all `_v2` script pairs, `ghl_store_name.txt`: all gone. EVIDENCE. Baseline Section 8's entire residue list is retired.

## Section 9 — Packaging / Compile Scope

- No `.py` under `agent_docs/` → nothing pytest could mis-collect; `testpaths = tests` scopes it anyway. EVIDENCE.
- `pytest.ini` `pythonpath = .` is a config-file setting, not a shell `PYTHONPATH` hack — satisfies CLAUDE.md "pytest must pass in a clean venv — no PYTHONPATH hacks" in letter; INFERENCE: it is the standard pytest idiom for a non-installed package. Alternative would be a `pyproject.toml`/`setup.cfg` editable install, which Tony ruled out (no pyproject). Consistent.
- `__pycache__/` dirs present in `discover_site/`, `smart_crawler/`, `tests/`; `.pytest_cache/` at root — all gitignored. EVIDENCE.

## Section 10 — Surprises (the gold)

1. **RESPONSES → RESPONSES/OLD move, uncommitted, mid-session (D0.8).** Four protocol docs now point at paths that no longer exist. Layout table in CLAUDE.md has no `OLD/` home. Needs a ruling before the next RESPONSES write (where do *new* response artifacts go — `RESPONSES/` root, presumably; and does `OLD/` get codified?).
2. **`crawl4ai 0.6.3` DOES support the content filter the crawler needs — EVIDENCE (validates carried finding #1):** `inspect.signature(CrawlerRunConfig.__init__)` has a `markdown_generator` parameter; `from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter` and `from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator` all import cleanly in the pinned venv. So the `fit_markdown`-empty problem is a **config omission in `crawler.py:48-53`, not a version gap** — the fix is available without any dependency bump. Architect can scope it as a small, pin-safe C2 task.
3. **Discovery → crawl handoff is still glued by a shell one-liner, not code (carried finding #2, verified):** `discover.py:14` writes `discovered_pages.json`; `crawler.py:28` reads `discovered_pages_final.json`; only `smart_discover.py:23` writes the `_final` name directly. README.md:33-37 documents the copy step. INFERENCE: the `_final` name was the donor project's "curated subset" convention. Architect decision: unify the filename, or add a `--input` flag, or keep the manual curation step as a feature.
4. **`.env.example` + `python-dotenv` pin with zero consumers (D0.5).** Either forward-staging or residue. One-line question.
5. **`outputs/*.json` absent** — crawler cannot run today without re-running discovery (Section 5). Not a bug; a fresh-clone reality check RUN_NOTES doesn't mention.
6. **Three path-anchoring strategies in three modules (Section 2)** — root-anchored, `Path.cwd()`, bare relative. Works because README mandates root CWD; brittle if C2 adds a wrapper CLI or tests that import `crawler`.
7. **Two logging idioms, no `logging` module** (Section 4). Fine for scripts; becomes a CLAUDE.md:783 conflict the moment a service layer appears.
8. **Protocol gaps unchanged since baseline (D0.7):** no `CHANGELOG.md`, no `KIP_REGISTRY.md`, empty `SKILLS/README.md`, empty `ACTION/`. The 2026-09-03 handoff listed this as known; still open.
9. **Two stale local branches** (`phase-c1-cleanup`, `repo-cleanup-1`) — Tony's to prune, noted so the Architect's brief doesn't assume a single-branch repo.
10. `cn()` helper check: N/A (no frontend).

## Section 11 / 12 — Nav, Auth-State, Verification Predicates

N/A (no UI). Verification predicates that DO apply, current state: identity-purge grep = 0 ✅ · `os.getenv` outside a config service = 0 ✅ (vacuously) · pytest fresh run = 6/6 ✅ · `pip freeze == requirements-lock.txt` ✅ · `pip check` clean ✅.

## Section 13 — Tree (2 levels, tracked + venv/outputs noted)

```
.
├── .env.example .gitignore .python-version CLAUDE.md README.md RECOVERY.md RUN_NOTES.md
├── pytest.ini requirements.txt requirements-lock.txt
├── discover_site/   __init__.py discover.py sitemap_utils.py smart_discover.py
├── smart_crawler/   __init__.py crawler.py
├── tests/           test_discover.py test_sitemap_utils.py
├── outputs/         .gitkeep  pages/ (5 .md, gitignored)   [no discovered_pages*.json]
├── agent_docs/      ACTION/ (empty)  RECON/ (2)  RESPONSES/OLD/ (6, uncommitted move)  SESSIONS/ (3)  SKILLS/ (README 0B + stark-recon-skill-v1.1/)
└── venv/            (gitignored; == requirements-lock.txt)
```

---

## Recommendation to Architect

**Safe to author C2 against (verified on disk, no re-verification needed):**
- Stack: Python 3.12.3 via pyenv + plain venv + pip; pins crawl4ai 0.6.3 / playwright 1.52.0 / bs4 4.13.4 / requests 2.32.3 / python-dotenv 1.1.0 / chardet 5.2.0 / pytest 8.3.5; lock file == live venv. No Poetry. No version bumps without a ruling.
- Pipeline: `discover_site.discover` (sitemap or homepage `<a>`) → `outputs/discovered_pages.json` → *manual copy/subset* → `outputs/discovered_pages_final.json` → `smart_crawler.crawler` → `outputs/pages/<slug>.md`. Module-form invocation only, from repo root.
- Public functions with test coverage: `is_valid_link`, `normalize_link` (discover.py:16-25), `fetch_sitemap_urls` (sitemap_utils.py:5). Untested: `extract_internal_links`, everything in `crawler.py` and `smart_discover.py`.
- crawl4ai 0.6.3 exposes `CrawlerRunConfig(markdown_generator=DefaultMarkdownGenerator(content_filter=PruningContentFilter(...)))` — the `fit_markdown` fix needs no dependency change.
- No env vars consumed; no secrets; no DB; no UI; no network in tests.
- Donor-identity purge: clean (grep = 0 outside `agent_docs/` + `CLAUDE.md`).

**Doc drift to correct (do NOT author from these claims):**
- `RECOVERY.md:5`, `session_2026-09-03.md:30`, `session_2026-09-02.md:41,47` → reference `agent_docs/RESPONSES/response_*.md` paths that moved to `RESPONSES/OLD/` today (D0.8).
- `crawler.py:3,47,190` "v0.6.x / v0.7.x" and `:218` "707 URLs" — strings lie about version and workload.
- `crawler.py:5-6` and `:195-197` promise "AI-cleaned fit_markdown" — false at runtime until the content filter is configured (falls through to `raw_markdown` on every page, per CP3 live test).
- CLAUDE.md:752-765 stack table, :782-783 config/logging-service rules, :727/733 `/types` — factory doctrine not applicable to this repo as it stands (same as baseline; unchanged).
- `RUN_NOTES.md` §3-4 imply `outputs/*.json` exist — they don't on this machine now.

**Cleanup candidates C2 could absorb (recon did NOT touch them):**
- Configure `PruningContentFilter` in `crawler.py` run config (unblocks `fit_markdown`).
- Unify discovery→crawl filename or add an input flag; retire the one-liner.
- Fix `crawler.py` banner strings (version, hardcoded 707).
- Anchor `crawler.py` and `smart_discover.py` paths to the repo root like `discover.py`; move `mkdir` out of import time.
- Drop unused `import sys` in `discover.py:1`.
- Decide `smart_discover.py`: keep (Docusaurus-only), generalize, or retire.
- Decide `.env.example` / `python-dotenv`: keep as C2 staging or remove until needed.
- Create `CHANGELOG.md` + `agent_docs/KIP_REGISTRY.md`; fill `agent_docs/SKILLS/README.md`; decide `ACTION/`.
- Neutralize `cyberizegroup.com` in test fixtures (cosmetic).

**Open questions for Tony (need rulings before or inside the C2 brief):**
1. `agent_docs/RESPONSES/OLD/` — new archival convention (codify in CLAUDE.md layout table, update 4 stale refs) or scratch? And where do new RESPONSES artifacts land?
2. Is `GEMINI_API_KEY` the intended C2 secret (keep `.env.example` + dotenv), or premature?
3. `smart_discover.py` — in C2 scope, out, or delete?
4. Discovery→crawl handoff: keep the manual "final" curation step as a feature, or make it code?
5. Are `CHANGELOG.md` / `KIP_REGISTRY.md` C2 scope, or a separate protocol-hygiene pass?

---

🛑 Recon complete. Read-only of the codebase. Writes: this report + session-log/RECOVERY updates per protocol. No source changes, no git mutations.
