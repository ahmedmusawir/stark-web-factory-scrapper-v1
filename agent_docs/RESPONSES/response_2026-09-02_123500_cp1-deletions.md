# CP1 REPORT — Deletions + GHL purge — 2026-09-02 12:35

**Branch:** phase-c1-cleanup (verified read-only). No git commands run.

## Deleted (1,466 tracked files)
| Path | Count |
|---|---|
| `outputs/**` (3 discovery JSONs + `pages/`) | 1,428 |
| `utils/` | 14 |
| `CLAUDE TRAINING GUIDES/` (incl. MISSION_BRIEF.md) | 14 |
| `docs/` | 4 |
| `smart_crawler/summary_generator_ghl.py` | 1 |
| `ghl_chatbot_streamlit.py`, `ghl_chatbot_streamlit-1.py`, `ghl_store_name.txt` | 3 |
| `pyproject.toml`, `poetry.lock` | 2 |

## Created
- `outputs/.gitkeep` (empty dir survives)

## Scrubbed (string-only)
- `smart_crawler/crawler.py` — removed `"   - Better RAG quality"` print; removed 2-line "Next step: Generate summaries / Run: python summary_generator_ghl.py" hint at end of `main()`
- `discover_site/smart_discover.py:201` — usage example URL `marketplace.gohighlevel.com/docs/oauth/GettingStarted` → `example.com/docs/getting-started`

## Survivors (non-protocol)
`discover_site/{discover.py, sitemap_utils.py, smart_discover.py}`, `smart_crawler/crawler.py`, `.gitignore`, `.python-version`, `README.md`, `outputs/.gitkeep` (+ `CLAUDE.md`, `RECOVERY.md`, `agent_docs/`)

## Purge grep
```
grep -rniE "ghl|gohighlevel|genai|filesearch|file search|chatbot|\brag\b" \
  --include=*.py --include=*.md --include=*.toml --include=*.txt --include=*.cfg . \
  --exclude-dir=agent_docs --exclude-dir=venv --exclude-dir=.git --exclude=CLAUDE.md
→ discover_site/smart_discover.py:237:        path = url.replace('https://marketplace.gohighlevel.com/docs/', '')
```
1 hit remaining — the logic line scheduled for CP3 (prefix derived from `base_url`). All string-only hits are gone. `README.md` (still the 2-line stub) has no hits; rewrite is CP4.

## Suggested commit (text only — your call)
```
git add -A
git commit -m "chore(c1): remove GHL RAG-era code, docs, artifacts, and Poetry packaging

- delete utils/, docs/, CLAUDE TRAINING GUIDES/, both Streamlit apps,
  summary_generator_ghl.py, ghl_store_name.txt
- delete 1,428 crawled GHL artifacts under outputs/ (keep dir via .gitkeep)
- delete pyproject.toml + poetry.lock (Poetry retired; pins carried to
  requirements.txt in CP2)
- scrub string-only GHL/RAG references in crawler.py and smart_discover.py"
```
Note: `git add -A` also stages the session log + two plan artifacts under `agent_docs/RESPONSES/`. Fine to include, or stage them at CP4 instead.

→ CP1 STOP. Awaiting confirm before CP2.
