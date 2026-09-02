# Session Log: 2026-02-23 — google-adk-wrapper-v2

**Agent:** Claude Code (Sonnet 4.6)
**Purpose:** Documentation Extraction — FastAPI ADK Wrapper Patterns
**Repo:** google-adk-wrapper-v2

---

## Session Context

### How I Was Loaded

User pointed me to `CLAUDE TRAINING GUIDES/MISSION_BRIEF.md` which provided full mission context. I also read the latest session file (`session-2026-02-23-google-adk-n8n-hybrid.md`) to understand what patterns had already been extracted.

This is **Repo #5** in the extraction mission. The mission brief listed this repo type as **HIGH PRIORITY** with the note: "FastAPI patterns — still needed (ADK Wrapper is the target)."

The n8n-hybrid session explicitly noted:
> "ADK Wrapper implementation — referenced in docs but the source isn't in this repo (it's a separate service). Would need to find that repo to extract the FastAPI pattern."

**This repo IS that service.**

---

## What This Repo Is

`google-adk-wrapper-v2` is a **stateless FastAPI middleware service** that acts as a gateway between any frontend (or N8N) and the ADK Agent Bundle (deployed separately on Cloud Run).

**The simplification it provides:**
- Input: `POST /run_agent { agent_name, message, user_id, session_id? }`
- Output: `{ response, session_id, agent_name, status }`

The wrapper handles everything in between: session creation, ADK API calls, event parsing, session 404 recovery, and history normalization.

---

## Files Read

- `main.py` — FastAPI app (all endpoints + helper functions)
- `main-org.py` — identical to main.py (backup copy, same content)
- `config.py` — environment-aware AGENT_REGISTRY builder
- `config.json` — active config (real Cloud Run URL, 5 agents)
- `config-org.json` — template config (placeholder URLs)
- `Dockerfile` — python:3.12-slim, shell form CMD
- `deploy.sh` — source-based Cloud Run deploy
- `start_cloud.sh` — local dev helper targeting cloud bundle
- `.gcloudignore` — excludes .venv, pycache, git, .env, *.json
- `requirements.txt` — fastapi, uvicorn, httpx, pydantic, streamlit
- `README.md` — brief (1 line)
- `deploy_docs/overview.md` — concierge metaphor, key responsibilities
- `deploy_docs/api-info.md` — endpoints + Python example code
- `deploy_docs/deployment.md` — deployment guide (corrected Dockerfile CMD)

---

## What Was Extracted (Docs Created)

```
docs/architecture.md           — System flow, two-service architecture, file structure, endpoints
docs/patterns.md               — 12 copy-pasteable patterns (run_agent, session, parsing, history, config)
docs/decisions.md              — 11 key decisions with rationale
docs/fastapi_adk_wrapper.md    — Deep-dive reference (ADK API contract, events format, session lifecycle)
session-2026-02-23-google-adk-wrapper-v2.md  — This file
```

---

## Key Patterns Discovered (Manual-Worthy)

### Pattern 1: The `/run_agent` Endpoint Shape

```
POST /run_agent
Input:  { agent_name, message, user_id, session_id? }
Output: { response, session_id, agent_name, status }
```

This is the canonical simple interface for talking to any ADK agent. `session_id` is optional on the first call; the wrapper creates one automatically.

**Manual topic:** "FastAPI ADK Wrapper — Core Endpoint"

---

### Pattern 2: ADK Event Parsing

ADK returns an `events[]` array from `/run`. To extract the final model response:
```python
for event in reversed(events):
    content = event.get("content")
    if content and content.get("role") == "model":
        for part in reversed(content["parts"]):
            if isinstance(part, dict) and "text" in part:
                return part["text"]
```

`reversed()` on both events and parts is essential — tool-use agents generate intermediate model events. The final text is always last.

**Manual topic:** "ADK Response Parsing"

---

### Pattern 3: Session 404 Auto-Recovery

```python
r = await _post_run(session_id)
if r.status_code == 404:
    new_session_id = await create_session(agent_url, user_id, app_name)
    r = await _post_run(new_session_id)
    return _parse_events(r.json()), new_session_id  # return NEW session_id
```

When ADK returns 404 (session expired or missing), create a fresh session and retry once. **Always return the effective session_id** so the caller can update their stored value.

**Manual topic:** "ADK Session Management + Expiry Recovery"

---

### Pattern 4: config.json Environment-Aware Registry

```json
{ "environments": { "local": {...}, "cloud": {...} }, "agents": [...] }
```

+ `APP_ENV` env var selects environment. All agents share one base URL (they're all in the same bundle). config.py builds `AGENT_REGISTRY = { agent_name: base_url }` at startup.

**Manual topic:** "Environment-Aware Configuration for FastAPI Services"

---

### Pattern 5: History Normalization

ADK events → clean `[{role, content}]` format:
- Filter for `author in ("USER", "MODEL")`
- Map `author` to `role`: `"USER" → "user"`, `"MODEL" → "assistant"`
- Extract first text part from each event

**Manual topic:** "ADK Session History Normalization"

---

### Pattern 6: Two-Service Architecture (Bundle + Wrapper)

The ADK bundle and the wrapper are separate Cloud Run services. Deploy order: bundle first (wrapper needs its URL). Bundle URL is injected as an env var at deploy time — not a secret, just configuration.

**Manual topic:** "ADK Two-Service Architecture"

---

### Pattern 7: APP_ENV Local/Cloud Toggle

Three development modes:
1. `APP_ENV=local` → localhost:8000 (full local)
2. `APP_ENV=cloud` + local uvicorn → live bundle (hybrid testing)
3. `APP_ENV=cloud` in Dockerfile → production

`start_cloud.sh` = one-command hybrid mode.

**Manual topic:** "Multi-Environment Development for ADK Apps"

---

## The Missing Piece — Now Found

The n8n-hybrid session (Repo #4) noted this gap:
> "ADK Wrapper implementation — referenced in docs but source isn't in this repo."

The call chain in n8n-hybrid was: `N8N → ADK Wrapper → ADK Bundle`

This repo IS the ADK Wrapper. With Repo #5 complete, the full call chain is documented across two repos:
- Repo #4 (n8n-hybrid): N8N workflow + ADK Bundle
- Repo #5 (this): FastAPI Wrapper between them

---

## Comparison to Previous Repos

| Aspect | VidGen | crawl4ai | adk-exp-v2 | n8n-hybrid | **This Repo** |
|--------|--------|----------|------------|------------|---------------|
| Type | Media pipeline | RAG pipeline | Patterns lab | Production bundle | API middleware |
| Deployment | Local | Local | Cloud Run | Cloud Run | Cloud Run |
| State | File-based | File-based | ADK in-mem | ADK+Supabase | None (stateless) |
| Framework | Streamlit | Python script | ADK native | ADK native | FastAPI |
| Secrets | .env | .env | .env | Secret Manager | None needed |
| Tests | pytest | None | None | None | None |
| Auth | None | None | None | None | None |

**Key jump this repo adds:** The only repo using FastAPI as an application framework. All previous repos either used Streamlit (VidGen) or ADK's built-in server. This is the pattern for building custom API layers.

---

## Confirmed Cross-Repo Patterns (Now 5 Repos)

Previously confirmed 11 patterns. Adding:

12. **FastAPI as ADK gateway** — `POST /run_agent` → session management → ADK `/run` → event parsing → clean response (this repo only, but it's the definitive pattern)
13. **`.org` file preservation** — `main-org.py` and `config-org.json` as backup before changes (seen in adk-exp-v2 + this repo)

Previously confirmed patterns status in this repo:
- Config-driven ✅ (`config.json` + `APP_ENV`)
- Optional AI components ✅ (session fallback if 404)
- `.gcloudignore` for secure source deploys ✅
- Shell form Dockerfile for `$PORT` ✅
- Per-agent module structure — N/A (this repo doesn't contain agents, only the wrapper)

---

## Bugs Found (Not Fixing — Extraction Only)

1. `requirements.txt` contains `streamlit==1.48.0` and related dependencies (numpy, pandas, pillow, etc.) that are not used by this FastAPI service. Dead weight from a previous project or template.

2. `deploy.sh` has `ADK_BUNDLE_URL` hardcoded with the actual production URL (not a placeholder). This is fine for the user's own use but the template (`config-org.json`) shows the correct approach: use a placeholder.

3. `main-org.py` is identical to `main.py`. This makes sense if it's a preservation copy, but if it's supposed to be the "before refactor" version, the two files are out of sync in their usefulness. Low priority.

---

## Gaps / Not Yet Documented

1. **Authentication** — still `--allow-unauthenticated`. The mission brief noted this as Priority 2. This repo doesn't add patterns beyond what n8n-hybrid showed.
2. **Streaming responses** — `/run_sse` endpoint is mentioned in decisions but not implemented here. Would be needed for typing-effect chat UIs.
3. **Testing patterns** — no tests in this repo. Same gap as Repos 2, 3, 4. VidGen (Repo 1) is still the only repo with tests.
4. **Multi-tenant** — `user_id` is used for separation but there's no auth enforcing it.

---

## Key Insights for Manual Creation

### For "FastAPI ADK Wrapper Manual":
- Full endpoint shapes (request/response) for `/run_agent`, `/get_history`, `/health`
- ADK events array structure and parsing algorithm
- Session creation URL format
- Session 404 auto-recovery pattern
- `config.json` + `config.py` pattern for agent registry
- Two-service deployment (bundle + wrapper)

### For "ADK API Reference Manual":
- ADK's internal API contract: `POST /run`, `POST /apps/.../sessions/...`, `GET /apps/.../sessions/...`
- Events array structure (role, parts, author fields)
- `app_name` = the agent name in ADK directory structure

### For "Python App Architecture Manual":
- Stateless middleware pattern (FastAPI with no DB)
- `APP_ENV` toggle for local/cloud targeting
- Shell form Dockerfile CMD for `$PORT` substitution (confirmed again)

---

## Status: MISSION COMPLETE for FastAPI ADK Wrapper

The mission brief stated:
> "The FastAPI Wrapper repo is the one remaining high-value extraction before consolidation makes sense."

This extraction fills the Priority 1 gap. The brief's "What's Covered" table can now be updated:

| Topic | Coverage | Source Repos |
|-------|----------|-------------|
| FastAPI as ADK gateway | ✅ Complete | **this repo** |

---

## Recommended Next Steps

Per the mission brief, with the FastAPI ADK Wrapper now documented:

1. **Consolidation phase is ready** — sufficient pattern depth across 5 repos
2. Sources for consolidation:
   - All 5 session files
   - All `/docs/` folders from each repo
   - `CLAUDE TRAINING GUIDES/docs/` (cross-repo deep dives)
3. Output: Python/ADK Manuals (architecture, patterns, decisions, integrations)
4. Then: Validate manuals by building a new app from scratch using only the manuals

---

## Files Created This Session

```
docs/architecture.md              — System flow, two-service architecture, file structure
docs/patterns.md                  — 12 patterns (run_agent, session, parsing, history, config, deploy)
docs/decisions.md                 — 11 decisions with rationale
docs/fastapi_adk_wrapper.md       — Deep-dive (ADK API contract, events, session lifecycle, comparison)
session-2026-02-23-google-adk-wrapper-v2.md  — This file
```

---

_Session Status: Complete_
_Docs Created: 5 files_
_Last Updated: 2026-02-23_
