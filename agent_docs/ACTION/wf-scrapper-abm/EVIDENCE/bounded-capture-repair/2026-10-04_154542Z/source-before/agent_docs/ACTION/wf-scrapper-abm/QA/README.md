# Canonical product QA lane

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.


Revision 1.2 · 2026-10-02 · JARVIS Architect amendment under Tony’s delegated authority.

[MASTER_QA_TEST_PLAN.md](MASTER_QA_TEST_PLAN.md) is the single product plan (T-01–T-24; AC-001–AC-048), including repair/RRM regression. [Acceptance](../ABM_ACCEPTANCE_SPEC.md) is canonical; [ledger](../ABM_LEDGER.md) records claims and independent results separately. Do not duplicate them under QAM.

SOL remains QA Lead. QA Executor is a **separate session**, actual binding PENDING. Cody is currently Engineer. Tony creates the QA branch and commits the candidate before QA pins it. Q1 proposes candidate-bound commands/assertions and one review package; SOL approves/amends; Q2 executes continuously, continuing unaffected safe checks after ordinary failures. No QA executed by this documentation/readback pass. Current dispositions: [Rulings 1.2](../ABM_RULINGS_1_2.md); engineering plan: [BUILD_READBACK](../BUILD_READBACK.md).

Use [QAM](../QAM/README.md) for workflow/state/packaging and [shared execution instructions](../QAM/EXECUTION_INSTRUCTIONS.md). Future `QA_WORK_JOURNAL.md` belongs here, created by the Executor at Q1/Q2; no fake result file is prewritten. Engineering evidence remains in the existing engineering log/evidence lanes. Fresh-Fable B7 cold-read remains before final Gate Q, judged by SOL; whole-app review and later Astra/fresh-Fable reviews remain required.

QA inventories proposed cleanup; Tony performs approved destructive actions; Executor verifies preserved evidence and candidate identity; SOL accepts cleanup **before final Gate Q**. Later review/RRM changes require scoped retest and cleanup acceptance as applicable. No full QA rerun merely for documentation cleanup. Deployment is out of scope.
