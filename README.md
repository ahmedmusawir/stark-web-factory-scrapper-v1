# Stark Web Recon — scraper v1

Discovery-and-crawl engine for Stark Industries web recon. Point it at a site, it enumerates the site's pages (sitemap or homepage links), then crawls each page with [crawl4ai](https://github.com/unclecode/crawl4ai) and writes one markdown file per page to `outputs/pages/`. That markdown is the raw material for later analysis phases. Nothing else lives here yet — this is the Phase C1 functional baseline.

## Setup

Python 3.12.3 via pyenv (`.python-version` selects it automatically), a plain venv, and pinned pip requirements. No Poetry.

```bash
pyenv install 3.12.3            # once, if missing
python -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/playwright install chromium
cp .env.example .env            # fill in values as later phases require them
```

`requirements.txt` holds the exact top-level pins. `requirements-lock.txt` is the full `pip freeze` of a known-good install; use it to reproduce the environment byte-for-byte:

```bash
venv/bin/pip install -r requirements-lock.txt
```

## Run

All commands run from the repo root using the module form (`python -m ...`). Running the scripts by file path does not work.

**1. Discover pages** — writes `outputs/discovered_pages.json`. Interactive menu: `1` = sitemap.xml, `2` = homepage `<a>` links.

```bash
venv/bin/python -m discover_site.discover https://example.com/
```

**2. Select what to crawl** — the crawler reads `outputs/discovered_pages_final.json`. Copy or subset the discovery output into that file, e.g. the first 5 URLs:

```bash
venv/bin/python -c "import json;d=json.load(open('outputs/discovered_pages.json'))[:5];json.dump(d,open('outputs/discovered_pages_final.json','w'),indent=2)"
```

**3. Crawl** — one `.md` per URL into `outputs/pages/`. Asks for a `y` confirmation before starting.

```bash
venv/bin/python -m smart_crawler.crawler
```

`discover_site/smart_discover.py` is an alternative discoverer for JavaScript sidebar-navigation doc sites (expands nested menus with Playwright); it is not used in the baseline run.

## Tests

```bash
venv/bin/pytest
```

Pure-logic smoke tests only (URL filtering, sitemap parsing with stubbed HTTP). No network, no env vars.

## Layout

```
discover_site/   discover.py (sitemap / homepage-link discovery), smart_discover.py, sitemap_utils.py
smart_crawler/   crawler.py (crawl4ai batch crawler)
tests/           pytest smoke tests
outputs/         run artifacts (gitignored except .gitkeep)
agent_docs/      Claude Code session protocol files
RUN_NOTES.md     exact commands + verification record for the C1 baseline
```
