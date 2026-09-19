# wf-scrapper-abm — CONTRACTS
## Raw Recon Package v2 (`abm-raw-v2`) and Architect Data Pack v1 (`abm-pack-v1`)

> **Version:** 1.0 · **Date:** 2026-09-18 · **Status:** BOUND from repo truth (READ_pre-abm_2026-09-18) + Director rulings R1–R8. Frozen at Engineer handoff; changes go through the erratum lane in `ABM_ACCEPTANCE_SPEC.md`.
> **One open binding:** REST payload field names in §2.5 are bound from Run 001 evidence (REST open, unauthenticated, `yoast_head_json` per page) and confirmed by the P0 Part B probe. If the probe contradicts §2.5, Claudy records the exact difference in the execution log and the Architect issues an erratum before Task C4 starts. No other binding waits on anything.

---

## 1. Rules that apply to both packages

1. **Evidence is never edited.** Raw bytes are written as received and never rewritten. Prepare reads raw and writes only into a pack folder.
2. **No absolute paths inside any JSON.** Every path is relative to the folder that contains the JSON. (Fixes the bim001 `input_path`/`command` portability hole; AC-004, AC-037.)
3. **One base per file.** All paths in `manifest.json` are relative to the run folder. All paths in `pack.json` are relative to the pack folder. (Fixes the bim001 two-bases `md_file` hole.)
4. **Every record carries provenance.** Raw records say how they were fetched. Derived records say which raw file and locator they came from.
5. **Absence is data.** Anything required that did not arrive is written as a typed absence, never omitted.
6. **Timestamps** are UTC ISO-8601 with seconds and `+00:00`.
7. **Hashes** are SHA-256 hex of file bytes, field name `sha256`.
8. **Schema field** is the first key of every top-level JSON object and is checked by the validator before anything else.

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
| `failed` | Attempted, no usable result: network error, timeout, 5xx, exception. |
| `unsupported` | Fetched but cannot be used under the contract: `redirect_out_of_scope`, `empty_body`, `no_html_attr` (result lacks html), `non_html_body`, `no_rest_object`, `off_host`, `http_401`. Reasons are distinct strings (journal v0.3 parking item on `no html in result`). |
| `skipped` | Not attempted: beyond `--limit`, after stop rule, or stream disabled by flag. |

Every absence record: `{ "stream": "html|rest|media|discovery|screenshots", "ref": "<canonical_url or object ref>", "outcome": "<type>", "reason": "<short string>", "at": "<ts>" }`.

### 1.4 Scope and redirect policy (AC-005)

- `hosts_allowed` = the hostname of `--url` plus its `www.`/apex twin. Bound for Cyberize: `["cyberizegroup.com", "www.cyberizegroup.com"]`.
- Discovery in sitemap mode drops any `<loc>` outside `hosts_allowed` into `absences.json` as `unsupported / off_host`.
- Redirects: the browser follows up to 5 hops. If `final_url` host is not in `hosts_allowed`, outcome is `unsupported / redirect_out_of_scope`, the HTML is **not** saved, and `redirect_chain` is recorded. If `final_url` is in scope but is a different canonical route, it is recorded; no second fetch is made.
- Request limits: one page at a time; pause `random.uniform(2.0, 5.0)` s between every network request in every stream (crawl, REST, media probe, sitemap children). Retries: **one** retry after a network exception or timeout, after a 10 s pause; never retry 4xx. Stop rule: 3 consecutive `blocked` on any stream stops the run, exit 2, manifest and absences are still written.
- Budgets (estimates, R4): full Cyberize run ≈ 194 routes, ≈ 35–45 min with pauses, ≈ 90 MB HTML + REST + media metadata. Media **bytes are never downloaded**; media is inventoried by URL and metadata only.
- `robots.txt` is fetched once, saved, and its `Sitemap:` lines are used; its `Disallow` rules are recorded but not enforced (Director's polite ladder rung (a) is the access policy). Recorded as `robots_policy: "recorded_not_enforced"` in the manifest.

---

## 2. Raw Recon Package v2 — `abm-raw-v2`

### 2.1 Folder layout

```
outputs/<project>/runs/<run_id>/
├── manifest.json                 abm-raw-v2 (§2.2)
├── absences.json                 list of §1.3 records
├── stage_log.txt                 "<ts> <stream> <line>" — every request, pause, stop, retry
├── discovery/
│   ├── robots.txt                as fetched, or absent + absence record
│   ├── sitemap_index.xml         as fetched (name = last path segment of the URL actually used)
│   ├── <child-sitemap>.xml       one per child, as fetched
│   └── routes.json               §2.3
├── html/
│   └── <slug>.html               utf-8 bytes of crawl4ai result.html, unchanged
├── rest/
│   ├── index.json                §2.4 — root discovery, collections, totals
│   ├── objects/<type>-<id>.json  one raw REST object per file, unchanged
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
  "access": { "rung": "a", "user_agent": "<USER_AGENT>", "pause_range_s": [2.0, 5.0], "retry_max": 1, "stop_rule_consecutive_blocked": 3, "page_timeout_ms": 90000, "delay_before_return_html_s": 3.0, "wait_for_images": false },
  "versions": { "python": "3.12.3", "crawl4ai": "0.9.3", "playwright": "1.52.0", "requests": "2.32.3", "tool_commit": "<git rev-parse HEAD or 'unknown'>" },
  "streams": { "discovery": "complete|partial|failed", "html": "...", "rest": "...", "media": "...", "screenshots": "authored|empty" },
  "counts": { "routes": 194, "captured": 190, "blocked": 0, "failed": 2, "unsupported": 2, "skipped": 0, "rest_objects": 210, "rest_mapped_routes": 188, "media_items": 640 },
  "stopped_early": false,
  "fallbacks_fired": [],
  "pages": [ { "...": "§2.2.1" } ]
}
```

`wait_for_images` is bound **false** for the ABM (J-24 evidence: cost, no capture gain). `retry_max: 1` is new. Key count is asserted in the validator; the validator, not a test literal, is the source of truth (J-16 lesson).

#### 2.2.1 Per-page record (`pages[]`, attempt order)

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
| `retries` | int | 0 or 1 |
| `html_file` | str\|null | `html/<slug>.html` — captured pages only |
| `block_file` | str\|null | `html/_blocked/<slug>.html` — body of a blocked response saved as evidence (journal v0.3 parking item A2); never counts as capture |
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

Homepage mode: `sources` has one entry (the homepage), `source_file: "homepage"`. Sitemap fallback order: `robots.txt` `Sitemap:` lines → `/sitemap.xml` → `/sitemap_index.xml` → `/wp-sitemap.xml`. First that returns XML wins; the rest are not fetched.

### 2.4 `rest/index.json`

```json
{ "schema": "abm-rest-index-v1", "root_url": "https://cyberizegroup.com/wp-json/", "root_status": 200, "root_file": "objects/root.json",
  "namespaces": ["wp/v2", "yoast/v1", "..."],
  "collections": [ { "type": "pages", "endpoint": "wp/v2/pages", "per_page": 100, "total": 60, "total_pages": 1, "fetched_objects": 60, "status": "complete|partial|unavailable" },
                   { "type": "posts", "...": "..." }, { "type": "media", "...": "..." }, { "type": "categories" }, { "type": "tags" }, { "type": "users", "note": "fetched only if the endpoint is public; else unavailable" } ],
  "fields_requested": "all (no _fields filter) so yoast_head_json and content.rendered are retained",
  "absences": "see ../absences.json stream=rest" }
```

Collections bound for the ABM: `pages`, `posts`, `media`, `categories`, `tags`. `users` is attempted once; 401/403 → `unavailable`, no retry. Pagination follows `X-WP-TotalPages`; every page of every collection is one request under the pause rule.

### 2.5 `rest/map.json` and the REST object

Object files are the raw JSON body, byte-for-byte, one per object, named `<type>-<id>.json`. Fields relied on (bound from Run 001 + WP core; confirmed by P0 Part B): `id`, `type`, `link`, `slug`, `status`, `date`, `modified`, `title.rendered`, `excerpt.rendered`, `content.rendered`, `author`, `featured_media`, `categories`, `tags`, `yoast_head_json` (object) and `yoast_head` (string). Yoast keys retained as-is: `title`, `description`, `robots`, `canonical`, `og_*`, `twitter_*`, `schema` (JSON-LD graph), `article_*`.

```json
{ "schema": "abm-rest-map-v1",
  "by_route": { "<canonical route>": { "outcome": "mapped", "object": "objects/pages-4952.json", "match": "link" } ,
                "<route>": { "outcome": "unmapped", "reason": "no object with matching link" },
                "<route>": { "outcome": "ambiguous", "candidates": ["objects/pages-1.json","objects/posts-9.json"] } },
  "unrouted_objects": [ "objects/posts-77.json" ],
  "content_rendered_empty": [ "objects/pages-4952.json" ] }
```

Matching rule: `canonical_url(object.link) == route`. Nothing else is inferred. `content_rendered_empty` lists objects whose `content.rendered` is empty or whitespace after tag-strip — the Thrive Architect signal (AC-014).

### 2.6 `media/inventory.json`

Plan §4A Phase 1 fields. Sources scanned: REST `media` collection objects; every captured HTML (`<img src/srcset>`, `<picture><source>`, `<video poster>`, `<link rel=icon>`, `og:image`, `twitter:image`, JSON-LD `image`/`logo`, inline `style="background-image:url()"`). Media **bytes are not fetched**; one HEAD request per unique URL is allowed under the pause rule to record `retrieval` (status, content-type, content-length). `--no-media-head` disables it (then `retrieval.status: "skipped"`).

```json
{ "schema": "abm-media-v1", "items": [ {
  "url": "<absolute>", "canonical_url": "...", "origin": "internal|external|staging_domain", "host": "...",
  "wp_media_id": 123, "type": "image/jpeg", "width": 1200, "height": 600, "alt": "...", "caption": "...", "title": "...",
  "source_pages": [ { "slug": "web-design-process", "locator": "img[3]" , "context": "img|srcset|og:image|jsonld|css_bg|link_icon" } ],
  "seo_social_usage": ["og:image"], "rest_ref": "rest/objects/media-123.json",
  "retrieval": { "method": "HEAD|skipped", "status": 200, "content_type": "...", "content_length": 12345 },
  "provenance": ["html/web-design-process.html", "rest/objects/media-123.json"] } ],
  "counts": { "items": 640, "internal": 500, "external": 57, "staging_domain": 83 } }
```

`staging_domain` is bound: any host matching `*.mystagingwebsite.com`. Nothing is filtered; "apparently unused" is not a raw concept.

### 2.7 `screenshots/README.md` (fixed text, written by the tool)

"Director-authored evidence slot. Drop screenshots here. The tool never writes files into this folder. Files here are listed in `manifest.streams.screenshots` as `authored` with their sha256; if empty, `absences.json` carries `stream: screenshots, outcome: skipped, reason: none_supplied`."

### 2.8 Validator — `python -m smart_crawler.validate --project X --run <run_id>`

Exit 0 only if: every schema field present and equal to the bound value; every path in every JSON resolves inside the run folder; `counts` equal what the files contain; every route in `routes.json` appears exactly once across `pages[]` ∪ `absences[stream=html]`; every `rest_ref` file exists and its `link` canonicalizes to the page url; no absolute path anywhere; every captured `sha256` matches file bytes. Prints a one-line report per check. This is the **automatic engineering checkpoint** (Campaign Map, Stage C → P).

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
  "counts": { "routes": 194, "content_records": 190, "seo_records": 188, "media_items": 640, "forms": 6, "embeds": 11, "disagreements": 4, "losses": 9 },
  "completeness": { "status": "complete|partial|blocked", "reason": "...", "unresolved_mandatory": [] },
  "labels": ["observed", "inferred", "absent", "recommendation"] }
```

`completeness.status` is `complete` only when `streams.html`, `streams.rest`, `streams.media` in the raw manifest are all `complete` and `unresolved_mandatory` is empty (AC-038).

### 3.3 Every derived record shares this envelope

```json
{ "id": "<stable id>", "label": "observed|inferred|absent|recommendation", "confidence": "high|medium|low|n/a",
  "sources": [ { "file": "raw/html/<slug>.html", "locator": "css:head>title | jsonpath:$.yoast_head_json.title | line:120" } ],
  "...": "record fields" }
```

`label` is mandatory. `inferred` requires `basis`. `absent` requires `absence_ref` into `raw/absences.json`. `recommendation` is allowed only in `findings.md` and is never a fact record (AC-022).

### 3.4 `site_map.json`, `content_inventory.json`, `disagreements.json`

- `site_map`: routes as a tree by path segment, each node `{route, slug, type: page|post|category|unknown, title (observed), parent, children, rest_ref|null, html_file|null}`. Type comes from `rest/map.json` (`type` field); routes without REST are `unknown`, never guessed.
- `content_inventory`: per route `{route, title_rendered (from HTML <title>), title_rest, h1[], headings_outline[], word_count_rendered, word_count_rest, content_source: "rendered|rest|both|none", thrive_signal: bool, excerpt_rest, date, modified, author_id, categories[], tags[]}`. `content_source: rendered` with `thrive_signal: true` is the AC-014 case. Boilerplate is **not** stripped; `word_count_rendered` is of the whole `<body>` text with a documented main-content heuristic result stored separately as `main_content_wordcount` labeled `inferred`.
- `disagreements`: one record per field where REST and rendered disagree (`title`, `h1 vs title.rendered`, `canonical`, `og:image`, `date`), both values, both sources, no winner (AC-024).

### 3.5 `seo_inventory.json` and `seo_summary.md`

Per route: every Yoast field from `yoast_head_json` copied verbatim under `rest`, plus the same fields parsed from rendered `<head>` under `rendered` (`<title>`, `meta[name=description]`, `meta[name=robots]`, `link[rel=canonical]`, all `og:*`, all `twitter:*`, every `<script type="application/ld+json">` parsed or kept as string on parse failure). `disagree: [field,...]`. No field is synthesized; a missing field is `null` with `label: absent`. `seo_summary.md` is generated from the JSON (twin, AC-031).

### 3.6 `forms_embeds.json`

Forms: `{route, locator, action, method, input_names[], has_submit, function_status: "observed_markup_only"}`. Embeds: `{route, locator, kind: iframe|script_widget|video|map|social, src_host, third_party: bool, function_status: "observed_markup_only"}`. `function_status` has exactly one allowed value in this ABM. No submissions, no script execution beyond what rendering already did (AC-026).

### 3.7 `design_evidence.json` / `.md`

Observed only: colors seen in inline styles and computed `<style>` blocks (hex/rgb literals, counted), font-family declarations, heading font sizes if literal, section vocabulary = distinct top-level `<section>/<header>/<footer>/<nav>` class names with counts, viewport meta. Everything `label: observed`; anything not literally present is `absent`, not estimated. No palette recommendation (AC-027).

### 3.8 `media_classification.json`, `loss_ledger.json`, `findings.md`

- Classification classes (Plan §4A Phase 2, AC-028): `referenced`, `social_only`, `brand_global`, `editorial`, `integration`, `external`, `duplicate_variant`, `broken`, `apparently_unused`, `unknown`. Each item keeps its raw `url` and a `raw_ref` into `raw/media/inventory.json`; a `staging_domain` flag is carried, never rewritten. Class rules are deterministic and listed in `prepare/rules/media_rules.md`; every rule cited per item under `basis`.
- `loss_ledger`: one record per required derivation that could not be made: `{requirement: "AC-0xx or field", route|null, cause: "absent_raw|unsupported_raw|parse_failure|rule_gap", absence_ref|null, effect}`.
- `findings.md`: human twin of loss_ledger + disagreements + the staging-domain fossils count + a `recommendation`-labeled section that is clearly separated.

### 3.9 `SITE_RECON_BRIEF.md`

Fixed section order: 1 Identity and source run · 2 Completeness and limits · 3 How to read this pack (links to every artifact, counts must equal `pack.json`) · 4 Site structure at a glance · 5 Content notes (incl. Thrive/rendered-only routes) · 6 SEO notes · 7 Media notes · 8 Integrations, forms, embeds · 9 Observed design · 10 Disagreements and losses · 11 Answering the B7 questions (each of the 12 questions in `ABM_ACCEPTANCE_SPEC.md` §B7 with the artifact and field that answers it, or "not answerable — see loss L-n"). Every link is relative and must resolve after copy.

### 3.10 Reproducibility normalization (AC-032)

Two Prepare runs on the same raw are equivalent when all JSON artifacts are equal after removing `built_at`, `pack_id`, `prepare_version`, and after sorting arrays whose order is not semantic (`sources[]`, `source_pages[]`, `categories[]`). `pack.json.normalization` names this rule. Markdown twins are compared after stripping the generated header line.
