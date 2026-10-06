# Checkpoint packaging — instruction driven

No validator/exporter is claimed to exist. Package using ordinary local file/ZIP tools and explicit inventory; preserve relative paths. Do not fabricate missing inputs or approvals. Use existing QA records, ledger and journal rather than new competing templates.

## Required in every package

- `START_HERE.md`: plain-English status, requested reviewer decision and owner, read order and next authorized action.
- Candidate identity: repo/branch/commit/dirty state, contract+errata revision/hashes, plan identity/hash and approval reference. Before Tony commits, label base HEAD and dirty changes, with candidate PENDING.
- Results **or readiness**, exact command/fixture/environment and expected versus actual evidence; gaps/untested items; live budget consumed/remaining and reuse decision.
- Inventory with relative paths, file hashes and explicit exclusions/missing files; readable governing inputs needed by a reviewer outside this repository. No dependence on chat.
- Reproduction instructions with prerequisites, scope/writes, expected outcomes, safety/stop policy and whether they have been run. Historical commands are labeled historical, not replay instructions.

Exclude .env/secrets/cookies/private headers, dependencies/caches and bulk raw captures. Include concise governing docs and supporting reports; reference preserved local raw evidence precisely and disclose when it is not portable in the ZIP. Do not edit cited historical evidence. Tony controls any cleanup/deletion.

## Owner and checkpoint contents

| Checkpoint | Producer → reviewer | Required content beyond common fields |
|---|---|---|
| Engineering completion | Cody → JARVIS/SOL | Changed files, all AC mappings, exact commands, runtime/config, fixtures, expected/actual checks, raw/pack evidence, known gaps, budget usage, reproduction; no self-issued QA PASS |
| Q1 | Executor → SOL | Independent candidate/readiness inspection, completed concrete master-plan bindings, per-T assertions/fixtures, proposed live-evidence reuse and one requested plan decision |
| Q2 findings | Executor → SOL | All results so far, failures/gaps, unaffected checks continued, defect reproductions and required adjudication |
| Repair/retest | Engineer then Executor → SOL/JARVIS | Explicit Architect repair scope, separate helper corrections, Tony commit chain, re-pin and impacted/regression evidence; one active writer |
| Cleanup | Executor → Tony then SOL | Retain/delete inventory and proposal; Tony action record; post-cleanup identity/reference checks; acceptance before final Gate Q |
| Gate Q | SOL → JARVIS | Exact certificate issued by Lead, candidate/plan/contract identity, coverage/limitations and accepted cleanup, retained certificate path/hash |
| Reviews/RRM/closeout | Reviewers/Engineer/Executor/JARVIS → designated owner then Tony | Independent review reports/dispositions, bounded RRM or no-repair ruling, impact retests and certificate disposition; JARVIS carries exact Lead certificate; Tony integration record |

Every future checkpoint starts NOT RUN/PENDING. Conditional paths not exercised remain UNTESTED. A document-only package cleanup never by itself mandates a full QA rerun.
