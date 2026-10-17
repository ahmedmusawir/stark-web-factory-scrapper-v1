# Q1 candidate-bound readiness report — CANDIDATE BOUND; plan decision requested

**Executor:** Opy (OpenCode, GLM 5.3), independent QA Executor seat, previously Claudy · **Date:** 2026-10-15 20:08 (+06) / 14:08Z · **Requested reviewers:** new QA Lead (plan decision), Tony (delivery/handoff)
**Verdict: Q1 BINDING COMPLETE. The candidate is established and independently verified.** The previously blocked steps of the authorized Q1 resume were executed on 2026-10-15 20:06–20:09 +06: committed and working source verified against the 52-file inventory, saved fixture identities re-verified, and the candidate-bound test plan finished. Q1 did not restart: every completed inspection from `Q1_STOP_2026-10-15_121229/` is reused; only the binding steps that were blocked ran now. No tests were executed, no external requests, no installs, no product/QAM repair, no Git mutation, no certificate.

## 1. Binding verification — expected vs actual

| Check | Expected | Actual | Status |
|---|---|---|---|
| Branch | `qa/wf-scrapper-abm` | checked out; `origin/qa/wf-scrapper-abm` in remote-tracking refs; branch reported up to date with origin (live ls-remote not used — zero network) | ✅ verified |
| Candidate commit | `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4` | `git rev-parse HEAD` = `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4`; subject "Prepare DECIDE COLLECT PREPARE candidate for independent QA"; author Ahmed Musawir; 2026-10-15 18:59:22 +0600 | ✅ verified |
| Working source vs inventory | 52 paths hash to per-file SHA-256 in `governing/source-inventory.json` | 52/52 worktree files match | ✅ verified |
| Committed source vs inventory | 52 committed blobs hash to the same per-file SHA-256 | 52/52 `git cat-file blob HEAD:<path>` hashes match; summary SAME 52 / MODIFIED 0 / UNTRACKED 0 | ✅ verified |
| Source52 combined identity | `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` | recomputed from worktree hashes AND from committed-blob hashes — both equal the expected value; engineer's method confirmed (sorted path→sha256 JSON, compact separators, no trailing newline) | ✅ verified (the STOP report's "any other value → re-decide reuse" condition did not trigger) |
| Fixture archives | `d54bbaf0c07e1fbd41937afc11e3111378743d8903bdc6254d2e3bb329cc5a63` (432,966 B); `fdf18de8838f36344459555041a12e4f0cf46f044a1f211f6241a7bf420ab4a8` (107,429 B) | both present at `agent_docs/RESPONSES/…`; hashes and byte sizes match exactly | ✅ verified |
| Fixture reference files | 34 manifest files present and hash-match | 34/34 present, hash-and-byte match | ✅ verified |
| Dependencies | `requirements.txt` `231e1d8f…5f46`; `requirements-lock.txt` `e6c3e1a9…594c` | both match on disk | ✅ verified |
| Environment | Python 3.12.3 · crawl4ai 0.9.3 · playwright 1.52.0 · bs4 4.13.4 · pytest 8.3.5 · markdown-it-py 4.2.0 | re-recorded from `venv/` this session; all match; no installs performed | ✅ recorded |

Machine evidence: `checks/source52-recompute.json` (per-file worktree/committed/expected hashes + combined identity), `checks/committed-vs-tested.json` (52 SAME at candidate), `checks/fixture-verification.json` (archives/34 files/dependencies), `checks/readiness-checks.json` (candidate, environment, worktree, harness notes).

## 2. What changed since the STOP package

- The STOP blockers are resolved: candidate commit and `qa/wf-scrapper-abm` exist (Tony, 2026-10-15 18:59 +06) and are verified here. The four previously uncommitted source files (`recon_pipeline/decide.py`, `tests/test_decide.py`, Prepare helper + test) are now committed at the candidate and hash-identical to the tested bytes.
- The draft plan is superseded by the candidate-bound `Q1_PROPOSED_TEST_PLAN.md` in this package (§0 filled; T-01–T-24 unchanged).
- Nothing in the prior STOP package was modified; it remains preserved at `QAM/HANDOFFS/Q1_STOP_2026-10-15_121229/` with its Downloads ZIP.

## 3. Evidence reuse — the binding condition is now satisfied

The STOP report §4 conditioned engineering-evidence reuse on: *"Accept engineering JUnit/pytest/native timelines as candidate-compatible reference **only if** the committed candidate's 52 files hash to source52."* That condition is now met and independently verified (§1). Therefore the Executor puts to the QA Lead, unchanged from the STOP proposal:

- (a) Engineering's combined 97-test JUnit/pytest/native timelines may be treated as **candidate-compatible reference**.
- (b) An **independent Q2 re-run** of the same three modules on the candidate with a fresh basetemp (≈21 s, zero network) is still recommended — cheap enough that reuse-as-PASS is unnecessary.
- (c) `governing/fixture-manifest.json` + `restore-fixtures.py` (STOP package) remain the restoration *procedure*, with QA re-verifying hashes (34/34 verified this session; nothing was restored — nothing was missing).
- (d) The 9 offline accepted-package checks remain a *checklist* for QA re-execution against the same hashed inputs.
- (e) Dated live captures remain preserved observations, not evidence of current pacing/access.

**This is a proposal for the QA Lead's decision, not a settled reuse ruling.**

## 4. Preserved observations and open expected-behavior questions

All ten observations O1–O10 from the STOP readiness report §3 are preserved verbatim in `Q1_PROPOSED_TEST_PLAN.md` §4, including their T-row bindings. They remain **unsettled expected-behavior questions for the QA Lead**; nothing was silently decided in binding the plan. The four historical retired-path findings (media 1,661/1,753; two unconfirmed late aborts; stopped-run bootstrap/route accounting; supervisor counters) remain OPEN with disposition owned by the QA Lead.

## 5. Environment facts and worktree state (recorded, not touched)

- **Director's archiving:** between the 13:38Z and 14:06Z checkpoints the five `agent_docs/RESPONSES/*_review/` directories were moved into `agent_docs/RESPONSES/OLD/` (61 unstaged tracked deletions + untracked OLD/ copies), and an untracked root `AGENTS.md` appeared. This matches the documented Director-managed archive lane. **None of these intersect the 52 source paths, the fixture archives, or the 34 reference files**; the candidate HEAD is unchanged. The Executor did not restore, stage, or modify any of it. The Q2 executor will see this dirty state; pre-Q2 gate G1 ("no modified tracked product/test files") remains satisfiable.
- **Harness:** `python3` executed normally in this OpenCode harness — the prior session's tool rejections did not recur. **Zero tool denials this session.** Network: zero external requests; git used read-only (`rev-parse`, `status`, `log`, `cat-file`); no `ls-remote`.
- **Non-blocking, unchanged:** `agent_docs/KIP_REGISTRY.md` absent; the 2026-10-14 engineering ZIP is still absent from `/home/moose/Downloads` (its content exists in-repo); `governing/source-inventory.json`'s `candidate_commit` field still reads "PENDING Tony" (stale by design — the per-file hashes are the verified content; the copy in this package is byte-identical, not edited).

## 6. Live budget

Consumed by Q1: **0 external requests, 0 live allocations** (Q1 is inspect-and-bind). Remaining: unchanged; any live check requires Tony's separate explicit scope. The proposed Q2 network budget is 0 external requests (loopback only).

## 7. Plan identity

- `Q1_PROPOSED_TEST_PLAN.md` (this package) — SHA-256 `fc2cfdcc3170008689ad87001f4519d1ccf899c2486071fe3d147f2f04855826` (19,192 bytes), assigned post-finalization as the draft specified.
- QA Lead approval reference: **PENDING** — the requested decision.

## 8. Reproduction (Q1 binding steps — already run; safe, read-only)

Prerequisites: repo at candidate `8fbcff2…` on `qa/wf-scrapper-abm`; existing `venv/`; no network. Scope/writes: reads repository files and git objects only; writes only into this package directory and `/tmp/opencode/q1_resume/` scratch. Steps: (1) hash the 52 paths from `governing/source-inventory.json` in the worktree and via `git cat-file blob HEAD:<path>`; (2) recompute the combined identity as sha256 of the sorted path→sha256 compact JSON; (3) hash the two fixture archives, the 34 manifest reference files and the two dependency files; (4) compare all against the STOP package's governing values. Expected outcomes: all matches as recorded in `checks/*.json`. These were run this session by the Executor; results are the recorded evidence above. The T-01–T-24 test commands in the plan are NOT run — they are Q2 proposals.

## 9. Decision requested and next authorized action

**Requested from the QA Lead:** approve or amend the candidate-bound `Q1_PROPOSED_TEST_PLAN.md` (applicability of T-01–T-24, the O1–O10 expected-behavior bindings, the evidence-reuse proposal §3, the Q2 evidence-workspace lane). One decision, then Q2 may be bound and scheduled.

**Requested from Tony (no rush, non-blocking):** the package, response report and RECOVERY checkpoint are uncommitted working-tree additions, as is the Director's own archiving; commit when convenient. Also still open from the STOP package: the Downloads engineering ZIP and `KIP_REGISTRY.md` are absent (non-blocking).

**Next authorized action:** STOP. No Q2 execution, no tests, no live work, no Git mutation, no product change until the QA Lead's plan decision.

## 10. Package contents

| Path | What it is |
|---|---|
| `START_HERE.md` | Indexed entry: status, decisions requested, read order |
| `Q1_BOUND_READINESS_REPORT.md` | This report |
| `Q1_PROPOSED_TEST_PLAN.md` | Candidate-bound plan (§0 filled; T-01–T-24; O1–O10 preserved) |
| `checks/source52-recompute.json` | 52 per-file hashes (worktree/committed/expected) + combined identities |
| `checks/committed-vs-tested.json` | Tested vs committed vs worktree at candidate — 52 SAME |
| `checks/fixture-verification.json` | 2 archives + 34 reference files + 2 dependencies verified |
| `checks/readiness-checks.json` | Candidate, environment, worktree, harness notes |
| `governing/binding-instruction.md` | Tony's GO text verbatim + execution record |
| `governing/source-inventory.json` | Byte-identical copy of the verified 52-file inventory |
| `governing/fixture-manifest.json` | Byte-identical copy of the verified fixture manifest |
| `FILE_HASH_INVENTORY.json` | Every member of this package with SHA-256 and bytes |

ZIP: `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/WebFactory_QA_Q1_BOUND_2026-10-15_200820.zip` with a byte-identical copy at `/home/moose/Downloads/WebFactory_QA_Q1_BOUND_2026-10-15_200820.zip` — SHA-256 recorded in the RESPONSES report and RECOVERY.md (not inside the ZIP).