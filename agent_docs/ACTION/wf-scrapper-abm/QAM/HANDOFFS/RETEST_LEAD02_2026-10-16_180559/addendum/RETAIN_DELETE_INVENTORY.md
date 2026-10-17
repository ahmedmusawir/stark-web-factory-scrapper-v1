# Proposed retain/delete inventory (Tony decides; nothing deleted by QA)

## RETAIN — durable records
| Item | Why |
|---|---|
| Lane `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/RETEST_LEAD02_2026-10-16_180559/` incl. `addendum/` and both exports ZIPs | the LEAD-02 retest + LEAD-03 addendum evidence record |
| `/home/moose/Downloads/WebFactory_LEAD02_QA_Retest_2026-10-16_183150.zip` (sha `b734010a…fab9d0`) | delivered retest package, referenced by LEAD-03 |
| `/home/moose/Downloads/WebFactory_LEAD03_Evidence_Addendum_<ts>.zip` | this addendum |
| `/home/moose/Downloads/WebFactory_LEAD02_Engineering_Rework_2026-10-16_173633.zip`, `WebFactory_QA_Q2_Package_2026-10-16_155121.zip` | historical packages bound into LEAD-02/03 |
| Repo lanes `Q2_2026-10-16_142632/`, `ENGINEERING_REWORK_LEAD02_2026-10-16_172752/`, RESPONSES records, session logs, RECOVERY, CHANGELOG | committed/record history |

## DISPOSABLE after Lead review and Tony's acceptance (delete candidates)
| Item | Size | Note |
|---|---|---|
| `/tmp/claudy-lead02-retest-20261016/` | ~24 MB | retest scratch: repaired snapshot (incl. qa-c1/c3 collections now EXPORTED to the addendum), c2 run trees, a3 clone, stages. All measurement specimens needed by the record are in the lane/addendum ZIPs. |
| `/tmp/opencode/q2-scratch-20261016/` | ~29 MB | Q2 scratch, retained through LEAD-02 §6; completion items now closed |
| `/tmp/cody-lead02-2026-10-16_172752/` | ~3 MB | engineering scratch, reproducible from the engineering lane |

Deleting the retest scratch removes the live snapshot named in LEAD-03; the addendum preserves every artifact that decision asked for. If the Lead prefers the raw snapshot kept until Gate Q, retain `/tmp/claudy-lead02-retest-20261016/` and delete only the two older scratches.
