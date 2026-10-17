# Web Factory current-tool QA — final amended Q1 plan

Date: 2026-10-15 (Asia/Dhaka). Plan revision: LEAD-01.
Authoring: Opy's Q1 proposal, amended by JARVIS in the QA Lead seat.
Status: PLAN APPROVED through the separate `02_QAM_APPROVAL.md`; Q2 NOT RELEASED.
Every execution result is NOT RUN. This file contains expectations, not findings or a product certificate.

## 0. Identity, authority and limits of this approval

| Binding | Value |
|---|---|
| Repository | `/home/moose/PYTHON/stark-web-factory-scrapper-v1` |
| Branch | `qa/wf-scrapper-abm` |
| Product candidate | `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4` |
| Source52 | `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` |
| Source52 method | SHA-256 of UTF-8 `json.dumps(path_to_sha256, sort_keys=True, separators=(',', ':'))`, no trailing newline; exactly the 52 paths in the supplied source inventory |
| Original proposal | SHA-256 `fc2cfdcc3170008689ad87001f4519d1ccf899c2486071fe3d147f2f04855826` |
| Independent QA Executor | Opy (OpenCode, GLM 5.3), succeeding Claudy's QA session; Cody remains Engineer |
| QA Lead | JARVIS; approves plan, adjudicates, accepts retention/cleanup, issues any later certificate |
| Director | Tony; owns Git, release, credentials, destructive cleanup and scope/risk acceptance |
| Environment | Existing venv: Python 3.12.3, crawl4ai 0.9.3, playwright 1.52.0, beautifulsoup4 4.13.4, pytest 8.3.5, markdown-it-py 4.2.0, requests 2.32.3, python-dotenv 1.1.0; record actual browser binary/version at execution |
| requirements.txt | `231e1d8f8b3b1b2b8d382b98beadc05361529805cd93081890fff47606df5f46` |
| requirements-lock.txt | `e6c3e1a9a89f6cd8f5dfb71694c74d54d6b34237929f06a0ce3aa519b89a594c` |
| Prepare fixture ZIP | `response_2026-10-11_210309_prepare-v01.zip`: 432966 bytes; `d54bbaf0c07e1fbd41937afc11e3111378743d8903bdc6254d2e3bb329cc5a63` |
| Growth Call fixture ZIP | `response_2026-10-13_223736_growth-call-follow-up.zip`: 107429 bytes; `fdf18de8838f36344459555041a12e4f0cf463044a1f211f6241a7bf420ab4a8` |
| Fixture manifest | 34 named saved data/package files; validate paths, hashes and byte counts against the included manifest |
| Network | Zero external requests. Only the QA-owned loopback fixture server may receive requests. Saved public URLs are data, never fetch instructions |
| Approval identity | Final plan hash is in `02_QAM_APPROVAL.md`, outside this file; never insert a self-referential hash here |

The Lead verified the exported package and recomputed source52 from its recorded per-file maps. The Lead did not access Tony's checkout or independently hash the actual Git blobs/fixture archives there. Opy must recheck these actual inputs at entry. Local remote-tracking refs are not proof of live remote state; no network Git verification is required.

### 0.1 Governing interpretation

For this current-scope QA engagement, apply Tony's explicit instructions, the current accepted scope, this exact approved plan/approval, and the supplied QAM v1.0 workflow. Keep repository/tool restrictions in force. A material conflict stops affected work for its owner; it is never silently waived.

Active scope is DECIDE → COLLECT → offline agent-assisted PREPARE. These exact reviewed snapshots define its behavior:

| Source in `GOVERNING/` | SHA-256 |
|---|---|
| CURRENT_TOOL_SCOPE.md | `639070b6b7f297104678da307b95ba39ddc8176797fcd8dafbb22f9b0dc1c87c` |
| DECIDE.md | `1ecc155f8b14c5dd726946c881bf7ce8ceca318a28e20b8ba2d41f2a61425790` |
| COLLECTOR_SIMPLIFICATION.md | `ed2c7b35125560570827678ae4aa538977fe7ce05c3df01a1584cf5b78109114` |
| PREPARE_SKILL.md | `27a3f832b908073fa27c867710d01ed0c758b75e5e6d5924f5a9eec910df518a` |
| QAM_PLAYBOOK_v1_0.md | `5359701bb7d9ed1558907f7310433eff80433bc7c6f5fb9d18de9168ebe7e03e` |
| QA_PLAYBOOK.md | `b6c70f14af18bb187ca7980954317af486e43b682821245d9911f2160d5198a5` |

The supplied QAM playbook's actual hash is the one above. The template-review letter's abbreviated `97e111e2…5c897` is not a verified identity for this supplied file; this approval does not assert they are byte-identical or that the template sync landed. The text of QAM-SR SR-1…SR-11 was not supplied with Q1; do not reconstruct it from the adoption summary. Apply the concrete requirements here and QAM v1.0. If a locally installed governing risk requirement adds a material obligation, surface it before executing affected tests.

Historical QAM entry/state text about BUILD_READBACK, custom CDP/pre-dispatch five-hop control, CHK/E2 live allocations, mandatory whole-site Capture+Prepare and the earlier controller is not current execution authority. The October 14 current-scope pointer supersedes those behavior bindings. This plan is the active Q2 assignment, not a new global doctrine or replacement of the historical records.

Retain the module-specific cleanup order: inventory → Tony's destructive cleanup → Executor verification → Lead cleanup acceptance → final Gate Q. Routine closure of QA-owned servers/browsers is permitted phase-exit hygiene. No deletion of retained fixtures, credentials, recovery/session records or old evidence is granted here. Later application reviews, any RRM, Architect closeout and Tony integration remain separate obligations.

The original ABM acceptance specification, errata/rulings, master plan and ledger were referenced but not included in either review ZIP. This approval grades the expressly supplied current-scope crosswalk, not all original literal AC requirements. Read and hash those original records locally at entry to detect any remaining applicable conflict; do not fabricate their contents or mark historical requirements passed. Store snapshots needed for subsequent adjudication in the new QA evidence lane. An unexpected live obligation, prohibition, or materially different acceptance requirement returns to the Lead/Architect. The original frozen records stay unchanged.

### 0.2 Applicability and result vocabulary

Use all 48 original AC IDs as a traceability index into the current-scope crosswalk. Retained rows test current behavior. Mixed rows record current sub-obligation and retired sub-obligation separately. AC-015, AC-018, AC-028 and AC-040's retired implementations are NOT APPLICABLE TO CURRENT SCOPE, HISTORICAL STATUS PRESERVED; no historical PASS or defect closure follows. AC-035 has the current cold-read check in T-20.

Measurement labels: PASS, FAIL, BLOCKED, NOT RUN, ADJUDICATE. Map any local synonyms explicitly. Applicability is a separate column, not a successful test. AC-001 remains PARTIALLY TESTED/NOT RUN for clean-install reproducibility even if snapshot operator checks pass. Required unmet acceptance is never silently optional; final certification/risk decisions remain with the appropriate owners.

## 1. Installation and release boundary

Q1b is exact document installation, not another QA campaign. Preserve both original Q1 exports. Place this review folder under `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/`; install these bytes without editing the final plan. Verify its SHA-256 against the approval, record its path and this decision in the existing QAM state/approval lane, and produce a short installation receipt. Update only existing QA-owned routing/state records where authorized. Do not rewrite root AGENTS.md, frozen acceptance, historical plans, or Engineer-owned records. Use the stable instruction to read this final plan if older entry routing remains stale.

Before Q2, Tony commits the required planning/approval records under the established Git policy and explicitly releases the campaign. A documentation-only successor to the product candidate is allowed only after proving candidate ancestry, inspecting the COMPLETE name/status/mode/content diff and proving that product, dependency, config, fixture and maintained-test bytes remain unchanged. This limited check includes every changed path, not only source52. Record product SHA and actual execution HEAD separately. New executable product/config/test content or changed contract meaning requires a new Lead decision. Expected QA helper files in the declared lane are reviewed instruments, not candidate product changes. No Git mutation by Opy, including clone, checkout, worktree creation, pull, commit or reset.

No Q2 command runs until the exact approval, required record commit and Tony's explicit release are recorded. The prior Q1 resume GO authorized Q1 only. This approval never supplies Tony's release.

## 2. Readiness and execution controls

### G0 — authority and complete identity

Verify the final plan hash, separate approval, Director release, repo/branch, product SHA, execution HEAD and ancestry. Read actual root/module/QAM instructions, including the newly appeared root AGENTS.md, without editing them. Record their paths/hashes and resolve material conflicts before use. Inventory tracked/untracked/staged changes and file modes. The reported 61 archived deletions and untracked OLD copies require exact path and content correspondence; never exempt a whole directory by name. Source52 alone does not prove config, instructions or import paths unchanged. Inventory changes since Q1 and preserve unrelated work.

Archive relocation may be accepted when the exact referenced bytes are found and verified; record old path → new path → hash in `PATH_RESOLUTION.json`. The reviewed snapshots can provide governing/reference inputs when a working path moved. No broken reference is treated as an empty PASS. Restore neither Tony's archive moves nor stale root files.

### G1 — source and environment

Recompute the exact 52-file map from candidate Git blobs and the effective test source; verify dependencies separately. Check for untracked shadow modules, alternate imports, configuration or test plugins changing execution. Record cwd, interpreter path, effective module `__file__` paths and relevant test configuration. For isolated tests use a fresh file-only snapshot made from the candidate with read-only `git archive` or an equivalent verified tracked-file export into a new QA scratch directory; no `.git` database and no network clone. Safe extraction must reject escapes. Verify code in the snapshot and imports resolve there, not to the original checkout or installed editable modules. Use the existing venv's absolute interpreter path; a snapshot need not contain `venv/`.

Record installed versions and run `pip check` without installs. An import/dependency incompatibility blocks dependent tests. Do not alter dependencies, TLS, transport, USER_AGENT or retry settings. Record free ports/storage and the QA-owned loopback listener. A separate bounded instrument-control fixture validates that off-loopback requests are intercepted before dispatch; no external connection or DNS lookup may be used to prove the guard. Expected blocked synthetic attempts are evidence, not actual egress. A broken guard is STOP-INSTRUMENT; actual unauthorized egress is STOP-AUTHORITY.

### G2 — fixtures and lanes

Verify both archives against §0 and the 34 manifest files. Use the included restoration helper only to create missing named data in a new snapshot/test tree or the specifically approved missing fixture paths. It must verify archive hashes, reject escaping paths/conflicting existing files, skip only exact matches, and never restore source/instructions from an archive. A corrupt original is preserved and blocks dependent work; do not overwrite it. The old source inventory's `candidate_commit: PENDING Tony` remains preserved historical metadata; the independently recorded current binding supplies identity.

Durable QA lane: `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/Q2_<timestamp>/`, with helpers, matrices, attempts, control results and safe exports underneath it. Disposable test trees, generated collections and derived outputs live under a fresh owned scratch directory. Because Prepare confines inputs relative to its script's repo root, put its test collections under the file-only candidate snapshot root, and run its copied script there. Preserve all source/fixture originals; never mutate accepted packages. Use separate snapshots/directories for negative tampering. Do not write results into Engineering evidence. New response/session records are allowed only by existing repository policy. Keep per-run QA disk use (scratch plus evidence) within 500,000,000 bytes; preflight available space and stop before crossing the bound when measurable. This QA storage ceiling is separate from product `--max-bytes` semantics.

### G3 — run policy

After readiness, run each required complete suite once into a fresh attempt directory. There is no mandatory second T-22 rerun after the initial suite. Ordinary product assertion failures are recorded; continue unaffected safe checks. Only compromised identity, environment, scope, instrument, privacy or evidence stops affected execution. Preserve failed attempts. Helper corrections within the declared QA lane are permitted with old/new hashes, failure cause and a control check; rerun only invalidated measurements. No hidden retries, test weakening, product edits or maintainable-test edits. Expected failures in named negative fixtures are successful negative controls only when the specified failure mechanism is proved; an unrelated import error is not that result.

All commands and helpers record exact command/arguments, working directory, start/end time, exit code, expected/actual result, full output retained safely, fixture and source hashes, and evidence paths. Evidence extraction must not turn missing files, zero collected tests, an empty grep or skipped tests into PASS. Safely redact sensitive values in review exports and disclose redaction; do not publish unsafe unfiltered logs.

## 3. Approved test bindings

All T groups use local synthetic fixtures or hash-verified saved inputs. Existing tests are reused as instruments, not as the oracle merely because they pass. Before each new helper executes, record its precise invocation, fixture definition, assertions and instrument boundaries. This is implementation of the approved cases; material scope/expected-result changes return to the Lead. No dependency install or direct transport substitution is authorized.

### T-01 — setup/operator path (AC-001, AC-047)

Use the file-only candidate snapshot from G1, existing absolute venv interpreter, and current DECIDE/collector/Prepare instructions. Run each of the three entry points with `--help`; expect exit 0 and documented subcommands/options. Before fixture restoration, run ONLY the saved-capture-dependent Prepare case selected by its actual node ID; expect a failure specifically identifying the missing saved input, not a skip, import failure or arbitrary exception. Then restore the manifest data and run the complete required suite in T-22. Preserve both attempts. This demonstrates documented fixture dependency and operation from candidate files with an existing environment. It is not a clean Git clone or clean-venv install claim. Record fresh-install reproducibility as untested against AC-001, never PASS by omission.

### T-02 — input and output boundaries (AC-002, AC-004)

In fresh synthetic directories, invoke collector validation on non-HTTP URLs, credential-bearing URLs using synthetic placeholders, fragments, REST root enumeration, pagination without max_pages, pagination starting at page 2 and unknown keys. Require documented refusal exit 2 and no new collection directory. Existing collection/output destination must refuse without altering its bytes. DECIDE rejects unknown IDs/rows, conflicting include/exclude and HTML selection of a REST collection row without saving a decision. Prepare refuses existing output or output inside the collection and preserves inputs. Keep URL/file references confined; add a traversal and symlink-escape negative control in an isolated tree. Evidence: command/exit/refusal table and before/after file maps. Exact punctuation in error strings is secondary to the current refusal contract; do not import obsolete CLI wording.

### T-03 — explicit stages and selection (AC-003)

On copied saved data, run DECIDE import → list → select with a QA/example actor → export using explicit paths. Verify separate outputs and no implicit next-stage invocation; only explicitly included HTML/REST choices export, excluded choices stay excluded and unspecified rows remain undecided. A one-item REST choice must not expand to a collection; whole-collection export requires an explicit page bound. Use `add --collection COPY --plan EXPORT` offline; observe zero transport invocations, not only unchanged runtime files. A decision bound to different exact inventory bytes, including reformatting/reordering, must refuse export. Never pass an example with saved external URLs into collect/resume. Actual collection in T-21 uses a separate loopback-only decision.

### T-04 — planned-call pacing and stop controls (AC-005)

Reuse applicable complete-suite evidence once. Add one real Crawl4AI/Chromium loopback run with two planned documents and the default gap (omit an override; record resolved gap 5). Assert next planned start minus previous completion is at least 5.0 seconds using native monotonic timing and server observations. Treat redirects/background resources as separate browser traffic, not planned-call counts. Include an unlinked, unselected route and verify it is not requested; a linked subresource is not a valid no-request oracle. Test selected-response 429 and 200 + `cf-mitigated: challenge`; later planned items must stay unattempted, no retry/fallback. JSON containing quoted challenge markup is a negative detector control. All fixture stop outcomes are local expected results; they do not consume or authorize live allocations.

### T-05 — failure, explicit resume and cleanup outcomes (AC-006, AC-017)

Transport-double timeout on first of two items: first records failed/browser-read-failure, later item remains pending/unattempted, partial exit 2, no automatic retry. A separately invoked explicit resume may attempt that failed item once; successful saved items are skipped after validation. This conservative stop is acceptable under current scope, not a requirement to auto-continue. Verify missing/corrupt metadata/body cannot count complete. Exercise interruption and explicit reopening, write failure and cap partials using existing fixtures plus targeted negatives. Verify collector exit semantics: 0 selected scope complete with no observed cleanup error; 2 partial/failed; 3 complete collection but observed cleanup error; 130 interruption. Collection status and cleanup status stay distinct. Native-crash/teardown cancellation guarantees remain unproved; doubles do not prove them.

### T-06 — discovery, labels and inventory identity (AC-007, AC-008)

Exercise sitemap and bounded default modes, dedup, depth, same-origin candidate rules, preserved source locators, stable IDs, order-dependent row/version identity, explicit stream choices and bounded type/metadata discovery. No guessed sitemap fallback or link-mode fallback when sitemap evidence is absent. Native loopback evidence must show `wp/v2/types` requested without `_fields`, individual metadata with its documented projection, and selected collection export without that projection. Media/users/taxonomies must not become automatic content collection. Unknown counts/types remain unknown, not verified empty. Test generic label variants `Read more →`, `READ MORE…`, punctuation-only and whitespace-only labels against an informative control. Per DECIDE's October 11 correction, generic CTA text must not supply or replace a candidate title; preserve its raw locator while keeping title unknown or the earlier informative label. Acceptance of the arrow variant as a title is a finding against current behavior, not a preaccepted limitation. Recheck the nine actual saved h2 texts from their raw source when validating that follow-up; never use ellipses or an Engineer's count as an oracle.

### T-07 — HTML fidelity and false success (AC-009, AC-010)

Use real loopback Chromium with Unicode markup and a controlled DOM mutation to distinguish rendered HTML from original response bytes. Compare the collector's saved UTF-8 body and hash to an independently observed rendered capture at the declared boundary; record timing/serialization, not a circular comparison to its own digest. Exercise empty/no-useful-body capture, 401/403/429, challenge header, challenge-platform markup and title-plus-phrase block-page fixtures. Such responses must not become successful captured content or trigger later planned requests. Record actual documented stop reasons; if Chromium synthesizes an empty HTML shell, assess the captured-content semantics rather than assuming a zero-byte network response stays zero bytes. Include normal HTML with an incidental quoted phrase and valid JSON quoting block markup as false-positive controls. Detector behavior is heuristic and bounded to these fixtures.

### T-08 — raw REST, pagination and bounded metadata (AC-011, AC-012, AC-013)

Use the suite's malformed/partial coverage variants plus native loopback response bodies with known Unicode, whitespace, optional SEO fields and nested/unknown fields. Compare saved decoded entity bytes byte-for-byte with the controlled server's response payload, not JSON reserialization. Verify allowed headers only; synthetic Set-Cookie must not appear in exported result metadata. Check no collector-injected `_fields`. No pagination opt-in means selected-response-only coverage. Explicit pagination obeys max_pages and exposes missing/changing advertised headers, empty/short intermediate pages, duplicate IDs, count mismatch and page-limit partials. Missing mandatory identities must fail visibly. Retain evidence of types metadata and counts separately from full captured content; full source inventory is not claimed.

### T-09 — HTML/REST disagreement (AC-014, AC-024)

Import hash-verified saved REST for post11945 and inspect the saved selected HTML offline. Require explicit present-empty REST warning and HTML-review warning without erasing substantive rendered content. Derive expected seven paragraphs, fifteen list items and six headings directly from the identified Andromeda raw subtree; compare exact text/order and meaningful links/CTAs to the prepared sample. Keep October 7 REST, October 10 advertised metadata totals and October 11 HTML separately dated. Inspect current authored claims for unsupported plugin/root-cause conclusions; keyword presence alone is not a failure if the text explicitly says the cause is unknown.

### T-10 — media applicability (AC-015, AC-028)

Automatic whole-site inventory/classification is retired, not passed. Perform the limited current check that prepared packages expose image references/notes where available and explicitly leave image/hidden/deferred completeness unverified. Do not download, HEAD-probe or classify the full media library. Preserve historical media discrepancy as OPEN outside this current-scope test.

### T-11 — audit and authored boundaries (AC-016, AC-018)

For native QA runs inspect checklist/attempt records: start/end, selected scopes, effective gap/limits, planned start/completion relationships, browser traffic and runtime/config including browser version, UA, cache, waits and timeouts. Cleanup error is separate. Captured source, generated extraction and agent-authored interpretation must be distinguishable. Historical authored screenshot-stream schema is retired; it does not justify omitting current labels or provenance.

### T-12 — raw preservation and invalid references (AC-019, AC-020)

Hash all source collection bytes before/after offline Prepare into a NEW derived directory; require zero source changes. In separate scratch copies, tamper one body byte, metadata/hash and escaping reference; expect refusal exit 2 before derived output is created. Corrupt fixture controls are not changes to canonical fixtures. Preserve negative-control failure logs separately. Test a symlink escape without touching any file outside the owned synthetic tree.

### T-13 — provenance and meaningful headings (AC-021, AC-022)

Enumerate every reference from each accepted SOURCE_INDEX, including raw/metadata/prepared/authored/context entries, resolve it and recompute hashes. Derive the reference set independently; 29 is an Engineer's comparison count, not the oracle. Cite raw CSS boundary and distinguish source facts/agent interpretation/unknowns. Add a synthetic `article > header > h1` with meaningful title, main paragraphs and CTA, plus genuine global navigation/footer controls. Useful title/content must remain discoverable in the final reviewed main content with source provenance. If the helper puts the title into boilerplate, preserve that observation and classify the helper limitation; do not call final content preservation PASS merely because raw bytes or boilerplate still contain it. Agent review may produce a separate, accurately indexed derived rendition as the skill explicitly allows, preserving the initial output. If meaningful content remains absent from the final reviewed output, record acceptance failure. No helper/product repair is authorized by this test.

### T-14 — inventories, exact content and design interpretation (AC-023, AC-027)

Compare inventory JSON/Markdown for the same version: every row, ID and selected-scope state must agree. Validate the saved heading correction with exact source text (T-06) and substantive paragraph/list/CTA preservation (T-09). Design implications must be labeled interpretation with evidence citations; a matching citation string alone does not prove support. Agency Services must remain a category/listing classification when that is what the saved content shows. Do not extrapolate selected pages into site-wide conclusions.

### T-15 — SEO fidelity (AC-025)

Offline saved bodies prove retention of the specific hashed payloads, not an independent reconstruction of what the historical server returned. Inspect every returned SEO/custom field in those payloads without inventing absent fields. Use T-08's controlled native response for independent full-field and byte-fidelity proof. Distinguish DECIDE's intentional metadata projection from COLLECT's selected full response. No live call or Yoast-wide certification.

### T-16 — Growth Call and embed honesty (AC-026)

Run offline extraction on a snapshot copy of the saved Growth Call collection, preserve initial helper output and inspect the raw parent. Verify observed parent form/label counts, booking iframe source, native-main content boundary and unavailable child content. Compare independently against both initial and reviewed saved packages. The helper's article hint is a known limitation expressly handled by agent review; the final reviewed output must identify the booking-container evidence and leave child content/form function UNKNOWN. Do not fetch iframe, execute scripts, submit forms or invent booking fields. A helper-only empty extraction is not a completed package.

### T-17 — losses, refresh and non-destructive operation (AC-029, AC-030)

Exercise pending-item gap output and explicit add/refresh/resume on scratch copies with doubles or loopback. All previous attempt bytes must remain unchanged; new explicit attempts have new paths. Refresh of a paginated collection must refuse in favor of a new collection. Confidence never authorizes URL promotion, fetching, overwrite or deletion. Gaps identify missing evidence and reasons rather than fabricated pages.

### T-18 — repeatability and twins (AC-031, AC-032)

Prepare identical hashed inputs twice into distinct new directories. Compare main page and boilerplate content exactly. Inspect index differences field-by-field: only explicitly identified run timestamps/output locations and their derived reference hashes may differ; record an exact normalization allowlist before normalized comparison and retain the full raw diff. Any content/provenance difference remains visible; do not broadly exclude hash fields or timestamps embedded in source content. Agent-authored interpretation is not required to be bitwise identical. Inventory twin agreement is covered by T-14.

### T-19 — delivery portability and drill-down (AC-033, AC-036, AC-037)

Copy each accepted package and all required saved references into a new tree preserving declared relative layout, using only verified files. Enumerate and resolve every reference/link independently; 13 is a prior comparison count, not a pass threshold. Require source URL/date/body/metadata/hash/CSS drill-down and usable brief/gap entry points. Run the copied helper from the normal relative script location under the candidate snapshot with inputs under that root. An external-root collection must refuse visibly under the documented confinement rule; this is not a promise of a standalone relocatable helper. Broken/missing packaged dependencies are failures or blockers, not silently rewritten links. No installs or network to make the relocation work.

### T-20 — independent offline consumer cold-read (AC-034, AC-035, AC-038)

Opy prepares a sanitized consumer packet containing only the two accepted reviewed packages and their required saved references, plus the questions below. A fresh reader session, independent of Cody and Opy and not already primed with their analysis, answers using only that packet, without live access. Record reader identity/session, supplied file manifest, task and untouched response. This reader judges consumer usefulness only, not product certification or code quality. If no such reader is available, mark T-20 BLOCKED, finish other safe tests and return the packet; do not claim a cold-read from Opy or an already-briefed Lead. This plan does not require spawning an agent in this review turn.

Questions: (1) What positioning is supported, and what are merely source marketing claims? (2) What offerings are evidenced, and which pages are listings versus detail pages? (3) What meaningful article/service content and CTAs are available, with destinations? (4) What does Growth Call show, and what cannot be known about its iframe/form? (5) How do empty REST, rendered content and advertised counts differ by source/date? (6) What design/content implications are interpretations, with supporting references? (7) Which missing evidence would you request next, and why, without fetching it? (8) Can you trace at least one claim from EACH reviewed package to source ID, capture date, CSS boundary and verified saved bytes?

Rubric: every substantive factual answer has a resolvable supporting citation; interpretations are labeled; unknown answers cite the relevant gap; no unsupported source claim, unavailable child content, count-as-content claim or site-wide extrapolation is presented as fact. An explicit well-supported unknown can pass a question. Missing answerable essentials or broken drill-down is a finding. Record all eight answer dispositions and limits; do not invent a numeric score threshold or revive the historical twelve-B7 certificate requirement.

### T-21 — whole current flow on a local fixture (AC-039, AC-040)

Build a small known loopback fixture with a meaningful heading, paragraph, list and CTA, plus controlled types/metadata/REST. Through existing APIs/CLI and the established fixture-only guard, run DECIDE recon → numbered review → explicit QA/example selection → export → COLLECT → offline Prepare → real agent-authored ARCHITECT_BRIEF/GAPS_AND_REQUESTS and updated index. No stub is sufficient for the agent-assisted stage. Production code is unchanged; a QA wrapper may supply the existing local test transport hook but may not replace the behavior being measured. All native calls go through installed Crawl4AI/Chromium. Compare stage interfaces, selected-only scope, known raw content, generated content and authored claims to the independent fixture oracle. Each stage consumes the previous output without manual interface repair. Record a CLI/wrapper boundary if not every step can be invoked unchanged through public CLI; do not claim otherwise. Old two-run E2/full-site live campaign is not executed or certified.

### T-22 — full required regression and limit semantics (AC-041, AC-042)

After readiness/restoration, run all tests in these three current modules once, without `-k` filtering: `tests/test_selected_collector.py`, `tests/test_decide.py`, `agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py`. Also run all tests in `tests/test_rest_client.py`, `tests/test_raw_reader.py`, `tests/test_offline_inventory.py` after confirming their paths/configuration and zero external effects. These six modules are the required regression scope; historical full-Capture suites are not silently reactivated. Inventory any additional tests that actually cover changed current code; a material uncovered obligation returns to the Lead, not arbitrary full-repository/live execution.

Use the absolute existing interpreter, cwd at the verified candidate snapshot, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, a fresh `--basetemp`, and `--junitxml` under Q2 evidence. Set `SELECTED_COLLECTOR_EVIDENCE` and `DECIDE_EVIDENCE` to distinct QA-owned native-evidence paths. Log the fully resolved command; no placeholder command is executed. Expected current-suite baseline is 97 passing cases; expected retained-suite baseline is 27. Independently collect/reconcile node IDs and parametrizations. Extra or missing tests require explanation; zero collected, skips, collection errors or changed assertions cannot satisfy the baseline. Normal assertion failures are findings and do not automatically halt unrelated checks. New QA negatives are additional cases, not a reason to force total count 97.

Test max_requests=1, a bounded tiny work deadline and a small persisted-byte allowance with exact fixtures and partial outcomes. For O2, record directory bytes including `.runtime` and writer-lock overhead: the current estimate includes existing collection files plus next body and 64 KiB metadata reserve. Do not claim an exact aggregate hard cap, per-hop budget, wire/memory streaming bound or guaranteed teardown cancellation. Demonstrate refusal/partial outcomes and preserved evidence when bounds trigger. Any new observed overrun is reported with actual semantics, not hidden by choosing only an easy fixture.

### T-23 — untrusted input, instrument attack and privacy (AC-043, AC-044)

In isolated synthetic data, exercise script/template content, javascript/data destinations, traversal/symlink references and embedded prompt-like commands. Captures stay data: do not execute page instructions or browser-open saved public HTML. Derived presentation must not execute script/active destinations; preserved raw source remains unchanged. Report unsupported sanitization boundaries honestly rather than assuming every unsafe string is removed by the converter. No product repair is authorized.

Validate the privacy/export checker with a clean control AND a synthetic leak fixture containing fake credential, Authorization/Set-Cookie values and a prohibited `.runtime` member. Add a nested-archive control if nested members are supported; otherwise reject nested archives explicitly. Independently corrupt one copied file/digest and prove integrity detection. The scanner must fail on actual synthetic values/prohibited files and pass clean documentation that merely mentions words such as `cookie`, `.env` or `Set-Cookie`. Do not ban those words globally or use blanket exemptions. Classify false positives at exact locations without excluding genuine leaks.

Use explicit export inclusion lists; exclude runtime profiles, cookies/auth storage, credential/env files, dependencies, caches, Git internals and unreviewed sensitive traces. Scan actual selected content and expanded archive members; verify archive membership, size and hashes after packaging. No real credential file is needed or authorized. Examine `.runtime` metadata only as needed without printing secrets, and prove it is excluded. Any real secret/private-state exposure blocks export and certification; contain it under existing authority, do not publish it. Preserve safe counts/locations and approved sanitized evidence.

### T-24 — traceability, unchanged specimen and handoff (AC-045, AC-046, AC-048)

Maintain `AC_EVIDENCE_MATRIX.md` within the Q2 evidence lane with all 48 IDs, current obligation, applicability, original historical status reference, independent observation, command/exit/evidence, candidate/attempt and remaining gaps. Keep original canonical ledger history and frozen text unchanged; link this matrix from the existing QA-owned state rather than writing the parent ABM_LEDGER merely because the draft proposed it. Recheck complete tracked/untracked changes, product and execution HEAD, source52, dependency and fixture hashes. Account for every expected QA write and every pre-existing Director-owned change. No claim of a clean working tree until it is actually proven.

Return readiness rechecks, matrix, execution report, findings, instrument corrections, native/offline evidence, exact identities, preservation/cleanup inventory, cold-read results or blocked consumer packet, metrics and an indexed ZIP under QAM/HANDOFFS, plus a byte-identical Downloads copy as previously requested. The receipt records full ZIP hash, file count, byte size, paths and exact decision sought. Do not nest old exports. Include actual governing sources and this exact plan/approval; exclusions and referenced-but-omitted raw fixtures must be explicit.

## 4. O1–O10 adjudication for this run

| Observation | Binding decision |
|---|---|
| O1 timeout stops later planned calls | Accept conservative visible stop and explicit resume; no automatic retry; test T-05 |
| O2 runtime/lock bytes count | Accept documented estimate semantics; measure T-22; no exact-hard-cap claim |
| O3 runtime profile inside collection | Exclude from all review/consumer exports and validate checker; T-23; not proof of production privacy beyond tested scope |
| O4 helper root confinement | Accept current repo-layout constraint; test isolated snapshot plus outside-root refusal; T-19 |
| O5 article header/H1 | Meaningful heading preservation required in reviewed output; preserve helper limitation separately; final loss fails T-13/T-14 |
| O6 arrow CTA label | Generic CTA cannot become candidate title under the explicit October 11 contract; a reproduction is a finding, not a waiver; T-06 |
| O7 Growth Call hint | Known helper limitation; independently verify raw + initial + reviewed output; no automatic iframe collection/helper repair; T-16/T-20 |
| O8 default pacing | Require one native default-five-second loopback measurement; historical timing is reference only; T-04 |
| O9 challenge heuristic | Exercise positives and false-positive controls locally; no comprehensive bypass/access guarantee; T-07/T-08 |
| O10 old four findings | Preserve OPEN / retired-path historical findings, outside current-scope repair; no closure or PASS through reclassification |

## 5. Evidence reuse and run order

Approved reuse: Q1's completed inspection and candidate-compatible Engineering JUnit/pytest/native timelines are reference evidence only. Opy's actual binding observations can establish Q1 readiness with provenance; recheck volatile entry conditions. Reuse fixture manifest/restoration procedure after hash validation. Reuse the nine Engineering offline checks as a checklist, independently rerun against the verified inputs. All required current/retained regression and content assertions receive fresh independent Q2 measurements. Dated live captures are saved fixtures/observations, never proof of current live access or pacing. No Engineering PASS becomes a QA PASS by copying.

Order: G0 → G1/G2 readiness and instrument controls → T-01 missing-fixture negative → fixture restoration → T-22 complete required regression once → offline high-risk T-12/T-13/T-16/T-18/T-19 → T-02/T-03/T-05/T-08/T-17 cases not already covered → T-04/T-07/T-21 native cases → remaining T-06/T-09/T-10/T-11/T-14/T-15/T-23 → T-20 independent reader → T-24 and safe exit. Avoid duplicate complete-suite runs and cite reusable measurements between groups. Validate export/integrity controls before any export. An isolated product FAIL continues through independent safe coverage; no need to wait for a repair to finish unaffected checks.

## 6. Stops, exit and certification boundary

STOP-IDENTITY: unexplained HEAD/product/config/test/source/fixture drift. STOP-CONTRACT: unresolved applicable scope or authority contradiction. STOP-ENV: required environment/input/service unavailable. STOP-INSTRUMENT: guard, fixture, oracle or helper cannot establish the measurement. STOP-AUTHORITY: needed install/Git/product mutation/external traffic/storage overrun beyond approved scope. STOP-PRIVACY: unsafe retained/exported sensitive data. STOP-EVIDENCE: cannot preserve trustworthy results. Record exact condition, time, affected tests, owner and safe resume point; continue independent permitted inspection only where it cannot undermine the stop. Tool denial is recorded, never evaded. No live checks against cyberizegroup.com or any other external host.

Q2 exit closes owned browser/server processes, records cleanup outcomes and preserves partial failures. Do not kill unrelated processes, delete shared recovery/editor files or perform destructive Q5 cleanup. Provide a retain/delete proposal for Tony; Lead accepts verification at the module's governed cleanup checkpoint. Conditional Q4 also has owned-process exit hygiene if it later runs. Product defects follow Lead adjudication → Architect bounded repair → Cody Engineer → Tony commit → independent re-pin/retest including required regression. No self-repair of product and no self-certification.

Known unclosed areas: clean-venv install, native crash/cancellation breadth, broad hostile-viewer coverage, hidden/deferred/image/iframe child content, current external-site access and four historical controller findings. A blocked fresh reader is additionally explicit if applicable. Measure preparation, active execution, waits, packaging, helper corrections, stops and Director touches separately. Q2 completion, Gate Q, pilot success, cleanup acceptance and deployment/Gate D are different claims. None is granted by this plan.
