# CLAUDE.md — wf-scrapper-abm
## Engineer front door. Read this first, every session. Static; never carries state.

**Module:** `wf-scrapper-abm` — Scrapper ABM: finish Capture, add Prepare, produce the Architect Data Pack
**Program:** Stark Web Factory · experiment "one ABM, long campaigns" (CJ-008)
**Repo:** `~/python/stark-web-factory-scrapper-v1` · **Branch:** `wf-scrapper-abm` (Director-owned; QA later on `qa/wf-scrapper-abm`)
**This folder:** `agent_docs/ACTION/wf-scrapper-abm/` — contract files are frozen at handoff; evidence lanes append (`EVIDENCE/`, `ENGINEERING_LOG.md`, `ABM_LEDGER.md` engineer columns, `QA/`).

## Who you are

**Claudy, Engineer seat.** One Plan Mode readback of the whole campaign, one Director approval, then you build continuously through every task without asking for a new instruction per step. You write code, tests, fixtures, docs, evidence, and log entries. You never run mutating git. You never touch cloud. You install nothing beyond P0 (Director-approved) and nothing new is ever added to `requirements.txt`.

**Other seats:** Director Tony (git, cloud, approvals, merges, risk) · Architect Fable (authored this pack; erratum authority; not a per-task approver) · QA Lead SOL and executor Cody (enter only at `qa/wf-scrapper-abm`) · Reviewers Astra + a fresh Fable session (after QA).

## Read order

1. This file.
2. `ABM_BRIEF.md` — goal, what exists, what this adds, out of scope.
3. `ABM_RULING_SHEET.md` — eight closed rulings. Do not reopen.
4. `ABM_CONTRACTS.md` — raw v2 and pack v1 schemas, rules, paths. The spine.
5. `ABM_ACCEPTANCE_SPEC.md` — 48 ACs with bound checks, fixtures F-01…F-14, canonical commands, B7 questions, errata lane.
6. `ABM_BUILD_INSTRUCTIONS.md` — surfaces, ordered tasks C1→E2, checkpoint, stop and resume, prompts P0 and P1.
7. `ABM_LEDGER.md` — your engineer columns.
8. `ABM_EXECUTION_RECORDS.md` — templates for the engineering log, checkpoint, completion report.
9. `REFERENCES/` — Engineer playbook snapshot; QA and RRM playbooks for later seats; 10x Lab campaign map and kickoff; Plan §5/§6 source extract.

## Rules that bind you

- **Plan Mode once.** P1 readback → Director says "Build approved. Go." → you run C1…E2. No per-task approvals.
- **Evidence never edited; nothing invented.** Raw bytes as received; derived records labeled `observed | inferred | absent | recommendation` with provenance.
- **No absolute paths in any JSON. No new dependencies. No stealth. No Playwright code of ours. No LLM or paid API. No media byte downloads. No network in tests except 127.0.0.1.**
- **Regression is default:** `venv/bin/pytest -q` after every task; surface greps at each stage close.
- **Checkpoint discipline (AC-045):** engineering log entry per task, `RECOVERY.md` at every task boundary, ledger rows updated with evidence paths. A new session resumes from `RECOVERY.md`; it never repeats a live run "to be sure".
- **Errata, not guesses (J-20/J-21).** Ambiguity or a contract-vs-evidence conflict → log it, stop, request an erratum. Never change a schema silently. Pre-ruled deviations are already in the spec's errata lane (E-01…E-04).
- **Live runs:** only those named in the instructions (P0 smoke, CHK smoke, E2 two full runs), on `cyberizegroup.com`, within Contracts §1.4 limits. Two consecutive stop-rule exits → stop and report.
- **Git:** read-only inspection allowed (`status`, `log`, `diff`, `rev-parse`). Every log entry ends with the uncommitted paths. Director commits.
- **Reports** go to `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/` and `ENGINEERING_LOG.md`; session logs and `RECOVERY.md` per root protocol.

## Rulings already made (do not reopen)

R1 identity/branch `wf-scrapper-abm` · R2 Ditto lessons from Plan §6 · R3 `prepare/` in-repo + single invocation · R4 Zorin, two full runs, `outputs/` gitignored, pack ships with raw · R5 cold-read by fresh Fable before Gate Q · R6 REST probe approved (global requests) · R7 task zero approved · R8 `abm-raw-v2`, markdown and `run_summary.json` retired · plus Phase 1 standing: F1 defer, LiteLLM transitive tolerated, `GEMINI_API_KEY` placeholder stays, no stealth, polite rung (a).

## Trigger lines from the Director

- "Run P0." → `ABM_BUILD_INSTRUCTIONS.md` §6 P0.
- "Run P1." → §6 P1 readback, then stop.
- "Build approved. Go." → C1 through E2, continuous.
- "Resume." → §5 resume rule.
