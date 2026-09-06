# Response — web-factory-p1-bim000: Handoff understanding

**Status:** Awaiting Director's CP1 handoff
**Read (in order):** `agent_docs/ACTION/web-factory-p1-bim000/CLAUDE.md` → `BIM000_BRIEF.md` → `BIM000_ACCEPTANCE_SPEC.md` → `BIM000_CLAUDY_PROMPTS.md`. Module folder is frozen; not edited.

---

## My understanding

- **Goal:** make the scraper an honest, current base for bim001. Same job as run-002, nothing new captured.
- **Stage 1, CP1:** isolated crawl4ai upgrade. Only `requirements.txt` and `requirements-lock.txt` change. Gated by the 6 existing tests plus a 10-page Cyberize smoke with the old crawler code. Stop rule: if the baseline breaks or migration goes past config and argument renames, revert the two files, reinstall 0.6.3, write the finding, stop.
- **Stage 2, CP2:** the cleanup. Crawler gets `--input` and `--limit`; the manual trim dies. Status validation with `run_summary.json`; 403/429 named `blocked`; three consecutive blocks halt the run. Random 2–5 s pause between pages. Full Chrome UA on the crawler and a shared `requests.Session` UA on discovery. Truthful banner strings from package metadata. `smart_discover.py` retired. Root-anchored paths, no import-time mkdir. Hygiene, docs, CHANGELOG, the four stale path repoints, new offline tests.
- **Rules:** Plan Mode before each stage, git-zero, reports to `agent_docs/RESPONSES/` base, module folder frozen, do-not-touch list respected. Rulings already made stay closed (F1 fit_markdown deferred, no stealth, LiteLLM tolerated, GEMINI_API_KEY placeholder stays, RESPONSES/OLD is Director archive).

## Branch check (read-only)

Current branch: `web-factory-phase1-a` (Director-created). Local branches: `main`, `phase-c1-cleanup`, `repo-cleanup-1`, `web-factory-phase1-a`. 5 uncommitted paths (protocol files from 2026-09-04/05). Brief suggested `bim000-stage-prep` as a name; prompt says Director names it → taking `web-factory-phase1-a` as the working branch unless told otherwise.

## Note for Stage 1 planning

CP1 step 7 uses the manual trim one last time, and the pre-Stage-2 crawler cannot surface a soft 403/429 (crawl4ai Playwright strategy never fails a 4xx; `crawler.py` prints status only on failure). Proposal at plan time: reuse the run-002 scratchpad status observer for the CP1 smoke so AC-06 evidence carries real status codes. Director's call.

→ Waiting for CP1 handoff. Then: read-only research (steps 1–3), present plan, stop for approval.
