# Web Recon + Prepare — Master QA Test Plan

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.


Version: 1.2 | 2026-10-02 | Owner: SOL QA Lead (actual session binding PENDING)
JARVIS Architect amendment under Tony’s delegated authority. See [amendment](../ABM_AMENDMENT_1_1.md) and [QAM](../QAM/README.md).
Executor: independent QA Executor session, binding PENDING; Cody is currently Engineer | State: DESIGNED, NOT EXECUTED

This is one whole-product QA plan for the ABM. In Q1 the independent Executor inspects the committed candidate and completes concrete bindings, then exports one review package. SOL approves/amends that candidate-bound plan before Q2 continuous execution. Test groups organize the work; they do not create 24 Director approval steps. The plan remains the canonical product QA record through repair and RRM regression.

## 1. Q1 identity, readiness and independent plan binding

Record candidate SHA and branch, dirty state, test environment, exact install/test/run commands, frozen spec version, raw/derived schemas, target routes, fixtures, approved network actions, request/time/disk bounds, writable QA workspace, and retained evidence paths. Include the repo-local QA playbook snapshot. Inspect commands for external effects before running them.

Use engineering reports as claims. Verify the real runner, code paths, output ownership, and dependency pins. Do not create substitute green implementations of the same algorithm. Expected fixture outputs must be derived from explicit input facts and the approved contract. Name mocked boundaries. A mocked crawl cannot establish real-site capture.

Executor must propose concrete commands/assertions for every group below, exact fixtures/expected values and all AC mappings. SOL approves/amends those bindings. Executor may correct disposable QA helpers within its lane, recording those changes separately from product defects. Product repairs belong to Cody only within explicit JARVIS-authorized scope, one active writer on the forward QA branch. Missing setup or authorization is BLOCKED; it is not PASS.

## 2. Coverage matrix and executable intentions

| Test | AC coverage | Exercise and expected result | Evidence |
|---|---|---|---|
| T-01 Setup and operator path | AC-001, AC-047 | Start in a clean isolated environment; follow only shipped instructions, including a failure/recovery path. All required steps are reproducible and documented. | Commands, environment/pins, outputs, operator observations |
| T-02 Input and output boundaries | AC-002, AC-004 | Valid project/site, missing project, bad URL/scheme, traversal strings, repeat/colliding run IDs. Valid writes stay in scope; invalid input fails helpfully; old runs survive. | Input/exit matrix and before/after file inventory |
| T-03 Whole invocation and offline Prepare | AC-003 | Run the documented whole pipeline; disable network for a Prepare-only rerun against retained raw inputs. Both required outputs exist; Prepare makes no crawl dependency. | Command traces, output paths, network isolation evidence |
| T-04 Polite access enforcement | AC-005 | Controlled redirects in every intentional stream: scope checked before each hop, five-hop bound. Independent refusal/challenge cases stop on first event; zero retries/switching/restarts. Prove shared ≥5 s after operation completion, normal background POST allowed and incidental resource failure separated from document denial. | Local fixture server request log, status/timing table |
| T-05 Partial failure and interruption | AC-006, AC-017 | Inject timeout, malformed response, interruption after partial capture, skip/limit case. Expect correct exit/summary, typed outcomes, prior captured evidence retained, documented rerun behavior. | Fault inputs, status/logs, partial artifact accounting |
| T-06 Discovery and stream accounting | AC-007, AC-008 | Seed sitemap duplicates/variants and mixed captured/missing streams. Compare the selected route set to per-stream outcomes. Exactly one pages[] outcome and REST mapping per selected/known route; HTML absences refer to outcomes without adding pages. | Independently computed route/outcome table |
| T-07 HTML fidelity and false success | AC-009, AC-010 | Feed known rendered bytes, empty response, explicit denial, and a soft-block page. Persist valid evidence faithfully; classify unsuccessful evidence under the declared policy. | Byte comparisons, fixture expected outcomes, capture records |
| T-08 REST, pagination, and SEO capture | AC-011, AC-012, AC-013 | Serve multiple REST pages with full/missing SEO, no-REST routes, ambiguous identities, available/unavailable site inventory. Full response bytes/hash at declared browser boundary survive; derivative values/unknown fields, response reference/array position/serialization reconcile. Missing/null optional fields differ from malformed mandatory structure. No root enumeration or four-field filter. | Fixture response digests, object-to-route map, absence records |
| T-09 Cross-stream content | AC-014, AC-024 | Use empty REST plus meaningful rendered content, and deliberately contradictory non-empty streams. Show content evidence and both conflicting sources. Empty raw REST remains empty and never erases rendered text. Legacy thrive_signal is explicitly heuristic with cited basis, not a plugin cause. File size alone does not satisfy the check. | Extracted source excerpts and cross-stream record links |
| T-10 Media capture and classification | AC-015, AC-028 | Seed referenced/social/global/editorial/integration/external/broken/duplicate/unused/unknown assets. Retain every raw item, provenance, available metadata, and justified classes. Only in-scope HEAD; offscope external/staging inventoried as skipped/untested with no deliberate probes. Browser image loading is not separate media harvesting. | Full fixture input-output reconciliation |
| T-11 Manifest and authored evidence | AC-016, AC-018 | Compare manifest facts to observed run facts; add an authored screenshot and repeat without one. Preserve bytes and distinguish authored, captured, and missing evidence. | Schema checks, execution comparison, screenshot digest |
| T-12 Raw immutability and invalid package | AC-019, AC-020 | Hash a saved raw package; run successful and failing Prepare cases using corrupt JSON, missing mandatory files, bad versions/references. Source run inventory/bytes unchanged; NEW pack/raw copy permitted and byte-identical; resolved filesystem write guards distinguish these roots. Invalid packages refused, not merely labeled incomplete. | Before/after manifests and explicit failure results |
| T-13 Provenance and honest labels | AC-021, AC-022 | Resolve all fixture source references and inspect real samples. Mix known facts, unsupported inference, absence, and uncertainty. Labels and schema-declared refs expose actual evidence; raw source/quoted values are not authored envelope fields or advice. | Reference-validation report and source spot checks |
| T-14 Content and observed design | AC-023, AC-027 | Use a known small site structure/content/style fixture and a case with unobservable styles. Expected site/content inventory survives; design observations cite sources and unknowns stay unknown. | Expected-versus-actual records, source excerpts and authored-advice versus quoted-source checks |
| T-15 SEO preservation through Prepare | AC-025 | Compare all supported derived SEO fields against raw sources, including conflicts, absent fields, and approved fallback paths. No invention or silent fallback. | Field-level semantic comparison and fallback provenance |
| T-16 Forms and embeds | AC-026 | F-07: exactly two forms, two embeds (iframe/script), mailto separately a link. Inventory correctly; untested function remains unverified. No live submissions. | Fixture inventory and function-status assertions |
| T-17 Loss and non-destructive processing | AC-029, AC-030 | Feed structurally valid F-12 with two typed source losses and intact route/map/reference structure, uncertain duplicate assets and staging URLs; malformed F-10 belongs to T-12 refusal. Loss is explicit; original evidence and URLs remain available; no unauthorized promotion/deletion. | Loss ledger, raw/derived comparisons, mutation checks |
| T-18 Twins and deterministic processing | AC-031, AC-032 | Generate human/machine twins and rerun Prepare on identical input. Check matching facts/counts and semantic reproducibility under approved normalization. | Semantic diff, ignored metadata list, twin comparisons |
| T-19 Pack inventory and portability | AC-033, AC-036, AC-037 | Validate all entry links/source references, including disagreements; relocate the declared handoff unit and repeat. Required references resolve without original workspace paths. | Link/reference report before/after relocation |
| T-20 Consumer usefulness and completeness | AC-034, AC-035, AC-038 | Separate consumer answers the frozen B7 questions using only complete/partial pack fixtures and the real pack. Missing answers are explicit; no invented content or unqualified complete status. | Cold-read answers, evidence citations, remaining questions, Tony/SOL assessment |
| T-21 Real integration and repeatability | AC-039, AC-040 | First run complete F-09 and mixed-partial F-01/F-02 variants through the installed full pipeline at E1; then assess the two authorized E2 Cyberize collections/processing runs under SOL’s explicit shared-evidence reuse decision; do not automatically repeat them in QA. Check structure/accounting/provenance, not byte equality of a changing live site. | Boundary traces, both real run manifests, output comparisons |
| T-22 Regression and resource limits | AC-041, AC-042 | Run certified baseline/no-break suite and integrated regression; measure requests, duration, output size, and limit-trigger behavior. Required behavior green, with only E-01/E-05/E-06/E-07 documented regression exceptions; wait_for_images=True/90000 ms/3 s/BYPASS/UA preserved; budgets respected or visibly stopped. | Test output, command/exit record, measurements |
| T-23 Hostile data and evidence hygiene | AC-043, AC-044 | Exercise traversal/bad source links and malicious HTML/JSON as data; seed synthetic secret sentinels in private environment inputs. No traversal/write escape or active generated markup; raw archive/source strings stay byte-faithful. Exact E-16 generated scan inventory/exemptions and isolated leak-detection control, no sentinel echoed; no generated-report blanket exemption. | Actual boundary probes, scanned path list, redacted results |
| T-24 Campaign evidence and final specimen | AC-045, AC-046, AC-048 | Read checkpoint/logs; reconcile every AC with test evidence and current specimen. At final closeout verify review/RRM disposition, retests, certification, cleanup, and merge records. | Complete ledger, SHA chain, verdict and closeout evidence |

## 3. Run order

After SOL approves/amends the Q1 plan, the separate Executor runs preflight and controlled checks T-01 through T-19, T-22 through T-24 as dependencies allow. Collect related defects into one actionable batch instead of sending Tony every command. Continue unaffected tests after ordinary failures so the first report has broad coverage; stop dependent or unsafe paths with reasons.

Run controlled end-to-end T-21 before its authorized real-target portion. Run T-20 on completed fixture and actual packs. Manual cold-read judgment and Director git actions remain explicit human checkpoints; a long QA run does not fabricate their completion. Do not silently increase live crawl volume or rerun large collections merely to clear an unrelated failure.

T-24 has two moments: initial QA assesses build/QA provenance; review, RRM, and final-closeout fields remain PENDING until those events occur. Final Gate Q for the QA candidate (after accepted cleanup) does not certify later review/RRM/integration work. Final closure requires those fields to be resolved.

## 4. Result and defect record

For each test, record: test ID; AC IDs; candidate SHA; fixture/input identity; environment; exact command; expected result; actual result; PASS / FAIL / BLOCKED / NOT RUN; evidence path; substituted components; limitation; defect IDs. Record start/end times for long batches.

Each defect states the observed failure, expected contract, reproduction, affected ACs, consequence/severity, and proposed verification. SOL adjudicates. Architect/Director settle contract and scope issues; the QA Executor cannot waive a requirement or repair product source; Cody acts only in the Engineer seat with explicit repair scope.

## 5. Repair and RRM regression

1. SOL adjudicates/batches findings; JARVIS explicitly authorizes the product-repair scope.
2. Cody, Engineer, repairs the approved set on the forward QA branch and runs engineering checks.
3. Tony commits; the independent Executor re-pins the candidate and runs affected tests plus required regression.
4. SOL records which earlier evidence can carry forward and why. New product changes invalidate affected earlier evidence.
5. Repeat until required checks are green or explicitly blocked. Do not rerun the whole expensive campaign without a concrete impact reason.

Post-review RRM uses the same product regression baseline. Add finding → disposition → repair AC → test → evidence mappings to this plan's RRM appendix. One RRM may contain many ordered repairs; accepted objectives remain bounded. The RRM's own required module contract and QA records are preserved under the included RRM playbook; do not create a competing second whole-product test plan.

## 6. Verdict and closeout

SOL applies the governing QA playbook's verdict vocabulary. A mandatory failed or unrun check cannot be represented as passed. Scope-inapplicable checks require a reason; accepted risk requires a Director ruling, not a model assumption. Report actual coverage and limitations beside the verdict.

Required cleanup is completed and accepted **before final Gate Q**. Executor inventories retained evidence and proposes disposable deletions; Tony alone performs destructive cleanup. Executor verifies candidate identity and preserved evidence afterward; SOL accepts cleanup. Documentation-only cleanup does not require a full QA rerun. Product/test/contract changes require impact assessment and affected retests. SOL issues the exact candidate-bound certificate; JARVIS carries it verbatim with its path/hash in closeout. Later independent Astra/fresh-Fable reviews, dispositions and any RRM remain obligations; their product changes require re-pin/retest and certificate disposition. Tony controls history and final integration.

Deployment and Gate D are outside this campaign.

## Execution binding sheet — Executor proposes at Q1; SOL approves/amends before Q2

| Field | Value |
|---|---|
| Candidate branch/SHA and contract version | UNBOUND |
| Environment and dependency pins | UNBOUND |
| Exact setup/regression/Capture/Prepare commands | UNBOUND |
| Fixture identities and expected records | UNBOUND |
| Per-test commands/assertions (T-01–T-24) | UNBOUND |
| Authorized target/routes, request/time/disk bounds | UNBOUND |
| Evidence workspace and retention | UNBOUND |
| Manual/cold-read owner and B7 checklist | UNBOUND |
| QA plan approval by SOL, candidate/plan hash and decision reference | PENDING |
| Engineering handoff and reproduction references | PENDING |
| Live evidence reuse/allocation decision; used/remaining budget | PENDING |
| Cleanup inventory, Tony action and SOL acceptance | PENDING |

No execution evidence or QA verdict has been generated in this handoff.


## Amendment checks to bind, not execute now

M-01–M-04 are APPROVED: [Rulings 1.2](../ABM_RULINGS_1_2.md) binds lock setup, complete/partial variants, snapshot comparison, one shared CHK smoke and precise leak scans. Execution remains NOT RUN. SOL’s candidate-bound reuse decision remains PENDING. All other amended intentions above remain planned, NOT RUN. Q1 binds exact installed-runtime hooks/API, byte boundary, redirect interception, intentional/background event classification, response/object hashes and fixture identity. Current browser TLS default was observed as ignore_https_errors=True in diagnostics, not a TLS assurance; record effective config, make no unapproved security change.

QAM pilot measurement and checkpoint state live in [STATE](../QAM/STATE.md); product PASS does not imply pilot PASS. No viewport/frontend QA is required for this CLI tool. Packaging follows [HANDOFFS](../QAM/HANDOFFS/README.md) by instruction; no exporter/validator exists yet.

## Revision 1.2 concrete binding references (all execution NOT RUN)

- T-01: lock install/pip check/normalization and tooling exclusions, Rulings 1.2 §2; actual clean environment remains unexecuted.
- T-03/06/08/12/17/18/20/21: exact fixture variant consumers and integrity-first snapshots, §3. T-03 C6/CHK uses --skip-prepare and C6 reader; full default invocation complete in Stage P and verified E1/E2. F-01 404 and F-02 pagination/ambiguity/optional/malformed cases retained.
- T-02/12/13/14/17/19/23: boundary-aware path/escaping/immutability/advice checks, §5, replacing contradictory blanket greps.
- T-23: exact generated artifact/exemption inventory and isolated leak control, §4.
- T-04/07: real installed soft-block signals and redirect/pacing fixture gates, BUILD_READBACK §2–3. Do not infer a CrawlResult flag.
- T-21/22: CHK one shared Capture-only smoke and E2 two full runs ≥1h apart; proposed ceilings in BUILD_READBACK §6 await Tony build approval; no automatic QA duplicate pair.
- T-24: source hash/mode inventory → Tony commit → independent QA byte identity attestation → SOL reuse decision, BUILD_READBACK §7. All 24 existing group mappings and NOT RUN states retained.
