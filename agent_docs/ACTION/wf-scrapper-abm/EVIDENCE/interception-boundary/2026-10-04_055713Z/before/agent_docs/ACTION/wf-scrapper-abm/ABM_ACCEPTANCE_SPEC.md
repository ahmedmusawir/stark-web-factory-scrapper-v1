# wf-scrapper-abm — ACCEPTANCE SPEC (bound)

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.

## Master Acceptance Spec v0.2 (10x Lab) + repo bindings (Architect) — 48 ACs, IDs preserved

> **Version:** 1.2 · **Date:** 2026-10-02 · **Status:** rulings applied; BUILD_READBACK review/build approval pending; build NOT STARTED. JARVIS Architect amendment under Tony’s delegated authority. Current prospective rulings E-13–E-19 below; earlier errata E-05–E-12 retained; retained historical E-01–E-04 are scoped by those supersessions.
> **Bindings referenced:** `ABM_CONTRACTS.md` (schemas, paths, rules) · fixtures §0 · commands §0.2 · B7 questions §B7.
> **Grading rule (J-16, J-20):** QA grades the literal check. Intent met but wording not met → PASS-PENDING-ADJUDICATION → erratum. Engineer "implemented" and QA "verified" are separate columns in `ABM_LEDGER.md`.

---

## 0. Bindings shared by many ACs

### 0.1 Fixtures — `tests/fixtures/` (all offline; served by `tests/fixture_server.py` on `127.0.0.1:<random port>` via `http.server`; fixed origin 127.0.0.1:8765 for deterministic snapshots, ephemeral ports for other control cases; per-execution request log retained)

| ID | Fixture | Serves |
|---|---|---|
| F-01 | `site_basic/` | 6 HTML pages, `robots.txt` with `Sitemap:`, `sitemap_index.xml` → 2 children, one duplicate `<loc>`, one `<loc>` with `utm_source`, one off-host `<loc>`, one missing page (404). |
| F-02 | `site_rest/wp-json/` | Static declared collections only (no root enumeration): `wp/v2/pages` (2 pages of 100 → `X-WP-TotalPages: 2` via server rule), `posts`, `media`, `categories`, `tags`; `users` → 401. One page object with empty `content.rendered` whose HTML has 400 words (REST-empty/rendered-present heuristic, no plugin attribution). One object whose `link` matches no route. Two objects with the same `link` (ambiguous). Full `yoast_head_json` on 3 objects, missing on 1; separate null optional fields, unknown nested fields, malformed mandatory identity/structure, complete response bytes and object-array provenance cases. |
| F-03 | `site_block/` | Routes returning 403, 429, a 200 "Access Denied" soft-block page (<10 KB), an empty 200 body, a stall exceeding the preserved 90 s timeout (or a controlled timeout injected at the declared boundary, with that limitation recorded); independent fresh cases for each refusal; ordinary background POST and incidental third-party failure cases. |
| F-04 | `site_redirect/` | 301 → in-scope route; 302 → `www.` twin; 301 → `evil.example`; 6-hop loop. Cover each intentional stream; denied destination must receive no request, permitted hops share completion-based pacing. |
| F-05 | `site_media/` | Pages referencing: internal img, `srcset`, `og:image`, JSON-LD logo, CSS background, external img, `*.mystagingwebsite.com` img, duplicate URL variants (`?v=1`), broken (404), one media object in REST not referenced by any page. |
| F-06 | `site_conflict/` | REST `title.rendered` ≠ rendered `<title>`; canonical differs; `og:image` differs. |
| F-07 | `site_forms/` | `<form action=/x>`, `<iframe src=youtube>`, `<script src=hubspot>`, mailto link, inert `<form>` without action. |
| F-08 | `site_design/` | Inline hex colors, `<style>` with font-family, sections with class names; a second page with no literal styles. |
| F-09 | `raw_valid/complete/` | Explicit six-route complete variant from Rulings 1.2 §3, excluding F-01’s required missing route from this variant’s declared set. All required captures/REST mappings succeed; retain F-02 pagination and optional-absence cases. Fact-driven deterministic snapshot procedure in that section; no automatic golden acceptance. |
| F-10 | `raw_broken/` | Copies of F-09 with: malformed `manifest.json`; missing `rest/map.json`; `schema: abm-raw-v1`; `rest_ref` to a nonexistent file. |
| F-11 | `input_hostile/` | Project names `../x`, `a b`, 65 chars; URL `ftp://`, `not a url`; `--input` JSON with `{"url": "../../etc"}`; HTML with `<script>` and JSON with `"</script>"` strings. |
| F-12 | `raw_partial/` | Structurally valid partial package: all mandatory files/route outcomes/map entries retained; one HTML capture failure (null html_file with typed absence) and a different route with REST unavailable (map entry retained with reason). Reconcile hashes/counts and exactly 2 required evidence losses. For AC-029/038; never remove a mandatory map entry or corrupt an artifact. |
| F-13 | `secrets_sentinel` | `.env` containing `SENTINEL_TOKEN=abm-sentinel-9f3c`; named synthetic fixture input for the boundary-aware AC-044 scan. |
| F-14 | `screenshots/` | One PNG for the authored-evidence case. |

All fixture/helper paths in §0 are planned build artifacts, **not existing test infrastructure**. M-01–M-04 are APPROVED in [Rulings 1.2](ABM_RULINGS_1_2.md). §3 there binds exact variants, consumers, required versus optional losses and snapshot procedure; §4 binds leak scan scope. No fixture/product checks executed by this documentation/readback pass.

### 0.2 Canonical commands (must match README, RUN_NOTES, and CLI error text verbatim)

```
venv/bin/pytest -q                                                    # regression (bound count recorded in ledger at C1 close)
python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com [--limit N] [--mode sitemap|homepage] [--skip-prepare] [--no-media-head]
python -m discover_site.discover https://cyberizegroup.com --mode sitemap --out <dir>
python -m smart_crawler.crawler --project CyberizeGroup [--routes <routes.json>] [--limit N]
python -m smart_crawler.validate --project CyberizeGroup --run <run_id>
python -m prepare.build --project CyberizeGroup --run <run_id> [--no-copy-raw]
```
Exit codes: 0 success (including partial with typed absences) · 1 input/IO/contract error · 2 usage error or stop rule · 3 Prepare refused invalid raw (AC-020).

### 0.3 Live-run bindings (R4/R7 history; E-05 current policy)
Target: `https://cyberizegroup.com`, sitemap mode, all selected routes; machine binding Zorin at the declared repo. E2 retains two full runs ≥1 hour apart. CHK retains one integrated `--limit 10` smoke. CHK uses `--limit 10 --skip-prepare` and is the **single shared outstanding smoke allocation** (E-15); the separate old-code P0 smoke is retired. No live run is authorized by the readback instruction. Approx. 40 min/90 MB are historical estimates, not proven current limits. Default disk bound remains 500 MB; exact request/time budgets must be bound before collection, with no enlargement here. First intentional 403/429/challenge stops further collection; no automatic retry/restart. See Contracts §1.4, Rulings 1.2 E-15 and BUILD_READBACK §6–7 for the current shared allocation/source identity; earlier register is history. QA Lead decides candidate-bound reuse; T-21 is not an automatic additional pair of full runs.

---

## A — Operability and input boundaries

| ID | Requirement | Bound check |
|---|---|---|
| AC-001 | Reproducible setup | In an independently authorized clean environment follow README §Setup: Python 3.12.3, fresh venv, `venv/bin/pip install -r requirements-lock.txt`, `venv/bin/pip check`, normalized sorted exact-package comparison per Rulings 1.2 §2 (only unlocked pip/setuptools/wheel tooling excluded and recorded), then lock-matched Chromium setup. Record Python/platform, actual browser identity and lock hash. Regression green and `python -m recon_pipeline --help` exit 0 after implementation. Clean-environment check NOT RUN; working environment not reinstalled here. |
| AC-002 | Inputs validated | F-11 cases: each prints the three-line actionable error (what was wrong naming the flag, canonical example, `--help`) to stderr, exit 2; valid input exit 0. Test `tests/test_pipeline_cli.py`. |
| AC-003 | One invocation, plus separable entry points | C6 fixture and CHK Capture milestone explicitly use `python -m recon_pipeline --project Fix --url http://127.0.0.1:<port> --skip-prepare`; C6 owns minimal reader/validation adapter. Stage P completes default invocation; E1 runs F-09 complete plus separate F-01/F-02 mixed-partial variant, producing raw manifest and pack. Prepare-only rerun with fixture server stopped and network denied (`tests/netblock.py`) produces a NEW pack with zero network calls. Exact variants: Rulings 1.2 §3. |
| AC-004 | Paths stay inside outputs, no overwrite | F-11 project names rejected before writes; two runs have different new folders; run-1 file inventory/hashes unchanged after run 2. Validate schema-declared tool-owned filesystem references: reject absolute paths, traversal and symlink escapes. Preserve untouched source strings/HTTP(S) URLs even when they look like filesystem paths; do not blanket-grep source JSON. |
| AC-005 | Scope, redirects, limits | F-04: in-scope 301 → captured with `redirect_chain`; `www.` twin → captured; `evil.example` → `unsupported/redirect_out_of_scope`, no HTML file, fixture request log shows **no** request to `evil.example`; loop → `failed/redirect_loop`. F-03 independent cases: first intentional 403/429/challenge → blocked, exit 2 with manifest and remaining work skipped; no further intentional request. Shared logs prove ≥5.0 s after operation completion before next intentional operation/hop; retries = 0. Normal background POST is allowed without form interaction; incidental third-party failure is recorded separately; document-preventing challenge stops. No transport/identity fallback or automatic restart. |
| AC-006 | Failures visible | F-03 timeout → `failed/timeout`, exit 0, absence recorded; SIGINT during F-01 run (test sends signal after page 2) → manifest written with `stopped_early: true`, `streams.html: partial`, exit 130; F-10 malformed input JSON → exit 1 with message; README §Rerun documents that reruns create new run folders and never resume in place. |

## B — Capture fidelity

| ID | Requirement | Bound check |
|---|---|---|
| AC-007 | Route set + identity rule | F-01 → `routes.json`: duplicate `<loc>` collapsed with `input_urls` length 2; `utm_source` stripped with original kept in `input_urls`; off-host in `dropped` with `off_host`; missing page still a route (absence comes later). Test asserts exact route list. |
| AC-008 | Every route accounted per stream | Validator check: selected/known `routes` == unique `pages[].url`, exactly one outcome each; HTML absences reference those outcomes and add no pages; counts reconcile without double-counting; for rest: every route has a `by_route` entry; for media: n/a per route. Run on F-09 and on each live run. |
| AC-009 | HTML untouched | Test captures `result.html` via a stub crawler returning known bytes including `\r\n`, BOM, and non-UTF-8-safe chars; file bytes == `result.html.encode("utf-8")`; sha256 in manifest matches. Serialization boundary declared: crawl4ai `result.html` (str) → utf-8 bytes. |
| AC-010 | Block pages never captured | F-03 independent cases: intentional 403/429 blocked; explicit denial/challenge HTTP 200 blocked with recorded header/DOM predicate and library reason when available; empty 200 → unsupported/empty_body, timeout → failed. No invented CrawlResult anti-bot flag: installed is_blocked() returns tuple, propagated as success/error_message/crawl_stats; near-empty heuristic alone is not explicit challenge. Concrete detection/negative cases in BUILD_READBACK §3. Available block bytes retained separately; never captured HTML, unavailable body explicitly absent. Live captured pages still status 200 and html_bytes >1000. Detection/control implementation NOT PROVEN. |
| AC-011 | REST + SEO survive | F-02: each complete `rest/responses/<collection>-<page>.body` equals fixture bytes at the declared browser-decoded response boundary and hash matches. Indexed object derivatives deep-equal their saved response array element including unknown fields; response reference, zero-based position, serialization and derivative hash validated. Present Yoast survives value-for-value; missing versus null optional content/Yoast recorded separately, never fabricated. Mandatory identity/structure malformed → explicit failure. No root read or four-field production filter. |
| AC-012 | Pagination + non-REST routes | F-02 pages collection: both pages fetched, `fetched_objects == total`; route with no object → `unmapped`; two objects same link → `ambiguous` with both candidates; object with no route → `unrouted_objects`. |
| AC-013 | Site-level inventory retained | `discovery/` holds robots + every sitemap fetched, `rest/index.json` lists every collection with status; F-02 `users` 401 → collection `unavailable` + absence. |
| AC-014 | REST-empty / rendered-present | F-02 REST-empty/rendered-present object → `map.json.content_rendered_empty` lists it; Prepare `content_inventory` for that route: `content_source: rendered`, `thrive_signal: true` with heuristic basis citing both streams (no plugin cause), `word_count_rendered ≥ 300`; empty raw REST stays empty and does not erase rendered text. Live: at least one Cyberize route shows the same signal (October diagnostics establish one post, not site-wide prevalence); if none, recorded as a finding, not a fail. |
| AC-015 | Media inventory with provenance | F-05: every referenced URL appears once in `inventory.json` with `source_pages[]` and `context`; REST-only media item appears with `rest_ref` and empty `source_pages`; staging item `origin: staging_domain`; in-scope broken → `retrieval.status: 404`; off-scope external/staging URLs → skipped/off_scope_untested with zero deliberate HEAD/GET probes; missing width/height → `null`, never guessed. |
| AC-016 | Manifest + stage log explain the run | Validator passes; typed `stage_log.txt` intentional-operation/pause/stop records reconcile with the controlled server log, including redirect hops and shared completion-based gaps; incidental browser host/resource/status events counted separately, not mislabeled as deliberate collection or per-resource-paced; `versions.tool_commit` equals `git rev-parse HEAD` at run time or `"unknown"` outside a repo; `counts` recomputed by validator match. |
| AC-017 | Typed absences | F-01 404 → `failed/http_404`; F-03 independent fresh cases → blocked ×3, unsupported ×1, failed ×1 (not three refusals in a single live run); F-02 users → `unsupported/http_401`; `--limit 2` → remaining routes `skipped/limit`; stop rule → `skipped/stop_rule`; SIGINT test proves earlier captured files survive. |
| AC-018 | Authored evidence distinct | F-14: run with a PNG in `screenshots/` → manifest `streams.screenshots: authored`, file sha256 listed, bytes unchanged; run without → `empty` + absence `screenshots/skipped/none_supplied`. Tool never writes into `screenshots/` except README.md. |

## C — Prepare and provenance

| ID | Requirement | Bound check |
|---|---|---|
| AC-019 | Raw untouched by Prepare | Hash and inventory source run before/after successful F-09 and failing F-10 Prepare; identical. Observe filesystem write/open/rename/delete calls resolved to canonical targets and deny any source-run mutation (including symlink escape). Read-only source access, plus byte-identical copy into NEW pack/raw, is permitted. Compare copied raw hashes; do not grep for every write mode and reject legitimate pack construction. |
| AC-020 | Invalid raw fails visibly | Each F-10 case → exit 3, no `pack.json` written, error names the file and check; no partial pack folder left behind (or it is named `*.failed`). |
| AC-021 | Provenance on every derived record | Walk tool-authored derived artifact records (exclude archived source data under raw): label and nonempty sources[] required; source refs resolve within raw and CSS locators resolve; absence records cite existing typed outcome. Source object unknown fields remain untouched, not mistaken for tool provenance envelopes. Live independent Executor spot-checks 10 records with selection recorded. |
| AC-022 | Labels distinguishable | F-09 complete with optional absences and F-12: at least one observed, inferred with basis, and absent with absence_ref record. Tool-authored recommendation labels/advice appear only in findings.md, not generated fact records. Raw/quoted source strings and unknown object fields containing those words are preserved with provenance; check typed authored fields, not all JSON text. |
| AC-023 | Sitemap/IA + content inventory | F-01+F-02 expected `site_map.json` snapshot (tree, types from REST, `unknown` for no-REST route); `content_inventory` has one record per route including the 404 route with `content_source: none` and `absence_ref`. |
| AC-024 | Disagreements visible | F-06 → `disagreements.json` has 3 records (title, canonical, og:image) each with both values and both sources; `seo_inventory` for that route has `disagree: [...]`; no field chooses a winner. Separate F-02 check records REST-empty/rendered-present content difference and distinct missing/null fields without changing the F-06 three-conflict count. |
| AC-025 | SEO preserved | Test: for every route in F-09 pack, present `seo_inventory[route].rest.*` deep-equals the object's `yoast_head_json`; `rendered.*` equals parsed `<head>` values; missing → `null` with `label: absent`. No observed field value is invented when absent from both sources; explicit absent/null metadata remains allowed with provenance. Missing and explicit source null are distinguished. |
| AC-026 | Forms/embeds honest | F-07 → 2 forms (one `action: null`), 2 embeds (`iframe`, `script_widget`); `mailto` classified as a link, excluded from embed count; every `function_status == "observed_markup_only"`; test asserts the enum has one value. |
| AC-027 | Design observed, not prescribed | F-08 literal colors/fonts/sections observed; absent styles labeled absent. Inspect tool-authored design labels/advice fields/sections for prohibited recommendations. Preserve source class/title/quoted strings containing words such as should or recommend, with provenance. Positive quoted-source and negative authored-advice fixtures prove the distinction; no blanket word grep. |
| AC-028 | Media classes preserve everything | F-05 → every raw inventory item appears exactly once in `media_classification.json` with a class from the bound enum and a `basis` citing `prepare/rules/media_rules.md` rule id; `apparently_unused` item retains `url` and `raw_ref`; staging item keeps `staging_domain: true` and original URL. |
| AC-029 | Loss surfaced | Use the structurally valid F-12 with all route/map entries intact and two typed unsuccessful-source outcomes (HTML failure and a different route’s REST unavailability), null optional file refs and reconciled hashes/counts → `loss_ledger` has 2 records with correct `cause`; `findings.md` lists them; `pack.json.completeness.status == partial`. |
| AC-030 | Confidence ≠ authority | Instrument resolved filesystem mutation targets: no source-run/prior-pack deletion, rename or writes; creation within NEW pack and byte-identical raw copy allowed. Hash source before/after. Staging URLs remain byte-for-byte and duplicate variants retained; no deletion/URL promotion based on classification. Test symlink/traversal escapes explicitly. |
| AC-031 | Twins agree | For `site_map`, `seo_summary`, `design_evidence`, `findings`: the `.md` is generated from the JSON by `prepare/twins.py`; test parses counts and identifiers back out of the `.md` and compares to JSON. |
| AC-032 | Prepare reproducible | Two Prepare builds on same F-09 produce NEW pack-1/pack-2; compare by Contracts §3.10 and Rulings 1.2 §3: validate all actual hashes first, then canonicalize only declared volatile metadata and recompute comparison hashes of metadata references from leaf to parent. Preserve raw bytes, content, meaningful ordering, references, outcomes and counts. Print normalization rules; negative mutations must be detected. Repeat offline on one retained E2 raw run; no extra collection. |

## D — Architect Data Pack usability

| ID | Requirement | Bound check |
|---|---|---|
| AC-033 | Entry brief points to real inventory | Test: every relative link in `SITE_RECON_BRIEF.md` resolves; counts quoted in §3 of the brief equal `pack.json.counts`. |
| AC-034 | Pack answers B7 | Brief §11 maps each of the 12 B7 questions to an artifact+field or a loss id; test asserts all 12 present. |
| AC-035 | Cold-read without live access | **R5:** a fresh Fable session, during QA, before Gate Q, receives only the pack folder (with `raw/`), answers the 12 B7 questions citing records, lists residual questions. SOL judges against §B7 required fields. Any answer not backed by a cited record = FAIL. |
| AC-036 | Drill-down works | From 5 chosen records (incl. one disagreement, one loss) follow `sources[]` into `raw/` and confirm the locator; independent QA Executor records the trace. |
| AC-037 | Portable delivery unit | Copy NEW pack to isolated different-depth directory; AC-033 link and AC-021 provenance checks pass. No workspace-absolute tool-owned filesystem references. Raw archived strings/URLs and quoted source values remain intact; test resolved reference graph rather than blanket searching all bytes for a workspace path. |
| AC-038 | Honest completeness | F-09 → `complete`; F-12 → `partial` with reason and the 2 absences listed in `unresolved_mandatory`; a raw run with `stopped_early: true` → `blocked` or `partial`, never `complete`; the brief §2 states the status in its first sentence. |

## E — Integrated quality and regression

| ID | Requirement | Bound check |
|---|---|---|
| AC-039 | Full chain on fixture site | E1 `tests/test_e2e_fixture.py` runs default Capture+Prepare on F-09-complete source variant (complete) AND separate F-01 base + F-02 gap + F-05/07/08 variant (honest partial). Full real installed Crawl4AI/browser-session transport; fixture server replaces target only. Validate exact fact-derived records and deterministic snapshot procedure Rulings 1.2 §3, not an auto-accepted tool output. |
| AC-040 | Real target reproducible | Two full Cyberize runs (E-2), ≥1 hour apart: both validators green; `counts.routes` equal; `captured` differ by ≤2 (site may change); both packs `complete` or `partial` with reasons; manifests, `routes.json`, `pack.json` of both retained in `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/live/`. |
| AC-041 | Certified behavior stays green | Bound no-break suite: all bim000/bim001 tests except documented rewrites under E-01 and E-05/E-06/E-07 (manifest/output bindings, intentional browser transport, completion-based pacing, zero retries, first-refusal stop, redirect scope and image wait) which are rewritten with the contract reason in the test docstring and listed in `CHANGELOG.md`. Behaviors that must not change: status validation, USER_AGENT single source, `--project` validation and error text, run-folder-per-run, slug and collision rules, exit code 2 on stop rule, no stealth. |
| AC-042 | Limits recorded | Each live run's manifest and stage log give elapsed, request count, retries, bytes; a test proves `--limit 3` on F-01 stops at 3 with `skipped/limit`; a disk-budget guard (`--max-bytes`, default 500 MB) aborts with a typed absence and `stopped_early`. |
| AC-043 | Untrusted input contained | F-11 tool-owned project/URL/reference traversal rejected before unsafe write; source markup is data. Raw HTML/JSON in source run and pack/raw retain exact bytes/hashes, including script strings. Generated JSON parses and recovers source values; generated Markdown/HTML presentation quotes/escapes adversarial scripts, tags, quotes, backticks and closing fences so they cannot become active markup. Presentation scanner explicitly excludes the raw archive only from escaping checks; verify raw hash fidelity separately. README states viewer limitations. |
| AC-044 | No secrets leak | F-13 injects the synthetic value into private input/env. Enumerate and scan every generated run, pack (including raw), evidence, log, report and ZIP member for that execution per Rulings 1.2 §4. Only exact named/hash-verified fixture/governing source exemptions; no blanket report exemption. Isolated intentional-leak control must be detected/nonzero, then clean-artifact scan zero. Log paths/counts/exit, not matched bytes. Actual scans/control NOT RUN here. |

## F — Handoff and certification evidence

| ID | Requirement | Bound check |
|---|---|---|
| AC-045 | Auditable, resumable | `agent_docs/ACTION/wf-scrapper-abm/ENGINEERING_LOG.md` has one entry per task (C1…P6, E1, E2) in the template; `RECOVERY.md` checkpoint updated at every task boundary; a cold reader can name the next task from `RECOVERY.md` alone. |
| AC-046 | Ledger complete | `ABM_LEDGER.md` has all 48 rows with engineer state, evidence path, QA test ids; no mandatory row is PASS without a QA evidence path. |
| AC-047 | Instructions match tool | independent QA Executor follows README + RUN_NOTES on a clean clone (T-01) without any undocumented step; every command in docs equals CLI error text (grep test `tests/test_docs_commands.py`). |
| AC-048 | Candidate and evidence agree | Closeout record names implementation SHA, QA verdict, review dispositions, RRM id or no-repair ruling, cleanup and merge SHAs; any product change after Gate Q triggers impact retest (J-22). |

---

## B7 — The 12 questions the pack must answer (AC-034/035)

1. How many routes does the site have, by type (page/post/category/unknown)?
2. Which routes could not be captured, and why (typed)?
3. For a given route, what are its rendered title, REST title, meta description, canonical, and do they agree?
4. Which routes have content only in the rendered stream (legacy thrive_signal heuristic, with its basis and no plugin-cause assertion)?
5. What JSON-LD types are present site-wide?
6. How many media items exist, how many are internal/external/staging-domain, how many broken?
7. Which media items are apparently unused, and is the evidence for that stated?
8. What forms exist, and what is known about whether they function?
9. What third-party embeds and script integrations are present?
10. What colors, font families, and section vocabulary are literally observed?
11. Where do REST and rendered evidence disagree?
12. What is the completeness status and what mandatory evidence is unresolved?

Required fields per question are the artifact fields named in `ABM_CONTRACTS.md` §3; QA Executor proposes exact expected values and commands in Q1; SOL approves/amends the candidate-bound plan. No live answer is invented in advance.

---

## Errata lane — append after freeze (J-20, J-21)

| Erratum | AC IDs | Original wording / issue | Approved interpretation / change | Provenance / date (historical vs amendment) | QA confirmation |
|---|---|---|---|---|---|
| E-01 | AC-041 | "Previously certified required behavior remains green" — bim001 tests literally assert `schema == bim001-manifest-v1`, 23 manifest keys, 11 page keys, `md_file`, `run_summary.json`. | Those assertions change to the `abm-raw-v2` contract; markdown and `run_summary.json` outputs are retired. Contract reason: R8. All other bim000/bim001 assertions unchanged. Test docstrings and CHANGELOG cite E-01. | R8, 2026-09-18, Director-approved, pending QA confirmation | |
| E-02 | AC-005 | "respects the approved site scope, redirect policy, and access limits" | `robots.txt` is fetched and recorded, not enforced (polite ladder rung (a) is the access policy; Director-owned). Scope = `hosts_allowed`; redirect policy per Contracts §1.4. | R4/R6 context, 2026-09-18, Director-approved, pending QA confirmation | |
| E-03 | AC-035 | "A separate Architect/QA session answers B7" | The cold-reader is a fresh Fable session during QA, before Gate Q; SOL judges. | R5, 2026-09-18 | |
| E-04 | AC-015 | "retrieval status" | Media bytes are never downloaded; retrieval = one HEAD per unique URL under pacing, or `skipped` with `--no-media-head`. | Architect binding under R4 limits, 2026-09-18, Director-approved by R4 (estimates), pending QA confirmation | |

### Amendment provenance and supersession

E-01–E-04 above are preserved historical entries, not new approvals. E-05–E-12 are newly allocated here: the inspected packet ended at E-04; the intake's alleged missing E-05–E-09 were not found. P0 finding E-5 is a different identifier. These new rows do not reconstruct missing records or claim earlier Director approval. All use **JARVIS Architect amendment under Tony’s delegated authority**, 2026-10-02. QA confirmation is PENDING.

| Erratum | AC IDs | Old rule / defect | Current amendment | Provenance | QA |
|---|---|---|---|---|---|
| E-05 | AC-005,006,010,013,016,017,040,041,042 | 2–5 s/request, retry once/10 s, three blocked, historical recovery retry | Intentional operations shared five seconds after completion; no retry/switch/restart; first intentional refusal/challenge stops; background observed separately, normal POST allowed without form actions | JARVIS delegated amendment | PENDING |
| E-06 | AC-005,007,009,011,012,013,025,041 | requests/root REST enumeration; wait_for_images=False; falsely confirmed Yoast | Browser-session discovery/REST; declared collections/all fields/pagination; rendered Crawl4AI and demonstrated True/90 s/3 s/BYPASS/UA settings; optional fields not assumed | JARVIS delegated amendment | PENDING |
| E-07 | AC-005,015,018,028,041 | Check scope after redirect; HEAD every media host; ambiguous no-media-download text; screenshot README paradox | Check each intentional hop before dispatch, max five; inventory offscope media but do not probe; renderer resources separate; tool writes only screenshot README | JARVIS delegated amendment | PENDING |
| E-08 | AC-011,012,013,014,021,024,025 | Per-object files falsely called original bytes; empty REST treated as plugin signal | Complete browser-response bytes + hashes; indexed object derivatives preserve values/unknown fields; mandatory structure validation vs optional missing/null; complementary rendered content and heuristic-only legacy signal | JARVIS delegated amendment | PENDING |
| E-09 | AC-008,016,019,020,023,029,038 | Pages union absences double count; invalid fixture expected partial pack | One page outcome and REST mapping per route; absences refer to outcomes; invalid mandatory structure refused; valid F-12 partial losses retained | JARVIS delegated amendment | PENDING |
| E-10 | AC-026 | Mailto counted among three embeds | F-07 two forms, two embeds; mailto remains a link | JARVIS delegated amendment | PENDING |
| E-11 | AC-001,039,040,041,042,047 | P0 treated as passed; obsolete recovery commands; install equality unresolved | P0 stays partial, diagnostic success not certification; current readiness planned; historical recovery/root commands superseded; dependency and shared-budget decisions M-01/M-03 remain open | JARVIS delegated amendment; no new live budget | PENDING |
| E-12 | AC-021,035,036,045,046,047,048 | Cody both engineer/executor, Gate Q before cleanup, precommit candidate mislabeled | QAM: Cody Engineer, separate Executor, SOL Lead; Q1/Lead decision/Q2; Tony cleanup accepted before final Gate Q; candidate pinned after Tony commit; later reviews/RRM remain | JARVIS delegated amendment | PENDING |

The preceding 1.1 rows retain their historical decision state. M-01–M-04 are now resolved prospectively by E-13–E-16 below; no implementation/QA result is implied. All test/fixture paths remain plans until implemented. This amendment performs documentation checks only.


### Prospective rulings — revision 1.2 (2026-10-02)

Provenance for every row: **JARVIS Architect ruling under Tony's delegated authority**. These rows supersede conflicting earlier active text prospectively; E-01–E-12 approval/provenance states above are not rewritten. QA confirmation remains NOT RUN/PENDING. BUILD_READBACK is authorized and delivered; the build is not approved.

| Erratum | AC IDs | Ruling / precise effect | QA groups | QA confirmation |
|---|---|---|---|---|
| E-13 | AC-001, AC-047 | M-01 approved: existing lock install, pip check, normalized exact package comparison with recorded unlocked tooling exclusions, environment/browser/hash identity | T-01 | PENDING |
| E-14 | AC-003, AC-007, AC-008, AC-009, AC-011, AC-012, AC-013, AC-014, AC-017, AC-019, AC-020, AC-021, AC-022, AC-023, AC-024, AC-025, AC-029, AC-031, AC-032, AC-033, AC-034, AC-035, AC-036, AC-037, AC-038, AC-039 | M-02 approved: complete F-09 variant distinct from F-01 required 404/F-02 faults; F-12 valid two-loss partial; deterministic fact-driven snapshots with integrity-first reference-aware normalization | T-03, T-05, T-06, T-07, T-08, T-09, T-12, T-13, T-14, T-15, T-17, T-18, T-19, T-20, T-21 | PENDING |
| E-15 | AC-039, AC-040, AC-042 | M-03 approved: CHK one shared limit-10 --skip-prepare smoke; old-code P0 smoke retired; E2 two full runs ≥1h apart, SOL reuse; further live volume requires Tony | T-21, T-22 | PENDING |
| E-16 | AC-044 | M-04 approved: exact generated scan/exemption inventory, include reports/raw, isolated leak control, no sentinel echoed in clean reports | T-23 | PENDING |
| E-17 | AC-003, AC-008, AC-019, AC-020, AC-039 | Minimal reader in C6; C6/CHK Capture-only --skip-prepare; P1 pack construction; default complete during Stage P, full integration E1/E2 | T-03, T-06, T-12, T-21 | PENDING |
| E-18 | AC-004, AC-019, AC-021, AC-022, AC-027, AC-030, AC-037, AC-043 | Check authored filesystem/presentation/advice boundary; preserve source strings/raw bytes; NEW pack/raw copy allowed, source mutation forbidden; replace contradictory greps with behavioral checks | T-02, T-12, T-13, T-14, T-17, T-19, T-23 | PENDING |
| E-19 | AC-005, AC-010, AC-017, AC-041 | Identify real installed is_blocked tuple/error/crawl_stats instead of nonexistent flag; explicit challenge versus empty/ordinary failure maintained; detector and redirect mechanisms are engineering proposals requiring fixture proof, no silent fallback | T-04, T-05, T-07, T-22 | PENDING |

Read [ruling dispositions and exact bindings](ABM_RULINGS_1_2.md) and [BUILD_READBACK](BUILD_READBACK.md). No product/fixture/helper implementation is claimed by these documents.

## Launch errata — E-20/E-21 (QA PENDING)

| ID | Binding | ACs | QA groups | QA disposition |
|---|---|---|---|---|
| E-20 | Browser-observed correlated redirect completion; ≥5s pre-dispatch gate; delayed fixtures; no redirect-body prerequisite | AC-005,006,010,016,041,042 | T-04,05,07,11,22 | PENDING |
| E-21 | Retain cf-mitigated; exclude sensitive headers; positive/false-positive detector proof | AC-005,010,011,016,017,041 | T-04,07,08,11,22 | PENDING |
