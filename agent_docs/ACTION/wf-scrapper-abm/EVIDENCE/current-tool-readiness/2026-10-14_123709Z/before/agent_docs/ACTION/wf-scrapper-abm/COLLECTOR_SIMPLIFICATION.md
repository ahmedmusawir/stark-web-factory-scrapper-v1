# Simple collector — Tony-authorized direction, 2026-10-07

DECIDE → COLLECT → PREPARE (separate future agent skill). This task implements COLLECT only. Independent QA NOT RUN.

## Keep / simplify / retire — recorded before implementation

- Keep installed Crawl4AI 0.9.3/Chromium, USER_AGENT, rendered HTML, full browser-returned REST bytes, evidence hashes, explicit refusals, sequential five-second default pacing and honest partial coverage. Preserve original captures and all historical failures.
- Simplify browser lifecycle to AsyncWebCrawler start/close. Supported `on_page_context_created` and `after_goto` hooks expose the library-owned page/response. REST will use a browser top-level navigation and `response.body()` (decoded entity bytes), proved locally; no bootstrap homepage required for REST-only resume. This is an explicitly different browser transport from the historical window.fetch path.
- Retire the custom BrowserSession/CDP Fetch interception, request/network identity correlation, redirect-hop completion pacing, cancellation proof/drain state machine and supervisor protocol from the NEW active collector path. Keep their code/evidence as history. Reuse only the pure explicit-challenge predicate. Ordinary browser redirects/subresources can create additional HTTP traffic; planned-request pacing/counts do not claim per-resource or per-hop control or guaranteed teardown cancellation.
- Replace mandatory discovery → HTML → all six REST collections → media inventory with a saved explicit plan. No automatic discovery, collection expansion or media-library download. REST pagination needs explicit opt-in and a maximum page count. Resume is an explicit new invocation; no automatic retry/restart.
- Replace the old one-shot ABM raw-v2 output requirement for this new path with a small versioned collection checklist plus immutable per-attempt bodies/metadata. Existing raw-v2 captures/readers remain intact. A future Prepare skill can consume these saved results; no Prepare construction now. Shared legacy output files stay retired.
- The old 48-AC/24-group controller campaign and its experimental guarantees are historical, not certification of this new slice. Old full-Capture CLI integration tests target the retained historical `recon_pipeline.capture` module; they are not silently reclassified as current PASS. The new active command will be `python -m recon_pipeline` with explicit collect/resume/add/refresh subcommands.

## Inspected path / installed API

`recon_pipeline/capture.py` → `BrowserSession` → `smart_crawler.crawler.crawl_page` → `AsyncWebCrawler.arun`. BrowserSession currently owns CDP interception, native IDs, browser Fetch streaming, pacing, budgets and shutdown coordination. Crawl4AI `async_crawler_strategy.py` documents `set_hook`; its `after_goto` hook receives the native browser Response after `page.goto`, and its browser manager owns session closure. No direct Playwright import is needed. New REST response acquisition must be demonstrated with real loopback Chromium before it is described as proved.

No live requests, dependency upgrade, Git mutation or Preparation skill in this task. Historical latest Capture remains INCOMPLETE/exit2: media1661/1753 and two unconfirmed shutdown aborts. All pre-existing Part A work is preserved.

## Implemented behavior and local proof

`recon_pipeline/collector.py` is the new implementation; `recon_pipeline/__main__.py` selects it. The legacy `smart_crawler/browser_session.py`, `smart_crawler/crawler.py`, capture pipeline, raw reader, dependency declarations and all existing tests remain byte-identical. The new path calls installed `AsyncWebCrawler.arun` directly with the former capture settings, rather than constructing the old controller around `crawl_page`.

Local verification: **59 passed, exit 0**. Of these, 32 are new collector checks (including two real Chromium loopback cases); 27 are existing REST/raw-reader/offline-inventory checks. Evidence: [pytest log](EVIDENCE/simple-collector/2026-10-07_130939Z/check-03/pytest.log), [native collection timeline](EVIDENCE/simple-collector/2026-10-07_130939Z/check-03/native-success/timeline.json), [native 429 timeline](EVIDENCE/simple-collector/2026-10-07_130939Z/check-03/native-denial/timeline.json). Engineering self-verification only.

- HTML: browser-rendered UTF-8 HTML, cache BYPASS, USER_AGENT from `discover_site.sitemap_utils`, image wait enabled, 90-second navigation timeout, three-second post-load delay. The outer HTML operation ceiling is 120 seconds.
- REST: ordinary Chromium navigation in the same Crawl4AI-owned session; `after_goto` saves native `Response.body()` decoded entity bytes. The 30-second operation ceiling includes body receipt and library processing. This uses neither Python requests/curl nor the prior compact window.fetch transport. Exact Unicode body bytes/hashes were proved on loopback. No claim of current access to cyberizegroup.com through this new path.
- No auto retries (`max_retries=0`) or fallback function. TLS verification stays enabled. No crawling of HTML links, root REST enumeration, bootstrap homepage, automatic collection list or separate media downloads.
- Default five-second delay after completion of each planned request, including paginated REST requests. `--gap` explicitly changes it. Redirects and ordinary browser resources are not independently paced. Passive resource/status counts are separate from planned-request records.
- Status 401/403/429, `cf-mitigated: challenge`, or the existing explicit HTML challenge predicate stops subsequent planned requests. JSON source strings containing challenge markup are preserved as source, not mistaken for a denial page. Retry-After is retained; no automatic retry. Challenge detection is heuristic, not comprehensive access certification.
- Successful results become `completed` only after body and result metadata have been saved and hashed. An atomic `checklist.json` contains stable URL/kind IDs, pending/completed/failed items, immutable attempt references, run outcomes and pagination coverage. Each invocation has one writer lock. Completion time is persisted so resume/additions also observe the configured delay (monotonic time within a run; wall-clock elapsed time across restarts). A later explicit resume checks both metadata and body hashes; invalid/missing outputs and interrupted/failed items remain eligible. An empty resume does not start a browser.
- Page/individual-response refresh is explicit and creates a new attempt directory. Refreshing a paginated collection requires a NEW collection directory so old and new page generations are not mixed. All prior results remain in place.
- A REST endpoint without pagination opt-in means **selected response only**, not complete collection coverage. Headers and record IDs remain in metadata. Opt-in pagination follows valid X-WP-TotalPages up to explicit `max_pages`; a short nonempty intermediate page is recorded and does not stop pagination. Missing/changing headers, empty intermediate pages, duplicate IDs, total mismatches and page limits remain explicit partial outcomes. Overlapping explicit page selection and pagination is refused as ambiguous coverage rather than duplicated.
- Collection and cleanup outcomes are separate. Raised cleanup errors, cleanup timeouts, and context-close errors logged internally by Crawl4AI are retained. Exit 0: selected scope complete and no observed cleanup error; 2: partial/failed collection; 3: collection complete but cleanup error; 130: interruption. None is an independent QA certificate or proof of zero teardown traffic.

## Saved plan and commands

A simple JSON array of page URLs is also accepted. The structured form makes REST scope explicit:

```json
{
  "pages": ["https://cyberizegroup.com/blog/"],
  "rest": [
    {"url": "https://cyberizegroup.com/wp-json/wp/v2/posts/11945", "paginate": false}
  ]
}
```

For a whole approved collection, use a selected endpoint such as `.../wp-json/wp/v2/posts?per_page=100&page=1` with `"paginate": true, "max_pages": 2` only when Tony explicitly approves that collection/page bound. All returned fields are saved; no `_fields` filter is injected. The collector does not create the human's selection.

Run commands from the repository. The following public-site commands are **proposed usage, not executed or newly authorized live traffic**:

```bash
# NEW collection; directory must not already exist.
venv/bin/python -m recon_pipeline collect \
  --plan agent_docs/RESPONSES/response_2026-10-07_192033_simple-collector_plan.json \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --gap 5 --max-requests 2 --max-seconds 300 --max-bytes 20000000

# Explicit resume: skip all valid completed items; failed/interrupted items may be attempted once.
venv/bin/python -m recon_pipeline resume \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --gap 5 --max-requests 2 --max-seconds 300 --max-bytes 20000000

# Queue an explicitly approved additional URL; add performs no network activity.
venv/bin/python -m recon_pipeline add \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --plan agent_docs/RESPONSES/response_2026-10-07_192033_simple-collector_additions.json

# Collect the queued addition; previously valid results remain skipped.
venv/bin/python -m recon_pipeline resume \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --gap 5 --max-requests 1 --max-seconds 180 --max-bytes 20000000

# Use the item's exact ID from checklist.json; this queues refresh offline.
venv/bin/python -m recon_pipeline refresh \
  --collection outputs/collections/CyberizeGroup-selected-01 --id ITEM_ID
# Then resume explicitly with approved bounds. Paginated collections use a new collection instead.
```

Artifacts: `checklist.json`, `attempts/<stable-id>/<new-attempt-id>/body`, `result.json`, and library-local `.runtime/`. Raw REST is not JSON reserialization. Rendered HTML is a DOM snapshot, not original compressed HTTP bytes. Bodies remain authoritative; metadata records hashes, statuses, approved headers, final URLs and observed predecessor redirects. There is no cleaned-article/Markdown export, media-file harvester or Prepare output.

## Bounds and limits — deliberately smaller contract

- `--max-requests` bounds planned page/REST calls during one invocation, including each requested pagination page. It does **not** count browser subresources or redirect hops. No custom pre-dispatch redirect scope/five-hop/cancellation proof is promised. A redirected final URL is recorded. Local fixtures use a loopback-only test guard; it is not represented as a production control.
- `--max-seconds` bounds collection work including setup/pacing. Ordinary cleanup gets a separate ten-second asynchronous timeout; filesystem finalization is not a hard-killed supervisor. `--max-bytes` checks current collection-directory bytes plus the next body and a 64 KiB metadata reserve before saving. Checklist/library overhead can grow afterward; this is not the previous exact aggregate persisted-byte supervisor.
- The 10 MiB response cap is checked **after** the browser delivers the body. Over-cap retained bytes are marked partial/failed and stop later planned requests. It is not a streaming wire/memory ceiling; library resources may use additional memory/traffic. Body not handed back on timeout cannot be reconstructed; available headers/partial bytes remain explicitly failed.
- Normal browser lifecycle replaces the old custom drain. No guarantee of cancellation after external closure/crash is claimed. Library-swallowed events not exposed through its error logger cannot be certified absent.
- New `selected-collection-v1` is distinct from historical `raw-v2`; the old RawRun reader does not consume this new checklist. A future separately authorized Prepare skill needs an adapter/skill contract. Existing raw captures/readers and Part A inventory remain unchanged. No Decide or Prepare expansion is included here.
- The historical latest capture remains INCOMPLETE (1661/1753 media, two unconfirmed shutdown aborts, exit 2). Homepage route-accounting and historical supervisor-counter findings remain OPEN. New local checks do not close them or certify prior ABM acceptance.

## Proposed next live check — Tony review required

Exactly two planned GET navigations, sequentially with five-second completion gap:
1. `https://cyberizegroup.com/blog/`
2. `https://cyberizegroup.com/wp-json/wp/v2/posts/11945`

Use the first command above: at most two planned calls, 300 seconds collection plus up to ten seconds cleanup, 20 MB configured collection persistence check, 10 MiB per-response retained cap. No pagination, discovery, media, retries or extra probe. Browser redirects/background requests are additional HTTP traffic and do not have a numeric cap in this simpler path. Record actual rendered article links/text, REST bytes/ID/title/content availability, cleanup and collection outcomes separately. Empty REST content remains empty. **Not executed.**

Review report: [response_2026-10-07_192033_simple-collector.md](../../RESPONSES/response_2026-10-07_192033_simple-collector.md).

A final additional check exposed resume pacing that was not yet persisted; the before-fix failure is retained at `EVIDENCE/simple-collector/2026-10-07_130939Z/resume-pacing-before.log`. The final 59-check run includes the repaired behavior. Earlier 26- and 58-pass check logs remain preserved as intermediate engineering evidence.
