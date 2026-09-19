# wf-scrapper-abm — Campaign Journal

Version: 1.0 | 2026-09-18 | Canonical owner: project Architect (Fable). Entries CJ-007…CJ-011 carried verbatim from the 10x Lab handoff v0.2.
Current state: Block 1 packaged; P0 and P1 pending; build not started.

Append events and source references. Preserve old entries; supersede with a new ruling. The Engineer maintains detailed execution records; Cody maintains QA evidence; this journal links them and records decisions and outcomes. The existing project Doctrine Journal remains separate, with supported lessons promoted by its Architect owner.

## CJ-007 — Scope settled by Director

Date: 2026-09-17 | Source: Tony's latest instruction | Status: DIRECTED

One ABM must cover Web Recon AND its data processing through the Architect-ready Data Pack. Prepare is required. The nine-phase manual Factory journey is irrelevant to this build scope. No deployment. This supersedes the Phase-1-only pilot and the A1/A2 choice in CJ-002/CJ-003 of the earlier ABM Campaign Journal.

## CJ-008 — Long campaigns replace routine handoffs

Date: 2026-09-17 | Source: Tony's latest instruction | Status: DIRECTED

Bundle the existing Factory method into a few long steps: one engineering campaign, one broad independent QA campaign with repair/retest, reviews, then consolidated review rework. Capture and Prepare are internal build stages; engineer checks govern auto-advance. Routine independent QA between BIMs/stages is omitted for this experiment. Genuine unresolved scope/contract/authority issues still need a ruling.

## CJ-009 — Reviewers and repair module corrected

Date: 2026-09-17 | Source: Tony + RRM_PLAYBOOK.md v0.1 | Status: DIRECTED

Reviewers are Astra and Fable. RRM means Review Rework Module. These replace Astra/GLM and RBM in earlier ABM drafts for this engagement. Read the existing RRM playbook and reviewer pilot guidance; use their disposition, evidence, repair, independent QA, cleanup, and closeout rules. One consolidated RRM covers accepted findings; create no empty repair module when none are accepted.

Fable review uses a fresh session and declares prior architectural/engineering involvement. Astra supplies a different-model review. Both review the same frozen candidate and remain unaware of each other's new report until both complete.

## CJ-010 — Lab boundary preserved

Date: 2026-09-17 | Source: Tony's prior explicit lab boundary, carried forward | Status: CONFIRMED

10x Lab writes method and handoff material. The existing project Architect performs/directs recon and authors the actual executable ABM. Tony takes one package to that lab. No separate Architect project or recon run has been started here.

## CJ-011 — Handoff contents delivered

Date: 2026-09-17 | Type: artifact record | Status: PREPARED

Created a consolidated scope/kickoff document, five-block Campaign Map, master acceptance baseline (48 ACs), master QA design (24 groups covering all ACs), this journal, execution templates, and governing reference snapshots. Repo bindings and QA commands remain honestly UNBOUND. The package replaces the earlier seven drafts as the current handoff entry point for this experiment.

The exact Ditto extraction reports were not among the local inputs used to author this package. The scoped product plan records the required donor lessons; the existing Architect must reconcile those against the reports already held in the project. No new Ditto extraction claims are asserted here.

## CJ-012 — Pre-ABM recon landed

Date: 2026-09-18 | Author: Claudy (Engineer), read-only | Status: RECORDED

`agent_docs/RECON/READ_pre-abm_2026-09-18.md`. Checkout is a fresh clone: no venv, no run folders, no real manifest on disk (bim001 live evidence was never tracked). Certified: bim000 `81099ee`, bim001 `eee039a`/pkg `7517049`, main = `73f96db`, linear history, no tags. 54 tests (static count). Manifest v1 = 23 keys / 11 per page; absolute paths in `input_path`/`command`; markdown outside run folder; no dedup or host filter in sitemap discovery; no REST, media, screenshots, or Prepare code. Part B probe not run (awaited approval).

## CJ-013 — Director rulings R1–R8 (consolidated)

Date: 2026-09-18 | Source: Tony | Status: DIRECTED

See `ABM_RULING_SHEET.md`. Headline: identity `wf-scrapper-abm`, existing branch kept; Ditto lessons bound from Plan §6; Prepare in-repo with single invocation; Zorin, two full Cyberize runs, pack ships with raw; fresh-Fable cold-read before Gate Q; REST probe approved; task zero approved (venv, regression, smoke); `abm-raw-v2` with markdown and `run_summary.json` retired.

## CJ-014 — Block 1 packet authored

Date: 2026-09-18 | Author: Fable (Architect) | Status: AUTHORED, awaiting P0 → P1 → Director build approval

Pack `wf-scrapper-abm/`: CLAUDE.md, ABM_BRIEF, ABM_RULING_SHEET, ABM_CONTRACTS (raw v2, pack v1), ABM_ACCEPTANCE_SPEC (48 ACs bound; fixtures F-01…F-14; commands; B7; errata E-01…E-04 pre-ruled per J-21), ABM_BUILD_INSTRUCTIONS (surfaces; C1–C6, CHK, P1–P6, E1–E2; stop/resume; P0, P1 prompts), ABM_LEDGER (48 rows), ABM_EXECUTION_RECORDS, this journal, QA/ (10x master QA plan for SOL), REFERENCES/. Bindings B1–B8 status: B1 bound (CJ-012) · B2 bound (spec §0.2) · B3 bound; REST field names confirmed at P0 part D · B4 bound (F-01…F-14) · B5 bound (Contracts §1.4, estimates per R4) · B6 bound (Contracts §3, rules files named) · B7 bound (spec §B7; owner per R5) · B8 bound (instructions §1). **Not build-ready until P0 report lands and P1 readback is approved.**

## Next campaign entry

- Date / entry ID / author and seat:
- Event and block/task/AC/finding IDs:
- Evidence or source:
- Decision and approving owner (or OPEN):
- Implementation/evidence/merge SHA where applicable:
- What changed in the map/spec/plan (errata if frozen):
- Next step and owner:

## Speed record — fill from actual runs

| Measure | Actual |
|---|---|
| Architect/recon preparation time | NOT MEASURED |
| Engineering elapsed time and active sessions | NOT STARTED |
| QA elapsed time and sessions | NOT STARTED |
| Review and RRM time | NOT STARTED |
| Director interventions and reasons | NOT MEASURED |
| Defects found by QA / reviews; repair rounds | NO EXECUTION DATA |
| Resumptions/context interruptions | NO EXECUTION DATA |
| Measured provider usage, if available | NOT MEASURED |

Close with what actually reduced handoffs, which checks caught defects, and what to reuse for the Next.js ADK experiment. No promise of duration or first-pass perfection is implied.
