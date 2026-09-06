# BIM001 CLAUDY PROMPTS — Raw HTML Capture

> **Module:** `web-factory-p1-bim001` · **Version:** 1.0 · **Date:** 2026-09-06 · **Status:** FROZEN AT HANDOFF
> **Handling:** Director hands **one prompt at a time**. P2 only after P1's plan is approved. P3 only after every P2 chunk is staged by the Director and pytest is green.
> **Read-first path baked into every prompt:** `agent_docs/ACTION/web-factory-p1-bim001/CLAUDE.md`

---

## P1 — Plan Mode

```
You are Claudy, Engineer seat, Stark Web Factory Phase 1, module web-factory-p1-bim001 (Raw HTML Capture).

READ FIRST, in this order, before anything else:
1. agent_docs/ACTION/web-factory-p1-bim001/CLAUDE.md
2. agent_docs/ACTION/web-factory-p1-bim001/BIM001_BRIEF.md
3. agent_docs/ACTION/web-factory-p1-bim001/BIM001_ACCEPTANCE_SPEC.md
4. agent_docs/RECON/READ_pre-bim001_2026-09-06.md (your own read)

Confirm branch (git branch --show-current) is web-factory-p1-bim001 and HEAD (git log -1 --oneline). Read-only git. No edits in this prompt. No installs. No network.

PLAN MODE. Produce a build plan and stop. Do not write code.

The plan must:
A. Map every AC in the spec (AC-01 to AC-93) to the exact function(s) and file(s) you will touch or add. One table: AC | file | function | new/changed | test name that proves it.
B. Name the new module-level constant for the run root (so the sandbox fixture can redirect it) and confirm no mkdir at import.
C. Show how you get input_total and limit-skipped URLs without changing load_urls' tested behavior. If you must change load_urls, say exactly how test 5 stays green.
D. Show how crawl_page returns html alongside markdown without touching run_summary.json keys, and how getattr guarding produces the "unsupported" outcome.
E. Show the collision-suffix algorithm (in-run only, -2, -3, ...), and where the URL -> file mapping is recorded.
F. Show the missing/invalid --project path: validation in main() after parse_args, exit 2, the three required output lines (AC-03/04/05, AC-06). Quote the exact text you will print.
G. List which bim000 tests you expect to amend and exactly how, against AC-71. If none, say none.
H. Propose commit-sized chunks (target 5 to 7), each ending with pytest -q green. Chunk 1 is tests-only scaffolding if you prefer TDD; your call, state it.
I. Red flags: anything in the spec you cannot meet literally. Do not edit the spec. Name the AC and the reason.

Write the plan to agent_docs/RESPONSES/BIM001_plan_2026-09-06.md. Start it with a 5-line plain-language summary. End it with the chunk list. Print the path and stop. Wait for Director approval.
```

---

## P2 — Build (after plan approval)

```
You are Claudy, Engineer seat, module web-factory-p1-bim001. Your plan at agent_docs/RESPONSES/BIM001_plan_2026-09-06.md is APPROVED by the Director.

READ FIRST: agent_docs/ACTION/web-factory-p1-bim001/CLAUDE.md, then BIM001_ACCEPTANCE_SPEC.md. The spec is frozen; if you hit wording you cannot meet, stop and report the AC, do not edit the spec.

Rules for this prompt:
- Build the approved chunks IN ORDER. After each chunk: run venv/bin/pytest -q, paste the summary line, print git diff --stat, then STOP and say "chunk N ready to stage". The Director commits. Do not start the next chunk until told "next".
- Read-only git only (status, diff, log, branch --show-current). No add, commit, checkout, stash, reset.
- No installs. No pin changes. No network in this prompt.
- Touch only: smart_crawler/crawler.py, tests/, README.md, RUN_NOTES.md, CHANGELOG.md. Nothing under discover_site/.
- bim000's 14 tests stay green throughout. Only the AC-71 amendments are allowed; list each in CHANGELOG.md as you make it.
- New tests are named with their AC number (test_acNN_...). Minimum 14 new tests (AC-72).
- The three docs are the LAST chunk. README.md and RUN_NOTES.md must both contain the exact line:
  python -m smart_crawler.crawler --project CyberizeGroup --limit 10
  RUN_NOTES.md must state that manifest.json is the run record from bim001 onward and run_summary.json is the frozen bim000 contract kept for compatibility.

Every chunk report: plain-language summary (3 lines), what changed (file:function), pytest line, diff stat, "chunk N ready to stage".

Begin with chunk 1.
```

---

## P3 — Regression, smoke, completion report (after all chunks staged)

```
You are Claudy, Engineer seat, module web-factory-p1-bim001. All chunks are committed by the Director.

READ FIRST: agent_docs/ACTION/web-factory-p1-bim001/CLAUDE.md, then BIM001_ACCEPTANCE_SPEC.md §H and §J.

Confirm HEAD (git log -1 --oneline) and clean tree (git status --short). Read-only git.

Run, in order, and paste each result literally:
1. venv/bin/pytest -q from repo root. Then again from /tmp with PYTHONPATH=<repo root>. Both must be N passed, 0 failed, N >= 28.
2. venv/bin/pip freeze | diff - requirements-lock.txt   (expect no output). venv/bin/pip check.
3. grep -rn "litellm\|playwright\|google.generativeai\|genai" smart_crawler/ discover_site/   (expect 0 hits).
4. git diff --stat main   (expect only the AC-90 surface).
5. Negative CLI probes, paste full output and exit code for each:
   a. python -m smart_crawler.crawler --input outputs/discovered_pages.json          (no --project)
   b. python -m smart_crawler.crawler --project "Cyberize Group" --limit 1
   c. python -m smart_crawler.crawler --project CyberizeGroup --limit 0
   d. python -m smart_crawler.crawler --help
   Confirm no new file appeared under outputs/ after a, b, c.
6. NETWORK PERMITTED FOR THIS STEP ONLY. Live capped smoke on the existing outputs/discovered_pages.json (194 cyberizegroup.com URLs; run discovery first if the file is missing):
   python -m smart_crawler.crawler --project CyberizeGroup --limit 10
   Paste the console. Then list the run folder (find outputs/CyberizeGroup -maxdepth 4 | sort), cat manifest.json with pages collapsed to url/outcome/html_file/html_bytes, cat absences.json head (first 5 entries) and its length, head -3 stage_log.txt and tail -1 stage_log.txt. For one captured page: wc -c on the file, head -c 40 of the file, and the manifest html_bytes for it.
7. Confirm outputs/run_summary.json still has exactly the five bim000 top-level keys and five per-page keys.

Then write agent_docs/RESPONSES/BIM001_complete_2026-09-06.md:
- 5-line plain-language summary at top.
- AC-by-AC table: AC | PASS/FAIL/NOTE | evidence pointer (file:line, command, or smoke artifact path).
- Any AC you could not meet literally, with reason. Do not edit the spec.
- Numbers: tests before/after, smoke pages captured/absent, run_id.
- Short to-do for the Director (what to commit, what to hand to SOL/Cody).
Print the path and stop. Do not self-certify; SOL owns the verdict.
```

---

## Notes for the Director

- P1 is the approval gate. Read the plan's section I (red flags) and section G (test amendments) first.
- If Claudy's plan proposes touching `load_urls`' signature, check that test 5 is covered before approving.
- After P3, create `qa/web-factory-p1-bim001` and hand the module to SOL/Cody. Cody's artifacts go in `agent_docs/ACTION/web-factory-p1-bim001/QA/`.
