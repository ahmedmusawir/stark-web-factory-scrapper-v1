# READ — pre-ABM recon — 2026-09-18

**Seat:** Claudy (Engineer). **Mode:** read-only. No edits to product/tests/docs, no installs, no mutating git, **no network** (Part B not run — see end).
**Labels:** EVIDENCE = read directly from a file or command output · INFERENCE = derived · GAP = could not be established on this machine.

## 0. Repo state

| Item | Value | Label |
|---|---|---|
| Branch | `wf-scrapper-abm` | EVIDENCE (`git branch --show-current`) |
| HEAD | `73f96db 7sep2026 - bim001 closed after qa` | EVIDENCE (`git log -1 --oneline`) |
| Tree | clean except `?? agent_docs/SESSIONS/session_2026-09-18.md` (today's session log, created at session start) | EVIDENCE (`git status --short`) |
| HEAD vs main | `73f96db` is also `main`, `origin/main`, `origin/HEAD`, `origin/qa/web-factory-p1-bim001` | EVIDENCE (`git log main --oneline --decorate`) |
| Remote | `origin https://github.com/ahmedmusawir/stark-web-factory-scrapper-v1.git` | EVIDENCE (`git remote -v`) |

**GAP-0 (affects §3, §7, §9): this checkout is a fresh clone.** Every file mtime is `Sep 18 19:13`; there is **no `venv/`** and `outputs/` holds only `.gitkeep`. No live run folder, no `discovered_pages.json`, no `run_summary.json`, and no installed crawl4ai/playwright exist on this machine's copy. A disk-wide search (`find ~ -name manifest.json -path '*runs*'`, `discovered_pages.json`, `run_summary.json`) found nothing outside the committed QA evidence tree.

---

## PART A

### 1. Certified state

- **Tags: none.** `git tag -l` prints nothing. EVIDENCE.
- **Merge commits on main: none.** `git log main --merges` prints nothing; history is linear (rebase-and-merge, consistent with `RECOVERY.md:4`). EVIDENCE. So certification is anchored by SHA + branch ref, not tag/merge commit:

| Module | Certified SHA | Close-out commit on main | Branch refs | Source |
|---|---|---|---|---|
| bim000 | `81099eedb0b7072ceaa8ee20ebaf336466a369bb` ("test(bim000): record AC-21 QA retest") | `57a0f59` "6sep2026 - bim000 close out" (= `origin/qa/web-factory-p1-bim000`) | dev: `origin/web-factory-p1-bim000` @ `9d40ca5` | EVIDENCE `RUN_NOTES.md:131`; git log |
| bim001 | `eee039a2c06cc1aeaa3e9dfb52e17db9d3ddb20a` (candidate) ; package `7517049` | `73f96db` "7sep2026 - bim001 closed after qa" (= `main` = `origin/qa/web-factory-p1-bim001`) | dev: `origin/web-factory-p1-bim001` @ `657e25e` | EVIDENCE `agent_docs/RESPONSES/BIM001_GATE_Q_RECORD_2026-09-07.md:7-8`; git log |

- **Regression command:** `venv/bin/pytest -q` → **54 passed (14 bim000 + 40 bim001)**. EVIDENCE `RUN_NOTES.md:152`; `README.md:68` prints `venv/bin/pytest`. `pytest.ini:1-3` = `testpaths = tests`, `pythonpath = .`.
- **Test count by file** (static count of `def test_`; not executed — no venv, GAP-0):

| File | `def test_` | Collected | Note |
|---|---:|---:|---|
| `tests/test_crawler.py` | 47 | 48 | one `parametrize` with 2 values at `tests/test_crawler.py:218` |
| `tests/test_discover.py` | 3 | 3 | |
| `tests/test_sitemap_utils.py` | 3 | 3 | |
| **Total** | 53 | **54** | INFERENCE: matches the recorded 54 |

### 2. Interface

Two entry points, both module-form only (`README.md:25`). No console scripts, no `pyproject.toml`/`setup.py`. EVIDENCE (`git ls-files`).

**A. `python -m discover_site.discover <url>`** — `discover_site/discover.py:57-91`
- One positional `url` (`:59`). No flags.
- **Interactive**: prompts `[1] sitemap.xml / [2] homepage <a> links / [q] quit` via `input()` (`:62-67`). Canonical non-interactive form pipes the choice: `printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com` (`RUN_NOTES.md:150`).
- Output path fixed: `<repo>/outputs/discovered_pages.json` (`:12-13`), no override flag.
- **Exit codes: always 0** on handled paths — empty sitemap, no links, invalid choice, quit all `return` (`:72-84`); only argparse usage errors give 2. INFERENCE from code; no explicit `sys.exit` in the file.

**B. `python -m smart_crawler.crawler`** — `smart_crawler/crawler.py:347-358`

| Flag | Type | Default | Rule | Line |
|---|---|---|---|---|
| `--project` | str | `None` | required, validated at runtime (not by argparse) against `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`; case preserved | `:349-350`, `:52`, `:78-84` |
| `--input` | Path | `<repo>/outputs/discovered_pages.json` | discovery JSON | `:351-352`, `:47` |
| `--limit` | int | `None` (all) | `< 1` → `parser.error` | `:353-357` |

**Exit codes** (`README.md:63`; code lines):
- `0` normal, including runs with failed pages and empty input (`:483-489`).
- `1` input file missing / JSON decode error / other load error (`:325-338`).
- `2` missing or invalid `--project` (`:457-460`); `--limit < 1` (argparse, `:357`); 3 consecutive blocked pages (`:540-541`) — manifest and absences are written first (`:514`).
- Order note: project validation runs **before** the input is read or anything is created (`:457` precedes `:462`, `:467`).

**Canonical text printed on error** (EVIDENCE: `crawler.py:53-54`, `:87-95`; transcripts in `agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/cli_*.stderr.txt`):

```
❌ --project is required. Name the project this run belongs to.
   Example: python -m smart_crawler.crawler --project CyberizeGroup --limit 10
   Help:    python -m smart_crawler.crawler --help
```
```
❌ --project is invalid: 'Cyberize Group'. Allowed: letters, digits, '-' and '_'; 1-64 characters; must start with a letter or digit.
   Example: python -m smart_crawler.crawler --project CyberizeGroup --limit 10
   Help:    python -m smart_crawler.crawler --help
```
```
usage: crawler.py [-h] [--project PROJECT] [--input INPUT] [--limit LIMIT]
crawler.py: error: --limit must be >= 1
```
```
❌ File not found: <path>
   Run discovery first: python -m discover_site.discover <url>
```
The first two go to stderr; the file-not-found pair goes to **stdout** (`:326-327` use bare `print`). EVIDENCE.

### 3. Raw contract as it exists

**Run folder layout** — `crawler.py:197`, `:218-219`, `README.md:44-51`:
```
outputs/<project>/runs/<run_id>/
├── html/<slug>.html     raw HTML, utf-8 bytes of crawl4ai result.html, one per captured page
├── manifest.json
├── absences.json
└── stage_log.txt        "<utc iso> <line>": run start, one per attempted URL, stop rule, run end
```
Also still written outside the run folder: `outputs/pages/<slug>.md` and `outputs/run_summary.json` (`:45-46`). Markdown is **not** inside the run folder; it is a shared, overwritten location. EVIDENCE.

**run_id rule** — `make_run_id`, `crawler.py:73-75`: `started_at[:19].replace(":", "-") + "Z"`, e.g. `2026-09-06T14:30:00+00:00` → `2026-09-06T14-30-00Z`. `started_at` = `datetime.now(timezone.utc).isoformat(timespec="seconds")` (`:69-70`). Same-second clash: `create()` sleeps 0.2 s and re-stamps until the dir does not exist — never shares a folder (`:225-232`); `main` then adopts the moved `started_at` (`:468`).

**Slug rule** — `slugify`, `crawler.py:64-66`: strip scheme (`https://`/`http://` by literal `str.replace`, `:368`), lower-case, every run of non-`[a-z0-9]` → `-`, trim `-`, empty → `root`. So host is part of the slug (`cyberizegroup-com-blog`), and query strings / trailing slashes collapse into hyphens. INFERENCE: two URLs differing only in case, trailing slash, or punctuation map to the same base slug.

**Collision rule** — `allocate_slug`, `crawler.py:238-242`: per-run counter; first use → `base`, then `base-2`, `base-3`. `save_html` refuses to overwrite (`:248-249`). Slug is allocated **only on the captured path** (`:380`); non-captured entries carry the bare base slug. Known asymmetry: `md_file` always uses the un-suffixed base (`:369`), so under collision the second page's markdown **overwrites** the first while HTML is kept separately (recorded as AC-35 PASS WITH NOTE, `BIM001_complete_2026-09-06.md:92`).

**manifest.json** — schema `bim001-manifest-v1`; exactly **23** top-level keys, asserted at `crawler.py:295`; built at `:269-294`:

| Key | Type | Value rule |
|---|---|---|
| `schema` | str | `"bim001-manifest-v1"` (`:200`) |
| `project_name` | str | `--project` verbatim |
| `run_id` | str | see rule above |
| `run_dir` | str | `outputs/<project>/runs/<run_id>` (relative, literal `outputs/` prefix, `:223`) |
| `started_at` / `finished_at` | str | UTC ISO-8601, seconds, `+00:00` |
| `command` | str | `"python -m smart_crawler.crawler " + argv[1:]` (`:464`) |
| `input_path` | str | **absolute** resolved path (`:474`) |
| `input_total` | int | all URLs in input, before `--limit` (`:462`) |
| `limit` | int \| null | |
| `input_hosts` | list[str] | sorted unique `urlparse().hostname` (no port, lower-case) (`:315-317`) |
| `access_rung` | str | `"a"` (`:201`) |
| `fallbacks_fired` | list | always `[]` |
| `stopped_early` | bool | |
| `crawl4ai_version` / `playwright_version` / `python_version` | str | `importlib.metadata` / `platform` |
| `wait_for_images` | bool | `true` (literal mirror) |
| `delay_before_return_html_s` | float | `3.0` |
| `page_timeout_ms` | int | `90000` |
| `pause_range_s` | list[int] | `[2, 5]` |
| `summary_path` | str | `"outputs/run_summary.json"` |
| `pages` | list[obj] | attempt order |

Per-page entry — **11 keys** (`crawler.py:258-263`): `url` str · `status` int\|null · `ok` bool · `elapsed_s` float · `error` str\|null · `slug` str · `outcome` one of `captured|blocked|failed|unsupported` (`:202`) · `reason` str\|null · `html_file` str\|null (`html/<slug>.html`, relative to run dir) · `html_bytes` int\|null · `md_file` str\|null (`pages/<base>.md`, relative to `outputs/`).
Outcome precedence (`:373-385`): blocked (403/429) > failed (not fetched) > unsupported (fetched, no html) > captured / `write failed: …`.

**absences.json** — a bare JSON **list** (`crawler.py:300-303`); each item 3 keys `url` str · `outcome` str · `reason` str (`:306-312`). Outcomes: `blocked|failed|unsupported` (attempted, attempt order) then `skipped` with reason `stop_rule` (in the limit window, not reached) then `skipped`/`limit` (beyond `--limit`, input order). captured + absences = `input_total`.

**What `run_summary.json` still carries** — frozen bim000 contract, `crawler.py:182-192`: 5 top-level keys `started_at, finished_at, crawl4ai_version, pause_range_s, pages`; per page 5 keys `url, status, ok, elapsed_s, error`. Single file, **overwritten every run**, including empty input and early stop. Retirement queued for bim004 or later (`RUN_NOTES.md:160`).

**One real manifest.json — GAP.** No live run folder exists on this machine (GAP-0). The 2026-09-07 session log already recorded that the live evidence dirs (`QA/evidence/live_2026-09-07_eee039a/live_run_snapshot/`) were never tracked (`agent_docs/SESSIONS/session_2026-09-07.md:21`). What survives of the live runs is prose only:
- Run `2026-09-06T07-30-16Z`: all 22 scalar values quoted in `agent_docs/RESPONSES/BIM001_complete_2026-09-06.md:49`.
- Run `2026-09-07T04-10-56Z`: per-page table in `QA_LIVE_BIM001_2026-09-07_1017.md:59-70`.

Substitute, clearly **not live**: a committed, machine-written manifest from Cody's offline artifact driver (stubbed crawler, `example.invalid` URLs). It is the only on-disk file that exercises every outcome. Path: `agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/artifact_cases/mixed/outputs/CyberizeGroup/runs/2026-09-06T09-00-45Z/manifest.json` (3,437 bytes), verbatim:

```json
{
  "schema": "bim001-manifest-v1",
  "project_name": "CyberizeGroup",
  "run_id": "2026-09-06T09-00-45Z",
  "run_dir": "outputs/CyberizeGroup/runs/2026-09-06T09-00-45Z",
  "started_at": "2026-09-06T09:00:45+00:00",
  "finished_at": "2026-09-06T09:00:45+00:00",
  "command": "python -m smart_crawler.crawler --project CyberizeGroup --input /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/artifact_cases/mixed/input.json",
  "input_path": "/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/artifact_cases/mixed/input.json",
  "input_total": 7,
  "limit": null,
  "input_hosts": [
    "example.invalid"
  ],
  "access_rung": "a",
  "fallbacks_fired": [],
  "stopped_early": false,
  "crawl4ai_version": "0.9.3",
  "playwright_version": "1.52.0",
  "python_version": "3.12.3",
  "wait_for_images": true,
  "delay_before_return_html_s": 3.0,
  "page_timeout_ms": 90000,
  "pause_range_s": [
    2,
    5
  ],
  "summary_path": "outputs/run_summary.json",
  "pages": [
    {
      "url": "https://example.invalid/page0",
      "status": 200,
      "ok": true,
      "elapsed_s": 0.0,
      "error": null,
      "slug": "example-invalid-page0",
      "outcome": "captured",
      "reason": null,
      "html_file": "html/example-invalid-page0.html",
      "html_bytes": 9,
      "md_file": "pages/example-invalid-page0.md"
    },
    {
      "url": "https://example.invalid/page1",
      "status": 403,
      "ok": false,
      "elapsed_s": 0.0,
      "error": "blocked",
      "slug": "example-invalid-page1",
      "outcome": "blocked",
      "reason": "blocked",
      "html_file": null,
      "html_bytes": null,
      "md_file": null
    },
    {
      "url": "https://example.invalid/page2",
      "status": 500,
      "ok": false,
      "elapsed_s": 0.0,
      "error": "HTTP 500",
      "slug": "example-invalid-page2",
      "outcome": "failed",
      "reason": "HTTP 500",
      "html_file": null,
      "html_bytes": null,
      "md_file": null
    },
    {
      "url": "https://example.invalid/page3",
      "status": null,
      "ok": false,
      "elapsed_s": 0.0,
      "error": "exception: QA arun exception",
      "slug": "example-invalid-page3",
      "outcome": "failed",
      "reason": "exception: QA arun exception",
      "html_file": null,
      "html_bytes": null,
      "md_file": null
    },
    {
      "url": "https://example.invalid/page4",
      "status": 200,
      "ok": true,
      "elapsed_s": 0.0,
      "error": null,
      "slug": "example-invalid-page4",
      "outcome": "unsupported",
      "reason": "no html in result",
      "html_file": null,
      "html_bytes": null,
      "md_file": "pages/example-invalid-page4.md"
    },
    {
      "url": "https://example.invalid/page5",
      "status": 200,
      "ok": false,
      "elapsed_s": 0.0,
      "error": "empty markdown",
      "slug": "example-invalid-page5",
      "outcome": "captured",
      "reason": null,
      "html_file": "html/example-invalid-page5.html",
      "html_bytes": 8,
      "md_file": null
    },
    {
      "url": "https://example.invalid/page6",
      "status": 200,
      "ok": false,
      "elapsed_s": 0.0,
      "error": "HTTP 200",
      "slug": "example-invalid-page6",
      "outcome": "failed",
      "reason": "HTTP 200",
      "html_file": null,
      "html_bytes": null,
      "md_file": null
    }
  ]
}
```
Its sibling `absences.json` lists page1/2/3/4/6 with the same `outcome`/`reason` strings. To get a real one, a live `--limit 10` run is needed (requires venv + network + Director approval).

**ABM binding notes (INFERENCE):** `input_path` and `command` embed an absolute machine path, so manifests are not byte-portable across machines; `md_file` is relative to `outputs/` while `html_file` is relative to the run dir — two different bases in one record; the manifest carries no per-page content hash, no final URL after redirects, no response headers, no fetch timestamp per page (only in `stage_log.txt`).

### 4. Discovery output

- **Shape:** JSON list of objects with **exactly one field**: `{"url": "<str>"}` — `write_to_json`, `discover.py:50-54`. No title, lastmod, source sitemap, post type, depth, or discovery method. EVIDENCE.
- Reader tolerance: the crawler accepts dicts with `"url"` **or** bare strings, and drops falsy entries (`crawler.py:332`).
- **Identity/dedup rule:**
  - Sitemap mode (choice 1): **none.** `fetch_sitemap_urls` concatenates `<loc>` text from every child sitemap in document order, no dedup, no normalisation, no host filter (`sitemap_utils.py:32-50`). Only `/sitemap.xml` is tried (`:17`) — no `robots.txt`, no `sitemap_index.xml`/`wp-sitemap.xml` fallback. One level of index nesting only. A failed child sitemap is skipped with a warning (`:44-45`).
  - Homepage mode (choice 2): `set()` dedup + `sorted()` (`discover.py:40-48`); fragment and query stripped (`:23-24`); same `netloc` or relative only (`:21`); must `startswith(base_url)` (`:45`). Homepage only — no recursion.
- **No dedup at crawl time either:** duplicate URLs in the input are crawled twice and disambiguated only by the `-2` HTML suffix. INFERENCE from `crawler.py:406-435`.
- Observed: cyberizegroup.com → 194 URLs from 3 child sitemaps (post, page, category), 4 GETs, <1 s (`RUN_NOTES.md:31`, `:135`).

### 5. Fetch posture

| Aspect | Value | Line |
|---|---|---|
| Pacing (crawl) | sequential, one page at a time; `random.uniform(2, 5)` s pause before every page except the first | `crawler.py:58`, `:407-410` |
| Pacing (discovery) | **none** — child sitemaps fetched back-to-back | `sitemap_utils.py:35-45` |
| Page timeout | `page_timeout=90000` ms | `crawler.py:110` |
| Post-load delay | `delay_before_return_html=3.0` s; `wait_for_images=True` | `:111-112` |
| Cache | `CacheMode.BYPASS` | `:109` |
| Discovery timeout | `timeout=10` s on every `SESSION.get` | `sitemap_utils.py:21`, `:39`; `discover.py:31` |
| Retries | **none** anywhere (grep `retry|retries` → 0 hits in product code). One attempt per URL; an exception becomes a `failed` record | `crawler.py:122-127` |
| Stop rule | 403/429 = blocked; 3 consecutive blocked → stop, exit 2; any non-blocked page resets the counter | `:56-57`, `:428-442` |
| UA source | single constant `USER_AGENT` in `discover_site/sitemap_utils.py:7-10` (Chrome/140 on Windows shape); imported by the crawler (`crawler.py:36`) into `BrowserConfig(headless=True, user_agent=USER_AGENT)` (`:448`); discovery uses shared `requests.Session` with the same header (`sitemap_utils.py:13-14`) | |
| Stealth | none; `access_rung "a"` = plain headless fetch | `crawler.py:201` |
| Redirects | **not handled or recorded.** Browser follows them; `requests` follows by default (`allow_redirects` never set). Manifest keeps the input `url` only — no final URL, no redirect chain | grep `redirect` → only an unrelated comment at `crawler.py:48` |
| Scope filter (crawl) | **none.** The crawler fetches whatever URLs are in the input; `input_hosts` is descriptive, not enforced | `crawler.py:315-317`, `:462-463` |
| Scope filter (discovery, homepage mode) | exact `netloc` match → subdomains **excluded** (test: `other.example.com` rejected, `tests/test_discover.py:18`); query strings and fragments **stripped** | `discover.py:21-24` |
| Scope filter (discovery, sitemap mode) | **none** — every `<loc>` is taken as-is, including off-host or query-string URLs | `sitemap_utils.py:42`, `:49` |
| robots.txt | not read anywhere (grep `robots` → 0) | INFERENCE: absent |
| Config/env | no `os.getenv`, no dotenv import in product code; `.env.example` has only `GEMINI_API_KEY=` (unused) | grep → 0 hits |

### 6. What does NOT exist yet (grep over `smart_crawler/ discover_site/ tests/ requirements.txt`, case-insensitive)

| Capability | Pattern(s) | Hits | Label |
|---|---|---:|---|
| REST client | `wp-json`, `wp/v2`, `rest_` | 0 / 0 / 0 | EVIDENCE absent |
| Yoast capture | `yoast` | 0 | EVIDENCE absent |
| Media inventory | `media`, `attachment` | 0 / 0 | EVIDENCE absent |
| Screenshot slot | `screenshot` | 0 | EVIDENCE absent (`CrawlerRunConfig` at `crawler.py:108-113` sets no `screenshot=`) |
| Prepare | `prepare` | 0 | EVIDENCE absent |

Also absent: any `/services`, `/types`, config_service or logging_service layer — the product is three flat modules (1 crawler, 2 discovery). `requests` is already a pinned dependency and `SESSION` already carries the project UA, so a REST client has an identity to reuse. INFERENCE.

### 7. Pins

`requirements.txt`, verbatim (8 lines):
```
# Exact pins. Carried over from the retired poetry.lock (2026-09-02); crawl4ai bumped 0.6.3 -> 0.9.3 in bim000 Stage 1 (2026-09-05). Do not bump without a ruling.
crawl4ai==0.9.3
playwright==1.52.0
python-dotenv==1.1.0
beautifulsoup4==4.13.4
requests==2.32.3
pytest==8.3.5
chardet==5.2.0
```
- `requirements-lock.txt`: 98 lines; `Crawl4AI==0.9.3` (`:19`), `playwright==1.52.0` (`:61`), `requests==2.32.3` (`:78`). EVIDENCE.
- `.python-version`: `3.12.3`. EVIDENCE.
- **Installed versions: GAP.** No `venv/` in this checkout. The pyenv global interpreter (3.12.3) has neither package: `importlib.metadata.version('crawl4ai')` and `('playwright')` both raise `PackageNotFoundError`. It does have `requests 2.31.0` — **not** the pinned 2.32.3. Last recorded installed state: crawl4ai 0.9.3 / playwright 1.52.0, pins == lock (`session_2026-09-07.md:21`). Chromium build last recorded: Headless Shell 136.0.7103.25, playwright build v1169 (`RUN_NOTES.md:13`); whether `~/.cache/ms-playwright` still has it was not checked.
- **Consequence:** before any ABM work can run the 54-test regression or a smoke here, the venv must be rebuilt (`README.md:10-13`) — an install, so outside this mission.

### 8. Surfaces

- **`.gitignore` on outputs** — `.gitignore:176-178`: `outputs/*` ignored, `!outputs/.gitkeep` kept. Everything a run writes is local-only. Also ignored: `.env`, `venv/`, `.venv` (`:131-134`), and note `*.manifest` (`:32`, PyInstaller block) — it does **not** match `manifest.json`, harmless. EVIDENCE.
- **`agent_docs/` layout** (7.4 MB, all tracked):
```
agent_docs/
├── ACTION/    README.md, web-factory-p1-bim000/ (spec, brief, prompts, retrospective, CLAUDE.md),
│              web-factory-p1-bim001/ (same five + QA/: 6 reports, journal, 4 driver scripts, INPUTS/, evidence/)
├── RECON/     README.md (0 bytes), OLD/
├── RESPONSES/ 11 BIM001_* files, OLD/ (19 C1 + bim000 files)
├── SESSIONS/  session_2026-09-02 … 09-07, + 09-18 (untracked)
└── SKILLS/    README.md, stark-recon-skill-v1.1/ (SKILL.md, CLAUDE.md, README.md, examples/, references/, templates/)
```
  No `KIP_REGISTRY.md` anywhere (root CLAUDE.md names it as mandatory) — GAP. No ABM/bim002 module folder under `ACTION/` yet.
- **`RECON/` contents:** live folder holds only the empty `README.md`. `RECON/OLD/` holds four files:
  - `READ_pre-bim001_2026-09-06.md` (14,581 B)
  - `RECON_crawl4ai-exp-project-v1_baseline_2026-09-02.md` (12,818 B)
  - `RECON_stark-web-factory-scrapper-v1_post-c1_2026-09-04.md` (21,083 B)
  - `RUN_ANALYSIS_baseline-run-002_2026-09-05.md` (15,547 B)
- **Ditto extraction reports: none present.** `grep -ril ditto agent_docs` → 0 files; no filename contains "ditto". EVIDENCE.

### 9. Sizes

- **On disk now: GAP.** `outputs/` = `.gitkeep` (0 bytes), 0 run folders, 0 pages (GAP-0).
- **Last recorded runs (both partial, `--limit 10` of 194; no full-site run is recorded anywhere):**

| Run | Pages | HTML bytes (sum) | Range per page | Wall | Source |
|---|---:|---:|---|---|---|
| `2026-09-07T04-10-56Z` (Cody live, latest) | 10 captured / 184 skipped | **4,330,489** (4.13 MiB) | 378,922 – 598,952 | 85 s (04:10:56 → 04:12:21) | `QA_LIVE_BIM001_2026-09-07_1017.md:49`, `:59-70` |
| `2026-09-06T07-30-16Z` (Claudy smoke) | 10 captured / 184 skipped | 4,331,951 | 378,924 – 600,508 | 100.6 s | `BIM001_complete_2026-09-06.md:34`, `:49` |

  Sums are my arithmetic over the listed per-page values — INFERENCE. The 09-06 report's own "3.6 MB total" (`BIM001_complete_2026-09-06.md:122`) does not match its listed bytes (4.33 MB) — flagging the discrepancy, not resolving it.
- **Projection (INFERENCE):** mean ≈ 433 KB HTML/page → 194 pages ≈ **84 MB** HTML per full run; at ~7 s fetch + 3.5 s mean pause ≈ **34 min**. Markdown adds ≈ 19 KB/page (`RUN_NOTES.md:107-125`, 6–30 K chars). Manifest overhead ≈ 0.35 KB/page.

---

## PART B — NOT RUN

The mission text makes Part B conditional on Director approval, and no approval was given in this session. **Zero network requests were made.** Nothing was saved to the scratchpad.

Ready to execute on a "go": three GETs via `requests` with `discover_site.sitemap_utils.USER_AGENT`, 3 s apart, raw bodies + headers to the session scratchpad. One thing to rule on first: the only `requests` available without an install is pyenv-global **2.31.0** (pin is 2.32.3, no venv). For three plain GETs the difference is immaterial, but it is not the pinned stack — say if you want the venv rebuilt first instead.

## Open items for the Director

1. No tags and no merge commits exist — if ABM bindings want a tag anchor (`bim000-certified`, `bim001-certified`), that is an Operator git action.
2. No real manifest survives anywhere; live evidence dirs were never tracked. A fresh `--limit 10` run would restore one.
3. No venv on this checkout: regression (54) is unverified here today.
4. `RECOVERY.md` still says "pending Director merge" — stale; the merge is on `main`.
5. `agent_docs/KIP_REGISTRY.md` does not exist.
6. Part B awaits approval.
