# BIM001 — Handoff read — 2026-09-06

**Plain language:** I read the bim001 module folder in its prescribed order. bim001 adds raw HTML capture to the crawler: a required `--project` flag, a per-run folder under `outputs/<project>/runs/<run_id>/` holding `html/*.html`, `manifest.json`, `absences.json`, `stage_log.txt`. bim000's markdown output and `run_summary.json` stay byte-identical. Only `smart_crawler/crawler.py`, `tests/`, and the three docs may change. Nothing is pending from me until the Director hands P1 (Plan Mode).

**Read (in order):** `CLAUDE.md` → `BIM001_BRIEF.md` → `BIM001_ACCEPTANCE_SPEC.md` (AC-01…AC-93, grading rule J-16: literal Check wins) → `BIM001_CLAUDY_PROMPTS.md` (P1 plan / P2 build in chunks / P3 regression+smoke+report) → my `READ_pre-bim001_2026-09-06.md` → `BIM000_RETROSPECTIVE.md` §Carry into bim001. Folder frozen; not edited. Branch `web-factory-p1-bim001` @ 57a0f59.

**What I take as fixed (closed rulings):** R1 markdown KEEP · R2 manifest is truth, `run_summary.json` unchanged · R3-A explicit `--project`, validated in `main()`, no default, exit 2 with corrective usage · R4 `-2/-3` collision suffix, never overwrite · R5 timing untouched · F1 · R-A · R-D · no stealth · no Playwright code of ours.

**Things I already see that the P1 plan must answer (not answering them now):**
- AC-33/41/42 need `input_total` and limit-skipped URLs while test 5 pins `load_urls(path, limit)` behavior — mechanism to propose in P1.C.
- AC-26: stub results have no `html` → `getattr` guard → outcome `unsupported`.
- AC-27: HTML capture independent of markdown; `run_summary.json` `ok` keeps bim000 meaning.
- AC-71: only three permitted amendments to bim000 tests (sandbox redirects run root; `main()`-invoking test gains `--project`; stub gains optional `html`).
- AC-30/34: 23 manifest keys / 11 per-page keys, exact.
- AC-12: no mkdir at import; AC-13: empty input still creates the run folder.
- Reports go to `agent_docs/RESPONSES/BIM001_<stage>_<date>.md` (module convention, differs from the bim000 `response_<ts>_` pattern).

**Status:** waiting for P1. No edits, no installs, no network, no mutating git.
