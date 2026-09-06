# Response — bim000: Is the acceptance spec ready for SOL?

**Short answer:** Yes. The spec is frozen and untouched at `agent_docs/ACTION/web-factory-p1-bim000/BIM000_ACCEPTANCE_SPEC.md`; every AC from 01 to 53 has evidence in one of the two reports. Four things SOL should know before grading.

1. **Stage 2 is committed at f124cb0** — but that commit captured the report under its old name (`..._bim000-stage2-prep.md`). The rename shows as `D` old + `??` new in the working tree, along with the RECOVERY/RUN_NOTES/session reference fixes and this file. One small follow-up commit makes the tree match what SOL reads.
2. **AC-41 will show 1 grep hit**, `CHANGELOG.md:11`, the line recording that `smart_discover.py` was deleted. Needs an accept-or-rule from SOL.
3. **AC-10 needs `PYTHONPATH=<repo>`** when run from `/tmp`, because the package is not installed; the output file lands in the repo's `outputs/` as required. Module resolution is outside bim000.
4. **AC-45 says four refs; three existed.** The fourth (`RECOVERY.md:5`) was already superseded before Stage 2. Seven occurrences repointed in total.

Also: `outputs/run_summary.json` and `outputs/pages/*.md` (AC-21, AC-51 evidence) are gitignored, so they exist on this VM only. SOL grading from a fresh clone would need to rerun the two-command smoke, about 90 seconds.

**Evidence map:** Stage 1 → `response_2026-09-05_123610_bim000-stage1-upgrade.md` (AC-01…07). Stage 2 → `response_2026-09-05_131346_bim000-stage2-complete.md` (AC-10…53). AC-54 is SOL's own line.
