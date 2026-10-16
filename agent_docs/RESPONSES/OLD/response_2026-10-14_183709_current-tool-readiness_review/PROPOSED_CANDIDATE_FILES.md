# Proposed selective candidate files — Tony only

No staging or Git mutation was performed. Review the existing mixed dirty changes/hunks; keep unrelated work intact. These are a proposal, not a command or authorization to discard anything. All tested product/test source must match source52 after your commit; QA independently verifies the actual candidate SHA.

## Required changed/untracked source (already reviewed work, unchanged by Shot2)

- `agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py`
- `agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py`
- `recon_pipeline/decide.py`
- `tests/test_decide.py`

## Current operating documents and skill

- `CLAUDE.md`
- `README.md`
- `agent_docs/ACTION/wf-scrapper-abm/AGENTS.md`
- `agent_docs/ACTION/wf-scrapper-abm/CLAUDE.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_ACCEPTANCE_SPEC.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_CONTRACTS.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_BRIEF.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_BUILD_INSTRUCTIONS.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_LEDGER.md`
- `agent_docs/ACTION/wf-scrapper-abm/DECIDE.md`
- `agent_docs/ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md`
- `agent_docs/ACTION/wf-scrapper-abm/QA/README.md`
- `agent_docs/ACTION/wf-scrapper-abm/QA/MASTER_QA_TEST_PLAN.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/README.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/MANIFEST.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/STATE.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/EXECUTION_INSTRUCTIONS.md`
- `agent_docs/ACTION/wf-scrapper-abm/CURRENT_TOOL_SCOPE.md`
- `agent_docs/SKILLS/web-recon-prepare/SKILL.md`
- `agent_docs/SKILLS/web-recon-prepare/AGENTS.md`
- `agent_docs/SKILLS/web-recon-prepare/CLAUDE.md`

## Normal checkpoint records

- `RECOVERY.md`
- `CHANGELOG.md`
- `agent_docs/SESSIONS/session_2026-10-14.md`
- `agent_docs/ACTION/wf-scrapper-abm/ENGINEERING_LOG.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_CAMPAIGN_JOURNAL.md`

## Small factual handoff/proof artifacts

- `agent_docs/RESPONSES/response_2026-10-14_183709_current-tool-readiness.md`
- `agent_docs/RESPONSES/response_2026-10-14_183709_current-tool-readiness_review/source-inventory.json`
- `agent_docs/RESPONSES/response_2026-10-14_183709_current-tool-readiness_review/engineering-results.json`
- `agent_docs/RESPONSES/response_2026-10-14_183709_current-tool-readiness_review/fixture-manifest.json`
- `agent_docs/RESPONSES/response_2026-10-14_183709_current-tool-readiness_review/restore-fixtures.py`
- `agent_docs/RESPONSES/response_2026-10-14_183709_current-tool-readiness_review/FIXTURE_ACCESS.md`
- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness/2026-10-14_123709Z/combined/command.json`
- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness/2026-10-14_123709Z/combined/result.json`
- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness/2026-10-14_123709Z/combined/junit.xml`
- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness/2026-10-14_123709Z/combined/pytest.log`
- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness/2026-10-14_123709Z/fixture-checks.json`
- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness/2026-10-14_123709Z/offline-content-checks.json`
- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness/2026-10-14_123709Z/acceptance-crosswalk.json`

## Preserve separately; do not bulk stage

- `agent_docs/RESPONSES/response_2026-10-11_210309_prepare-v01.zip` — immutable QA fixture archive, included in this review ZIP.
- `agent_docs/RESPONSES/response_2026-10-13_223736_growth-call-follow-up.zip` — immutable QA fixture archive, included in this review ZIP.

Keep bulk raw/prepared/recon outputs, caches/dependencies and unrelated historical work outside the candidate commit. Keep referenced fixture archives/evidence retained and supplied to QA; their hashes/restoration instructions are part of the handoff. Tony decides final staging, commit and QA branch.
