# Web Recon + Prepare — Master QA Test Plan

Version: 0.2 | 2026-09-17 | Owner at execution: SOL QA Lead
Executor: Cody in a separate QA session | State: DESIGNED, NOT EXECUTED

This is one whole-product QA plan for the ABM. SOL completes its repo-specific bindings after QA recon, then Cody executes the approved campaign in long batches. Test groups organize the work; they do not create 24 Director approval steps. The plan remains the canonical product QA record through repair and RRM regression.

## 1. Before Cody runs

Record candidate SHA and branch, dirty state, test environment, exact install/test/run commands, frozen spec version, raw/derived schemas, target routes, fixtures, approved network actions, request/time/disk bounds, writable QA workspace, and retained evidence paths. Include the repo-local QA playbook snapshot. Inspect commands for external effects before running them.

Use engineering reports as claims. Verify the real runner, code paths, output ownership, and dependency pins. Do not create substitute green implementations of the same algorithm. Expected fixture outputs must be derived from explicit input facts and the approved contract. Name mocked boundaries. A mocked crawl cannot establish real-site capture.

SOL must bind concrete commands/assertions to every group below, identify the exact fixtures and expected values, and account for every AC. Cody may write authorized test/probe helpers in the QA workspace. Product repairs belong to Claudy. Missing setup or authorization is BLOCKED; it is not PASS.

## 2. Coverage matrix and executable intentions

| Test | AC coverage | Exercise and expected result | Evidence |
|---|---|---|---|
| T-01 Setup and operator path | AC-001, AC-047 | Start in a clean isolated environment; follow only shipped instructions, including a failure/recovery path. All required steps are reproducible and documented. | Commands, environment/pins, outputs, operator observations |
| T-02 Input and output boundaries | AC-002, AC-004 | Valid project/site, missing project, bad URL/scheme, traversal strings, repeat/colliding run IDs. Valid writes stay in scope; invalid input fails helpfully; old runs survive. | Input/exit matrix and before/after file inventory |
| T-03 Whole invocation and offline Prepare | AC-003 | Run the documented whole pipeline; disable network for a Prepare-only rerun against retained raw inputs. Both required outputs exist; Prepare makes no crawl dependency. | Command traces, output paths, network isolation evidence |
| T-04 Polite access enforcement | AC-005 | Controlled redirects/out-of-scope locations, 403/429 and repeat failures. Observe actual request destinations, pauses, stop/retry behavior against frozen limits. | Local fixture server request log, status/timing table |
| T-05 Partial failure and interruption | AC-006, AC-017 | Inject timeout, malformed response, interruption after partial capture, skip/limit case. Expect correct exit/summary, typed outcomes, prior captured evidence retained, documented rerun behavior. | Fault inputs, status/logs, partial artifact accounting |
| T-06 Discovery and stream accounting | AC-007, AC-008 | Seed sitemap duplicates/variants and mixed captured/missing streams. Compare the selected route set to per-stream outcomes. No missing or contradictory accounting. | Independently computed route/outcome table |
| T-07 HTML fidelity and false success | AC-009, AC-010 | Feed known rendered bytes, empty response, explicit denial, and a soft-block page. Persist valid evidence faithfully; classify unsuccessful evidence under the declared policy. | Byte comparisons, fixture expected outcomes, capture records |
| T-08 REST, pagination, and SEO capture | AC-011, AC-012, AC-013 | Serve multiple REST pages with full/missing SEO, no-REST routes, ambiguous identities, available/unavailable site inventory. Exact payloads survive and mapping gaps remain visible. | Fixture response digests, object-to-route map, absence records |
| T-09 Cross-stream content | AC-014, AC-024 | Use empty REST plus meaningful rendered content, and deliberately contradictory non-empty streams. Show content evidence and both conflicting sources. File size alone does not satisfy the check. | Extracted source excerpts and cross-stream record links |
| T-10 Media capture and classification | AC-015, AC-028 | Seed referenced/social/global/editorial/integration/external/broken/duplicate/unused/unknown assets. Retain every raw item, provenance, available metadata, and justified classes. | Full fixture input-output reconciliation |
| T-11 Manifest and authored evidence | AC-016, AC-018 | Compare manifest facts to observed run facts; add an authored screenshot and repeat without one. Preserve bytes and distinguish authored, captured, and missing evidence. | Schema checks, execution comparison, screenshot digest |
| T-12 Raw immutability and invalid package | AC-019, AC-020 | Hash a saved raw package; run successful and failing Prepare cases using corrupt JSON, missing mandatory files, bad versions/references. Raw bytes unchanged; invalid packs never appear complete. | Before/after manifests and explicit failure results |
| T-13 Provenance and honest labels | AC-021, AC-022 | Resolve all fixture source references and inspect real samples. Mix known facts, unsupported inference, absence, and uncertainty. Labels and references expose the actual evidence. | Reference-validation report and source spot checks |
| T-14 Content and observed design | AC-023, AC-027 | Use a known small site structure/content/style fixture and a case with unobservable styles. Expected site/content inventory survives; design observations cite sources and unknowns stay unknown. | Expected-versus-actual records and source excerpts |
| T-15 SEO preservation through Prepare | AC-025 | Compare all supported derived SEO fields against raw sources, including conflicts, absent fields, and approved fallback paths. No invention or silent fallback. | Field-level semantic comparison and fallback provenance |
| T-16 Forms and embeds | AC-026 | Seed form, iframe, script integration, external target, and inert markup. Inventory correctly; untested function remains unverified. No live submissions. | Fixture inventory and function-status assertions |
| T-17 Loss and non-destructive processing | AC-029, AC-030 | Feed missing/unsupported inputs, uncertain duplicate assets, staging-domain URLs. Loss is explicit; original evidence and URLs remain available; no unauthorized promotion/deletion. | Loss ledger, raw/derived comparisons, mutation checks |
| T-18 Twins and deterministic processing | AC-031, AC-032 | Generate human/machine twins and rerun Prepare on identical input. Check matching facts/counts and semantic reproducibility under approved normalization. | Semantic diff, ignored metadata list, twin comparisons |
| T-19 Pack inventory and portability | AC-033, AC-036, AC-037 | Validate all entry links/source references, including disagreements; relocate the declared handoff unit and repeat. Required references resolve without original workspace paths. | Link/reference report before/after relocation |
| T-20 Consumer usefulness and completeness | AC-034, AC-035, AC-038 | Separate consumer answers the frozen B7 questions using only complete/partial pack fixtures and the real pack. Missing answers are explicit; no invented content or unqualified complete status. | Cold-read answers, evidence citations, remaining questions, Tony/SOL assessment |
| T-21 Real integration and repeatability | AC-039, AC-040 | First run the installed pipeline against controlled HTTP/site fixtures; then two authorized Cyberize collections and processing runs. Check structure/accounting/provenance, not byte equality of a changing live site. | Boundary traces, both real run manifests, output comparisons |
| T-22 Regression and resource limits | AC-041, AC-042 | Run certified baseline/no-break suite and integrated regression; measure requests, duration, output size, and limit-trigger behavior. Required behavior green; budgets respected or visibly stopped. | Test output, command/exit record, measurements |
| T-23 Hostile data and evidence hygiene | AC-043, AC-044 | Exercise traversal/bad source links and malicious HTML/JSON as data; seed synthetic secret sentinels in private environment inputs. No unauthorized execution/write escape or private sentinel leak. | Actual boundary probes, scanned path list, redacted results |
| T-24 Campaign evidence and final specimen | AC-045, AC-046, AC-048 | Read checkpoint/logs; reconcile every AC with test evidence and current specimen. At final closeout verify review/RRM disposition, retests, certification, cleanup, and merge records. | Complete ledger, SHA chain, verdict and closeout evidence |

## 3. Run order

After SOL binds the plan, Cody runs preflight and controlled checks T-01 through T-19, T-22 through T-24 as dependencies allow. Collect related defects into one actionable batch instead of sending Tony every command. Continue unaffected tests after ordinary failures so the first report has broad coverage; stop dependent or unsafe paths with reasons.

Run controlled end-to-end T-21 before its authorized real-target portion. Run T-20 on completed fixture and actual packs. Manual cold-read judgment and Director git actions remain explicit human checkpoints; a long QA run does not fabricate their completion. Do not silently increase live crawl volume or rerun large collections merely to clear an unrelated failure.

T-24 has two moments: initial QA assesses build/QA provenance; review, RRM, and final-closeout fields remain PENDING until those events occur. Initial Gate Q does not falsely certify future work. Final closure requires those fields to be resolved.

## 4. Result and defect record

For each test, record: test ID; AC IDs; candidate SHA; fixture/input identity; environment; exact command; expected result; actual result; PASS / FAIL / BLOCKED / NOT RUN; evidence path; substituted components; limitation; defect IDs. Record start/end times for long batches.

Each defect states the observed failure, expected contract, reproduction, affected ACs, consequence/severity, and proposed verification. SOL adjudicates. Architect/Director settle contract and scope issues; Cody cannot waive a requirement or repair product source.

## 5. Repair and RRM regression

1. SOL batches verified defects; Architect supplies a ruling only where needed.
2. Claudy repairs the approved set on the forward QA branch and runs engineering checks.
3. Tony commits; Cody re-pins the candidate and runs affected tests plus required regression.
4. SOL records which earlier evidence can carry forward and why. New product changes invalidate affected earlier evidence.
5. Repeat until required checks are green or explicitly blocked. Do not rerun the whole expensive campaign without a concrete impact reason.

Post-review RRM uses the same product regression baseline. Add finding → disposition → repair AC → test → evidence mappings to this plan's RRM appendix. One RRM may contain many ordered repairs; accepted objectives remain bounded. The RRM's own required module contract and QA records are preserved under the included RRM playbook; do not create a competing second whole-product test plan.

## 6. Verdict and closeout

SOL applies the governing QA playbook's verdict vocabulary. A mandatory failed or unrun check cannot be represented as passed. Scope-inapplicable checks require a reason; accepted risk requires a Director ruling, not a model assumption. Report actual coverage and limitations beside the verdict.

Gate Q precedes cleanup. Retain concise reproducible evidence, final reports, errata/disposition records, test mappings, and specimen identities. Remove disposable workspaces/caches; retain reproduction scripts when needed. Confirm cleanup did not change product/test/contract behavior. Architect then issues closeout; Tony controls history and merge.

Deployment and Gate D are outside this campaign.

## Execution binding sheet — SOL completes once at QA entry

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
| QA plan approval by SOL | PENDING |

No execution evidence or QA verdict has been generated in this handoff.
