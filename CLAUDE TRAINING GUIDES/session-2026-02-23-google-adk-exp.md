# Session Log: 2026-02-23 — google-adk-exp-v2

**Agent:** Claude Code (Sonnet 4.6)
**Purpose:** Documentation Extraction — ADK Agent Patterns
**Repo:** google-adk-exp-v2

---

## Session Context

### How I Was Loaded

User pointed me to `CLAUDE TRAINING GUIDES/` folder containing:
- `MISSION_BRIEF.md` — full mission context (AI App Factory, extraction agent role)
- `session-2026-02-22.md` — VidGen extraction session
- `session-2026-02-23-crawl4ai-rag.md` — crawl4ai RAG extraction session
- `docs/` — VidGen extraction docs (architecture, patterns, decisions, Vertex AI, testing)

This is Repo #3 in the extraction mission. The previous two repos confirmed 8 cross-repo patterns. **ADK agent patterns were identified as the #1 gap** — no ADK repo had been seen yet. This repo fills that gap entirely.

### What This Repo Is

`google-adk-exp-v2` is an **ADK patterns laboratory**. Not a single production app — a curated collection of working agent examples covering every major ADK primitive:

1. `greeting_agent` — Baseline simple agent (inline instruction)
2. `calc_agent` — Agent with `BuiltInCodeExecutor` + GCS callable instructions
3. `jarvis_agent` — Agent with `google_search` + GCS callable instructions
4. `travel_agent` — `SequentialAgent` pipeline with `output_key` + template variables
5. `parallel_agent` — `ParallelAgent` for concurrent execution
6. `combo_agent` — Complex: `Agent(AgentTool(SequentialAgent(ParallelAgent, Synth)))`
7. `focus_group_agent` — 7-persona `ParallelAgent` + `FunctionTool` file output
8. `ghl_mcp_agent` — `MCPToolset` + `LiteLlm` for non-Gemini models + CRM integration

**Value:** The complete ADK cookbook.

---

## Session Progress

### [Start] — Repo Exploration

**Files read:**
- All 8 `agent.py` files (all agent types)
- All `.org.py` and `_gcs.py` variants (evolution comparison)
- `utils/gcs_utils.py` — GCS instructions pattern
- `utils/context_utils.py` — GCS context store pattern
- `utils/focus_group_utils.py` — FunctionTool file output pattern
- `Dockerfile` — Cloud Run deployment
- `deploy.sh`, `deploy-org.sh`, `deploy-w-docker.sh` — three deployment approaches
- `requirements.txt` — full dependency picture
- `.env_example` — minimal config (2 vars)
- `README.md` — minimal (just a title line)

**Key insight immediately:** This is precisely the ADK patterns gap identified in previous sessions. Every pattern needed for an ADK manual is here.

---

### [Extraction] — Docs Created

**4 docs created in `/docs/`:**

1. **`docs/architecture.md`**
   - Full agent inventory (8 agents, types, tools, key patterns)
   - Flow diagrams for each agent topology
   - GCS live instructions architecture
   - Deployment architecture (two paths)
   - Module entry point pattern

2. **`docs/patterns.md`**
   - 15 copy-pasteable patterns
   - Every ADK agent type (Agent, Sequential, Parallel, Combo, MCP, LiteLlm)
   - GCS live instructions (both callable and startup-cached variants)
   - FunctionTool with JSON output
   - Dockerfile for Cloud Run
   - `output_key` convention

3. **`docs/decisions.md`**
   - 12 key decisions documented
   - Each with context, decision, rationale, alternatives rejected
   - Notable: callable vs cached instruction is Decision #3 (very high leverage)

4. **`docs/adk_integration.md`**
   - Complete ADK reference guide
   - All agent types with full constructor signatures
   - All tool types with usage examples
   - Session context and `output_key` mechanics
   - Instruction patterns (3 variants)
   - Local development (`adk web`, `adk run`, `adk api_server`)
   - Cloud Run deployment (both methods)
   - LiteLlm integration for non-Gemini models
   - Known issues / gotchas (6 documented)
   - ADK vs direct Vertex AI comparison table
   - N8N integration pattern

---

## Key Patterns Discovered (Manual-Worthy)

### Pattern 1: The ADK Agent Constructor

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="agent_name",         # underscore format
    model="gemini-2.5-flash",  # or LiteLlm instance
    description="What it does",
    instruction="...",         # string or callable
    tools=[],                  # FunctionTool, google_search, AgentTool, MCPToolset
    output_key="key",          # saves output to session context
    code_executor=...,         # BuiltInCodeExecutor (NOT in tools=[])
)
```

This is the atom of ADK. Everything builds on this.

---

### Pattern 2: The Three Orchestrator Patterns

```python
# Sequential: stage 1 → stage 2 → stage 3
root_agent = SequentialAgent(sub_agents=[a, b, c])

# Parallel: all run concurrently
root_agent = ParallelAgent(sub_agents=[a, b, c])

# Hybrid: chatbot delegates to workflow on demand
root_agent = Agent(tools=[AgentTool(agent=SequentialAgent(sub_agents=[ParallelAgent(...), synth]))])
```

Three fundamental topologies. Real apps combine them.

---

### Pattern 3: `output_key` + Template Variables (Data Flow)

```python
stage_one = Agent(output_key="ideas")
stage_two = Agent(instruction="Review: {ideas}")  # ADK substitutes from context
```

The `{key}` → `output_key` binding is how inter-agent data flows in ADK. Learn this first.

---

### Pattern 4: Callable Instruction (Hot-Reload)

```python
def get_instructions(ctx): return fetch_from_gcs("agent_name")
agent = Agent(instruction=get_instructions)  # NOT instruction=get_instructions()
```

This one pattern eliminates an entire class of redeployments. Very high leverage.

---

### Pattern 5: LiteLlm for Model Flexibility

```python
from google.adk.models.lite_llm import LiteLlm
model = LiteLlm(model="openrouter/openai/gpt-4o", api_key=os.getenv("OPENROUTER_API_KEY"))
agent = Agent(model=model)
```

ADK isn't Gemini-only. LiteLlm makes it model-agnostic. Critical for production where model choice matters.

---

### Pattern 6: MCPToolset for External Services

```python
tools=[MCPToolset(connection_params=StreamableHTTPConnectionParams(url="...", headers={...}))]
```

Any service with an MCP endpoint = one pattern for all. GHL CRM, internal tools, anything.

---

### Pattern 7: FunctionTool JSON Output Pattern

```python
def write_output(data: str, filename: str = "results.json"):
    """Writes data to JSON file. ..."""
    try: data_obj = json.loads(data)
    except json.JSONDecodeError: data_obj = {"raw_output": data}  # graceful fallback
    ...
    return f"Wrote to {path}"
```

Always handle JSON decode errors — LLMs occasionally return slightly malformed JSON.

---

### Pattern 8: GCS as Agent Knowledge Base

```
GCS_BUCKET/ADK_Agent_Bundle_1/
├── agent_name/agent_name_instructions.txt  ← per-agent prompts
└── context_store/document.txt              ← knowledge base docs
```

Two-tier GCS structure: instructions (hot-reloaded per run) + knowledge base (read on demand by FunctionTool).

---

## Agent Evolution (Versions in Codebase)

Each agent has multiple versions showing the evolution:

| File Pattern | What It Represents |
|--------------|-------------------|
| `agent.org.py` | Original scaffold (hardcoded instruction) |
| `agent.gc_bucket.py` | GCS instruction loaded at startup (cached) |
| `agent_gcs.py` | GCS callable instruction (hot-reloadable) |
| `agent.py` | Current best version |

**Lesson:** The evolution path is `hardcoded → GCS cached → GCS callable`. Each step improves operability. The callable pattern is the target state.

---

## Observations vs Previous Repos

| Aspect | VidGen | crawl4ai-exp | google-adk-exp-v2 |
|--------|--------|--------------|-------------------|
| Framework | Direct Vertex AI | LangChain | Google ADK |
| State | File-based | File-based | ADK session context |
| Multi-agent | No | No | Yes (native) |
| Tools | Custom functions | LangChain tools | ADK tools + MCP |
| LLM provider | Gemini only | Multi-provider | Gemini + LiteLlm |
| Deployment | Streamlit | Not deployed | Cloud Run |
| Config | JSON config | site_config.json | .env (minimal) |
| Instruction storage | Hardcoded | Hardcoded | GCS (hot-reloadable) |
| Tests | pytest | None | None |

**Key difference from previous repos:** ADK manages session state natively — no file-based state needed for inter-agent communication. `output_key` + template variables = ADK's version of the file-based state pattern, but in-memory and typed.

---

## What's Confirmed Cross-Repo (Now 3 Repos)

All 8 previously confirmed patterns still hold (file-based state, sequential stages, config-driven, optional AI, confirmation gates, Rich output, Path objects, per-project folders). Plus new ADK-specific confirmations:

1. **Callable instruction pattern** — appears in calc_agent, jarvis_agent, ghl_mcp_agent, greeting_agent GCS variants
2. **GCS for hot-reloadable prompts** — appears in 4 different agents
3. **`output_key` for data flow** — core to every multi-agent pattern

---

## Gaps / Not Yet Built

1. **Tests** — no test files anywhere in the repo
2. **Error handling in agents** — no try/catch in agent.py files (relies on ADK)
3. **N8N integration** — JSON file exists but pattern not fully documented
4. **ghl_mcp_agent typo** — `"openrcouter/..."` should be `"openrouter/..."` (live bug)
5. **Cloud Run auth** — `--allow-unauthenticated` in deploy.sh (fine for internal tools, risky for production)
6. **No ADK evaluation** — no agent output quality testing

---

## Bugs Found (Not Fixing — Extraction Only)

1. `ghl_mcp_agent/agent.py:14` — `"openrcouter/openai/gpt-5"` typo in model ID
2. `deploy-w-docker.sh:15` — hardcoded API key in deploy script (`--set-env-vars="GOOGLE_API_KEY=AIza..."`) — should be env var reference, not value

---

## Files Created This Session

```
docs/architecture.md          — Agent inventory, flow diagrams, GCS architecture
docs/patterns.md              — 15 copy-pasteable ADK patterns
docs/decisions.md             — 12 key decisions with rationale
docs/adk_integration.md       — Complete ADK reference guide
session-2026-02-23-google-adk-exp.md  — This file
```

---

## Key Insights for Manual Creation

### For "ADK Agent Manual" (PRIMARY deliverable from this session):
- All constructor signatures for Agent, SequentialAgent, ParallelAgent
- `output_key` + template variable data flow
- Three orchestration topologies (Sequential, Parallel, Hybrid/Combo)
- Callable instruction = hot-reloadable prompts
- Tool types: FunctionTool, AgentTool, MCPToolset, google_search, BuiltInCodeExecutor
- Module structure: one folder per agent, `__init__.py` exports `root_agent`
- 6 gotchas (code_executor parameter, callable vs cached, no model on orchestrators, etc.)

### For "GCS Live Context Manual":
- Two-tier GCS structure (instructions + knowledge base)
- Callable instruction pattern
- FunctionTool for on-demand doc retrieval
- ADK uses ADC automatically in Cloud Run — no credential management needed

### For "LiteLlm / Multi-Model Manual":
- `LiteLlm` class wraps any LiteLlm-supported model
- Pass `model=LiteLlm(...)` instead of `model="gemini-..."`
- OpenRouter as unified gateway for GPT, Claude, etc.

### For "Cloud Run Deployment Manual":
- Two paths: gcloud (Dockerfile) vs `adk deploy cloud_run`
- Always use `$PORT` in Dockerfile CMD
- `--with_ui` flag for ADK native deploy includes web UI
- ADC works automatically in Cloud Run (no key management for GCS/Vertex)

### For "Python App Architecture Manual":
- ADK session context = evolved version of file-based state for agent pipelines
- Each agent is stateless — state lives in ADK session, not agent code
- `__init__.py` convention is ADK's discovery mechanism

---

## Quotes / Notable Observations

The evolution files (`agent.org.py` → `agent.gc_bucket.py` → `agent_gcs.py` → `agent.py`) are a rare find — they show the exact learning journey from hardcoded → GCS cached → GCS callable. This is unusual to find preserved in a repo and is highly valuable for the manual (shows not just the pattern but why each step is an improvement).

The ghl_mcp_agent is the most sophisticated agent in the repo — it combines three non-trivial patterns: LiteLlm (non-Gemini model), MCPToolset (external service integration), and callable instruction (dynamic prompt). Any production CRM/ERP integration would follow this exact shape.

---

## Next Steps

1. **Copy docs + session files to next repo's CLAUDE TRAINING GUIDES**
2. **Next repo to extract** — user to provide
3. **Pattern accumulation:** 3 repos done, 3-5 more before consolidation
4. **After 5-6 repos:** Begin manual synthesis phase

### Patterns Still Needed (Updated):
- ~~ADK agent patterns~~ ✅ DONE (this repo)
- FastAPI patterns (no API server repo yet)
- Testing patterns for AI apps (VidGen had it, crawl4ai and ADK didn't)
- LangGraph / agent orchestration
- Cloud Run deployment (partially covered — need more depth on auth, secrets)
- Authentication patterns
- Agent evaluation frameworks

---

_Session Status: Complete_
_Docs Created: 5 files_
_Last Updated: 2026-02-23_
