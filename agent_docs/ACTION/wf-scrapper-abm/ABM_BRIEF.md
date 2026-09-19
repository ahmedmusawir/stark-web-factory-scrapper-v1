# wf-scrapper-abm — BRIEF
## Scrapper ABM: Capture (rest of it) + Prepare → Architect Data Pack

> **Module:** `wf-scrapper-abm` · **Type:** ABM (App Build Module, experiment CJ-008) · **Version:** 1.0 · **Date:** 2026-09-18
> **Branch:** `wf-scrapper-abm` (R1, exists, clean at `73f96db` = main) → `qa/wf-scrapper-abm` → main
> **Repo:** `~/python/stark-web-factory-scrapper-v1` on Zorin (R4)
> **Seats:** Director Tony · Architect Fable (this lab) · Engineer Claudy · QA Lead SOL · QA execution Cody · Reviewers Astra + fresh Fable · Method owner 10x Lab (handoff v0.2)
> **Parent docs:** `REFERENCES/00_START_HERE.md`, `REFERENCES/CAMPAIGN_MAP_10x_v0_2.md` · Phase map v0.4 records the absorption of bim002/003/004 + Phase 2 Prepare.

---

## 1. Goal

One tool, one invocation: website in → Raw Recon Package v2 (evidence, untouched) → Architect Data Pack v1 (derived, labeled, with provenance) that a chat Architect can read cold. Cyberize is the acceptance target. Nothing is interpreted in the raw layer; nothing is invented in the derived layer.

## 2. What exists (certified, bim000 + bim001)

Two-command flow, status validation, pacing, real identity, `--project`, per-run folders with HTML, manifest v1, absences, stage log. 54 tests. No REST, no media, no Prepare, no single invocation. Markdown output and `run_summary.json` still written (retired here, R8).

## 3. What this ABM adds

**Capture:** raw contract v2 (portable, hashed, redirect-aware) · hardened discovery (fallbacks, dedup, scope, robots recorded) · access policy (one retry, out-of-scope redirects typed, SIGINT-safe, byte budget) · WP REST stream with Yoast retained verbatim · media evidence inventory (metadata only) · Director screenshots slot · validator · single `recon_pipeline` invocation.
**Prepare:** pack skeleton with read-only raw guard · site map + content inventory + disagreements · SEO inventory preserved one-for-one · forms/embeds with honest status · observed design evidence · deterministic media classification · loss ledger + findings + entry brief + JSON/Markdown twins · reproducibility tool.
**Evidence:** fixture site + e2e test, hardening, docs, two full Cyberize runs, ledger, completion report.

## 4. How it runs (CJ-008)

Block 1 (this packet) → P0 task zero → P1 whole-campaign readback → **one** Director approval → Claudy runs C1…E2 continuously with engineering checks, auto-advancing at the CHK checkpoint → one candidate → SOL/Cody QA campaign on `qa/wf-scrapper-abm` (with the R5 cold-read before Gate Q) → Astra + fresh-Fable reviews → one RRM if findings are accepted → cleanup → closeout → merge. No per-task Director approvals; no per-stage QA.

## 5. Out of scope

Frontend/FFM · site generation or redesign · deployment · Workbench/Hermes · multi-site generality as a promise · LLM/Gemini extraction (proto001 stays reserved) · `fit_markdown` · stealth rung (b) · downloading media bytes · new dependencies.

## 6. Exit

All 48 ACs IMPLEMENTED with evidence (Engineer) → QA campaign verdict PASS (SOL) → cold-read judged (SOL) → reviews dispositioned (Tony) → RRM verified or no-repair ruled → QA Cleanup COMPLETE → closeout → Director merge. Deployment remains a separate decision.

## 7. Risks, plain

- Pressable changes posture mid-campaign → stop rule fires; report, don't force. Two full runs at ≈40 min each are the only expensive steps.
- Yoast payload shape differs from Contracts §2.5 → caught at P0/C4, fixed by erratum, not by guessing.
- Main-content heuristic and media class rules are the two places "deterministic" gets hard; both are labeled `inferred` with cited rules, never silent.
- One long engineering campaign means more resumes; `RECOVERY.md` discipline is the safety net (AC-045).
- The fresh-Fable reviewer is the same model as the Engineer; Astra is the different-model check. Stated, not hidden.
