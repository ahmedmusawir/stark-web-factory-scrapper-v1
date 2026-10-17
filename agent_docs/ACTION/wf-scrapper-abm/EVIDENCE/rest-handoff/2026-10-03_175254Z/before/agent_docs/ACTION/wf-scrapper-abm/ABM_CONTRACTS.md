# wf-scrapper-abm — CONTRACTS

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.

## Raw Recon Package v2 (`abm-raw-v2`) and Architect Data Pack v1 (`abm-pack-v1`)

> **Version:** 1.2 · **Date:** 2026-10-02 · **Status:** rulings applied; BUILD_READBACK review/build approval pending; build NOT STARTED. JARVIS Architect amendment under Tony’s delegated authority. Current prospective authority: [Rulings 1.2](ABM_RULINGS_1_2.md), E-13–E-19; retained [amendment](ABM_AMENDMENT_1_1.md) and E-05–E-12; historical R1–R8 are retained with explicit supersessions.
> **Evidence boundary:** §2.5 is intended coverage, not confirmed site-wide availability. P0 collections failed; the October filtered sample verified only id/link/title/content structure, with empty content. Yoast and remaining fields are unconfirmed. Optional absences are recorded; malformed mandatory structure fails explicitly. M-01–M-04 now have prospective dispositions in Rulings 1.2; runtime mechanisms still require the fixture proof specified by BUILD_READBACK.

---

## 1. Rules that apply to both packages

1. **Evidence is never edited.** Raw response bytes at their declared capture boundary are written once and never rewritten; parsed REST object files are declared serialized derivatives (§2.4–2.5), not original response bytes. Prepare never mutates the source run; writes into a NEW pack, including its required byte-identical raw copy, are authorized output construction. Filesystem guards resolve targets, not literal path-name greps.
2. **No absolute paths inside any JSON.** Every tool-authored filesystem reference is relative to the folder that contains the JSON; source HTTP(S) URLs and untouched source object string values are not filesystem references. (Fixes the bim001 `input_path`/`command` portability hole; AC-004, AC-037.)
3. **One base per file.** All paths in `manifest.json` are relative to the run folder. All paths in `pack.json` are relative to the pack folder. (Fixes the bim001 two-bases `md_file` hole.)
4. **Every record carries provenance.** Raw records say how they were fetched. Derived records say which raw file and locator they came from.
5. **Absence is data.** Anything required that did not arrive is written as a typed absence, never omitted.
6. **Timestamps** are UTC ISO-8601 with seconds and `+00:00`.
7. **Hashes** are SHA-256 hex of file bytes, field name `sha256`.
8. **Schema field** is the first key of each tool-authored metadata envelope and is checked by the validator. Untouched collection responses and value-preserving object derivatives are source data, not envelopes; never inject a schema key into them.

### 1.1 URL identity rule (AC-007)

`canonical_url(u)`:
- lowercase scheme and host; strip default port; strip fragment;
- keep the path as given, except collapse repeated `/` and add a trailing `/` when the last path segment has no `.` (WordPress convention);
- keep the query string, but drop known tracking params (`utm_*`, `fbclid`, `gclid`, `cat_source`, `cat_medium`) — the raw sitemap `<loc>` is preserved untouched in `routes.json`;
- percent-decode then re-encode unreserved characters only.

Two input URLs with the same `canonical_url` are one route. The first occurrence wins the slug; later occurrences are recorded in `routes.json` under `aliases`.

### 1.2 Slug rule (unchanged from bim001, `crawler.py:64-66`)

Strip scheme, lowercase, every run of non-`[a-z0-9]` → `-`, trim `-`, empty → `root`. Collision within a run: `base`, `base-2`, `base-3`. Slug is computed from `canonical_url`.

### 1.3 Absence types (AC-017)

| Type | Meaning |
|---|---|
| `blocked` | Server refused: 403, 429, or a detected block page. |
| `failed` | Attempted, no usable result: network error, timeout, 404/5xx, exception or malformed mandatory response structure. |
| `unsupported` | Fetched but cannot be used under the contract: `redirect_out_of_scope`, `empty_body`, `no_html_attr` (result lacks html), `non_html_body`, `no_rest_object`, `off_host`, `http_401`. Reasons are distinct strings (journal v0.3 parking item on `no html in result`). |
| `skipped` | Not attempted: beyond `--limit`, after stop rule, or stream disabled by flag. |

Every absence record: `{ "stream": "html|rest|media|discovery|screenshots", "ref": "<canonical_url or object ref>", "outcome": "<type>", "reason": "<short string>", "at": "<ts>" }`.

### 1.4 Scope and redirect policy (AC-005)

- `hosts_allowed` = the hostname of `--url` plus its `www.`/apex twin. Bound for Cyberize: `["cyberizegroup.com", "www.cyberizegroup.com"]`.
- Discovery in sitemap mode drops any `<loc>` outside `hosts_allowed` into `absences.json` as `unsupported / off_host`.
- Redirects: enforce allowed scheme/host **before dispatch of each intentional top-level, discovery, REST or media redirect hop**. At most five hops; out-of-scope destination → `unsupported/redirect_out_of_scope` without requesting it; loop/excess hops → `failed/redirect_loop`. Record observed chain, proposed denied destination and final URL separately. An in-scope final URL with different canonical identity is recorded without a duplicate fetch. Transport limitations must fail closed; prove hop interception on local fixtures before live use.
- Intentional collection operations: **one at a time; five seconds after completion before the next operation starts**, shared across navigation, discovery, REST, in-scope media HEAD and intentional redirect hops. No automatic retries, transport fallback, identity switching or automatic restart. First 403/429 or explicit challenge on an intentional read stops all further collection, exit 2; preserve available partial evidence and mark remaining work `skipped/stop_rule`. Record Retry-After without retrying. Failed non-refusal operations remain typed failures; no repeat attempt.
- Crawl4AI is the rendered-content path. Intentional discovery/REST reads use the demonstrated browser session (Chromium page `window.fetch` or explicitly evidenced browser-response handling); never silently substitute requests/curl. Exact API, browser/session identity and response boundary are recorded, not merely called “browser.” Collection reads have no `_fields` restriction. No root REST enumeration.
- Browser-loaded public resources may be concurrent and are **not** paced individually at five seconds. Observe their host/resource type/status separately from deliberate collection. Ordinary page-generated background POSTs are allowed; no clicking, filling or submitting forms. Incidental failures, including third-party analytics 403/429, are recorded without automatically declaring requested-document refusal. A challenge that prevents document access is a stop. Background access never authorizes deliberate collection from those hosts. Already in-flight resource completion is reported honestly.
- Budgets (estimates, R4): full Cyberize run ≈ 194 routes, ≈ 35–45 min with pauses, ≈ 90 MB HTML + REST + media metadata. No separate media-byte harvesting or saving; rendering browsers naturally load images and other public resources. Media inventory records URLs/metadata and permitted HEAD outcomes.
- `robots.txt` is fetched once, saved, and its `Sitemap:` lines are used; its `Disallow` rules are recorded but not enforced (Director's polite ladder rung (a) is the access policy). Recorded as `robots_policy: "recorded_not_enforced"` in the manifest.

---

## 2. Raw Recon Package v2 — `abm-raw-v2`

### 2.1 Folder layout

```
outputs/<project>/runs/<run_id>/
├── manifest.json                 abm-raw-v2 (§2.2)
├── absences.json                 list of §1.3 records
├── stage_log.txt                 "<ts> <stream> <line>" — intentional operation, pause, stop and separately tagged incidental browser events
├── discovery/
│   ├── robots.txt                as fetched, or absent + absence record
│   ├── sitemap_index.xml         as fetched (name = last path segment of the URL actually used)
│   ├── <child-sitemap>.xml       one per child, as fetched
│   └── routes.json               §2.3
├── html/
│   └── <slug>.html               utf-8 bytes of crawl4ai result.html, unchanged
├── rest/
│   ├── index.json                §2.4 — collection outcomes, transport, totals, response/object provenance
│   ├── responses/<collection>-<page>.body  complete browser-response bytes + indexed hash
│   ├── objects/<type>-<id>.json  serialized object derivative; indexed response/array position
│   └── map.json                  §2.5 — route → object mapping
├── media/
│   └── inventory.json            §2.6
└── screenshots/
    ├── README.md                 Director slot instructions (fixed text, §2.7)
    └── <any files Tony drops>    authored evidence, never generated
```

`run_id` rule unchanged: `started_at[:19]` with `:`→`-` plus `Z`; same-second clash re-stamps (bim001). Retired: `outputs/pages/*.md`, `outputs/run_summary.json` (R8).

### 2.2 `manifest.json`

```json
{
  "schema": "abm-raw-v2",
  "project_name": "CyberizeGroup",
  "run_id": "2026-09-19T10-00-00Z",
  "started_at": "...", "finished_at": "...",
  "command": "python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com",
  "input": { "url": "https://cyberizegroup.com", "mode": "sitemap", "limit": null },
  "scope": { "hosts_allowed": ["cyberizegroup.com","www.cyberizegroup.com"], "redirect_max_hops": 5, "robots_policy": "recorded_not_enforced" },
  "access": { "rung": "a", "user_agent": "<USER_AGENT>", "operation_gap_after_completion_s": 5.0, "retry_max": 0, "stop_on_first_intentional_refusal": true, "automatic_restart": false, "background_resources_paced": false, "page_timeout_ms": 90000, "delay_before_return_html_s": 3.0, "wait_for_images": true, "cache_mode": "BYPASS", "headless": true, "discovery_rest_transport": "chromium_page_window_fetch" },
  "versions": { "python": "3.12.3", "crawl4ai": "0.9.3", "playwright": "1.52.0", "requests": "2.32.3", "tool_commit": "<git rev-parse HEAD or 'unknown'>" },
  "streams": { "discovery": "complete|partial|failed", "html": "...", "rest": "...", "media": "...", "screenshots": "authored|empty" },
  "counts": { "routes": 194, "captured": 190, "blocked": 0, "failed": 2, "unsupported": 2, "skipped": 0, "rest_objects": 210, "rest_mapped_routes": 188, "media_items": 640 },
  "stopped_early": false,
  "fallbacks_fired": [],
  "pages": [ { "...": "§2.2.1" } ]
}
```

`wait_for_images=True`, 90000 ms page timeout, 3.0 s post-load delay, CacheMode.BYPASS and headless BrowserConfig retain demonstrated capture settings. USER_AGENT remains sourced from `discover_site.sitemap_utils.USER_AGENT`. E-05/E-06 supersede the older False/retry bindings. Record actual runtime/defaults; no stealth or security changes are authorized. Optimize only by a later evidenced amendment. Metadata schema and validator must agree; old key-count literals change only with cited errata.

#### 2.2.1 Per-page record (`pages[]`, selected/known route order)

| Key | Type | Rule |
|---|---|---|
| `url` | str | canonical_url |
| `input_url` | str | as it appeared in routes.json |
| `final_url` | str\|null | after redirects, from crawl4ai result |
| `redirect_chain` | list[str] | empty when none |
| `slug` | str | §1.2 |
| `status` | int\|null | HTTP status of final response |
| `outcome` | `captured\|blocked\|failed\|unsupported\|skipped` | precedence: blocked > failed > unsupported > captured |
| `reason` | str\|null | non-null unless captured |
| `fetched_at` | str\|null | ts of request start |
| `elapsed_s` | float | |
| `retries` | int | always 0 under this pilot policy |
| `html_file` | str\|null | `html/<slug>.html` — captured pages only |
| `block_file` | str\|null | `html/_blocked/<slug>.html` — available blocked response saved as evidence; if abort prevents body retention, record the explicit evidence absence, never count it as capture |
| `html_bytes` | int\|null | |
| `sha256` | str\|null | of html_file bytes |
| `rest_ref` | str\|null | `rest/objects/<type>-<id>.json` when mapped |
| `rest_outcome` | `mapped\|unmapped\|ambiguous\|rest_unavailable` | from map.json |

### 2.3 `discovery/routes.json`

```json
{ "schema": "abm-routes-v1", "mode": "sitemap", "sitemap_url_used": "https://cyberizegroup.com/sitemap.xml",
  "sources": [ { "file": "sitemap_index.xml", "url": "...", "status": 200, "child_count": 3 }, { "file": "post-sitemap.xml", "url": "...", "status": 200, "loc_count": 120 } ],
  "routes": [ { "url": "<canonical>", "input_urls": ["<loc as written>"], "aliases": [], "source_file": "post-sitemap.xml", "lastmod": "<as written or null>" } ],
  "dropped": [ { "loc": "...", "reason": "off_host|duplicate|invalid" } ],
  "counts": { "loc_total": 197, "routes": 194, "dropped": 3 } }
```

Homepage mode: `sources` has one entry (the homepage), `source_file: "homepage"`. Sitemap fallback order: `robots.txt` `Sitemap:` lines → `/sitemap.xml` → `/sitemap_index.xml` → `/wp-sitemap.xml`. First valid sitemap XML wins; the rest are not fetched. All reads use §1.4 browser transport and shared pacing. Any intentional 403/429/challenge ends fallback and the run immediately; fallback after an ordinary non-refusal unsuccessful candidate is not a retry of that candidate.

### 2.4 `rest/index.json`

`index.json` is collection metadata, not a root-response inventory. Do not request the REST root; no root_file, root_status or namespaces assertion is required.

```json
{
  "schema": "abm-rest-index-v1",
  "transport": {"client": "Chromium", "api": "page.evaluate/window.fetch", "session_ref": "../manifest.json", "response_boundary": "Fetch Response.body decoded entity bytes; ArrayBuffer-equivalent boundary, actual read API recorded; not compressed wire bytes"},
  "collections": [{"type": "pages", "endpoint": "https://cyberizegroup.com/wp-json/wp/v2/pages", "per_page": 100, "total": 60, "total_pages": 1, "fetched_objects": 60, "status": "complete", "response_refs": ["responses/pages-1.body"]}],
  "responses": [{"file": "responses/pages-1.body", "sha256": "<hash>", "bytes": 12345, "collection": "pages", "page": 1, "url": "https://cyberizegroup.com/wp-json/wp/v2/pages?per_page=100&page=1", "method": "GET", "started_at": "<UTC>", "finished_at": "<UTC>", "status": 200, "content_type": "application/json", "location": null, "retry_after": null, "x_wp_total": 60, "x_wp_total_pages": 1, "transport": "chromium_page_window_fetch", "boundary": "Fetch Response.body browser-decoded entity", "outcome": "complete"}],
  "objects": [{"file": "objects/pages-4952.json", "sha256": "<hash>", "response_file": "responses/pages-1.body", "array_position": 0, "serialization": "UTF-8 JSON; ensure_ascii=false; indent=2; original key order; trailing LF; no injected fields"}],
  "fields_requested": "all; no _fields filter",
  "absences_file": "../absences.json"
}
```

The example abbreviates collections; the actual index must include `pages`, `posts`, `media`, `categories`, `tags`, and optional-public `users` with complete/partial/unavailable/skipped outcomes, even after early stop. Use the declared `/wp-json/wp/v2/<collection>` endpoints directly. `users` gets one initial attempt: 401 → unavailable/absence; 403/429/challenge → unavailable plus global collection stop, no retry. Pagination follows X-WP-TotalPages; preserve totals when present, record missing totals/unknown coverage rather than claim completeness. Each collection page/hop obeys shared pacing and scope.

Save each complete response **before parsing**, with hash at the named browser-response boundary; declare browser content decoding, do not claim compressed wire-byte identity. Retain available malformed/refusal responses too, labeled separately, never as objects. An interrupted body is incomplete evidence with byte count/hash of what is available and explicit truncation, not a complete response. Do not reconstruct original bytes from JSON/string serialization. Transport/header/body access and redirect enforcement require local fixture proof; if an API cannot supply them, fail explicitly without switching clients.

### 2.5 `rest/map.json` and the REST object

`objects/<type>-<id>.json` is a **serialized derivative** parsed from a saved collection array; values and unknown fields are preserved. Index each file to its saved response and zero-based array position; declare serialization and hash. It is not an original HTTP response. Unexpected duplicate object identity with differing values is retained as a distinct occurrence with a disambiguated filename and mapping ambiguity, never overwritten.

Validate a JSON array of objects with positive integer `id`. Page/post identity requires nonempty HTTP(S) `link`; non-null title/content/excerpt containers must be objects, and their rendered field when present and non-null must be a string; missing/null optional containers or rendered fields are distinct absences, and missing optional fields remain distinct from null. Other collection shapes are type-aware (e.g. media, categories/tags, users are not posts); do not fabricate page fields for them. Malformed identity/container/type is `failed/malformed_response`, not optional absence. Expected coverage retained: `id`, `type`, `link`, `slug`, `status`, `date`, `modified`, `title.rendered`, `excerpt.rendered`, `content.rendered`, `author`, `featured_media`, `categories`, `tags`, `yoast_head_json` and `yoast_head`, where returned. Non-null Yoast JSON must be an object and Yoast head a string; absence/null is recorded separately. Keep every unknown field as well. Yoast keys include title/description/robots/canonical/og_*/twitter_*/schema/article_* without filtering. This is intended coverage, not a claim those fields exist site-wide; the four-field diagnostic is not the production contract.

```json
{ "schema": "abm-rest-map-v1",
  "by_route": { "<canonical route>": { "outcome": "mapped", "object": "objects/pages-4952.json", "match": "link" } ,
                "<route>": { "outcome": "unmapped", "reason": "no object with matching link" },
                "<route>": { "outcome": "ambiguous", "candidates": ["objects/pages-1.json","objects/posts-9.json"] } },
  "unrouted_objects": [ "objects/posts-77.json" ],
  "content_rendered_empty": [ "objects/pages-4952.json" ] }
```

Matching rule: `canonical_url(object.link) == route`. Nothing else is inferred. `content_rendered_empty` lists present string fields empty/whitespace after stripping markup. Missing and null fields are distinct absence records, not empty strings. Legacy `thrive_signal` is only a heuristic: empty REST content plus meaningful rendered text, with both sources cited; it does not establish Thrive or any other plugin as the cause (AC-014).

### 2.6 `media/inventory.json`

Plan §4A Phase 1 fields. Sources scanned: REST `media` collection objects; every captured HTML (`<img src/srcset>`, `<picture><source>`, `<video poster>`, `<link rel=icon>`, `og:image`, `twitter:image`, JSON-LD `image`/`logo`, inline `style="background-image:url()"`). No separate media-byte harvesting/saving. A rendering browser may load images. One intentional HEAD per unique **in-scope** URL is allowed under §1.4, with pre-dispatch redirect checks, to record status/content-type/content-length. External/staging off-scope URLs are inventoried from received evidence, never explicitly probed: `retrieval.method: "skipped"`, `status: "skipped"`, `reason: "off_scope_untested"`. `--no-media-head` similarly records `reason: "disabled"`; a stopped run records `reason: "stop_rule"`. Permitted HEAD transport/API must be named in evidence; no silent fallback.

```json
{ "schema": "abm-media-v1", "items": [ {
  "url": "<absolute>", "canonical_url": "...", "origin": "internal|external|staging_domain", "host": "...",
  "wp_media_id": 123, "type": "image/jpeg", "width": 1200, "height": 600, "alt": "...", "caption": "...", "title": "...",
  "source_pages": [ { "slug": "web-design-process", "locator": "img[3]" , "context": "img|srcset|og:image|jsonld|css_bg|link_icon" } ],
  "seo_social_usage": ["og:image"], "rest_ref": "../rest/objects/media-123.json",
  "retrieval": { "method": "HEAD|skipped", "status": 200, "content_type": "...", "content_length": 12345 },
  "provenance": ["../html/web-design-process.html", "../rest/objects/media-123.json"] } ],
  "counts": { "items": 640, "internal": 500, "external": 57, "staging_domain": 83 } }
```

`staging_domain` is bound: any host matching `*.mystagingwebsite.com`. Nothing is filtered; "apparently unused" is not a raw concept.

### 2.7 `screenshots/README.md` (fixed text, written by the tool)

"Director-authored evidence slot. Drop screenshots here. The tool writes only this README into this folder; screenshot bytes are Director-authored. Files here are listed in `manifest.streams.screenshots` as `authored` with their sha256; if empty, `absences.json` carries `stream: screenshots, outcome: skipped, reason: none_supplied`."

### 2.8 Validator — `python -m smart_crawler.validate --project X --run <run_id>`

Exit 0 only if mandatory tool-authored metadata files/references and schemas are valid; every declared non-null filesystem reference resolves inside the run folder; counts reconcile; every selected/known route has **exactly one** `pages[]` outcome and one `rest/map.json.by_route` entry. HTML absences refer to those page outcomes and add no pages. Counts.routes = len(pages) = captured + blocked + failed + unsupported + skipped, including known limit/stop-skipped routes. Discovery drops are not selected routes. Every mapped REST object matches route identity. Captured HTML hashes and complete collection-response hashes match. Each derivative's indexed response exists, array position is valid, parsed value deep-equals the corresponding response object including unknown fields, serialization is declared, and derivative hash matches. No absolute filesystem references are permitted; source URLs/values are preserved.

Missing mandatory files/references, corrupt structure or invalid hashes fail validation and cause Prepare refusal (AC-020). Valid packages may describe failed/blocked/skipped capture with null optional artifact refs and linked typed absences; these pass structural validation and produce partial/blocked packs with losses (AC-029), never fabricated success. Retain a complete structural skeleton on early stop, with collections/routes not attempted explicitly skipped. A malformed network response is saved if available and typed failed; it must not masquerade as a valid object derivative. Prints a one-line report per check. This is the **automatic engineering checkpoint** (Campaign Map, Stage C → P).

---

## 3. Architect Data Pack v1 — `abm-pack-v1`

### 3.1 Folder layout

```
outputs/<project>/packs/<pack_id>/
├── SITE_RECON_BRIEF.md           human entry point (§3.9)
├── pack.json                     abm-pack-v1 inventory (§3.2)
├── site_map.json / site_map.md   §3.3
├── content_inventory.json        §3.4
├── seo_inventory.json / seo_summary.md      §3.5
├── forms_embeds.json             §3.6
├── design_evidence.json / design_evidence.md §3.7
├── media_classification.json     §3.8
├── disagreements.json            §3.4
├── loss_ledger.json / findings.md            §3.8
└── raw/                          copy of the source run folder (R4: delivered with the pack; links resolve after copy)
```

`pack_id` = `<run_id>-pack-<seq>` (`-pack-1`, `-pack-2` for reruns on the same raw). Prepare CLI: `python -m prepare.build --project X --run <run_id> [--no-copy-raw]`. `--no-copy-raw` makes `raw/` a relative symlink to `../../runs/<run_id>`; default is a copy so the pack is a self-contained delivery unit (AC-037).

### 3.2 `pack.json`

```json
{ "schema": "abm-pack-v1", "pack_id": "...", "project_name": "...", "source_run": { "run_id": "...", "manifest_sha256": "...", "raw_path": "raw/" },
  "built_at": "...", "prepare_version": "<tool_commit>", "normalization": "abm-pack-v1 semantic diff rules (§3.10)",
  "artifacts": [ { "file": "site_map.json", "records": 194, "sha256": "..." }, "..." ],
  "counts": { "routes": 194, "content_records": 194, "seo_records": 188, "media_items": 640, "forms": 6, "embeds": 11, "disagreements": 4, "losses": 9 },
  "completeness": { "status": "complete|partial|blocked", "reason": "...", "unresolved_mandatory": [] },
  "labels": ["observed", "inferred", "absent", "recommendation"] }
```

`completeness.status` is `complete` only when required HTML/REST/media collection coverage is complete and unresolved_mandatory is empty (AC-038). Optional missing/null content/Yoast, optional users401, no screenshots and forbidden offscope HEAD remain recorded absences but are not required losses. Any required missing capture, incomplete collection/route evidence or unknown coverage remains a loss; malformed mandatory package structure is invalid. F-09-complete and F-12 are bound in Rulings 1.2 §3; F-01’s required 404 is never complete.

### 3.3 Every derived record shares this envelope

```json
{ "id": "<stable id>", "label": "observed|inferred|absent|recommendation", "confidence": "high|medium|low|n/a",
  "sources": [ { "file": "raw/html/<slug>.html", "locator": "css:head>title | jsonpath:$.yoast_head_json.title | line:120" } ],
  "...": "record fields" }
```

`label` is mandatory. `inferred` requires `basis`. `absent` requires `absence_ref` into `raw/absences.json`; its sources cite the existing absence/outcome record, never a nonexistent HTML file. The tool-authored `recommendation` label/advice is allowed only in findings.md, never as an observed fact record. Quoted/raw source values and unknown source fields containing that word remain unchanged with provenance; do not apply label checks recursively to source data (AC-022).

### 3.4 `site_map.json`, `content_inventory.json`, `disagreements.json`

- `site_map`: routes as a tree by path segment, each node `{route, slug, type: page|post|category|unknown, title (observed), parent, children, rest_ref|null, html_file|null}`. Type comes from `rest/map.json` (`type` field); routes without REST are `unknown`, never guessed.
- `content_inventory`: per route `{route, title_rendered (from HTML <title>), title_rest, h1[], headings_outline[], word_count_rendered, word_count_rest, content_source: "rendered|rest|both|none", thrive_signal: bool, excerpt_rest, date, modified, author_id, categories[], tags[]}`. `content_source: rendered` with `thrive_signal: true` is the AC-014 heuristic case; add a cited `basis` stating REST-empty/rendered-present, not plugin causation. Boilerplate is **not** stripped; `word_count_rendered` is of the whole `<body>` text with a documented main-content heuristic result stored separately as `main_content_wordcount` labeled `inferred`.
- `disagreements`: one record per field where REST and rendered disagree (`title`, `h1 vs title.rendered`, `canonical`, `og:image`, `date`, and content presence/absence across streams), both values, both sources, no winner (AC-024).

### 3.5 `seo_inventory.json` and `seo_summary.md`

REST and rendered HTML are complementary; an empty REST field never erases meaningful rendered content or labels the whole page empty. Preserve all returned REST fields in raw derivatives; optional missing/null content or Yoast fields have distinct typed absences. Per route: every returned Yoast field from `yoast_head_json` copied value-for-value under `rest`, plus the same fields parsed from rendered `<head>` under `rendered` (`<title>`, `meta[name=description]`, `meta[name=robots]`, `link[rel=canonical]`, all `og:*`, all `twitter:*`, every `<script type="application/ld+json">` parsed or kept as string on parse failure). `disagree: [field,...]`. No field is synthesized; a missing field is `null` with `label: absent`. `seo_summary.md` is generated from the JSON (twin, AC-031).

### 3.6 `forms_embeds.json`

Forms: `{route, locator, action, method, input_names[], has_submit, function_status: "observed_markup_only"}`. Embeds: `{route, locator, kind: iframe|script_widget|video|map|social, src_host, third_party: bool, function_status: "observed_markup_only"}`. `function_status` has exactly one allowed value in this ABM. A mailto link is a link, not an embed: F-07 expects two forms and two embeds. No clicking, filling or form submissions; no script execution beyond ordinary rendering and authorized browser-session read/observation logic (AC-026).

### 3.7 `design_evidence.json` / `.md`

Observed only: colors seen in inline styles and computed `<style>` blocks (hex/rgb literals, counted), font-family declarations, heading font sizes if literal, section vocabulary = distinct top-level `<section>/<header>/<footer>/<nav>` class names with counts, viewport meta. Everything `label: observed`; anything not literally present is `absent`, not estimated. No tool-authored palette recommendation (AC-027). Quoted source phrases and observed class/title identifiers are not authored advice; provenance distinguishes them. Checks inspect authored fields/sections rather than prohibit words inside source values.

### 3.8 `media_classification.json`, `loss_ledger.json`, `findings.md`

- Classification classes (Plan §4A Phase 2, AC-028): `referenced`, `social_only`, `brand_global`, `editorial`, `integration`, `external`, `duplicate_variant`, `broken`, `apparently_unused`, `unknown`. Each item keeps its raw `url` and a `raw_ref` into `raw/media/inventory.json`; a `staging_domain` flag is carried, never rewritten. Class rules are deterministic and listed in `prepare/rules/media_rules.md`; every rule cited per item under `basis`.
- `loss_ledger`: one record per required derivation that could not be made: `{requirement: "AC-0xx or field", route|null, cause: "absent_raw|unsupported_raw|parse_failure|rule_gap", absence_ref|null, effect}`.
- `findings.md`: human twin of loss_ledger + disagreements + the staging-domain fossils count + a `recommendation`-labeled section that is clearly separated.

### 3.9 `SITE_RECON_BRIEF.md`

Fixed section order: 1 Identity and source run · 2 Completeness and limits · 3 How to read this pack (links to every artifact, counts must equal `pack.json`) · 4 Site structure at a glance · 5 Content notes (rendered-only routes; legacy thrive_signal heuristic with basis, not plugin cause) · 6 SEO notes · 7 Media notes · 8 Integrations, forms, embeds · 9 Observed design · 10 Disagreements and losses · 11 Answering the B7 questions (each of the 12 questions in `ABM_ACCEPTANCE_SPEC.md` §B7 with the artifact and field that answers it, or "not answerable — see loss L-n"). Every link is relative and must resolve after copy.

### 3.10 Reproducibility normalization (AC-032)

Two Prepare runs on the same raw are equivalent after the **integrity-first, reference-aware comparison** in [Rulings 1.2 §3](ABM_RULINGS_1_2.md). Verify all actual hashes/references and source-byte fidelity first; replace only declared volatile metadata in a comparison view, then recompute corresponding metadata-reference hashes from leaves to parents. Preserve content, raw hashes, outcomes, counts, meaningful order and every reference edge. Existing unordered sources/source_pages/categories arrays may be canonicalized without losing records. Compare generated twin metadata headers consistently. Never blanket-ignore every hash, port or timestamp-looking source string. Negative mutations must fail. `pack.json.normalization` records this exact rule/version; source and output evidence are never rewritten to normalize them.

### 3.11 Authored-output security boundary (E-18)

Tool-authored filesystem refs are schema-bound and confined to their declared root; source strings and HTTP(S) URLs are preserved. Raw run and pack/raw HTML/JSON remain byte-faithful, including scripts. Escape/quote only generated presentation artifacts so hostile source cannot become active markup; generated JSON must round-trip source values. Preserve source before/after hash inventory and NEW pack/raw copy hashes. Detect authored advice independently from quoted source words. Exact tests/boundaries: Rulings 1.2 §5, AC-004/019/021/022/027/030/037/043. Secret-leak scans still include raw artifacts (E-16); the raw exception is for presentation escaping only.

### 3.12 Candidate provenance before commit

`versions.tool_commit` records actual base HEAD, never a fictional future candidate. Record dirty state plus a source identity manifest: sorted paths, SHA-256 bytes, executable/symlink identity for every product/test/fixture/config/governing input used, including untracked implementation files; exact commands/runtime and evidence hashes. Store its digest in run metadata. Tony later commits; independent QA compares the committed tree’s corresponding bytes/modes to the retained source identity and records a binding attestation without editing original run evidence. Any difference requires impact adjudication/retest; matching bytes permit SOL to consider reuse, never automatic QA PASS. See BUILD_READBACK §7.
