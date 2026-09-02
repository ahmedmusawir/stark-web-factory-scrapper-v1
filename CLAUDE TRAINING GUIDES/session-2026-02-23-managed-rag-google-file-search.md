# Session Log: 2026-02-23 — managed-rag-google-file-search-api-v1

**Agent:** Claude Code (Sonnet 4.6)
**Purpose:** Documentation Extraction — Google Managed RAG Patterns
**Repo type:** Basic/learning prototype (user used to learn File Search API)

---

## Session Context

### How I Was Loaded

User provided `CLAUDE TRAINING GUIDES/` folder with MISSION_BRIEF.md (updated through Repo #6) and all 6 previous session files. Fully operational from start.

### What This Repo Is

`managed-rag-google-file-search-api-v1` is a **Google Managed RAG tutorial project** — 6 progressive lessons that teach the complete lifecycle of Google's File Search API.

User's framing: "this is working example we will need it later" — suggests this is foundational knowledge for future repos that will use managed RAG.

**Key distinction from crawl4ai (Repo #2):**
- crawl4ai = DIY RAG (LangChain + Chroma + your own embeddings)
- This = **Google Managed RAG** (upload → Google handles everything)

---

## Files Read

- `src/lesson_1_check_api.py` — API availability check
- `src/lesson_2_create_store.py` — Store creation
- `src/lesson_3_upload_file.py` — Async upload with polling
- `src/lesson_4_query.py` — Batch test queries
- `src/lesson_5_create_summary.py` — PDF → structured summary
- `src/lesson_6_universal_summary.py` — Universal summary prompt
- `src/query_interactive.py` — Interactive chat loop
- `src/check_store.py` — Store inspection
- `src/verify_store.py` — Account-wide store list
- `src/cleanup_store.py` — Document deletion (force flag discovery)
- `src/test_gemini.py` — Vertex AI model test
- `src/test_auth.py` — Vertex AI auth test
- `src/utils/cost_calculator.py` — Cost estimation utility
- `src/_old/ingest.py` — Old deprecated API surface
- `src/_old/check_files_api.py` — API exploration
- `requirements.txt` — Dependency list
- `store_name.txt` — Persisted store ID
- `.gitignore` — Project config

---

## Docs Created

```
docs/architecture.md                                ← System flow, file structure, two auth modes, API evolution
docs/patterns.md                                    ← 12 copy-pasteable patterns
docs/decisions.md                                   ← 9 key decisions with rationale
docs/google_file_search_api.md                      ← Full API deep-dive (lifecycle, gotchas, cost, comparisons)
session-2026-02-23-managed-rag-google-file-search.md ← This file
```

---

## Key Patterns Discovered (Manual-Worthy)

### Pattern 1: Google File Search API — Core Lifecycle

Four operations, all extremely simple:

```python
# Create store
store = client.file_search_stores.create(config={'display_name': 'My-Store'})

# Upload (async — must poll)
operation = client.file_search_stores.upload_to_file_search_store(
    file=str(file_path),
    file_search_store_name=store.name,
)
while not operation.done:
    time.sleep(1)
    operation = client.operations.get(operation)

# Query (implicit retrieval — Gemini decides what to search)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=question,
    config=types.GenerateContentConfig(
        tools=[types.Tool(file_search=types.FileSearch(
            file_search_store_names=[store.name]
        ))]
    )
)

# Delete (MUST use force=True)
client.file_search_stores.documents.delete(name=doc.name, config={'force': True})
```

**For the manual:** This is the simplest possible RAG implementation. No embeddings, no vector store, no chunking config — just upload and query.

---

### Pattern 2: store_name.txt — Another File-Based State Confirmation

`store_name.txt` stores `fileSearchStores/storename-hash` — the resource path.

Every subsequent script reads it with `f.read().strip()`.

This is the 3rd repo to confirm file-based state as a cross-repo Python AI pattern (VidGen, crawl4ai, this).

---

### Pattern 3: config={'force': True} — Critical Delete Flag

```python
client.file_search_stores.documents.delete(
    name=doc.name,
    config={'force': True}  # ← Without this, deletion FAILS for chunked docs
)
```

Visible in code as `# ✅ FIXED` comment — this was a discovered bug, not known upfront.

**For the manual:** Always document this. Anyone building a "manage your documents" UI will hit this.

---

### Pattern 4: PDF Direct Analysis via bytes

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
        "Your prompt"   # ← plain string, not a Part object
    ]
)
```

**For the manual:** Gemini can read full PDFs directly without upload. Combine this with File Search to do "pre-process full doc → upload summary → query summary" pattern.

---

### Pattern 5: Summary + Original = Better RAG Quality

The most insightful technique in this repo:

**Problem:** RAG chunking breaks counting questions. "How many companies worked for?" — answer is spread across 9 chunks.

**Solution:**
1. Send full PDF to Gemini → generate structured summary listing ALL entities
2. Upload summary as a separate file alongside original
3. Now the store has two representations: detail (original) + enumeration (summary)
4. Gemini retrieves from both → accurate answers for both detail and counting questions

**For the manual:** Document this as "dual-document RAG strategy" — standard doc + structured summary.

---

### Pattern 6: API Key vs Vertex AI — Same Interface

```python
# Both produce identical client interface:
client = genai.Client(api_key="...")          # personal/dev
client = genai.Client(vertexai=True, ...)    # production/enterprise
```

**For the manual:** Confirm the pattern that all repos converge on Vertex AI in production, but API key is valid for development/tutorials.

---

### Pattern 7: Universal Summary Prompt Template

This prompt (from Lesson 6) works for ANY document type:

```
1. DOCUMENT TYPE
2. MAIN TOPICS (3-5)
3. KEY ENTITIES - ALL: people, companies, dates, numbers
4. MAIN POINTS (bullet points)
5. SEARCHABLE KEYWORDS

Be EXHAUSTIVE with entities. This will be used for search.
```

**For the manual:** A "ready to copy" pre-processing prompt for document ingestion pipelines.

---

## Critical Gotchas (Must Be in Manual)

1. **`force=True` for delete** — always required, no exceptions
2. **SDK API changed** — `client.files.*` is old/broken, `client.file_search_stores.*` is current
3. **Store name is a resource path** — `fileSearchStores/name-hash`, not a plain string
4. **Upload is async** — must poll `operation.done` loop
5. **Retrieval is implicit** — no explicit retriever call; Gemini decides internally

---

## Observations vs Previous Repos

### vs crawl4ai (Repo #2) — the closest comparison

| Aspect | crawl4ai (DIY RAG) | This (Managed RAG) |
|--------|-------------------|--------------------|
| Setup complexity | High (Chroma, embeddings, chunking) | Minimal |
| Control | Full (chunk_size, model, MMR vs similarity) | None |
| Vendor | Provider-agnostic (LangChain) | Google-only |
| State file | `site_config.json` | `store_name.txt` |
| Retrieval call | `retriever.invoke(query)` | Implicit (Gemini tool) |
| Citation info | Not built-in | `grounding_metadata` |

**Insight:** These two repos together give complete RAG coverage — DIY for control, managed for speed.

### vs All Repos — New Patterns

1. **Managed cloud service as RAG backend** — first repo to show this pattern
2. **Async operation polling** — new pattern (not seen in other repos)
3. **PDF direct analysis** — `types.Part.from_bytes` not seen before
4. **Dual-document strategy** — summary + original for better quality
5. **`grounding_metadata` for citations** — new pattern for understanding retrieval

---

## Gaps / Not Yet Built

1. **Vertex AI auth for File Search** — test scripts show Vertex AI works for generate_content, but File Search lessons use API key. Not tested: does `client.file_search_stores.*` work with Vertex AI auth?
2. **No tests** — zero pytest. Same gap as all ADK repos.
3. **No production wrapper** — lessons are standalone scripts, no FastAPI or Streamlit yet
4. **No multi-store patterns** — multi-store query is supported by the API but not demonstrated
5. **Streamlit UI** — `_old/streamlit_app.py` exists but is empty/incomplete

---

## Questions for Future Investigation

1. **Does File Search work with Vertex AI auth?** The lessons use API key, but production would want Vertex AI. Not tested in this repo.
2. **What document formats are supported?** Only `.txt` and `.pdf` tested here.
3. **Store lifecycle management** — can stores be updated/renamed? What's the delete-store pattern?
4. **Rate limits** — how many concurrent uploads? What are the store size limits?
5. **Vertex AI vs API Key for File Search** — same store accessible from both? Or different?

---

## Insights for Manual Creation

### For "Google Managed RAG Manual":
- Full lifecycle: create → upload → poll → query → delete
- `force=True` delete gotcha (critical — must be documented)
- `store.name` resource path format
- Summary + original dual-document strategy
- `grounding_metadata` for citations
- Cost model (storage free, only embedding at upload)
- Multi-store query pattern

### For "Google genai SDK Manual":
- API key vs Vertex AI auth — same interface
- `client.file_search_stores.*` is current (not `client.files.*`)
- `types.Part.from_bytes` for PDF/media input
- Async operation polling pattern
- Model choice (flash vs pro) for different use cases

### For "Python App Architecture Manual":
- File-based state confirmed again (store_name.txt)
- Tutorial/lesson structure as a valid project organization
- `_old/` folder for deprecated experiments (pattern confirmed across repos)

### For "RAG Manual":
- Managed vs DIY trade-off analysis (this + crawl4ai together cover both sides)
- Dual-document strategy (summary + original)
- When retrieval is implicit vs explicit

---

## Notable Code Comments (Signal High-Value Moments)

These comments in the code show where the author figured something out:

```python
config={'force': True}  # ✅ FIXED: Force delete with chunks
```
```python
"Your prompt"  # ✅ Just pass as string!
```

Comments with `# ✅ FIXED` or `# ✅ Just` pattern = documented discoveries. Good signal for "what trips people up."

---

## Files Created This Session

```
docs/architecture.md                                    ← System flow, file structure, two auth modes
docs/patterns.md                                        ← 12 copy-pasteable patterns
docs/decisions.md                                       ← 9 key decisions with rationale
docs/google_file_search_api.md                          ← Full API deep-dive
session-2026-02-23-managed-rag-google-file-search.md    ← This file
```

---

## Status of Coverage (Updated)

This repo adds to what's covered:

| Topic | Coverage Now | Source Repos |
|-------|-------------|-------------|
| Google managed RAG (File Search API) | ✅ Good | this repo |
| RAG comparison (managed vs DIY) | ✅ Good | crawl4ai + this |
| Async operation polling | ✅ Good | this repo |
| PDF direct analysis (bytes) | ✅ Good | this repo |
| Dual-document RAG strategy | ✅ Good | this repo |

---

_Session Status: Complete_
_Docs Created: 5 files_
_Last Updated: 2026-02-23_
