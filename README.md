# Stark Web Recon — scraper v1

Discovery-and-crawl engine for Stark Industries web recon. Point it at a site, it enumerates the site's pages (sitemap or homepage links), then crawls each page with [crawl4ai](https://github.com/unclecode/crawl4ai) and writes one markdown file per page to `outputs/pages/`. That markdown is the raw material for later analysis phases. Phase 1 so far: C1 baseline → bim000 stage prep → bim001 raw HTML capture (see `CHANGELOG.md`).

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

Two commands, from the repo root, module form (`python -m ...`; running the files by path does not work). No manual step between them.

**1. Discover pages** — writes `outputs/discovered_pages.json` (anchored to the repo root whatever your CWD). Interactive menu: `1` = sitemap.xml, `2` = homepage `<a>` links.

```bash
venv/bin/python -m discover_site.discover https://cyberizegroup.com
```

**2. Crawl** — `--project NAME` is required. Reads `outputs/discovered_pages.json`, writes one `.md` per URL into `outputs/pages/`, `outputs/run_summary.json`, and a **run folder** with each page's raw HTML. No prompt.

```bash
python -m smart_crawler.crawler --project CyberizeGroup --limit 10
```

Other forms: `venv/bin/python -m smart_crawler.crawler --project CyberizeGroup` (all discovered URLs) · `--input other.json --limit 3` (other input file). Missing or malformed `--project` refuses before anything is read or created, prints the example above and a `--help` pointer, and exits 2. Valid names: letters, digits, `-`, `_`; 1–64 characters; case preserved.

**Run folder** — one per run, never reused:

```
outputs/<project>/runs/<run_id>/          run_id = started_at, e.g. 2026-09-06T14-30-00Z
├── html/<slug>.html                      raw HTML, byte-for-byte as crawl4ai returned it, one per captured page
│                                         (same slug as the .md; same slug twice in a run → -2, -3 suffix, never overwritten)
├── manifest.json                         the run record: every attempted URL with status, ok, outcome, reason, files, sizes,
│                                         plus command, input file/hosts/total, limit, versions, timing config, timestamps
├── absences.json                         every input URL that produced no HTML: blocked / failed / unsupported / skipped (limit, stop_rule)
└── stage_log.txt                         timestamped lines: run start, one per attempted URL, stop rule, run end
```

Outcomes: `captured` (fetched, HTML saved) · `blocked` (403/429, nothing saved) · `failed` (status ≥ 400, `success=False`, exception, or HTML write error) · `unsupported` (fetched but the library returned no `html`). HTML capture does not depend on markdown: a page with empty markdown is `ok: false` in `run_summary.json` and still `captured` in the manifest.

Behaviour (unchanged from bim000):

- One page at a time, with a random 2–5 s pause between pages (each pause is printed).
- One status line per page. A page with `status_code >= 400`, or that crawl4ai reports as `success=False`, is **failed** and no `.md` is written for it. 403 and 429 are recorded as `blocked`; three consecutive blocked pages stop the run (exit code 2) — the manifest and absences are still written first.
- `outputs/run_summary.json`: `{started_at, finished_at, crawl4ai_version, pause_range_s, pages: [{url, status, ok, elapsed_s, error}]}` — written on every run, including empty input and an early stop. This is the frozen bim000 contract; `manifest.json` is the run record from bim001 onward.
- Identity: one complete Chrome-shaped user agent (defined once in `discover_site/sitemap_utils.py`) is sent by the crawler's browser and by every discovery request via a shared `requests.Session`. No stealth, no navigator patching.
- Content: crawl4ai's `raw_markdown` (full page including nav) — `fit_markdown` needs a content filter that is not configured yet.

Exit codes: `0` normal (including runs with failed pages) · `1` input file missing or unreadable · `2` missing/invalid `--project`, `--limit < 1`, or 3 consecutive blocked pages.

## Tests

```bash
venv/bin/pytest
```

Offline only — no network, no browser, no env vars. URL filtering, sitemap parsing with the HTTP session stubbed, and crawler behaviour (status handling, blocked-stop, pacing, `--limit`/`--input`, import side effects, `--project` validation, run folder, HTML capture, manifest, absences, stage log) with crawl4ai results and the browser stubbed. Test names carry their acceptance-criterion number (`test_acNN_…`).

## Layout

```
discover_site/   discover.py (sitemap / homepage-link discovery), sitemap_utils.py (sitemap parsing, shared UA + Session)
smart_crawler/   crawler.py (crawl4ai batch crawler)
tests/           pytest (offline): test_discover.py, test_sitemap_utils.py, test_crawler.py
outputs/         run artifacts (gitignored except .gitkeep): discovered_pages.json, run_summary.json, pages/*.md,
                 <project>/runs/<run_id>/{html/, manifest.json, absences.json, stage_log.txt}
agent_docs/      Claude Code session protocol files
RUN_NOTES.md     exact commands + verification record (C1 baseline, bim000, bim001)
CHANGELOG.md     doc/playbook change log
```
