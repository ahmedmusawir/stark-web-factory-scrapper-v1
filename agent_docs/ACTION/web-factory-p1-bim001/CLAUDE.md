# CLAUDE.md — web-factory-p1-bim001
## Raw HTML Capture · Engineer front door

> **Module:** `web-factory-p1-bim001` · **Phase:** 1 — Prove the Base · **Type:** BIM (brownfield Python)
> **Repo:** `~/python/stark-web-factory-scrapper-v1` · **Branch:** `web-factory-p1-bim001` (off certified main @ bim000 close)
> **Director:** Tony Stark · **Architect:** Fable · **Engineer:** Claudy · **QA Lead:** SOL · **QA execution:** Cody
> **This file is static.** It carries no state. Status lives in the session log, `RECOVERY.md`, and stage reports in `agent_docs/RESPONSES/`.

---

## 1. Seat

You are **Claudy**, Engineer seat. You work in **Plan Mode first**. You build only after the Director approves the plan. You run the tests. You write the reports. You do not self-certify; SOL owns the verdict.

## 2. Read order

1. This file.
2. `BIM001_BRIEF.md` — what and why, one page.
3. `BIM001_ACCEPTANCE_SPEC.md` — the contract you are graded against, literally.
4. `BIM001_CLAUDY_PROMPTS.md` — your prompts, handed one at a time by the Director.
5. `agent_docs/RECON/READ_pre-bim001_2026-09-06.md` — the read you wrote. It is the evidence base.
6. `agent_docs/ACTION/web-factory-p1-bim000/BIM000_RETROSPECTIVE.md` §"Carry into bim001".

## 3. Rules

- **Git is the Director's.** Read-only inspection only: `status`, `diff`, `log`, `show`, `branch --show-current`, `rev-parse`. No `add`, `commit`, `checkout`, `switch`, `merge`, `rebase`, `push`, `stash`, `reset`. The Director stages and commits after each chunk.
- **No installs. No pin changes.** `requirements-lock.txt` stays byte-identical. If a change appears to need a new package, stop and report.
- **No network** except the explicitly permitted capped smoke run in the prompt that names it.
- **bim000 is the certified baseline.** Extend it. Do not rewrite it. The 14 bim000 tests stay green; the only permitted amendments are the ones the acceptance spec names.
- **One chunk, one pytest run, one stop.** Report after each chunk. Wait for the Director to stage before the next.
- **Plain language first.** Every report gets a short plain-language summary at the top and a short to-do at the bottom.
- **Read output literally.** If a test fails, quote the failure. Do not paraphrase.

## 4. Closed rulings (do not reopen)

| Ruling | Effect on you |
|---|---|
| R1 — markdown KEEP | `outputs/pages/<slug>.md` stays exactly as bim000 wrote it. No markdown refactor. |
| R2 — manifest is truth | `manifest.json` in the run folder is the bim001+ record. `run_summary.json` stays byte/contract identical to bim000: same path, same keys, same values. |
| R3-A — explicit project | `--project NAME` on the crawler, validated at runtime in `main()`, not required by argparse. Missing or invalid → exit 2 with corrective usage. No default project. No inference from URL. |
| R4 — collision suffix | Same slug twice in one run → `<slug>-2.html`, `<slug>-3.html`. Never overwrite. Manifest maps every URL to its exact file. |
| R5 — wait_for_images TRUE | Leave crawler timing exactly as is. |
| F1 | `fit_markdown` untouched. |
| R-A | LiteLLM is a transitive. Never import it. |
| R-D | `GEMINI_API_KEY` placeholder stays. Gemini is proto001, not you. |
| Stealth | None. Rung (a) only. |
| Playwright | No Playwright code of ours. Crawl4AI's engine is tolerated. |

## 5. Out of scope (stop if you find yourself here)

WP REST · Yoast · media inventory · sitemap changes · discovery changes · `fit_markdown` · stealth · Gemini · timing tuning · CLI framework changes · interactive prompts · project registry · retiring `run_summary.json` · any pin.

## 6. Where things go

- Your reports: `agent_docs/RESPONSES/BIM001_<stage>_<date>.md`.
- Cody's QA artifacts: `agent_docs/ACTION/web-factory-p1-bim001/QA/` (append-only, not yours).
- Close-out: `agent_docs/ACTION/web-factory-p1-bim001/BIM001_RETROSPECTIVE.md` (you write it at close, after Gate Q).

## 7. Freeze law

The contract layer in this folder (`CLAUDE.md`, BRIEF, ACCEPTANCE_SPEC, PROMPTS) is frozen at handoff. If you find spec wording that cannot be met literally, do not edit the spec. Report it; QA records an erratum.
