# Session Log: 2026-02-23 — google-adk-n8n-hybrid-v2

**Agent:** Claude Code (Sonnet 4.6)
**Purpose:** Documentation Extraction — N8N + Cloud Run Production Patterns
**Repo:** google-adk-n8n-hybrid-v2

---

## Session Context

### How I Was Loaded

User pointed me to `CLAUDE TRAINING GUIDES/` folder containing:
- `MISSION_BRIEF.md` — full mission context
- `session-2026-02-22.md` — VidGen extraction
- `session-2026-02-23-crawl4ai-rag.md` — crawl4ai RAG extraction
- `session-2026-02-23-google-adk-exp.md` — google-adk-exp-v2 ADK patterns lab
- `docs/` — VidGen extraction docs

This is **Repo #4** in the extraction mission. Previous repos confirmed 8 cross-repo patterns and fully covered ADK agent patterns. **This repo fills the N8N integration gap and provides the production Cloud Run deployment template.**

### What This Repo Is

`google-adk-n8n-hybrid-v2` is a **production ADK multi-agent bundle** — 5 specialized agents deployed to Google Cloud Run, fronted by an N8N workflow and a FastAPI wrapper.

This is the most mature repo in the extraction sequence:
- VidGen = local desktop tool
- crawl4ai = local pipeline
- google-adk-exp-v2 = patterns laboratory
- **This repo = production deployed service** ← qualitative jump

---

## Files Read

- `README.md`
- `requirements.txt`
- `Dockerfile` + `Dockerfile.old`
- `.env_example`
- `.gcloudignore`
- `deploy.sh`, `store_secrets.sh`, `grant_permissions.sh`, `start_server.sh`
- `greeting_agent/agent.py`, `greeting_agent/__init__.py`
- `calc_agent/agent.py`
- `jarvis_agent/agent.py`
- `product_agent/agent.py`
- `ghl_mcp_agent/agent.py`
- `utils/gcs_utils.py`
- `utils/context_utils.py`
- `docs/overview.md`, `docs/deployment.md`, `docs/api-info.md`
- `Adk_N8N_Hybrid_v4.json`

---

## What Was Extracted (Docs Created)

```
docs/architecture.md         — 5-agent system, N8N flow, GCS knowledge base, deployment architecture
docs/patterns.md             — 13 copy-pasteable patterns (N8N, deploy scripts, Dockerfile, Secret Manager)
docs/decisions.md            — 10 key decisions with rationale
docs/n8n_and_deployment.md   — Deep-dive on N8N workflow + Cloud Run deployment (complete reference)
session-2026-02-23-google-adk-n8n-hybrid.md  — This file
```

---

## Key Patterns Discovered (Manual-Worthy)

### Pattern 1: N8N 4-Node Gateway Workflow

```
Webhook → Code(normalize) → HTTP Request → Code(package) → Respond
```

The exact pattern for connecting any N8N workflow to an ADK backend. The `Adk_N8N_Hybrid_v4.json` is importable directly to N8N. Key insights:
- `responseMode: responseNode` on Webhook is required for async response
- Timeout must be 90000ms+ (LLM calls are slow)
- Code Node 1 normalizes N8N's `.body` wrapping
- Code Node 2 JSON.stringifies to handle special chars in agent output
- `session_id` is passed through the entire chain for conversation continuity

**Manual topic:** "N8N + ADK Integration Pattern"

---

### Pattern 2: Three-Script Production Deployment

```
grant_permissions.sh   → IAM setup (one-time)
store_secrets.sh       → .env → Secret Manager (when secrets change)
deploy.sh              → source → Cloud Build → Cloud Run (every deploy)
```

This is the complete production lifecycle. The most common mistake: forgetting to update Secret Manager when secrets change, then deploying with stale values.

**Manual topic:** "Cloud Run Deployment Lifecycle for ADK"

---

### Pattern 3: Dockerfile Shell Form for $PORT

```dockerfile
# ✅ Correct — shell substitutes $PORT at runtime
CMD adk api_server . --host=0.0.0.0 --port=${PORT} --session_service_uri=${DB_URI}

# ❌ Wrong — exec form, $PORT treated as literal string
CMD ["adk", "api_server", ".", "--port=${PORT}"]
```

This is a gotcha that would cause silent failure (port mismatch, container doesn't start). The Dockerfile.old has the wrong form — the user apparently hit this bug and fixed it.

**Manual topic:** "Cloud Run Dockerfile Patterns + Gotchas"

---

### Pattern 4: Supabase for ADK Session Persistence

```bash
adk api_server . --session_service_uri="postgresql://..."
```

One flag turns ephemeral in-memory sessions into cross-restart persistent sessions. Without this, Cloud Run's scale-to-zero behavior loses all conversation history. This is essential for production — users expect memory.

**Manual topic:** "ADK Session Persistence Options"

---

### Pattern 5: .gcloudignore for Secure Source Deploys

```
.venv/          # gigabytes — would time out upload
.env            # secrets — NEVER upload to Cloud Build
*.json          # service account keys — NEVER upload
```

Without this file, `gcloud run deploy --source .` would upload secrets and your entire virtualenv to Cloud Storage. This is a critical security and performance concern.

**Manual topic:** "Secure Cloud Run Source Deployment"

---

### Pattern 6: GOOGLE_GENAI_USE_VERTEXAI Toggle

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE + GOOGLE_API_KEY    ← local dev (API key mode)
GOOGLE_GENAI_USE_VERTEXAI=TRUE + service account    ← production (Vertex mode)
```

Same agent code works in both modes. The env var determines which Google backend is used. Cloud Run always uses `TRUE` + service account (no key management needed).

**Manual topic:** "ADK Vertex vs API Key Modes"

---

### Pattern 7: GCS Two-Tier Structure

```
bucket/bundle/
├── {agent_name}/{agent_name}_instructions.txt    ← hot-reload per run (callable instruction)
└── context_store/*.md                            ← on-demand by FunctionTool
```

Instructions are fetched by the framework on every call. Context docs are fetched by the agent only when it needs them (LLM decides when to call the FunctionTool). This separation reduces latency — only one GCS call is guaranteed (instructions); context fetches are on-demand.

**Manual topic:** "GCS Knowledge Base Architecture for ADK"

---

### Pattern 8: Secret Manager --set-secrets Injection

```bash
--set-secrets="DB_URI=adk-db-uri:latest,TOKEN=my-token:latest"
```

Format: `ENV_VAR_NAME=secret-manager-name:version`

The container sees them as normal env vars. Secret values never appear in deploy commands, logs, or Cloud Run console. This is the correct pattern for all production credentials.

**Manual topic:** "Secret Manager for Cloud Run"

---

## Observations vs Previous Repos

| Aspect | VidGen | crawl4ai | adk-exp-v2 | **This Repo** |
|--------|--------|----------|------------|---------------|
| Deployment | Local | Local | Cloud Run | Cloud Run (prod) |
| State | File-based | File-based | ADK session (in-mem) | ADK session (Supabase) |
| Secrets | .env | .env | .env | Secret Manager |
| Instruction storage | Hardcoded | Hardcoded | GCS (callable) | GCS (callable) |
| Frontend gateway | Streamlit | None | adk web | N8N + FastAPI wrapper |
| Model vendor | Vertex only | Multi-provider | Vertex + LiteLlm | Vertex only |
| Tests | pytest | None | None | None |

**Key jump:** This is the only repo with real secrets management (Secret Manager) and persistent sessions (Supabase). Everything else ran locally or in-memory. This is what "production" looks like.

---

## Confirmed Cross-Repo Patterns (Now 4 Repos)

All 8 previously confirmed patterns remain relevant, though some manifest differently at production scale:

1. **File-based state** — Not applicable here (ADK session context replaces it)
2. **Sequential stages** — Not applicable (agent is stateless, session = state)
3. **Config-driven** — YES (GOOGLE_GENAI_USE_VERTEXAI, model string, GCS bucket)
4. **Optional AI components** — YES (fallback instruction string if GCS fails)
5. **Confirmation gates** — N/A (agent-based, not pipeline)
6. **Rich terminal output** — Not used (pure ADK + print statements)
7. **Path objects** — N/A (no file system state)
8. **Per-project output folders** — N/A (Supabase handles per-user separation)

**New pattern confirmed across 2 repos (adk-exp-v2 + this):**
- **GCS callable instruction** — appeared in both repos as the hot-reload pattern
- **ADK module structure** — `agent.py` + `__init__.py` per agent
- **Vertex AI as single vendor** — both repos converge on all-Vertex after experimenting with alternatives

---

## Bugs Found (Not Fixing — Extraction Only)

1. `utils/gcs_utils.py:5` — `BUCKET_NAME` is hardcoded as a string literal. Should come from `os.getenv("GCS_BUCKET_NAME")` since deploy.sh sets `GCS_BUCKET_NAME` as an env var.
2. `deploy.sh:8` — `GCS_BUCKET_NAME="your-agent-instructions-bucket-name"` — placeholder value not filled in.
3. No tests in this repo (consistent with adk-exp-v2 and crawl4ai, but VidGen had them).

---

## Gaps / Not Yet Fully Documented

1. **ADK Wrapper implementation** — referenced in docs but the source isn't in this repo (it's a separate service). Would need to find that repo to extract the FastAPI pattern.
2. **N8N authentication** — the webhook URL has no auth. How external clients authenticate is not documented.
3. **Supabase schema** — ADK creates its own tables, but the schema isn't documented.
4. **Multi-session management** — how does the client know when to start a new session vs. continue one?
5. **Agent evaluation** — no testing patterns for agent output quality.

---

## Key Insights for Manual Creation

### For "Cloud Run Deployment Manual":
- Three-script lifecycle (permissions → secrets → deploy)
- `.gcloudignore` is non-negotiable
- Shell form Dockerfile for env var substitution
- `--set-secrets` format for Secret Manager injection
- Source-based deploy (`--source .`) vs Docker-build deploy
- `GOOGLE_GENAI_USE_VERTEXAI` toggle for dev/prod mode

### For "ADK Session Persistence Manual":
- `--session_service_uri` with Postgres URI
- Supabase as the easiest option (managed, free tier)
- Session ID lifecycle (create → pass through → reuse)
- In-memory default is NOT suitable for production

### For "N8N + ADK Integration Manual":
- 4-node workflow pattern
- `responseMode: responseNode` required
- 90s timeout minimum
- Data contract: `{agent_name, message, user_id, session_id}` → `{response, session_id}`
- JSON.stringify for special character safety

### For "GCS Live Context Manual":
- Two-tier structure (instructions vs context_store)
- Callable instruction = fetched fresh per run
- FunctionTool docstring = LLM's instructions for when/how to call
- Consistent naming: `{agent_name}/{agent_name}_instructions.txt`

### For "Python App Architecture Manual":
- ADK bundle = one Cloud Run service = all agents accessible
- `adk api_server .` discovers agents by scanning for `__init__.py` with `root_agent`
- FastAPI wrapper abstracts ADK session complexity for upstream callers

---

## Quotes / Notable Observations

From the README:
> "Because, all other models w/ OpenRouter simply sux!"

This is the clearest statement of the vendor consolidation decision seen in any repo. After experimenting with multi-provider in adk-exp-v2, the production system went all-Vertex. Reliability > flexibility for production.

The `Dockerfile` vs `Dockerfile.old` pair is again valuable (like the `.org.py` files in adk-exp-v2) — they show a real bug that was hit and fixed. Shell form vs exec form for `CMD` is a subtle Docker gotcha that affects many deployments.

---

## Next Steps

1. **Find the ADK Wrapper repo** — the FastAPI service between N8N and ADK is a missing pattern
2. **Pattern accumulation:** 4 repos done, 2-4 more before consolidation
3. **Updated gaps list:**
   - ~~ADK agent patterns~~ ✅ DONE (adk-exp-v2)
   - ~~N8N integration~~ ✅ DONE (this repo)
   - ~~Cloud Run deployment~~ ✅ DONE (this repo — well covered)
   - ~~Secret Manager patterns~~ ✅ DONE (this repo)
   - **FastAPI patterns** — still needed (ADK Wrapper is the target)
   - **Testing patterns** — only VidGen had them
   - **Agent evaluation frameworks** — not seen yet
   - **LangGraph** — dependency seen, never used
   - **Authentication patterns** — `--allow-unauthenticated` is a placeholder

---

## Files Created This Session

```
docs/architecture.md               — 5-agent system, N8N flow, GCS architecture
docs/patterns.md                   — 13 patterns (N8N, deploy, Dockerfile, Secret Manager)
docs/decisions.md                  — 10 decisions with rationale
docs/n8n_and_deployment.md         — Deep-dive on N8N + Cloud Run deployment
session-2026-02-23-google-adk-n8n-hybrid.md  — This file
```

---

_Session Status: Complete_
_Docs Created: 5 files_
_Last Updated: 2026-02-23_
