# QA LEAD APPROVAL — Web Factory current-tool Q1

Date: 2026-10-15 (Asia/Dhaka). Seat: JARVIS, QA Lead. Director: Tony.

**DECISION: APPROVED — THE SUPPLIED EXACT AMENDED PLAN.**
**EXECUTION STATUS: Q2 STOPPED / AWAITING TONY'S EXPLICIT RELEASE.**

The original proposal is accepted with the exact amendments recorded in `03_EXACT_AMENDMENTS.md`. Those amendments are already applied in the final file below. This approval binds that final file, not an unspecified future revision or the original proposal.

| Approval field | Bound identity |
|---|---|
| Final plan file | `01_QAM_TEST_PLAN_FINAL.md` |
| Final plan SHA-256 | `4cf1673851f5a170391af4e3e3fa418069732108ff1828e9fead6e062b52da2f` |
| Final plan bytes | 42580 |
| Product candidate | `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4` |
| QA branch | `qa/wf-scrapper-abm` |
| Source52 | `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` |
| Current scope SHA-256 | `639070b6b7f297104678da307b95ba39ddc8176797fcd8dafbb22f9b0dc1c87c` |
| Governing source index SHA-256 | `8d5ff7249e6431f8d49c64145b989d779a3ef9ed4489faaf553240c9f7a5522d` |
| Reviewed input ZIP SHA-256 | `c92275bcdbec5b3833df8d382e531a93c3c767e13450abf6b00948d350f35886` |
| Original proposal SHA-256 | `fc2cfdcc3170008689ad87001f4519d1ccf899c2486071fe3d147f2f04855826` |
| Independent QA Executor | Opy (OpenCode, GLM 5.3), succeeding Claudy; Cody remains Engineer |
| Approved target | Local candidate snapshot, controlled loopback server and hashed saved fixtures only |
| Environment | Existing Python 3.12.3 venv and pinned recorded packages; no installs/upgrades; browser version must be recorded at Q2 entry |
| External network budget | Zero requests; no live-site access or Git network operations |
| Director Q2 release | NOT GIVEN BY THIS LETTER; pending Tony |
| Product/Gate Q verdict | NOT ISSUED |

## Approved scope and adjudications

Approve the final plan's T-01–T-24 current-scope bindings, O1–O10 dispositions, reference-only engineering evidence reuse, fresh independent required regression/content measurements, declared QA evidence/scratch lanes, instrument controls and limited continuous execution rules. The Growth Call fixture hash correction is an erratum to prose, not a changed fixture or a product repair.

For this review, the exported package's ten indexed payload hashes and sizes were checked, and the three recorded source52 maps independently recomputed. Candidate/fixture assertions from the remote checkout remain attributed to Opy's exported evidence until entry rechecks; this letter does not pretend the Lead executed tests or inspected that checkout. No test, cold-read, cleanup or live validation is recorded as passed here.

The supplied current-scope crosswalk is the grading scope approved here. Original ABM literal contracts/errata were not in the review inputs: their history is preserved, local hashes/conflict checks are required, and this approval cannot certify or waive all historical ACs. The supplied QAM playbook's actual hash is pinned in the plan; it is not assumed identical to the earlier template letter's abbreviated different hash. Unseen SR-1…SR-11 text is not reconstructed or certified installed.

O5 meaningful content and O6 generic titles are tested against current requirements. If independently reproduced as acceptance failures, report them; no preaccepted product waiver or fix is granted. Historical controller findings stay OPEN outside this current run. Clean-install reproducibility, current live access and the stated coverage gaps remain unverified; final verdicts must reflect them.

## Conditions before execution

1. Install the supplied final plan and approval byte-for-byte in the existing QAM/HANDOFFS review lane; preserve input exports. Record their actual paths, hashes, amendment record and independent Executor identity in existing QA-owned state. This exact document-installation work is the only next activity approved now.
2. Supply a brief installation receipt: actual branch/full HEAD, product candidate, final plan hash/bytes, approval and scope hashes, complete changed-path classification, governing/reference path resolution, and the exact pending release state. Do not run tests to produce the receipt.
3. Tony commits required planning/approval records using the established Git policy. If HEAD becomes a successor, prove candidate ancestry and the complete diff as required by plan §1; product/config/dependency/test changes or material contract changes require a new Lead decision. Keep tested product SHA, execution HEAD and later evidence commits distinct.
4. Tony explicitly releases Q2 against this final plan identity and the recorded execution HEAD. Prior Q1 GO is not Q2 release. Until then, STOP with Q2 NOT RUN.
5. At released Q2 entry, execute the plan's actual identity, governing-instruction, environment, fixture, import and instrument checks. Any material discrepancy follows its STOP and owner rule. Expected documentation-only installation with identical plan bytes requires no second Lead planning round.

No Git mutation, product repair, dependency install, live collection, destructive cleanup, certification, deployment or new Factory-wide adoption is authorized by this letter. Retain the module-specific cleanup and repair ownership/sequence stated in the final plan.

Issued by JARVIS, QA Lead, after reviewing the supplied Q1 package and current-scope sources.
