# Active tool — DECIDE → COLLECT → PREPARE

Current engineering readiness and historical acceptance mapping: [CURRENT_TOOL_SCOPE.md](agent_docs/ACTION/wf-scrapper-abm/CURRENT_TOOL_SCOPE.md). Start with [RECOVERY](RECOVERY.md) for the latest results and candidate handoff.

- **DECIDE:** `venv/bin/python -m recon_pipeline.decide` discovers bounded candidates, saves immutable numbered review and exact human HTML/REST choices, then exports a plan. [Usage](agent_docs/ACTION/wf-scrapper-abm/DECIDE.md).
- **COLLECT:** `venv/bin/python -m recon_pipeline collect --plan PLAN.json --collection NEW_DIR --gap 5 --max-requests N --max-seconds S --max-bytes B`; `resume --collection DIR` skips hash-valid completed items; `add --collection DIR --plan ADDITIONS.json` queues explicit additions offline; `refresh --collection DIR --id ID` queues replacement while retaining old attempts. Resume/collection require approved target scope/bounds. [Details](agent_docs/ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md).
- **PREPARE:** give the preparation agent a saved collection and [skill](agent_docs/SKILLS/web-recon-prepare/SKILL.md). Its offline helper extracts and validates; the agent inspects raw boundaries, corrects classifications and authors the source-linked brief/gaps. Growth Call’s known preliminary type error remains handled by that review; no automatic iframe capture.

Shot2 uses only local tests/saved evidence. Independent QA NOT RUN. The dated original README sections below preserve earlier tool/campaign/install history; old Capture+Prepare commands/output guarantees are not the current tool. Existing requirements lock/direct pins remain unchanged; clean-install proof remains pending.

## Current Prepare skill — 2026-10-11

Tony authorized [Web Recon Prepare v0.1](agent_docs/SKILLS/web-recon-prepare/SKILL.md): an offline agent workflow for a supplied saved collection. Cody/Claudy validate hashes, extract Markdown and author the architect brief/requests. This supersedes older “Prepare not implemented” wording for this small skill only; it does not resume the historical ABM P1–P6/E1/E2 campaign. Collection/recon are unchanged; no live requests/Git mutations. Current output/checkpoint: [RECOVERY.md](RECOVERY.md). Independent QA NOT RUN.

# DECIDE → COLLECT → PREPARE

DECIDE is now a separate command: `venv/bin/python -m recon_pipeline.decide`. It provides explicit sitemap/default recon, metadata-only WordPress review, saved human choices and export to the unchanged collector plan. See [DECIDE usage](agent_docs/ACTION/wf-scrapper-abm/DECIDE.md). Discovery/export does not start full collection. Prepare remains a future separate skill; independent QA NOT RUN.

# Current collector — explicit, resumable selection

The active `venv/bin/python -m recon_pipeline` command now takes **collect, resume, add, refresh** subcommands. Give it selected page URLs and explicitly approved REST endpoints; it does not discover a site, follow page links, collect every WordPress collection, or run Prepare.

See [current behavior and usage](agent_docs/ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md). The examples require Tony's live authorization before use against a public website. This implementation was checked locally only; independent QA NOT RUN.

The earlier README below documents the preserved historical discovery/crawl engine and installation baseline. It does not describe the new active collector or authorize its old live commands.

---

# Stark Web Recon — scraper v1

Discovery-and-crawl engine for Stark Industries web recon. Point it at a site, it enumerates the site's pages (sitemap or homepage links), then crawls each page with [crawl4ai](https://github.com/unclecode/crawl4ai) and writes one markdown file per page to `outputs/pages/`. That markdown is the raw material for later analysis phases. Phase 1 so far: C1 baseline → bim000 stage prep → bim001 raw HTML capture (see `CHANGELOG.md`).

## Setup

Canonical clean-install baseline (E-13, ABM revision 1.2). These are future setup instructions, **not authorization to install or test during the documentation/BUILD_READBACK pass**. Do not recreate the current working environment. Python 3.12.3 via pyenv; no Poetry. Use a new isolated environment only when setup/QA is authorized.

```bash
pyenv local 3.12.3
python -m venv venv
venv/bin/pip install -r requirements-lock.txt
venv/bin/pip check
```

Then run the normalized package comparison below. Only after that future setup is authorized, install the lock-matched browser if absent using `venv/bin/playwright install chromium`. No credentials are needed for public collection; do not print environment contents. `requirements.txt` remains the seven direct dependency declarations; `requirements-lock.txt` is the existing 98-pin installed-package snapshot. Neither is changed by this ruling. Matching it is a reproducibility check, not a promise of identical binaries across platforms.

**Exact comparison procedure:** use `pip freeze --all`; compare every distribution after normalizing package names (PEP-503) and versions. Exclude only pip/setuptools/wheel that are absent from the lock, recording their versions. If locked, they must match too. Reject non-exact pins/editables/URLs and duplicate normalized names; fail on any missing/extra/mismatch. `packaging` is already in the lock; this introduces no dependency.

```bash
venv/bin/python -B - <<'PYCOMPARE'
import hashlib, json, platform, re, subprocess, sys
from pathlib import Path
from packaging.utils import canonicalize_name, canonicalize_version
from packaging.version import Version

def pins(text):
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([^\s;]+)', line)
        if not match:
            raise SystemExit('Non-exact package entry; comparison refused')
        name = canonicalize_name(match[1])
        if name in result:
            raise SystemExit('Duplicate normalized package: ' + name)
        result[name] = canonicalize_version(str(Version(match[2])))
    return result

lock_path = Path('requirements-lock.txt')
expected = pins(lock_path.read_text())
installed = pins(subprocess.check_output(
    [sys.executable, '-m', 'pip', 'freeze', '--all'], text=True))
excluded = {name: installed.pop(name) for name in ('pip', 'setuptools', 'wheel')
            if name not in expected and name in installed}
differences = {name: {'expected': expected.get(name), 'actual': installed.get(name)}
               for name in sorted(set(expected) | set(installed))
               if expected.get(name) != installed.get(name)}
print(json.dumps({'python': sys.version, 'platform': platform.platform(),
    'lock_sha256': hashlib.sha256(lock_path.read_bytes()).hexdigest(),
    'tooling_excluded_only_when_unlocked': excluded,
    'normalized_packages': sorted(installed.items()), 'differences': differences}, indent=2))
raise SystemExit(bool(differences))
PYCOMPARE
```

Retain comparison output and separate `pip check` exit. Record Python executable/platform/architecture, lock hash, Playwright version and installed browsers.json revision/version. When a future authorized check launches Chromium, record actual browser.version and executable path/hash; cache presence alone does not prove the launched identity. Clean-environment QA remains NOT RUN. Full binding: [ABM rulings](agent_docs/ACTION/wf-scrapper-abm/ABM_RULINGS_1_2.md).

## Current product versus planned ABM

The run/output descriptions below document the existing product, which still has its older discovery/pacing/stop/Markdown behavior. They are **not the ABM launch plan or authorization to run live commands**. The future revision 1.2 implementation is described in [BUILD_READBACK](agent_docs/ACTION/wf-scrapper-abm/BUILD_READBACK.md); after implementation, E1 synchronizes shipped CLI examples with that behavior. Current checkpoint: AWAITING BUILD_READBACK REVIEW AND TONY'S BUILD APPROVAL.

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
