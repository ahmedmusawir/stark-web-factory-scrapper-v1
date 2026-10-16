# Proposed candidate-specific test plan — DRAFT (candidate UNBOUND)

Executor: Claudy · 2026-10-15 · For the QA Lead's review and amendment. Plan identity/hash is assigned only after the candidate SHA is inserted in §0. Every test below is NOT RUN. Scope is the current tool (DECIDE → COLLECT → agent-assisted PREPARE) per `CURRENT_TOOL_SCOPE.md`; the retired controller campaign is not executed. Applicability column follows the engineering crosswalk but is the QA Lead's call.

## 0. Binding sheet (to fill at re-pin)

| Field | Value |
|---|---|
| Candidate branch / full SHA | `qa/wf-scrapper-abm` / **PENDING Tony** |
| Expected 52-file source identity at candidate | `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` (any other value → re-decide reuse) |
| Dependency identity | `requirements.txt` `231e1d8f8b3b1b2b8d382b98beadc05361529805cd93081890fff47606df5f46`; `requirements-lock.txt` `e6c3e1a9a89f6cd8f5dfb71694c74d54d6b34237929f06a0ce3aa519b89a594c` |
| Environment | Python 3.12.3 · crawl4ai 0.9.3 · playwright 1.52.0 · bs4 4.13.4 · pytest 8.3.5 · markdown-it-py 4.2.0 · existing `venv/` (no installs) |
| Fixture archives | `response_2026-10-11_210309_prepare-v01.zip` `d54bbaf0c07e1fbd41937afc11e3111378743d8903bdc6254d2e3bb329cc5a63`; `response_2026-10-13_223736_growth-call-follow-up.zip` `fdf18de8838f36344459555041a12e4f0cf463044a1f211f6241a7bf420ab4a8`; 34 manifest files |
| Evidence workspace (proposed, QA Lead to confirm lane) | `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/Q2_<ts>/` with pytest `--basetemp` in the session scratch dir; never the engineering evidence paths |
| Network budget | **0 external requests.** Loopback fixtures only. Any live check needs Tony's separate explicit scope. |
| Plan hash / QA Lead approval reference | PENDING |

## 1. Pre-Q2 gates (all must pass; each failure is a STOP)

G1 Identity: `git rev-parse HEAD` equals candidate SHA; `git status --porcelain` shows no modified tracked product/test files; 52 paths hash to the expected identity.
G2 Fixtures: both archive hashes match; run `restore-fixtures.py` only if files are missing; afterwards 34/34 hash-match. Missing/corrupt = FAIL, never skip.
G3 Environment recorded (versions above; browser version from a native run's `runtime.browser`). `pip check` is read-only and allowed; no install.
G4 Smoke: engineering suite re-run on the candidate — command in T-22 — must be 97/0/0/0 before any other test.

## 2. Per-group bindings

Legend: **Cmd** = command or method; **Fix** = fixture; **Exp** = expected; **Neg** = negative case; **Stop** = stop condition. All commands run from repo root with `PYTHONDONTWRITEBYTECODE=1`.

**T-01 Setup/operator path (AC-001, AC-047) — Retained.** Cmd: follow only `CURRENT_TOOL_SCOPE.md` + DECIDE.md/COLLECTOR_SIMPLIFICATION.md/SKILL.md from a *fresh clone of the candidate* into scratch, using the existing venv interpreter (no install). Exp: every documented command resolves (`--help` exits 0 for 3 entry points); Prepare's saved-capture test is documented as needing fixture restoration. Neg: run `test_prepare_saved.py` in the clone *before* restoration → the actual-capture test must FAIL (not skip), proving the dependency is honest. Gap recorded: clean-venv install NOT performed. Evidence: command log, `--help` outputs.

**T-02 Input/output boundaries (AC-002, AC-004) — Mixed.** Cmd: `venv/bin/python -m recon_pipeline collect --plan P --collection C` with plans: non-HTTP scheme, credentials in URL, fragment, `/wp-json` root, `paginate:true` without `max_pages`, paginated URL starting at page 2, unknown key. Exp: exit 2, "Collector refused:", no collection directory created (assert dir absent). Existing dir → refused. DECIDE `select` with unknown row/ID, conflicting include/exclude, HTML on REST row → exit 2 "DECIDE refused:" and no decision file. Prepare `--out` existing / inside collection → exit 2 and input bytes unchanged (hash before/after). Fix: synthetic plans in scratch. Evidence: exit/stderr matrix, before/after inventory.

**T-03 Separable stages (AC-003) — Mixed.** Cmd: DECIDE `import --collection <restored first-selected>` → `list` → `select --by QA --example --include-html 1` → `export`; then `python -m recon_pipeline add --plan <exported plan>` into a *copy* of a collection; then Prepare on a restored collection. Exp: no stage launches the next; `add` makes no network (observe: no browser start — `.runtime` unchanged, zero `requests` appended); export plan validates with `plan_items`. Neg: `export` with decision whose `inventory_file_sha256` differs → "different inventory version". Evidence: produced files + hashes.

**T-04 Polite access (AC-005) — Mixed.** Cmd: pytest `tests/test_selected_collector.py -k "pacing or refusal or native"` plus one QA-authored loopback run: 2 pages, `gap=5`, `BrowserTransport(root, fixture_only=True)`. Exp: `requests[1].start − requests[0].completion ≥ 5.0`; `/unselected` never requested; 429 on item 1 leaves item 2 `pending` and stops. Neg: `cf-mitigated: challenge` header with 200 → `stop_reason=cf_mitigated_challenge`; JSON body quoting "Just a moment" → not a stop. Record: redirects/subresources are extra traffic by design (no per-hop claim). Stop: any non-loopback request observed in `browser_traffic` → STOP whole campaign.

**T-05 Partial failure/interruption (AC-006, AC-017) — Mixed.** Cmd: transport-double runs (existing tests `interruption_reopen`, `missing_and_corrupt`, `write_failure`, `cap_preserves_partial`) + QA case for **O1**: double raising `TimeoutError` on item 1 of 2. Exp (to be confirmed by QA Lead/JARVIS): item 1 `failed/browser_read_failed`, `stop_reason=browser_read_failed`, item 2 `pending`, exit 2; `resume` re-attempts item 1 once. Neg: corrupt `result.json` hash → item returns to pending with `saved_result_missing_or_invalid`, never counted complete. Evidence: checklist snapshots.

**T-06 Discovery/stream accounting (AC-007, AC-008) — Mixed.** Cmd: `tests/test_decide.py -k "dedup or depth or sitemap or robots or label or weak"`; QA negative for **O6**: sitemap/default fixture with link label "Read more →" and "READ MORE…" → expected per QA Lead (document current acceptance of arrow variant as a limitation or a finding). Exp: stable IDs survive reorder; row numbers change version; `https://outside.invalid` never a candidate or request. Evidence: inventory diff.

**T-07 HTML fidelity/false success (AC-009, AC-010) — Retained.** Cmd: native loopback page with known UTF-8 body incl. non-ASCII; empty 200 body; 403 page; soft-block "Just a moment…" + "checking your browser". Exp: saved `body` == rendered DOM UTF-8 with matching sha; empty → `page_capture_failed`; 403 → `http_403` stop; soft block → `explicit_block_document`, not completed. Evidence: byte compare + checklist.

**T-08 REST/pagination (AC-011–013) — Mixed.** Cmd: existing 6 `incomplete_coverage` variants + native pagination; QA case: single response without `paginate` → `coverage_scope=selected_response_only`. Exp: raw bytes saved verbatim (no reserialization: compare bytes to server fixture), headers allowlisted only (assert no `set-cookie`), count mismatch/duplicates/short pages explicit, no `_fields` injected in collector URL. Neg: X-WP-TotalPages missing → `pagination_headers_missing_or_invalid`, status partial. Evidence: coverage JSON.

**T-09 Cross-stream (AC-014, AC-024) — Mixed.** Cmd: offline — restored first-selected collection + saved Oct 7 REST evidence for post 11945 via DECIDE `import --collection outputs/collections/CyberizeGroup-selected-live-01`. Exp: Andromeda row carries `rest_content_rendered_empty` + `needs_HTML_review_if_selected`; prepared Markdown still holds 7 paragraphs; no plugin cause asserted anywhere in authored docs (grep). Evidence: inventory + grep log.

**T-10 Media (AC-015, AC-028) — Retired design.** No execution. Record: SOURCE_INDEX `images_note` present and `image_completeness: UNVERIFIED` for every prepared package. Disposition to QA Lead.

**T-11 Run records (AC-016, AC-018) — Mixed.** Cmd: inspect a QA native run's `checklist.json`. Exp: `runs[-1]` has started/finished, `gap_seconds`, limits, per-request start/completion/preceding_completion, `browser_traffic`, `runtime` (python/crawl4ai/playwright/browser/UA/cache BYPASS/wait_for_images/timeouts), `cleanup_error` separate. Authored brief sections labeled "observed" vs "interpretation" (T-13 covers). Evidence: schema checklist.

**T-12 Raw immutability / invalid package (AC-019, AC-020) — Mixed.** Cmd: hash entire restored collection; run Prepare → NEW out dir; rehash. Exp: zero input changes; `test_invalid_completed_reference_refused_before_output` 3 variants (body/metadata/escaping) → exit 2, no output dir created. Neg: tamper 1 byte of a `body` in a scratch copy → refused. Evidence: before/after hash lists.

**T-13 Provenance/labels (AC-021, AC-022) — Retained.** Cmd: resolve every `SOURCE_INDEX.json` reference (raw/metadata/prepared/authored) in both accepted packages (`…210309-v01`, `…223736-reviewed`) and recompute hashes (expected 29 refs valid as engineering reported, independently recomputed); check ARCHITECT_BRIEF has distinct observed/interpretation sections. QA negative for **O5**: synthetic `article > header > h1` page → report where the H1 lands; QA Lead decides if acceptable. Evidence: reference report.

**T-14 Content/observed design (AC-023, AC-027) — Mixed.** Cmd: `INVENTORY.md` vs `inventory.json` same rows/IDs for an import; brief design implications cite page IDs. Exp: twins agree; every implication cites a prepared page or source ID. Evidence: diff + citation grep.

**T-15 SEO (AC-025) — Mixed.** Offline only: saved REST body for 11945 retains all returned fields (compare key set with server bytes). No Yoast certification claim. Evidence: key-set compare.

**T-16 Forms/embeds (AC-026) — Retained.** Cmd: Growth Call restored collection → Prepare into new dir; compare with reviewed package. Exp: parent HTML has 0 forms/labels; iframe `src` to `link.cyberizegroup.com/widget/booking/…` recorded; helper hint "article" (known limitation) preserved; reviewed package says booking container + child content UNKNOWN; no fetch of iframe (no network). Evidence: extraction JSON + grep.

**T-17 Loss/non-destructive (AC-029, AC-030) — Mixed.** Cmd: `test_pending_item_is_gap_not_fabricated_page`; `refresh` then `resume` (double) → new attempt dir, old attempt retained; `refresh` of a paginated group → refused. Exp: all prior `attempts/` bytes unchanged. Evidence: attempt inventory.

**T-18 Reproducibility (AC-031, AC-032) — Mixed.** Cmd: Prepare twice on the same restored collection into two new dirs. Exp: identical `pages/*.md` and `BOILERPLATE.md` bytes; `SOURCE_INDEX.json` differs only in `prepared_at` and output paths. Agent-authored docs excluded from bitwise claim. Evidence: diff.

**T-19 Portability/drill-down (AC-033, AC-036, AC-037) — Mixed.** Cmd: copy an accepted prepared package + its referenced raw files (by SOURCE_INDEX paths) into a scratch tree with the same relative layout; resolve all 13 package links and every reference from there. QA case for **O4**: run `prepare_saved.py` with `--collection` pointing outside the repo root → expect exit 2 refusal; record as documented constraint. Evidence: relocation report.

**T-20 Consumer usefulness / cold-read (AC-034, AC-035, AC-038) — QA Lead decision.** Proposal: a fresh reader (not Cody, not this Executor) answers a short positioning/offer/CTA/gap questionnaire from the two accepted packages only, offline; "unknown" answers must point to GAPS_AND_REQUESTS. The original twelve-B7 certificate binding is history; QA Lead sets the question set. Evidence: answers + citations.

**T-21 Full chain on fixture (AC-039, AC-040) — Mixed.** Cmd: one loopback chain — DECIDE `recon --mode default` against a QA fixture server (fixture_only transport) → `select --by QA` → `export` → `collect` (loopback) → Prepare → agent-authored brief/gaps stub. Exp: each stage output feeds the next without edits; all hashes resolve. E2 full-site runs: retired; no live. Evidence: chain directory with hashes. Stop: any external request.

**T-22 Regression/limits (AC-041, AC-042) — Mixed.** Cmd (gate G4 and regression):
```bash
PYTHONDONTWRITEBYTECODE=1 \
SELECTED_COLLECTOR_EVIDENCE=<Q2 evidence>/collector-native \
DECIDE_EVIDENCE=<Q2 evidence>/decide-native \
venv/bin/python -m pytest -q tests/test_selected_collector.py tests/test_decide.py \
  agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py \
  -p no:cacheprovider --basetemp <scratch>/q2-basetemp --junitxml <Q2 evidence>/junit.xml
```
Exp: 97 passed / 0 / 0 / 0, exit 0, tracked source unchanged after run (`git status`). Also run the *historical* retained suites (`tests/test_rest_client.py tests/test_raw_reader.py tests/test_offline_inventory.py`, 27 cases per Oct 7 record) to show they still pass; old full-Capture controller suites are NOT reclassified. Limits: `max_requests=1`, `max_seconds` tiny, `max_bytes` small → `request_limit` / `time_limit` / `persisted_byte_limit` stop reasons with partial outcome, exit 2; QA case for **O2**: record `.runtime` size counted. Evidence: JUnit, measurements.

**T-23 Hostile data / hygiene (AC-043, AC-044) — Retained.** Cmd: synthetic HTML with `javascript:`/`data:` hrefs, `<script>`, `<template>`, traversal `../` in a checklist reference → Prepare strips/refuses (existing tests + QA additions); ZIP hygiene: assert no `.runtime/`, `.env`, cookie or `set-cookie` strings in any Q2 package (scan list recorded); HEADER_ALLOWLIST excludes cookies. QA case for **O3**: list `.runtime/` contents of a QA-run collection and confirm exclusion from packages. Evidence: scan inventory with exemptions.

**T-24 Campaign evidence/specimen (AC-045, AC-046, AC-048) — Retained.** Cmd: at Q2 end, reconcile each AC row with evidence paths; re-verify candidate SHA and 52-file identity unchanged; ledger rows updated by QA only in QA columns. Evidence: reconciliation table.

## 3. Run order and stop conditions

Order: G1→G4, then T-22, T-12, T-13, T-16, T-18, T-19 (offline, fast), then T-02/T-03/T-05/T-08/T-17 (doubles), then T-04/T-07/T-21 (native loopback), then T-06/T-09/T-14/T-15/T-23, then T-20 (fresh reader), finally T-24. Ordinary failures are recorded and unaffected checks continue.

Campaign STOP (no continuation without QA Lead): candidate SHA or 52-file identity changes; any tracked product/test file modified by a run; any non-loopback request observed; fixture hash mismatch; need for an install or dependency change; disk growth in evidence > 500 MB; any instruction to run against cyberizegroup.com.

## 4. Known gaps this plan does not close

Clean-venv install; native interruption/crash breadth (doubles only); hostile presentation breadth; image/hidden/deferred content; iframe child content; the four historical retired-path findings. Absence of a test is not success.
