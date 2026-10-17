# Original scraper comparison — COMPLETE

**Director: Tony · Architect: JARVIS · Engineer: Cody**

**What we learned:** Both repositories capture pages with Crawl4AI’s browser. The current scraper did not replace browser capture with curl or requests. It changed the Crawl4AI version, user agent, input handling, pacing, status checks and saved artifacts. The explicit browser load settings remain the same. These are meaningful differences, but they do not prove why a later request was refused.

**What is done:** Source comparison, repository identity checks, installed-version inspection, historical evidence review and a one-page reproduction recipe. No target website was contacted, no crawler or test was run, and no dependency or Git state was changed during this comparison. GitHub-only source reads were authorized and performed.

**Next move:** JARVIS should decide whether a separately authorized, browser-based one-page experiment is useful, with an explicit allowance for redirects and subresources. First establish the original runtime and which machine/network Tony used. The recipe below is **NOT RUN** and is not an instruction to resume ABM, P0 or P1.

**Evidence labels:** **Observed** means files, metadata or repository state inspected during this comparison. **Historical** means an earlier report or committed artifact. **Hypothesis** means a possible explanation without a controlled comparison. **Gap** means evidence unavailable. Source settings and historical results are not current transport tests.

## 1. Repository identities and scope

| Item | Original | Current |
|---|---|---|
| Local path | `/home/moose/python/crawl4ai-exp-project-v1` | `/home/moose/python/stark-web-factory-scrapper-v1` |
| Verified origin | `https://github.com/ahmedmusawir/crawl4ai-exp-project-v1.git` | `https://github.com/ahmedmusawir/stark-web-factory-scrapper-v1.git` |
| Branch | `main` | `wf-scrapper-abm` |
| Full HEAD | `aec5de5e46689f430762d662af80ef22409bf834` | `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f` |
| Working tree | Clean when checked | Pre-existing deletions/moved reports and untracked diagnostic/intake work; details in §8 |

**Observed change in availability:** The original was absent during the initial local search; the earlier blocked response and ZIP remain preserved. Following Tony’s GitHub authorization, public `main` was resolved to the original SHA above, whose commit date is `2026-09-02T05:33:05Z`. At `2026-10-01T15:37:47Z`, a local original checkout was present. Its origin, branch and HEAD were then verified read-only. All 17 downloaded source/document snapshots match that checkout byte-for-byte. This mission did not create the checkout; who created it was not established.

The ZIP records provenance in `crawl4ai-exp-project-v1/SNAPSHOT_PROVENANCE.json`, `TREE_METADATA.json` and `LOCAL_CHECKOUT_IDENTITY.json`. Each downloaded snapshot was checked against the pinned Git blob SHA and given a SHA-256. This fixes the comparison to a commit rather than a moving GitHub branch. [Original pinned source](https://github.com/ahmedmusawir/crawl4ai-exp-project-v1/tree/aec5de5e46689f430762d662af80ef22409bf834).

Below, **O:** means the original repository root; **C:** means the current root. Both prefixes also name separate directories inside the ZIP. Line references are to the inspected snapshot. Root `CLAUDE.md` and recovery/session context were treated as historical instructions where they conflict with this mission. No applicable `AGENTS.md` was found. Tony’s current Director / JARVIS Architect / Cody Engineer assignment governs; historical commands to build, test, install or resume were not executed.

## 2. Entry points: discovery is separate from capture

| Operation | Original implementation | Current implementation |
|---|---|---|
| Sitemap discovery | `python discover_site/discover.py <base-url>`, choose `1`; requests GET `/sitemap.xml`, then child sitemap URLs | `venv/bin/python -m discover_site.discover <base-url>`, choose `1`; same basic XML flow using a shared requests Session |
| Homepage link discovery | Same script, choose `2`; requests + BeautifulSoup | Same module, choose `2`; shared Session + BeautifulSoup |
| JS sidebar discovery | `python discover_site/smart_discover.py <docs-url>`; direct Playwright Chromium, expands navigation and writes `outputs/discovered_pages_final.json` | Module removed; its deletion is recorded in `C:RUN_NOTES.md:98` |
| Page capture | `python smart_crawler/crawler.py` from original root, or module invocation; reads fixed `outputs/discovered_pages_final.json`, asks for `y`, then Crawl4AI | `venv/bin/python -m smart_crawler.crawler --project CyberizeGroup --limit 10`; default `outputs/discovered_pages.json`, supports `--input`, requires project, no interactive confirmation |
| curl | Not used in the inspected product discovery/capture paths | Not used in those product paths; curl appears in the separate access diagnostic |

Evidence: `O:discover_site/discover.py:9,54–83`; `O:discover_site/sitemap_utils.py:6–35`; `O:discover_site/smart_discover.py:23,39–51,60–108,194–219`; `O:smart_crawler/crawler.py:132–177,180–221`; `C:discover_site/discover.py:9–13,57–86`; `C:smart_crawler/crawler.py:347–357,453–513`.

The original normal discoverer writes `discovered_pages.json`, while its crawler reads `discovered_pages_final.json`. The sidebar discoverer writes the latter directly. Therefore original normal discovery and capture were not a seamless two-command pipeline without preparing the expected input. Current code removed that mismatch.

**Documentation corrections:** Original crawler comments name `crawler_v2_batch.py` and claim v0.7.x, but the actual file is `smart_crawler/crawler.py` and the lock pins 0.6.3 (`O:smart_crawler/crawler.py:3–8`; `O:poetry.lock:661–662`). Its sidebar usage text similarly names an absent `smart_discover_v2.py` (`O:discover_site/smart_discover.py:199–201`). The older recon’s assertion that the flat `sitemap_utils` import prevents running `python discover_site/discover.py` from the repository root is incorrect: script execution adds the script directory to Python’s import path. The package-style `python -m discover_site.discover` is the problematic original form without path adjustments. This is static reasoning, not a command executed today (`C:agent_docs/RECON/OLD/RECON_crawl4ai-exp-project-v1_baseline_2026-09-02.md:56`; `O:discover_site/discover.py:9`).

## 3. What materially changed

| Behavior | Original | Current | Interpretation |
|---|---|---|---|
| Capture engine | AsyncWebCrawler, browser-backed | AsyncWebCrawler, browser-backed | Same basic capture method |
| Crawl4AI | Lock 0.6.3 | Pin and installed 0.9.3 | Library behavior/defaults can differ |
| Browser mode | Explicit `headless=True` | Explicit `headless=True` | Not a headful-to-headless switch |
| User agent | Short Windows/WebKit UA ending `AppleWebKit/537.36` | Full Windows Chrome/140 UA ending `Safari/537.36`, shared with discovery | Browser identity and derived headers can differ |
| Capture cache | `CacheMode.BYPASS` | Same | Not an intentional cache-mode change |
| Explicit load settings | 90,000 ms page timeout; 3-second post-load delay; wait for images | Same three settings | Neither is a 30-second hard mission deadline |
| Inter-page pacing | Sequential loop, no explicit inter-page sleep | Sequential loop, random 2–5 seconds before later pages | Pacing change affects batches; no pause precedes the sole page in a one-page run |
| Failure classification | Exception/no result/`success=False`/empty markdown; no independent HTTP ≥400 gate | Explicit HTTP ≥400 gate; 403/429 classified blocked | Current reports errors the original may have handled differently |
| Stop rule | Fail one page and continue | Stop after three consecutive 403/429 pages; other failures reset that counter | Neither product implements the recent diagnostic’s first-refusal global stop |
| Output location | Relative to process CWD; creates `outputs/pages` at import | Anchored to repository root; creates directories in main | CWD changes original output destination |
| Artifacts | Markdown file per successful page, console summary | Markdown + summary JSON + project run HTML, manifest, absences and stage log | Current has more evidence and different overwrite behavior |

Evidence: `O:smart_crawler/crawler.py:23–27,42–99,102–177`; `C:smart_crawler/crawler.py:43–58,102–191,225–295,393–450`. Original and current both prefer `fit_markdown`, then `raw_markdown`; neither inspected run configuration supplies a content filter (`O:76–99`; `C:153–164`). [Pinned original browser settings](https://github.com/ahmedmusawir/crawl4ai-exp-project-v1/blob/aec5de5e46689f430762d662af80ef22409bf834/smart_crawler/crawler.py#L151).

**Discovery HTTP behavior:** Both sitemap implementations use a 10-second requests timeout, allow requests’ default redirect following, parse child sitemaps, and lack a shared pacing coordinator or mission-wide request budget. Original calls `requests.get`; current uses a Session with the full project UA. A child sitemap error is caught while iteration can continue. Neither explicitly installs an automatic retry policy. Requests’ timeout is not a hard total wall-clock limit. Neither wrapper forcibly upgrades input `http://` URLs to HTTPS; sitemap-root construction preserves the supplied scheme. Redirects can change scheme or host, and there is no redirect destination allowlist. See `O:discover_site/sitemap_utils.py:6–43`; `C:discover_site/sitemap_utils.py:16–54`.

**Browser redirects and resources:** Neither capture wrapper blocks redirects, limits HTTP request count, restricts browser subresources to the page’s host, or supplies explicit request interception. One `arun` can generate redirects plus scripts, images, styles, fonts, frames and page-driven fetches. Browser traffic may be concurrent despite sequential top-level pages. `CacheMode.BYPASS` is not a promise that every browser asset is fetched or that exactly one request occurs. Current installed code calls `page.goto` at `C:venv/lib/python3.12/site-packages/crawl4ai/async_crawler_strategy.py:762–765`.

**Defaults are not frozen by these wrappers:** Current installed Crawl4AI defaults to Chromium, JavaScript enabled, `wait_until="domcontentloaded"`, no explicit proxy, and `ignore_https_errors=True`. Thus the current product browser does not inherit the access diagnostic’s explicit TLS-verification guarantee. These defaults were read, not changed. Original 0.6.3 implementation defaults were not inspected and must not be assumed identical. Evidence: current installed `async_configs.py:820,835–845,858,1667`; selected values and file hashes are retained in `C:OBSERVED_RUNTIME.json`, without packaging dependencies.

## 4. Dependency and environment evidence

| Package | Original poetry.lock | Current requirements / lock | Current installed |
|---|---:|---:|---:|
| Crawl4AI | 0.6.3 | 0.9.3 | 0.9.3 |
| Playwright | 1.52.0 | 1.52.0 | 1.52.0 |
| requests | 2.32.3 | 2.32.3 | 2.32.3 |
| beautifulsoup4 | 4.13.4 | 4.13.4 | 4.13.4 |
| python-dotenv | 1.1.0 | 1.1.0 | 1.1.0 |
| pytest | 8.3.5 | 8.3.5 | 8.3.5 |
| chardet | 5.2.0 | 5.2.0 | 5.2.0 |

Evidence: `O:poetry.lock:244,519,661,2213,2721,2757,2986`; `C:requirements.txt:1–8`; `C:requirements-lock.txt:10,14,19,61,72,73,78`. Full dependency snapshots are included, not installed dependency directories. The table covers relevant direct/runtime packages, not a claim that all transitive packages match across repositories.

**Observed:** Current venv Python is 3.12.3, compiled September 18, 2026, GCC 13.3.0, on Linux. Installed versions were read using `importlib.metadata`, without importing product or Crawl4AI code. Playwright’s installed browser manifest specifies Chromium/Headless Shell 136.0.7103.25, revision 1169. Cache directories for revisions 1169 and 1234 exist; directory presence does not prove what a particular historical process launched. No browser executable was run.

**Original runtime gap:** Neither `O:venv` nor `O:.venv` exists; no matching original Poetry environment was found in the standard user Poetry cache. Original `.python-version` specifies 3.12.3, but installed original-runtime versions and actual historical browser binary remain unverified. Original pyproject uses wildcard crawler/browser requirements; only the committed lock pins exact versions. Its phantom `prompt_agent` package and pip-versus-Poetry instruction drift are documented at `O:pyproject.toml:7–19` and `O:agent_docs/SESSIONS/session_2026-09-02.md:27,45`. No repair or install was attempted.

**Proxy finding, narrowly scoped:** No explicit proxy configuration is present in either inspected discovery/capture path. The eight common upper/lowercase HTTP(S)/ALL/NO_PROXY variables are absent in this comparison process. No `.env`, credentials, cookie store or global network configuration was opened. Requests’ default environment behavior is not disabled by either wrapper. This does not establish Tony’s historical proxy, VPN, browser profile or network state. Presence-only metadata is in `C:OBSERVED_RUNTIME.json`.

## 5. What actually succeeded historically

| Date / evidence class | What the evidence supports | Limits |
|---|---|---|
| Original artifact last changed in commit `25c47ce9f5625d0183cede2f4ae3592094680bbb`, December 18, 2025, 10:09:30Z | Original input includes `https://marketplace.gohighlevel.com/docs/oauth/GettingStarted`; matching Markdown is 6,254 bytes, titled “Getting Started” and contains that URL | Committed capture artifact, not a retained HTTP status/redirect trace or exact crawl timestamp; machine and generating runtime unknown |
| September 2, 2026, current derivative C1 | `RUN_NOTES.md` records discovery of 194 CyberizeGroup URLs and 5/5 page captures under Crawl4AI 0.6.3, Linux/pyenv Python 3.12.3, Playwright Chromium 1169 | This is the derivative’s C1 result, not proof that unmodified original source captured CyberizeGroup on Tony’s earlier machine |
| September 5, 2026, current derivative | Controlled 0.9.3 upgrade recorded 10/10 HTTP-200 captures; later UA/pacing flow also recorded successful capture | Shows that the upgrade and later settings have succeeded historically; does not establish current access |
| September 7, 2026, 04:10:55–04:12:21Z, current BIM001 QA | Exact project/limit command recorded 10 captures, all 200, on candidate `eee039a2c06cc1aeaa3e9dfb52e17db9d3ddb20a`; rendered HTML, Markdown and manifests reported | QA report remains, but its linked `QA/evidence/live_2026-09-07_eee039a/` and runtime run directory are absent locally; raw artifacts cannot be reverified here |
| October 1, 2026, 14:58:16–14:58:19Z, separate earlier diagnostic | One curl GET of CyberizeGroup `/sitemap_index.xml` returned 429 and stopped all live work | No Python comparison or browser attempt occurred; not a measurement of either capture implementation |

Original page provenance, hashes and commit metadata are in `O:HISTORICAL_PAGE_EVIDENCE.json`. Matching Markdown SHA-256: `14e8c150210d53ad14b720c1468581dbc4483916c19c6ae615a148450b233c58`. It was inspected from GitHub and matched locally, but its contents and bulk outputs are excluded from the ZIP. The pinned tree contains 712 page Markdown files and 710 summary files; these counts are not 712 verified HTTP successes. [Original committed page](https://github.com/ahmedmusawir/crawl4ai-exp-project-v1/blob/aec5de5e46689f430762d662af80ef22409bf834/outputs/pages/marketplace-gohighlevel-com-docs-oauth-gettingstarted.md), [artifact’s last-change commit](https://github.com/ahmedmusawir/crawl4ai-exp-project-v1/commit/25c47ce9f5625d0183cede2f4ae3592094680bbb).

Current historical references: `C:RUN_NOTES.md:3–52,78–128`; `C:agent_docs/ACTION/web-factory-p1-bim001/QA/QA_LIVE_BIM001_2026-09-07_1017.md:7,15–41,59–70`; `C:agent_docs/RESPONSES/response_2026-10-01_210015_web-recon-access-check.md:1–7,26–55`.

Previously successful CyberizeGroup URLs explicitly recorded include `/blog/`, `/web-design-process/`, `/what-to-look-for-in-ppc-agency/`, `/our-covid-19-plan/` and `/5-foundational-principles-for-online-success/`. The September 7 QA report gives ten exact URLs and HTML byte counts. Its documented command was `/home/moose/python/stark-web-factory-scrapper-v1/venv/bin/python -m smart_crawler.crawler --project CyberizeGroup --limit 10`, from the current repository root. Historical test counts in these documents were not rerun during this comparison.

## 6. One-page original reproduction — prepared, NOT RUN

**Can original capture run independently of sitemap discovery? Yes.** `O:smart_crawler/crawler.py:151–177` exposes `crawl_all(urls)` and creates its own browser with the original BrowserConfig. Calling it with one URL bypasses discovery, the fixed input JSON and the batch confirmation prompt. Current capture is also separable through a prepared one-item `--input` file or its `run(urls)` function (`C:smart_crawler/crawler.py:347–354,447–450`).

**Exact one-page source invocation:** The following is a derived recipe, not a recovered historical shell transcript. It retains the original source’s headless setting, short UA, bypass cache, 90-second timeout, 3-second delay and image wait. It deliberately selects the original GHL page with a committed capture artifact.

**Prerequisite:** `python` must resolve to an already provisioned original lock-matched environment with its browser available, while the original checkout remains at the recorded SHA. Such an environment was not found here. The two version guards prevent accidentally treating the current 0.9.3 environment as the original; they do not validate the entire environment. Do not run or provision this as part of the completed comparison.

```bash
cd /home/moose/python/crawl4ai-exp-project-v1 || exit 1
python -B - <<'PY'
import asyncio
from importlib.metadata import version

assert version("crawl4ai") == "0.6.3", "Original Crawl4AI required"
assert version("playwright") == "1.52.0", "Original Playwright required"

from smart_crawler.crawler import crawl_all

asyncio.run(crawl_all([
    "https://marketplace.gohighlevel.com/docs/oauth/GettingStarted"
]))
PY
```

**What it writes:** Importing the original module creates `O:outputs/pages/` if absent. If capture yields nonempty Markdown and writing succeeds, the application writes:

`/home/moose/python/crawl4ai-exp-project-v1/outputs/pages/marketplace-gohighlevel-com-docs-oauth-gettingstarted.md`

**Yes, it would overwrite an existing file:** that 6,254-byte historical artifact is already present. `write_text` does not request exclusive creation (`O:smart_crawler/crawler.py:23–27,115–119`). The invocation does not write the discovery input, summaries, a manifest or a raw HTML file. It prints to the console; no log redirection is included. Python `-B` suppresses bytecode writes, but Crawl4AI/Playwright can create runtime/cache/profile/temp files beyond the application output; exact original-library paths are unverified without that runtime. A future mission must decide how to preserve the existing artifact before execution.

**Request count is not bounded by one:** this supplies one top-level URL, but redirects, browser assets and page JavaScript can generate more requests, including other hosts. The original function has no global request ceiling or first-refusal stop. It therefore does not satisfy the earlier six-request diagnostic’s boundaries merely because its input list has one page.

## 7. Explanations worth testing, and what remains unknown

**Hypotheses, not causes:**

1. **Different layer measured:** Earlier curl/requests sitemap refusals do not predict browser page capture conclusively. They differ in client, URL and request context. A browser success would not prove discovery works either.
2. **Library and identity differences:** Crawl4AI 0.6.3 versus 0.9.3, the changed UA and derived client hints could alter behavior. Current UA advertises Chrome 140 while installed Playwright’s expected Chromium revision is 136. No controlled experiment establishes an effect. Recorded successful 0.9.3 captures weigh against treating the upgrade alone as a proven cause.
3. **Changed reporting:** Current explicit HTTP checks may classify some responses as failures that the original’s weaker success gate would handle differently. There is no matched response proving that happened.
4. **Environment or time:** Source IP/network, site rules, browser/runtime details, server load and elapsed time could matter. This mission contains no current target-site measurement to separate them.

**Still missing about Tony’s successful machine:** exact operating system/release, interpreter environment and transitive versions, browser binary/revision and launch arguments, source checkout/dirty changes at that time, working directory and command, timestamp, selected URL and scheme, redirect chain, request headers/profile state, IP/network/VPN/proxy state, and original console/HTTP evidence. Linux and Python 3.12.3 in the later current-repo C1 report cannot be assigned retroactively to the earlier original run.

**Architect decision:** Select the question before authorizing more traffic: reproduce the original GHL artifact, test original browser behavior against a previously captured CyberizeGroup page, or compare capture implementations under controlled conditions. These are different experiments. Any browser mission needs explicit request-scope and output-preservation terms. No cause or full-crawl readiness is certified here.

## 8. Preservation, deliverables and completion

**Current pre-existing uncommitted work:** Eleven tracked response paths were already deleted, with matching names untracked under `agent_docs/RESPONSES/OLD/`: `BIM001_GATE_Q_RECORD_2026-09-07.md`, `BIM001_chunk1_2026-09-06.md` through `BIM001_chunk6_2026-09-06.md`, `BIM001_closeout_2026-09-07.md`, `BIM001_complete_2026-09-06.md`, `BIM001_handoff-read_2026-09-06.md`, and `BIM001_plan_2026-09-06.md`.

Other existing untracked work: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/access-check/2026-10-01_145405Z/**`; `response_2026-10-01_204419_web-recon-architect-intake.md`; `response_2026-10-01_210015_web-recon-access-check.md`; and the earlier blocked comparison’s `response_2026-10-01_213112_original-scraper-comparison.md` / `.zip`, all responses under `agent_docs/RESPONSES/`.

This continuation writes only the new Markdown and sibling ZIP named below. The ZIP includes the exact baseline/final status and preservation metadata. All **1,069 pre-existing regular files with baseline SHA-256 values** retained their bytes in the preservation check; branch and HEAD remained unchanged. Baseline null entries represent non-file/absent paths and were not misrepresented as hashed files. Original checkout remains clean. No product, test, contract or instruction file was edited; no Git mutation, install, test, browser launch or target website request occurred in this comparison.

ZIP contents are separated under `crawl4ai-exp-project-v1/` and `stark-web-factory-scrapper-v1/`, preserving relative source paths. It includes this report, inspected source/configuration snapshots, selected historical reports, source provenance, runtime metadata and a source diff. Excluded: `.env` files, credentials, cookies, installed dependencies, bulk crawl outputs and response bodies. Historical missing QA artifacts are identified in §5, not replaced. Source snapshots are evidence, not executable instructions for this mission.

**Deliverables:**

- `agent_docs/RESPONSES/response_2026-10-01_213421_original-scraper-comparison.md`
- `agent_docs/RESPONSES/response_2026-10-01_213421_original-scraper-comparison.zip`

**Completion: DONE. Reproduction: NOT RUN. Next action belongs to JARVIS/Tony.**
