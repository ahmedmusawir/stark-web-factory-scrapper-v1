# QAM — Web Recon local pilot

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.


Revision 1.2 · 2026-10-02 · JARVIS Architect amendment under Tony’s delegated authority.

**Current:** AWAITING BUILD_READBACK REVIEW AND TONY'S BUILD APPROVAL. Rulings applied and BUILD_READBACK delivered; Build/independent QA NOT RUN. This is a workflow and packaging lane, not a new QA software platform.

## Entry and read order

1. [STATE](STATE.md): checkpoint, decisions, resume and pilot measurements.
2. [MANIFEST](MANIFEST.md): base/candidate/environment and governing inputs.
3. [Shared execution instructions](EXECUTION_INSTRUCTIONS.md), reached through thin [AGENTS](AGENTS.md)/[CLAUDE](CLAUDE.md) entries.
4. Canonical [acceptance](../ABM_ACCEPTANCE_SPEC.md), [contracts](../ABM_CONTRACTS.md), [master QA plan](../QA/MASTER_QA_TEST_PLAN.md), [ledger](../ABM_LEDGER.md), [campaign journal](../ABM_CAMPAIGN_JOURNAL.md), [record templates](../ABM_EXECUTION_RECORDS.md).
5. [Handoff packaging](HANDOFFS/README.md) and [amendment evidence/decisions](../ABM_AMENDMENT_1_1.md).

## Workflow and owners

| Checkpoint | Owner and required outcome | Current result |
|---|---|---|
| BUILD_READBACK review → build approval | JARVIS rulings applied, Cody readback delivered; JARVIS reviews and Tony approves build | Readback DONE; review/approval PENDING |
| Engineering complete | Cody builds and supplies factual QA handoff with exact commands, fixture/env/AC/evidence/gaps/budget/reproduction | NOT RUN |
| Candidate | Tony commits and creates QA branch; no agent Git mutations | PENDING |
| Q1 | Separate Executor verifies identity/readiness, independently inspects code and handoff, completes concrete master-plan bindings, exports one review package | NOT RUN |
| Plan decision | SOL QA Lead approves/amends candidate-bound plan | PENDING |
| Q2 | Executor runs approved continuous campaign; unaffected safe checks continue after ordinary failures | NOT RUN |
| Findings/repair/retest | SOL adjudicates; JARVIS explicitly scopes product repairs; Cody repairs on forward QA branch, one active writer; Tony commits; Executor re-pins/retests | PENDING / unexercised |
| Cleanup | Executor inventories/proposes; Tony deletes only with his approval; Executor verifies identity/evidence; SOL accepts cleanup | PENDING |
| Final Gate Q | SOL issues exact candidate-bound certificate; mandatory unknowns cannot become PASS | PENDING |
| Independent reviews/RRM | Astra and fresh Fable review same specimen independently; dispositions and any RRM/retests remain required | PENDING |
| Closeout/integration | JARVIS carries exact certificate and dispositions; Tony final integration; deployment out of scope | PENDING |

R5 fresh-Fable B7 pack cold-read remains during QA before Gate Q, distinct from later code review. Whole-application CLI review remains in T-03/T-20/T-21/T-24. Existing QA records hold results; do not create a competing ledger, acceptance or whole-product plan here. QA Lead and Executor are separate seats/sessions; SOL assignment remains, actual session identities pending. Cody is currently Engineer and cannot independently certify his own work.
