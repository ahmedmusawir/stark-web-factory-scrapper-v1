# Web Recon ABM — Execution Record Templates

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.


Version: 1.2 | 2026-10-02 | JARVIS Architect amendment under Tony’s delegated authority. Future templates only; no result/approval implied.

The Architect places these records in the repo's confirmed documentation layout. Avoid redundant journals: one campaign narrative, one engineering execution log, and one QA work journal are enough. The acceptance ledger links evidence rather than copying it.

## Acceptance ledger

Create one row for every AC-001 through AC-048. Keep requirements in the master spec, not in competing restatements here.

| AC ID | Engineer state | Files/task | Engineer evidence | QA tests | QA state | QA evidence/candidate | Final disposition |
|---|---|---|---|---|---|---|---|
| AC-001 | NOT STARTED | — | — | T-01 | NOT RUN | — | OPEN |

Engineer states: NOT STARTED / IN PROGRESS / IMPLEMENTED / BLOCKED. QA states: NOT RUN / PASS / FAIL / BLOCKED / NOT APPLICABLE WITH RULING. Required untested behavior never becomes PASS through a completion report.

## Engineering execution log — append after each meaningful task

- Timestamp, task/BIM identity, Capture or Prepare:
- Intent and affected ACs:
- Files/behavior changed:
- Exact checks/commands, exit codes, expected versus observed outcomes:
- Evidence paths:
- Deviations, approved errata, remaining problems:
- Current branch/commit and uncommitted work:
- Next ready task:

Keep an internal task map if useful; passing engineer checks automatically advances approved work. Do not require Tony to approve every log entry.

## Recovery checkpoint — update at task/session boundaries

- Approved ABM/spec versions and repo identity:
- Active seat and authorized work:
- Current branch/SHA, dirty state, running processes:
- Last completed task and its evidence:
- In-progress task and precise remaining action:
- Last successful check and unresolved failures:
- Decisions still needed; dependencies blocked:
- Next task/command and required inputs:
- Output/evidence locations and live-run budget already used:

Resume by confirming disk against the checkpoint. Do not blindly repeat state-changing operations or expensive live runs. A session restart itself is not a new approval gate.

## Engineering completion report — one campaign handoff

State implemented scope, changed files and per-AC/test-group mappings; exact commands, environment/runtime/configuration, fixture identities, expected versus actual results, evidence paths, raw-to-derived checks, known gaps, authorized live-budget usage/remaining and exact reproduction steps/writes. Before Tony commits, record **base HEAD plus dirty changes** and candidate PENDING; never call base HEAD the completed implementation commit. Tony commits, then independent QA pins the actual candidate. Include evidence rather than test-count claims; engineering success is not independent QA PASS. Package via [QAM handoffs](QAM/HANDOFFS/README.md).

## QA execution journal

- Timestamp/test IDs/ACs/candidate:
- Exact input/fixture and environment:
- Command/probe and actual outputs:
- Expected versus actual result and status:
- Evidence/helper paths, purpose, and retention classification:
- State mutations/restoration if any:
- Defect IDs, limitations, and next independent test:

Keep regression and live-evidence specimen identity explicit through every repair round.

## Review disposition and RRM trace

| Source finding | Reviewer/specimen | Current applicability | Architect proposal | Tony ruling | RRM repair AC | Allowed scope | Test/evidence | Final disposition |
|---|---|---|---|---|---|---|---|---|

Preserve raw review reports. Merge duplicates by reference, not deletion. Use the supplied RRM playbook's dispositions and lifecycle. Map RRM repair ACs back to affected product ACs and the master QA plan's relevant test groups. RRM scope is written after findings exist, never invented in advance.

## Final closeout record

- Certified implementation SHA and spec/errata version:
- SOL verdict and coverage limitations:
- Astra/Fable reports and dispositions:
- RRM identity or no-repair ruling:
- Repair retest/regression and final Astra confirmation:
- QA Cleanup outcome; evidence and closeout commit identities:
- Exact SOL certificate text/path/hash and cleanup acceptance before final Gate Q:
- Architect JARVIS closeout carrying that certificate; Cody engineering completion:
- Director merge/push identity when performed:
- Product run instructions and approved known limitations:
- Separate product and pilot verdicts; measured preparation/execution/review waits/repairs/cleanup/closeout, planned checkpoints, unexpected interventions and package omissions; unexercised paths UNTESTED:

Deployment remains a separate future decision.


## Candidate-bound QAM checkpoint record (existing journals use these fields)

Checkpoint / owner / actual session identity / UTC start-end; requested reviewer decision; candidate/contract/plan revision and hashes; readiness or results; exact evidence/commands/fixtures; gaps and dependencies; inventory/exclusions; shared live-evidence reuse/allocation and used/remaining budget; approval reference (PENDING until actually issued); next authorized action. Q1 Executor prepares canonical-plan bindings; SOL approves/amends. Q2 continues unaffected safe checks after ordinary failures. Product repairs need explicit JARVIS scope, one active writer, Tony commit and Executor re-pin/retest. Helper fixes are recorded separately.

Cleanup record: proposed deletions/retentions, why disposable, Tony action reference, preserved evidence and post-cleanup identity checks, SOL acceptance. **No agent deletion authorization is created.** Cleanup precedes final Gate Q; no full rerun merely for documentation cleanup. Later reviews/RRM and impacts remain tracked in T-24. Every package has START_HERE, readable governing inputs and a requested decision; no competing QA platform or exporter is assumed.

## Precommit evidence identity addendum (E-17/E-18)

Engineering handoff retains base HEAD + complete dirty source identity (path/hash/mode/symlink inventory, including untracked implementation/test/fixture/config/governing inputs), commands/runtime and evidence digests. Tony commits; QA compares committed tree bytes/modes with that inventory read-only and records a separate binding attestation. Original evidence is immutable; no retroactive replacement of base SHA. Differences require impact adjudication; SOL alone decides candidate-bound reuse. BUILD_READBACK §7 gives exact procedure. CHK evidence is raw-only (--skip-prepare); E2 supplies full pack evidence.
