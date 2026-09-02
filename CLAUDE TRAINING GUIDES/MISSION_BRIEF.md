# MISSION BRIEF — Read This First

**To:** Claude Code (every new instance)
**From:** Previous Claude instances + User
**Purpose:** Orient you in under 2 minutes

---

## What We're Building

**AI App Factory + Agentic Harness**

A system for building AI-powered Python apps fast — the same way Next.js docs enabled frontend builds in 2-3 hours. Right now that speed doesn't exist for Python/ADK/agent apps. We're fixing that.

**Two deliverables:**
1. **Python/ADK Manuals** — comprehensive reference docs (like Next.js docs but for AI backends)
2. **Playbooks** — step-by-step build guides for common app types (RAG pipeline, agent, API wrapper, etc.)

---

## Why This Mission Exists

User built Next.js apps in hours by following solid docs.
User built VidGen (Python/AI) without docs and struggled.
**Variable: documentation = speed.**

Strategy: extract patterns from existing Python/AI repos → synthesize into manuals → validate on new builds.

---

## Your Role Each Session

You are the **extraction agent**. Each session:

1. **Read this folder** (`CLAUDE TRAINING GUIDES/`) — restores your context
2. **Explore the repo** — read every relevant source file
3. **Create `/docs/` in app root** — your extraction output (never touch the guides folder)
4. **Write a session file** — `session-YYYY-MM-DD-{app-name}.md` in app root

That's it. Don't build features. Don't fix bugs. Extract patterns.

---

## Rules

| Rule | Detail |
|------|--------|
| `CLAUDE TRAINING GUIDES/` | **READ ONLY — except MISSION_BRIEF.md.** Only update MISSION_BRIEF when adding a completed repo. Never create docs here. |
| `/docs/` | **Create in APP ROOT** (`/docs/` next to `pyproject.toml`). All extraction docs go here. NOT inside `CLAUDE TRAINING GUIDES/`. |
| Session file | Create **inside `CLAUDE TRAINING GUIDES/`**. Named `session-YYYY-MM-DD-{app-name}.md`. |
| Scope | Extract patterns only. No feature work unless explicitly asked. |

---

## What to Extract Per Repo

Create these docs in `/docs/`:

- **`architecture.md`** — system flow, file structure, how stages connect
- **`patterns.md`** — repeating code patterns (copy-pasteable)
- **`decisions.md`** — key tech choices with context, alternatives, rationale
- **`{integration}.md`** — deep-dive on any major integration (RAG, LLM, cloud API, etc.)

Session file captures: what you found, insights for manuals, comparison to previous repos, gaps.

---

## Repos Completed

| Repo | App Type | Key Patterns Extracted | Session File |
|------|----------|----------------------|--------------|
| `project-bibo-youtube-v2` (VidGen) | Media pipeline (Vertex AI) | File-based state, sequential pipeline, Streamlit wrapper, Vertex AI (Gemini/Imagen/TTS/STT), approval gates | `session-2026-02-22.md` |
| `crawl4ai-exp-project-v1` | RAG pipeline (crawl4ai + LangChain + Chroma) | crawl4ai API, multi-provider LLM factory, Pydantic v2, RAG ingestion, optional LLM noop fallback, site_config naming | `session-2026-02-23-crawl4ai-rag.md` |
| `google-adk-exp-v2` | ADK patterns lab | All ADK agent types (Agent, Sequential, Parallel, Combo, MCP, LiteLlm), GCS callable instructions, output_key data flow | `session-2026-02-23-google-adk-exp.md` |
| `google-adk-n8n-hybrid-v2` | Production ADK bundle (Cloud Run + N8N) | N8N 4-node gateway workflow, Secret Manager, Supabase session persistence, source-based Cloud Run deploy, .gcloudignore, shell form Dockerfile | `session-2026-02-23-google-adk-n8n-hybrid.md` |
| `google-adk-wrapper-v2` | FastAPI ADK Wrapper (stateless middleware) | `/run_agent` endpoint, ADK event parsing, session 404 auto-recovery, history normalization, config.json env-aware registry, two-service architecture | `session-2026-02-23-google-adk-wrapper-v2.md` |
| `google-adk-n8n-hybrid-streamlit-v2` | Streamlit Frontend (auth + chat UI + admin panel) | Supabase email/password auth gate, gatekeeper() multi-page guard, per-user per-agent session bookmarks, Mission Control GCS admin panel, Procfile for Cloud Run, st.secrets dual path | `session-2026-02-23-google-adk-n8n-hybrid-streamlit-v2.md` |
| `managed-rag-google-file-search-api-v1` | Google Managed RAG (tutorial / working reference) | File Search API lifecycle (create store → async upload → poll → query → delete), `force=True` delete gotcha, dual-document strategy (original + structured summary), PDF direct analysis via `types.Part.from_bytes`, implicit retrieval via Gemini tool, store_name.txt state, API key vs Vertex AI auth | `session-2026-02-23-managed-rag-google-file-search.md` |
| `crawl4ai-exp-project-v1` (main branch) | GHL API documentation chatbot (Google managed RAG + Streamlit) | Synthetic master index for aggregation queries, system prompt as retrieval strategy, dual-representation upload (md + SUMMARY per page), filename-based category extraction over LLM parsing, split-panel Streamlit layout, batch upload with per-file error handling, targeted document deletion | `session-2026-02-23-ghl-rag-chatbot.md` |

---

## Confirmed Cross-Repo Patterns (Already Proven)

These patterns appeared across multiple repos — high confidence for manuals:

1. **File-based state** — no database, pipeline state = files on disk (VidGen, crawl4ai)
2. **Sequential stages** — each stage reads previous stage's output files
3. **Config-driven** — model/voice/settings in config, nothing hardcoded
4. **Optional AI components** — pipeline works degraded without LLM keys
5. **User confirmation gates** — prompt before expensive/irreversible operations
6. **Rich for terminal output** — `[green]`, `[red]`, `[yellow]` conventions
7. **`Path` objects** — never string concatenation for file paths
8. **Per-project output folders** — outputs organized by project/site, not globally
9. **GCS callable instruction** — `instruction=fn` (not `instruction=fn()`) fetches fresh from GCS per run (adk-exp-v2, n8n-hybrid)
10. **ADK module structure** — `agent.py` + `__init__.py` per agent, `root_agent` export (adk-exp-v2, n8n-hybrid)
11. **Vertex-only in production** — after experimenting with multi-provider, production repos converge on all-Vertex (n8n-hybrid)
12. **FastAPI as ADK gateway** — `/run_agent` endpoint wraps ADK session creation + `/run` + event parsing into one simple call; always return `effective_session_id` (adk-wrapper-v2)
13. **`.org` file preservation** — copy working file as `filename-org.ext` before changes; seen as backup/undo pattern (adk-exp-v2, adk-wrapper-v2, streamlit-v2)
14. **Supabase auth gate in Streamlit** — `st.session_state.session is None` gate + `supabase.auth.sign_in_with_password()` + `st.rerun()` on login; first user-facing auth pattern in the series (streamlit-v2)
15. **`gatekeeper()` for multi-page Streamlit apps** — single function calls `st.stop()` to block unauthenticated access to any `pages/` file; one call at top of every protected page (streamlit-v2)
16. **Per-user session bookmarks in Supabase** — store `{agent_name: session_id}` JSON blob per user; `upsert` handles new + returning users; restores conversations across logins and devices (streamlit-v2)
17. **`Procfile` for Streamlit Cloud Run** — `web: streamlit run chat.py --server.port $PORT --server.enableCORS false`; used instead of Dockerfile for pure Python/Streamlit apps; same `$PORT` shell-substitution principle (streamlit-v2)
18. **`st.secrets` → Secret Manager dual path** — same `st.secrets["KEY"]` reads `.streamlit/secrets.toml` locally and Secret Manager values (injected via `--set-secrets`) in Cloud Run; no code change between environments (streamlit-v2)
19. **`_old/` folder for deprecated code** — keep superseded scripts in `src/_old/` or `_old_keep/` rather than deleting; visible in crawl4ai (`_old_keep/`), managed-rag (`src/_old/`); acts as reference for API evolution and previous approaches
20. **Async operation polling** — `while not operation.done: sleep(1); operation = client.operations.get(operation)`; pattern for any google-genai SDK long-running operation (managed-rag upload); expect this in other managed Google Cloud APIs
21. **`config={'force': True}` for managed service deletion** — managed cloud services often require a force/cascade flag to delete resources that have sub-resources; always check for this when deletion fails; confirmed in google-genai File Search API document delete

---

## What's Covered (Good Enough for Manuals)

These topics have sufficient depth from the repos completed:

| Topic | Coverage | Source Repos |
|-------|----------|-------------|
| ADK agent types (Agent, Sequential, Parallel, Combo, MCP, LiteLlm) | ✅ Excellent | adk-exp-v2, n8n-hybrid |
| GCS callable instructions + knowledge base | ✅ Excellent | adk-exp-v2, n8n-hybrid |
| Vertex AI (Gemini, Imagen, TTS, STT) | ✅ Excellent | VidGen, n8n-hybrid |
| Cloud Run deployment (source-based, secrets, IAM) | ✅ Excellent | n8n-hybrid |
| RAG pipeline (crawl, chunk, embed, store, retrieve) | ✅ Good | crawl4ai |
| File-based state management | ✅ Excellent | VidGen, crawl4ai |
| Multi-provider LLM factory (LangChain abstraction) | ✅ Good | crawl4ai |
| N8N gateway integration | ✅ Good | n8n-hybrid |
| Supabase session persistence for ADK | ✅ Good | n8n-hybrid |
| Sequential pipeline + approval gates | ✅ Excellent | VidGen |
| FastAPI as ADK gateway (`/run_agent`, session mgmt, event parsing, history) | ✅ Excellent | adk-wrapper-v2 |
| Streamlit auth (Supabase login gate, multi-page gatekeeper, logout) | ✅ Excellent | streamlit-v2 |
| Supabase user profiles (upsert, per-user JSON blob, session bookmarks) | ✅ Excellent | streamlit-v2 |
| Streamlit Cloud Run deployment (Procfile, st.secrets, Secret Manager) | ✅ Excellent | streamlit-v2 |
| Mission Control admin panel (live GCS prompt editing from browser UI) | ✅ Good | streamlit-v2 |
| Google managed RAG (File Search API — create, upload, query, delete) | ✅ Good | managed-rag-v1 |
| Managed vs DIY RAG trade-off (control vs simplicity) | ✅ Good | crawl4ai + managed-rag-v1 |
| PDF direct analysis via `types.Part.from_bytes` | ✅ Good | managed-rag-v1 |
| Dual-document RAG strategy (original + structured summary) | ✅ Good | managed-rag-v1 |

---

## Patterns Still Needed (Prioritized)

### Priority 1 — HIGH VALUE, NOT YET SEEN

**Testing patterns for ADK agents**
- VidGen had good pytest patterns (unit mocks + integration marks + conftest fixtures)
- Zero ADK repos had tests — we don't know how to mock ADK, test agent tools, or validate agent output
- Target repo: any project with pytest + ADK
- Would unlock: how to test `FunctionTool` functions, how to mock GCS, how to validate agent responses

### Priority 2 — IMPORTANT, PARTIALLY COVERED

**Authentication for Cloud Run services**
- All 4 repos use `--allow-unauthenticated` (public endpoints)
- Real production services need API key auth, Bearer token, or Cloud Run IAM invoker
- Target repo: any project with private Cloud Run + auth middleware in FastAPI
- Would unlock: FastAPI auth middleware patterns, `--no-allow-unauthenticated` + invoker SA

**Agent evaluation / quality measurement**
- No repo shows how to measure agent output quality, compliance rate, or tool usage correctness
- Target repo: any project with LangSmith, Braintrust, or custom eval harness
- Would unlock: eval loop patterns, ground truth datasets, scoring functions

### Priority 3 — NICE TO HAVE

**LangGraph agent orchestration**
- `langgraph` appeared as a dependency in crawl4ai but was never used
- Would provide: stateful agent graphs, conditional branching, human-in-the-loop patterns
- Target repo: any project that actively uses LangGraph

**Multi-tenant / multi-user patterns**
- All repos are single-user or use `user_id` strings without real auth
- Would provide: user isolation in ADK sessions, per-tenant GCS paths, billing separation

---

## Next Repo Candidates

| Repo Type | Gaps It Fills | Priority |
|-----------|--------------|----------|
| Any project with pytest + ADK agents | Testing patterns for AI apps | HIGH |
| Any project with FastAPI + auth middleware | Authentication patterns for Cloud Run | MEDIUM |
| Any project using LangGraph | Agent orchestration, stateful graphs | LOW |

---

## The End Goal

**Consolidation phase is ready.** 7 repos extracted. Core patterns covered. Google managed RAG reference now added.

1. **Consolidation phase** — all session files + all `/docs/` + Next.js reference manuals → synthesize into Python/ADK manuals
2. **Skill creation** — turn manuals into Claude skills (on-demand loading)
3. **Validation** — build a new app using ONLY the manuals, measure gaps

Optional before consolidation: testing patterns repo (pytest + ADK) would strengthen coverage but is not a blocker.

---

## Context on the Broader System (AI App Factory)

```
Architect Agents (chatbot mode)
    ↓
app_brief.md + ui_specs.md
    ↓
Designer Agent → Stitch designs
    ↓
Claude Code → Build frontend (already works well with Next.js docs)
    ↓
[Backend phase — needs Python/ADK manuals ← YOU ARE BUILDING THIS]
```

The manuals you're helping create will power the backend build phase of this factory.

---

## How to Read This Folder

**Recommended order:**
1. `MISSION_BRIEF.md` ← you are here
2. Latest session file (most recent date)
3. Previous session files (for cumulative patterns)
4. `/docs/` files if you need deep detail on a specific topic

Then: explore the current repo and start extracting.

---

_Last updated: 2026-02-23 (Repo #8 complete — crawl4ai-exp-project-v1 GHL chatbot)_
_Maintained by: Claude Code instances across sessions_
