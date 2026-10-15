# DECIDE — recon and human selection

Tony-authorized direction, 2026-10-07. **DECIDE → COLLECT → PREPARE**. DECIDE and COLLECT have separate commands and output directories. The working collector and all its source/tests are unchanged. Prepare remains a separate future skill. Independent QA NOT RUN. This implementation was verified with localhost fixtures and saved captures only; no new live recon was run.

## Entry points and flow

- DECIDE: `venv/bin/python -m recon_pipeline.decide {recon,import,list,select,export}`.
- Existing COLLECT: `venv/bin/python -m recon_pipeline {collect,resume,add,refresh}` — unchanged.
- Recon/import saves a review; selection saves a new decision file; export saves a plan. None automatically invokes the next stage or collection. No embedded model, automatic ranking/exclusions, paid API or dependency change.
- Cody/Claudy can discuss the saved review with Tony. Only explicit recorded human choices become inclusions/exclusions. Unspecified rows stay UNDECIDED.

## Explicit modes and bounds

`recon --mode sitemap` reads a supplied sitemap, or reads `/robots.txt` for Sitemap directives. It follows same-origin sitemap index children within configured bounds. Without a usable declared/supplied sitemap, it records the gap; it never silently switches to link discovery or probes a list of guessed sitemap names.

`recon --mode default` reads the supplied page and expands same-origin links breadth-first. **This downloads some rendered pages and their ordinary browser resources**. It does not promise zero page downloads. It skips obvious image/script/style/archive links and REST links as HTML candidates. HTML MIME/title/date metadata and link labels are recorded where available; a linked label is evidence from the referring page, not proof of the target's own title/content.

Defaults: 12 planned requests total, 3 discovery page reads, depth 1, 1 metadata page per REST content type, 20 records per metadata page, 5,000 inventory candidates, 300 seconds collection work and five-second completion pacing. Bounds are configurable. `--max-pages` counts HTML or sitemap reads; `/robots.txt`, types and metadata calls also consume the shared `--max-requests` budget. Depth bounds followed pages/sitemap nesting; links found at the boundary can still be listed without being read. REST pagination uses the same pacing and overall request budget.

The existing browser transport is reused unchanged: ordinary Crawl4AI Chromium navigation, native Response.body for XML/text/JSON, rendered HTML for link discovery. No custom CDP controller, HTTP-client fallback or retry loop. TLS verification/USER_AGENT and timeouts remain those of the collector. First 401/403/429 or explicit challenge stops subsequent planned requests and preserves evidence/inventory. Cleanup errors are separate. Available partial recon is checkpointed at `recon-progress.json` and finalized into a review.

The candidate/next-request rule is **same origin** (scheme, host and port); www/apex are not silently merged. Browser redirects/resources can create additional traffic. An observed off-origin final redirect stops further recon, but there is no pre-dispatch per-hop scope interception or numerical background-resource bound in this simple transport. This limitation is inherited and explicit.

## Lightweight WordPress reconnaissance

- Directly request the standard `wp/v2/types` endpoint under the default `/wp-json/` API base, with `_fields=name,slug,rest_base,rest_namespace`. The root `/wp-json/` is never enumerated.
- `--wp-base` supports an explicitly supplied same-origin API mount. Other mounts are not automatically guessed. An absent `rest_namespace` uses the standard wp/v2 convention; unusual routes require review.
- Public types provide collection names/bases, including exposed custom post types. Pages/posts get priority. Attachment/media is explicitly excluded from enumeration; taxonomies/users are not content types and are not auto-collected.
- Each admitted collection request uses `per_page`, `page` and `_fields=id,link,title,type,slug,date,date_gmt,modified,modified_gmt`. Full content/SEO/media data is not requested for review. If the server ignores projection, the unexpected response is preserved as recon evidence, marked partial and not paginated further; it never becomes a completed full-capture task.
- Record X-WP-Total and X-WP-TotalPages separately from enumerated objects, unique IDs and actual review rows. Short nonempty pages do not terminate advertised pagination. Limits, unknown/changing totals, duplicate IDs, malformed responses, unavailable links and count mismatches stay explicit.
- Collection rows in the review are **REST scope choices**, separate from HTML document rows. Missing/unexposed types, blocked access and skipped budget-limited calls are not represented as verified empty collections.
- `--known-collection` reads validated saved collector output offline. An observed empty REST body can be attached as a **historical** warning with a file hash/date. It never causes a fresh content probe/retry. Post11945's warning is `needs_HTML_review_if_selected` in the supplied sample.

## Inventory and decision identity

`inventory.json` + `INVENTORY.md` hold stable URL/kind IDs, numbered rows, available title/MIME/WordPress type/dates, hashed source locators, REST item scope, unknowns and coverage limits. Fresh recon is labeled `FRESH_BOUNDED_RECON`; imports are `IMPORTED_CAPTURE_INVENTORY`. Old RawRun import reuses the existing offline adapter and keeps historical media/partial-capture facts.

The inventory content hash includes row order. A decision also binds the **exact saved inventory file SHA-256**. Rows are resolved against that file into stable IDs when selected. Reordering keeps URL IDs but creates a new version; old row-based decisions cannot silently apply to it. Even reformatting the file invalidates its decision-file binding. Treat saved inventories as immutable.

`select --include-html ROW_OR_ID` and `--include-rest ROW_OR_ID` are separate. `--exclude` records an explicit exclusion. Unknown rows/IDs and conflicting choices fail before saving. Every decision is a new file; pass all intended choices for that version (no implicit merge). `--by` records the stated decision-maker, not authenticated approval. An engineering illustration must use `--example` and an explicit example actor.

A REST choice on a document row exports only its evidenced item endpoint(s), with `paginate: false`. Choosing a whole collection row requires explicit `--collection-max-pages`. Exports do not contain the metadata `_fields` filter. Selecting one post never grants permission for all posts. Export preserves HTML URLs and REST scope as distinct arrays accepted by the unchanged collector.

## Exact usage

The following `recon` commands are **not executed** and require live authorization before use against cyberizegroup.com. Use new output directories.

```bash
# Sitemap mode; omit --sitemap to discover Sitemap directives from robots.txt.
venv/bin/python -m recon_pipeline.decide recon \
  --mode sitemap --url https://cyberizegroup.com/ \
  --sitemap https://cyberizegroup.com/sitemap_index.xml \
  --out outputs/recon/CyberizeGroup-sitemap-01 \
  --gap 5 --max-requests 8 --max-pages 2 --max-depth 1 \
  --max-rest-pages 1 --per-page 1 --max-candidates 500 --max-seconds 180 \
  --known-collection outputs/collections/CyberizeGroup-selected-live-01

# Default mode: read one page; list its links without following them.
venv/bin/python -m recon_pipeline.decide recon \
  --mode default --url https://cyberizegroup.com/blog/ \
  --out outputs/recon/CyberizeGroup-default-01 \
  --gap 5 --max-requests 4 --max-pages 1 --max-depth 0 \
  --max-rest-pages 1 --per-page 1 --max-candidates 100 --max-seconds 180 \
  --known-collection outputs/collections/CyberizeGroup-selected-live-01

# OFFLINE import instead of fresh recon.
venv/bin/python -m recon_pipeline.decide import \
  --collection outputs/collections/CyberizeGroup-selected-live-01 \
  --out outputs/reviews/CyberizeGroup-imported-01
# Older raw-v2 input alternative: --raw outputs/CyberizeGroup/runs/2026-10-05T14-10-49Z

venv/bin/python -m recon_pipeline.decide list \
  --inventory outputs/reviews/CyberizeGroup-imported-01/inventory.json

# Only after Tony actually chooses these rows/IDs; inspect the exact saved version first.
venv/bin/python -m recon_pipeline.decide select \
  --inventory outputs/reviews/CyberizeGroup-imported-01/inventory.json \
  --include-html ROW_OR_STABLE_ID --include-rest ROW_OR_STABLE_ID \
  --exclude ANOTHER_ROW_OR_ID --by Tony \
  --out outputs/reviews/CyberizeGroup-decision-01.json

venv/bin/python -m recon_pipeline.decide export \
  --inventory outputs/reviews/CyberizeGroup-imported-01/inventory.json \
  --decision outputs/reviews/CyberizeGroup-decision-01.json \
  --out outputs/reviews/CyberizeGroup-approved-plan-01.json
```

Export also writes a `.review.json` sidecar with inventory/decision hashes, actor, example-only marker, separate HTML/REST scope and selected gaps. No collection runs. For a later authorized capture, feed the plan to existing `recon_pipeline collect`; for an existing collection use its unchanged `add --plan ...`, then explicit `resume`. Recon metadata files never enter the collector checklist.

## Saved demonstration — no human approval implied

[Numbered imported sample](EVIDENCE/decide/2026-10-07_135659Z/sample-final/review/INVENTORY.md): ten rows from the previously saved blog/REST responses. Illustrative row3 + stable ID `doc-c6b9265b51bf57660bb4` selects the Andromeda article as HTML and REST11945 only; illustrative row1 exclusion demonstrates syntax. These are NOT Tony decisions, recommendations or automatic exclusions. All original rows remain UNDECIDED.

[Sample plan](EVIDENCE/decide/2026-10-07_135659Z/sample-final/EXAMPLE_ONLY_collector-plan.json) has one HTML URL and one REST item with pagination false. The historical empty content warning remains in its [review sidecar](EVIDENCE/decide/2026-10-07_135659Z/sample-final/EXAMPLE_ONLY_collector-plan.review.json). Actual recorded commands are in [commands.json](EVIDENCE/decide/2026-10-07_135659Z/sample-final/commands.json).

The separate older raw import contains 217 document candidates and still reports media1661/1753, a 92-record gap. It is historical imported evidence, never combined with fresh recon totals. Both imports were read-only; 229 unique referenced source files were hash-verified.

## Verification and limits

Final verification command/results are in the [review report](../../RESPONSES/response_2026-10-07_201138_decide-recon-selection.md). Working collector code, its CLI and all prior tests remain unchanged. Tests cover explicit modes, bounds, deduplication, projections/custom types, stops/pacing, malformed/partial coverage, stable and numbered choices, unknown rejection, single-item versus collection export, and metadata/full-capture separation. Native Chromium is loopback-only.

Current limits: no authenticated/admin-only types or exhaustive namespace discovery; no broad discovery guarantee; field projection depends on server support; unknown MIME is not inferred from a WordPress type; hidden/deferred content completeness unknown. Pacing applies to planned calls, not browser subresources. The 10 MiB post-receipt cap is not a wire/memory streaming bound; cleanup has a separate ten-second asynchronous timeout. No recon resume/retry loop or Prepare skill is added. Existing historical controller/accounting findings remain open.

## Proposed next live check — not authorized or executed here

Use the four-request **default** command above: one blog-page read, one projected public-types read, and at most two projected collection metadata reads (pages/posts prioritized if exposed, otherwise exposed custom types within the same cap). Metadata per_page1, one page per type, no media or content field, five-second gaps, 180-second collection deadline plus ordinary cleanup timeout. Browser resources/redirects add HTTP traffic. Save a bounded/partial inventory and stop; no selection or collection automatically follows. Tony reviews this proposal next. Independent QA NOT RUN.
