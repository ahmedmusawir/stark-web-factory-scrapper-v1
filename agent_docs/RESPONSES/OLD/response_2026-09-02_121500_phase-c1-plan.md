# PLAN — PHASE C1: Cleanup + Functional Baseline — 2026-09-02 12:15

**Status:** PENDING_APPROVAL

## STEP 0 — Arrival check (done, read-only)

| Item | Result |
|---|---|
| CLAUDE.md | PRESENT, tracked (factory-wide v3.1 doctrine, GHL-era stack table) |
| RECOVERY.md | PRESENT, tracked |
| agent_docs/ | PRESENT, tracked: ACTION/, RECON/, RESPONSES/, SESSIONS/, SKILLS/ (13 files) |
| KIP_REGISTRY.md, CHANGELOG.md | ABSENT (pre-existing gap; not in C1 scope) |

→ No scaffolding needed. I will NOT edit CLAUDE.md (its pip/FastAPI stack claims are wrong for this repo; flagged, out of scope).

## Findings that change the plan

1. **Poetry is not installed** on this machine (`poetry: command not found`; no pipx). Acceptance requires `poetry install`. I must install Poetry (official installer into ~/.local/bin, isolated). This is a machine change outside the repo — needs your OK.
2. **Locked crawl4ai is 0.6.3**, playwright 1.52.0 (poetry.lock, lock-version 2.1 → Poetry 2.x). crawler.py's "v0.7.x" docstring is stale. NO upgrade this phase. Removing deps from pyproject changes the content-hash, so `poetry lock` (no `--regenerate`) is required; I will diff the lock before/after and prove crawl4ai/playwright pins are unchanged.
3. **Recon's discover.py CWD claim was wrong.** `python discover_site/discover.py` from root actually works today (sys.path[0] is the script dir, output path is CWD-relative = root). It breaks under `python -m discover_site.discover` and when run from inside discover_site/. Fix below makes both forms work.
4. **Two more GHL references in KEEP files** beyond the docstring: `smart_discover.py:201,237` (gohighlevel example URL + hard-coded path prefix) and `crawler.py:248` ("Run: python summary_generator_ghl.py"). Acceptance grep requires zero, so these get minimal edits.
5. **Discovery→crawl handoff mismatch:** discover.py writes `outputs/discovered_pages.json`; crawler.py reads `outputs/discovered_pages_final.json` (smart_discover's output). Not fixing the crawler's input path (not in scope); baseline will write the 5-URL subset to the file the crawler expects, via a documented one-liner.
6. **Git doctrine conflict:** CLAUDE.md says git is Operator-only; your mission grants me git except merge / push to main. I treat your explicit instruction as the ruling for C1. Commits stay local; I will not push unless you say so.

## 📋 PLAN

1. **Branch** — `git checkout -b phase-c1-cleanup` from current HEAD (aa5b80f, same as main).
2. **Install Poetry 2.x** (official installer → ~/.local/bin). Verify `poetry --version`.
3. **Deletions (commit 1: "chore(c1): remove GHL RAG-era code, docs, and artifacts")** via `git rm`:
   - `smart_crawler/summary_generator_ghl.py`
   - `utils/` (14 files incl. `__init__.py`)
   - `ghl_chatbot_streamlit.py`, `ghl_chatbot_streamlit-1.py`, `ghl_store_name.txt`
   - `docs/` (4 GHL RAG docs)
   - `CLAUDE TRAINING GUIDES/` (14 files incl. MISSION_BRIEF.md — retires the session-location conflict)
   - `outputs/**` — 1,428 tracked files (3 JSON + pages/); add `outputs/.gitkeep` so the empty dir survives
4. **pyproject repair (commit 2: "chore(c1): repair pyproject, relock, add .env.example")**
   - Remove `prompt_agent` from packages; remove `google-genai` and `streamlit`
   - Keep crawl4ai, playwright, python-dotenv, beautifulsoup4, requests; pytest in dev
   - `poetry lock` (preserve pins) → diff proves crawl4ai 0.6.3 / playwright 1.52.0 unchanged
   - Add `.env.example` with `GEMINI_API_KEY=`
   - Add to `.gitignore`: `outputs/*` + `!outputs/.gitkeep` so baseline run artifacts stay local (see Assumption 3)
5. **Code fixes (commit 3: "fix(c1): root-runnable discovery, stale references")**
   - `discover_site/__init__.py`, `smart_crawler/__init__.py` — empty; makes them real packages (poetry-core include + `-m` invocation)
   - `discover_site/discover.py` — import `from discover_site.sitemap_utils import ...`; output path anchored to repo root via `Path(__file__).resolve().parents[1] / "outputs"`, mkdir; no other behavior change
   - `smart_crawler/crawler.py` — docstring line 8 → `Run: python -m smart_crawler.crawler` and fix "v0.7.x" → "v0.6.x"; line 247-248 next-step hint → remove the summary_generator_ghl reference
   - `discover_site/smart_discover.py` — lines 199-201 usage example → generic placeholder URL; line 237 hard-coded gohighlevel prefix → derive from `base_url`. Functional `/docs/` filter left as-is.
6. **Environment setup** — `poetry install`; `poetry run playwright install chromium` (cached chromium-1217 may not match playwright 1.52); `poetry run crawl4ai-setup` if the crawl fails without it. Browser downloads only — no dep version changes.
7. **Functional baseline (from repo root)**
   - `printf '1\n' | poetry run python -m discover_site.discover https://cyberizegroup.com/` (sitemap; fall back to option 2 = homepage links if sitemap is absent) → `outputs/discovered_pages.json`
   - One-liner writes first 5 URLs → `outputs/discovered_pages_final.json`
   - `printf 'y\n' | poetry run python -m smart_crawler.crawler` → ≤5 `.md` in `outputs/pages/`
   - `grep -rniE "ghl|gohighlevel|genai|filesearch|file search" --include=*.py --include=*.toml .` → expect zero hits
8. **RUN_NOTES.md (commit 4: "docs(c1): RUN_NOTES + session state")** — exact commands, outputs produced, grep proof, lock diff proof. Session file COMPLETE entry, RECOVERY.md update, this artifact — committed in the same chunk.

## FILES TO MODIFY
- `pyproject.toml`, `poetry.lock`, `.gitignore`
- `discover_site/discover.py`, `discover_site/smart_discover.py`, `smart_crawler/crawler.py`
- `agent_docs/SESSIONS/session_2026-09-02.md`, `RECOVERY.md`

## FILES TO CREATE
- `.env.example`, `outputs/.gitkeep`, `discover_site/__init__.py`, `smart_crawler/__init__.py`, `RUN_NOTES.md`

## FILES I WILL NOT TOUCH
- `CLAUDE.md` — doctrine; stack-table drift flagged, not C1 scope
- `README.md`, `.python-version`, `agent_docs/RECON/*`, `agent_docs/SKILLS/*`
- `discover_site/sitemap_utils.py` — no defects, no GHL refs
- `crawler.py` logic (BASE_DIR = cwd, input filename, interactive confirm, stale "707 URLs" message) — only docstring + GHL hint edited
- Dependency versions — nothing upgraded

## ASSUMPTIONS
1. Poetry install via official installer is acceptable on this machine.
2. Package name `crawl4ai-exp-project-v1` in pyproject stays (rename not requested).
3. Baseline run artifacts (discovered JSON, 5 md files) are NOT committed; `outputs/*` gets gitignored, `.gitkeep` tracked. Override if you want the baseline artifacts in the branch.
4. Commits are local; no push. Branch cut from repo-cleanup-1 HEAD.
5. `python -m <pkg>.<module>` is the blessed invocation; the direct `python discover_site/discover.py` form also keeps working after `poetry install`.

## RISKS
- cyberizegroup.com may have no `/sitemap.xml` (WordPress often serves `/wp-sitemap.xml`) → fall back to homepage-link mode; documented either way.
- crawl4ai 0.6.3 may need `crawl4ai-setup` / a matching chromium download; network-dependent.
- `poetry lock` on a 2-dep removal should only prune; if the resolver touches other pins I stop and report before committing.

→ Awaiting approval before proceeding.
