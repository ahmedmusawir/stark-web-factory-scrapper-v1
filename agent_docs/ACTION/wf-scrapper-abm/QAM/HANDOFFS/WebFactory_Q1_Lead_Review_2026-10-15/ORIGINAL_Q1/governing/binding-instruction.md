# Binding instruction — Q1 resume GO (Tony, 2026-10-15)

Recorded verbatim by the Executor as the authorization governing this package. Executor identity: **Opy** (OpenCode, GLM 5.3), occupying the independent QA Executor seat previously called Claudy. Cody remains Engineer.

> OPY — GO: COMPLETE THE AUTHORIZED Q1 RESUME
>
> You are Opy, running OpenCode with GLM 5.3, occupying the independent
> QA Executor seat previously called Claudy. Record that transition.
> Cody remains Engineer.
>
> Proceed with the existing Q1 resume. No further planning approval
> is needed for these already-authorized steps.
>
> Expected branch: qa/wf-scrapper-abm
> Expected candidate: 8fbcff289fde5149be0c0631b08e8a5fbcb3faa4
> Expected source52:
> 39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314
>
> 1. Verify committed source and working source against that inventory.
> 2. Re-verify the saved fixture identities.
> 3. Finish the existing candidate-bound recon and proposed test plan.
>    Preserve prior observations and unresolved expected-behavior
>    questions for the QA Lead. Do not silently settle acceptance rules.
> 4. Export the indexed Q1 review package under QAM/HANDOFFS, with a
>    byte-identical ZIP copy in /home/moose/Downloads.
> 5. Report exact paths, ZIP hash and the decision requested.
>
> Use completed inspection where still applicable; do not restart Q1.
>
> If a tool is denied, preserve the exact error. Do not evade the
> denial. Continue independent permitted inspection where useful,
> and stop dependent work if a required verification is blocked.
>
> No product changes, Git mutations, external website requests,
> full Q2 campaign or certification.
>
> STOP after delivering the Q1 package for the new QA Lead's approval.

## Executor record of execution against this instruction

| Instruction step | Result |
|---|---|
| Seat transition recorded | Opy (OpenCode, GLM 5.3) succeeds Claudy; session log `agent_docs/SESSIONS/session_2026-10-15.md` §14:06Z |
| 1. Committed + working source vs inventory | PASS — 52/52 worktree files and 52/52 committed blobs hash-match `governing/source-inventory.json`; combined identity recomputed from BOTH sides equals `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` (see `checks/source52-recompute.json`, `checks/committed-vs-tested.json`) |
| 2. Fixture identities | PASS — 2/2 archives, 34/34 manifest reference files, 2/2 dependency files hash-and-byte match (see `checks/fixture-verification.json`) |
| 3. Candidate-bound recon + plan | DONE — `Q1_BOUND_READINESS_REPORT.md` + candidate-bound `Q1_PROPOSED_TEST_PLAN.md`; prior observations and expected-behavior questions preserved, acceptance rules left for the QA Lead |
| 4. Indexed package + byte-identical Downloads ZIP | DONE — this directory + ZIP (paths and SHA-256 in `START_HERE.md` and the readiness report) |
| 5. Report paths, ZIP hash, decision requested | DONE — report and on-screen summary |
| No restart of Q1 | Prior STOP-package inspection reused; only the previously-blocked binding steps were executed |
| Tool denials | None this session; `python3` executed normally in this harness (prior 2026-10-15 harness rejections did not recur) |
| No product changes / Git mutations / external requests / Q2 / certification | Held — git used read-only (`rev-parse`, `status`, `log`, `cat-file`); zero network; no installs |

Received (local): 2026-10-15 20:06 +06 (13:52Z–14:06Z window). Executed: 2026-10-15 20:06–20:09 +06 so far.