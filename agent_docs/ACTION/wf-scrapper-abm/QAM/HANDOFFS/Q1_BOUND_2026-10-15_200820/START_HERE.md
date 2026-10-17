# START HERE — Q1_BOUND package (2026-10-15 20:08 +06)

**Status in plain English:** The candidate is now established and independently verified. Tony's commit `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4` on branch `qa/wf-scrapper-abm` contains exactly the engineering-tested source: all 52 files hash-match the tested inventory in the worktree AND as committed blobs, and the combined source52 identity recomputes to `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` from both sides. Both fixture archives, all 34 manifest reference files and both dependency files verify. The candidate-bound test plan is finished, with the prior session's observations and expected-behavior questions preserved for the QA Lead. **Q1 is complete; nothing was executed (no tests, no network, no installs, no Git mutation, no certificate).**

**Decisions requested**
- **QA Lead:** approve or amend `Q1_PROPOSED_TEST_PLAN.md` — applicability of T-01–T-24, the O1–O10 expected-behavior bindings (plan §4), the evidence-reuse proposal (report §3), and the Q2 evidence-workspace lane. This is the one decision that unblocks Q2.
- **Tony (non-blocking):** commit the uncommitted working-tree additions (this package, RESPONSES report, RECOVERY checkpoint, and the Director's own RESPONSES/OLD archiving) when convenient.

**Read order**
1. `Q1_BOUND_READINESS_REPORT.md` — binding verification table, what changed since STOP, reuse proposal, environment facts, plan identity, decision requested.
2. `Q1_PROPOSED_TEST_PLAN.md` — the candidate-bound plan: filled binding sheet §0, pre-Q2 gates G1–G4, T-01–T-24 bindings, run order/stop conditions, preserved O1–O10.
3. `checks/source52-recompute.json`, `checks/committed-vs-tested.json`, `checks/fixture-verification.json`, `checks/readiness-checks.json` — machine evidence for the report.
4. `governing/binding-instruction.md` — Tony's GO text verbatim and the Executor's execution record against it.
5. `governing/source-inventory.json`, `governing/fixture-manifest.json` — byte-identical copies of the verified governing inputs (note: `candidate_commit` field inside the inventory copy still reads "PENDING Tony"; stale — the per-file hashes are the verified content).
6. `FILE_HASH_INVENTORY.json` — every member with SHA-256.

**Identity:** repo `/home/moose/PYTHON/stark-web-factory-scrapper-v1`, branch `qa/wf-scrapper-abm`, candidate HEAD `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4`, source52 `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` (verified). Plan identity: `Q1_PROPOSED_TEST_PLAN.md` SHA-256 `fc2cfdcc3170008689ad87001f4519d1ccf899c2486071fe3d147f2f04855826`, QA Lead approval PENDING. Executor: Opy (OpenCode, GLM 5.3), seat previously Claudy. Contract/acceptance: Spec 1.2 + CURRENT_TOOL_SCOPE crosswalk (historical).

**What was NOT done:** no tests run, no external requests, no installs, no product/QAM/helper repair, no Git mutation, no certificate, no Q2. The prior STOP package is preserved unmodified; its completed inspection is reused, Q1 was not restarted.

**Next authorized action:** none for the Executor — STOP after this delivery. QA Lead plan decision precedes any Q2 binding; Tony owns all Git actions.