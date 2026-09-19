# Web Recon ABM — Execution Record Templates

Version: 0.2 | 2026-09-17

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

State the implemented scope, exact candidate SHA, changed-file summary, per-AC implementation claims, commands/results, end-to-end pack paths, raw-to-derived checks, known gaps, approved errata, how to run the tool, and where QA begins. Include evidence, not only a statement that tests passed. Tony commits the candidate before QA pins it.

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
- Architect closeout instruction and Claudy completion:
- Director merge/push identity when performed:
- Product run instructions and approved known limitations:
- Experiment duration/interventions/lessons:

Deployment remains a separate future decision.
