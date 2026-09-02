# RECON REPORT — crawl4ai-exp-project-v1 (baseline recon) — 2026-09-02

> Produced by `stark-recon` v1.1 (skill at `agent_docs/SKILLS/stark-recon-skill-v1.1/`).
> Read-only recon of the repo; zero source mutations, zero git operations.
> This is a **Python** repo — the mission's Next.js-specific sections (auth store,
> Tailwind tokens, Supabase, nav/auth-state, tsconfig) are marked **N/A** and replaced
> with their Python-stack equivalents. Where any doc and disk disagree, disk wins.

---

## Section 0 — Day-0 Ground-Truth Sweep (highest-value drift)

**D0.1 — Packaging doctrine vs disk: POETRY, not pip. — EVIDENCE**
`CLAUDE.md` § Tech Stack claims: *"Python Setup: requirements.txt + venv + pip (no Poetry/pyproject.toml)"* — **CLAIM, FALSE on disk.**
Reality: `pyproject.toml` (tool.poetry, poetry-core build backend) + `poetry.lock` (387 KB) at root; `ls requirements*.txt` → none; no `venv/` at root. — EVIDENCE: `pyproject.toml:1-27`, root listing.
**This is the single biggest doc-vs-disk drift in the repo.**

**D0.2 — pyproject names a package that does not exist. — EVIDENCE**
`pyproject.toml` packages list: `discover_site`, `smart_crawler`, **`prompt_agent`** — but `ls -d prompt_agent` → **MISSING**. A `poetry install` of the project package would fail on this. — EVIDENCE: `pyproject.toml:7-11`; `find` confirms absence.

**D0.3 — Architecture doc names files that do not exist. — EVIDENCE**
`docs/ghl_rag_chatbot_architecture.md:62-63` claims `smart_crawler/data_processing.py` ("LangChain + LLM summarizer") and `smart_crawler/schema.py` ("Pydantic output models"). Neither exists anywhere on disk (`find . -name data_processing.py -o -name schema.py` → nothing). The real summarizer is `smart_crawler/summary_generator_ghl.py` (google-genai, not LangChain). Classic handbook-lie class.

**D0.4 — Forbidden-zone grep (Python equivalent): direct `os.getenv` everywhere. — EVIDENCE**
`CLAUDE.md` failure-mode #20 forbids `os.getenv()` outside `config_service`. Reality: **13 files** call `os.getenv("GEMINI_API_KEY")` directly (both Streamlit apps, `smart_crawler/summary_generator_ghl.py:28`, and 10 files in `utils/`). No `config_service.py` and no `logging_service.py` exist anywhere. — EVIDENCE: grep output.
**INFERENCE:** the config/logging-service doctrine was written for the FastAPI stack; this repo predates it. Still a drift to resolve in doctrine (see Recommendation).

**D0.5 — Env ground truth. — GAP**
No `.env`, `.env.example`, or any env template on disk (`.env` is gitignored). The only env var the code reads is **`GEMINI_API_KEY`** (all 13 call sites); all entry scripts call `load_dotenv()`, so a local `.env` is the expected mechanism — but no example file documents this for a fresh clone. — GAP: expected `.env.example`; searched root.

**D0.6 — Test runner. — EVIDENCE / GAP**
`pyproject.toml` dev-deps: `pytest = "*"`. But there is **no `tests/` directory and no pytest-style unit tests**. The three `utils/test_*.py` files are manual connectivity scripts (module-level code, e.g. `utils/test_api_connection.py:21`), which pytest would try to collect and execute on import — they are not unit tests. — GAP: pytest declared, zero pytest suite.

**D0.7 — "Route table" equivalent (entry-point inventory). — EVIDENCE**
Actual runnable surfaces on disk:
- `discover_site/` — `discover.py`, `smart_discover.py`, `sitemap_utils.py` (URL discovery)
- `smart_crawler/` — `crawler.py` (crawl4ai batch crawler), `summary_generator_ghl.py` (per-page summaries)
- `utils/` — 13 scripts: store create/check, uploads (v1+v2), master-index generate (v1+v2) / upload (v1+v2) / cleanup / delete-old, CLI chatbot, 3 connectivity tests
- Root — `ghl_chatbot_streamlit.py` (split-panel UI) and `ghl_chatbot_streamlit-1.py` (sidebar UI) — two live variants

---

## Section 1 — Stack Versions

- Python: `>=3.12,<4.0` (pyproject) / `.python-version` = **3.12.3** — consistent. EVIDENCE. (Note: `.python-version` mtime is today 2026-09-02 10:46 — recently touched.)
- Packaging: **Poetry** (poetry-core backend) — contradicts CLAUDE.md (see D0.1).
- Key deps (pyproject): `crawl4ai *`, `playwright *`, `python-dotenv *`, `beautifulsoup4 *`, `requests *`, **`google-genai ^1.55.0`** (matches CLAUDE.md's RAG pin — one doctrine claim that IS true. EVIDENCE), `streamlit ^1.52.2`.
- Dev: `pytest *`.
- **Not present at all:** FastAPI, Uvicorn, Supabase, LangGraph, Google ADK, Next.js — the CLAUDE.md "Primary Stack" table is aspirational for this repo. INFERENCE: CLAUDE.md is the factory-wide doctrine file, not written for this repo specifically.

## Section 2 — Structure vs Doc Claims

- Actual tree: `discover_site/`, `smart_crawler/`, `utils/`, `docs/`, `outputs/` (+`outputs/pages/`, **1,425 files**), `agent_docs/` (ACTION, RECON, RESPONSES, SESSIONS, SKILLS), `CLAUDE TRAINING GUIDES/`, two Streamlit apps + `ghl_store_name.txt` at root. EVIDENCE.
- DRIFT: architecture doc's `smart_crawler/` contents wrong (D0.3).
- DRIFT: `smart_crawler/crawler.py:8` docstring says "Run: `python crawler_v2_batch.py`" — no such file; the file is `crawler.py`. EVIDENCE (stale self-reference).
- `discover_site/discover.py:10` does `from sitemap_utils import fetch_sitemap_urls` — a flat (non-package) import. INFERENCE: script must be run with CWD inside `discover_site/`; running `python discover_site/discover.py` from root would ImportError. No `sys.path` hacks anywhere (grep → none). Also `discover.py:12` writes to relative `outputs/discovered_pages.json`, which assumes root CWD — the two assumptions conflict. QUESTION for Tony: what's the blessed invocation?
- No `/types`, `/services`, `/reference` folders (CLAUDE.md preferences expect them). GAP — `reference/` matters most: CLAUDE.md says "SDK ground truth lives in reference/" for the File Search API, but no such folder exists here.
- `CLAUDE.md`, `RECOVERY.md`, `agent_docs/` are **untracked in git** (`git status`). EVIDENCE. This is exactly the loss class KIP 2026-08-11 records.

## Section 3 — Auth Pattern

N/A (no web auth). Secrets model: single `GEMINI_API_KEY` via `.env` + `load_dotenv()` (D0.4/D0.5). `ghl_store_name.txt` holds the live File Search store id `fileSearchStores/ghlapiv2docs-snonl43ig3vp` — committed to the repo. EVIDENCE. INFERENCE: store id alone isn't a secret (useless without the API key), but flagging for Tony's call.

## Section 4 — Design Reality

N/A (no frontend token system). UI = Streamlit. NOTE: `ghl_chatbot_streamlit.py:28-37` injects CSS via `st.markdown(..., unsafe_allow_html=True)` — the Streamlit analog of `dangerouslySetInnerHTML`; content is static so risk is nil. EVIDENCE.
DRIFT vs doctrine: CLAUDE.md says Streamlit dev rigs make "all calls through HTTP to FastAPI, no direct imports" — both Streamlit apps construct `genai.Client` directly (`ghl_chatbot_streamlit.py:90`). EVIDENCE. INFERENCE: this repo predates that rule.

## Section 5 — Database

N/A. No database. State = flat files: `outputs/*.json` (discovery results), `outputs/pages/` (1,425 crawled md + summary files), `ghl_store_name.txt`, plus the remote Google File Search store.

## Section 6 — Skills / Security / Env

- Skills: `agent_docs/SKILLS/stark-recon-skill-v1.1/` (this skill; complete: CLAUDE.md, SKILL.md, templates, references, examples). `agent_docs/SKILLS/README.md` is **0 bytes** — empty placeholder. EVIDENCE.
- `agent_docs/ACTION/` and `agent_docs/RESPONSES/` are empty. EVIDENCE.
- Launch CWD: `/home/moose/python/crawl4ai-exp-project-v1` (repo root) — recorded here per mission Q6.5.
- Required env: `GEMINI_API_KEY` only. No `.env.example` (GAP, D0.5).
- No security-audit artifacts (`agent_docs/security/` absent). N/A for npm audit (no package.json).

## Section 8 — Demo / Tutorial Scaffolding & Version Residue

No third-party demo APIs (no jsonplaceholder/dummyjson/etc.). The residue class here is **superseded versions**, all still live at top level:
- `ghl_chatbot_streamlit.py` (split-panel) vs `ghl_chatbot_streamlit-1.py` (sidebar) — two divergent UIs of the same bot; docs reference BOTH. QUESTION: which is canonical?
- `utils/master_index_generator.py` vs `_v2.py`; `utils/upload_master_index.py` vs `_v2.py`; plus `delete_old_master_index.py` / `cleanup_master_index.py` one-shot maintenance scripts. INFERENCE from docstrings: v2 = "quality edition" supersedes v1. QUESTION: retire v1s?
- `outputs/discovered_pages.json` vs `_final.json` vs `_final-org.json` — three generations of discovery output. QUESTION: keep all as data provenance, or prune?
Recommended bucket if a cleanup pass is authorized: one "version-residue retirement" task with the complete list above — one pass, not whack-a-mole.

## Section 9 — Packaging / Compile Scope

- No `.py` files under `agent_docs/` (nothing for pytest to mis-collect there). EVIDENCE.
- Real collection risk instead: `utils/test_*.py` are module-level scripts — a bare `pytest` run from root would import-execute them and make live API calls / fail on missing key. FLAG for any future pytest suite: either rename them (not `test_*`) or configure pytest `testpaths`. INFERENCE.
- `pyproject` package list broken by phantom `prompt_agent` (D0.2) — `poetry install` of the root package fails until fixed or the entry removed.

## Section 10 — Surprises (the gold)

1. **`prompt_agent` phantom package** in pyproject (D0.2) — likely a planned module never built, or deleted without pyproject cleanup.
2. **`CLAUDE TRAINING GUIDES/` mission conflict:** `MISSION_BRIEF.md` instructs each Claude instance to act as an "extraction agent" and to write session files **"in app root"** — directly contradicting CLAUDE.md's Session Memory Protocol (`agent_docs/SESSIONS/`, root logs forbidden, failure-mode #22). Two standing orders disagree. QUESTION: does MISSION_BRIEF still apply, or is it superseded by CLAUDE.md v3.1?
3. **Doctrine file describes a different stack than the repo** (D0.1 + Section 1): CLAUDE.md v3.1 is factory-wide (FastAPI/Next/Supabase/pip) while this repo is a Poetry-managed crawler/RAG scripts project. Anyone authoring a brief from CLAUDE.md's stack table without this recon would spec the wrong world.
4. **Empty protocol stubs:** `agent_docs/SKILLS/README.md` (0 bytes), `agent_docs/ACTION/` (empty). INFERENCE: scaffolding mid-setup, created today 10:47-10:51.
5. `smart_crawler/crawler.py` stale docstring self-reference (`crawler_v2_batch.py`).
6. `docs/` (4 GHL RAG docs) partially stale: architecture doc's file tree wrong (D0.3); docs also reference both Streamlit variants as coexisting.
7. Protocol state (`CLAUDE.md`, `RECOVERY.md`, `agent_docs/`) untracked in git — the exact KIP-2026-08-11 loss scenario, live right now.
8. No KIP_REGISTRY.md, no CHANGELOG.md yet (CLAUDE.md mandates both). GAP.

## Recommendation to Architect

**Safe to author against (verified):**
- Stack: Python 3.12.3, Poetry, crawl4ai + playwright + google-genai 1.55 + streamlit 1.52; single env var `GEMINI_API_KEY` via dotenv; state in flat files + Google File Search store `fileSearchStores/ghlapiv2docs-snonl43ig3vp`.
- Pipeline shape: discover (`discover_site/`) → crawl (`smart_crawler/crawler.py`) → summarize (`summary_generator_ghl.py`) → index/upload (`utils/*_v2.py`) → chat (Streamlit / CLI).
- 1,425 crawled artifacts in `outputs/pages/`; v2 scripts are the current generation.

**Doc drift to correct in doctrine (do NOT author from these claims):**
- CLAUDE.md "requirements.txt + pip, no Poetry" — false here (Poetry).
- CLAUDE.md config_service/logging_service/Streamlit-via-FastAPI rules — not implemented anywhere in this repo.
- `docs/ghl_rag_chatbot_architecture.md` file tree (`data_processing.py`, `schema.py`) — false.
- MISSION_BRIEF session-file location — conflicts with CLAUDE.md; needs an Operator ruling.

**Cleanup candidates (needs authorization — recon did not touch them):**
- Remove `prompt_agent` from pyproject packages (or create the package).
- Retire v1 scripts + one duplicate Streamlit app after Tony picks the canonical one.
- Fix `crawler.py` docstring; fix or document `discover.py`'s CWD-dependent import.
- Add `.env.example` (GEMINI_API_KEY=), `tests/` + pytest config guarding against `utils/test_*` collection.

**Open questions for Tony:**
1. Which Streamlit app is canonical — split-panel (`ghl_chatbot_streamlit.py`) or sidebar (`-1.py`)?
2. Does MISSION_BRIEF's extraction-agent role still stand, or is CLAUDE.md v3.1 the sole doctrine now?
3. Is `prompt_agent` planned work (build it) or dead (remove from pyproject)?
4. Keep all three `discovered_pages*.json` generations, or prune?

---
*Recon: read-only; the only writes were this report + session-log/RECOVERY updates per protocol. No source changes, no git.*
