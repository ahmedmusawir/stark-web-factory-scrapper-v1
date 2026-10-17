# Web Recon ABM — Engineer entry

## Current checkpoint — ENGINEERING BLOCKED AT CHK

Updated 2026-10-02T16:23:48.546151+00:00. C1–C6 Capture/minimal-reader implementation exists; final local regression **131 passed**, paired full **231-file** fixture comparison passed on the launched source. CHK's single live attempt exited 2 after **one intentional dispatch**: `ambiguous_intentional_request`. Root document returned 200; a same-URL GET stylesheet was misclassified as a duplicate intentional request. No observed 403/429 or explicit challenge. This is a failed control and incomplete smoke, not successful capture. No retry, restart, extra diagnostic or E2 run is authorized by the remaining ceiling. P1–P6/E1/E2 NOT STARTED; independent QA NOT RUN.

Evidence: `EVIDENCE/build/2026-10-02_135008Z/CHK-live-smoke/`, `blocker-review/root-event-excerpt.json`, `live-allocation-03-chk-stopped.json`; partial raw `outputs/CyberizeGroup/runs/2026-10-02T16-14-53Z/`. Base HEAD remains `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f` on `wf-scrapper-abm`, plus dirty/untracked source. Test/live source inventory SHA-256 `9875be4856c180ed97ccc25e4edc6fbf8f6cf41cfa0be59369920693dcda71df`; no completed candidate commit. The review package includes an exact launched-source snapshot and separate current checkpoint docs.

**Next decision:** JARVIS reviews the admission-classification defect and required local proof; Tony decides any replacement smoke allocation. Preserve the stopped run. Do not proceed past CHK or relaunch on resume. Tony alone handles Git mutations/destructive actions. Review report: `agent_docs/RESPONSES/response_2026-10-02_222348_abm-engineering-blocker.md` (sibling ZIP). QA candidate/plan/Executor session/SOL certification remain PENDING.


## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.

## Preserved pre-launch documentation checkpoint (superseded by Director GO above)


Revision 1.2 · 2026-10-02. Read and follow [AGENTS.md](AGENTS.md), the shared module entry for **Cody, Engineer**. Tony is Director; JARVIS is Architect. Tool/provider identity does not change the assigned seat.

Current checkpoint: AWAITING BUILD_READBACK REVIEW AND TONY'S BUILD APPROVAL. JARVIS authorized documentation-only BUILD_READBACK, now delivered. Do not implement C1 or execute old P0/recovery, tests, installs or live work. Independent QA uses a separate session and [QAM instructions](QAM/EXECUTION_INSTRUCTIONS.md), not this engineering session. See [RECOVERY](../../../RECOVERY.md) for state.
