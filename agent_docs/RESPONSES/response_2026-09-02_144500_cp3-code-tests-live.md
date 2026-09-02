# CP3 REPORT — Code fixes + tests + live discovery/crawl — 2026-09-02 14:45

**Branch:** phase-c1-cleanup. No git commands run.

## Code changes
| File | Change |
|---|---|
| `discover_site/__init__.py`, `smart_crawler/__init__.py` | NEW, empty — real packages |
| `discover_site/discover.py` | `from discover_site.sitemap_utils import ...`; output path anchored to repo root via `Path(__file__).resolve().parents[1] / 'outputs'`; `mkdir(parents=True, exist_ok=True)` before write. No logic change. |
| `smart_crawler/crawler.py` | Docstring only: `v0.7.x` → `v0.6.x`; run line → `python -m smart_crawler.crawler`; documents input/output paths. |
| `discover_site/smart_discover.py` | Pattern-analysis prefix derived from `base_url` (was hard-coded gohighlevel domain); usage text → `python -m discover_site.smart_discover`. `/docs/` filter untouched. |
| `pytest.ini` | NEW: `testpaths = tests`, `pythonpath = .` (pytest's own option — no PYTHONPATH env hack) |
| `tests/test_discover.py` | NEW: 3 tests — `is_valid_link` (reject empty/mailto/tel/fragment; accept relative + same-domain; reject foreign domain), `normalize_link` (strip query+fragment, resolve relative) |
| `tests/test_sitemap_utils.py` | NEW: 3 tests — flat sitemap, sitemap-index → child, unparseable → `[]`. `requests.get` stubbed via monkeypatch. |

## Tests
```
venv/bin/pytest -q
......                                                                   [100%]
6 passed in 0.23s
```

## Purge grep (exempt: agent_docs, CLAUDE.md, venv; +*.ini)
```
grep -rniE "ghl|gohighlevel|genai|filesearch|file search|chatbot|\brag\b" --include=*.py --include=*.md --include=*.toml --include=*.txt --include=*.cfg --include=*.ini . --exclude-dir=agent_docs --exclude-dir=venv --exclude-dir=.git --exclude=CLAUDE.md
→ (zero hits)
```

## Live run 1 — discovery (from repo root)
```
printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com/
```
- Sitemap index found at `/sitemap.xml` → 3 child sitemaps (post, page, category)
- EXIT 0 → `outputs/discovered_pages.json` — **194 URLs**

## Live run 2 — 5-page crawl
```
venv/bin/python -c "import json;d=json.load(open('outputs/discovered_pages.json'))[:5];json.dump(d,open('outputs/discovered_pages_final.json','w'),indent=2)"
printf 'y\n' | venv/bin/python -m smart_crawler.crawler
```
- EXIT 0 — 5/5 successful, 0 failed, ~6.5 s per page, no `crawl4ai-setup` needed
- `outputs/pages/`: 5 `.md`, 79,533 bytes total (7.4–25.9 KB each)
- `git status` shows no run artifacts (ignore rule from CP2 works)

## Findings (not fixed — outside C1 scope, flagging for later phases)
1. **`fit_markdown` was empty on all 5 pages** → crawler fell back to `raw_markdown`. Output is real content but nav-heavy (site menu, `?cat_source=` tracking params on every link). Cause: `CrawlerRunConfig` sets no `markdown_generator`/content filter; in crawl4ai 0.6.x `fit_markdown` needs an explicit `PruningContentFilter`/`BM25ContentFilter`. Later-phase item.
2. **Direct-path invocation no longer works**: `venv/bin/python discover_site/discover.py` → ImportError (package import, no editable install). Blessed form is `python -m discover_site.discover`. Documented in README/RUN_NOTES at CP4.
3. `crawler.py` still prints the stale banner `"UPGRADED BATCH CRAWLER - v0.7.x"` and `"~30-40 minutes for 707 URLs"` (runtime strings, not the docstring) — left per scope; flag.
4. discover.py writes `discovered_pages.json`; crawler reads `discovered_pages_final.json` — handoff needs the subset one-liner. Later-phase item.

## Suggested commit (text only)
```
git add discover_site/__init__.py smart_crawler/__init__.py discover_site/discover.py discover_site/smart_discover.py smart_crawler/crawler.py pytest.ini tests/
git commit -m "fix(c1): root-runnable discovery, scrub stale references, add smoke tests

- discover_site/, smart_crawler/ become packages; discover.py uses package
  import and repo-root-anchored output path (run: python -m discover_site.discover)
- crawler.py docstring: correct crawl4ai version (0.6.x) and run instructions
- smart_discover.py: derive docs prefix from base_url instead of hard-coded domain
- tests/: 6 pure-logic pytest smoke tests (no network, no env); pytest.ini
- baseline verified: 194 URLs discovered + 5/5 pages crawled from cyberizegroup.com"
```

→ CP3 STOP. Awaiting confirm before CP4 (README + RUN_NOTES + session state).
