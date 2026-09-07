# STARK WEB FACTORY — PHASE 1 MAP
## Prove the Base — internal module plan

> **Version:** 0.2 · **Date:** 2026-09-05 · **Status:** RULINGS LOCKED · bim000 authored
> **Parent:** `STARK_WEB_FACTORY_9_PHASE_PLAN_v1.0.md` §5 (Phase 1 ACTIVE)
> **Handoff:** `STARK_WEB_FACTORY_PHASE_1_ARCHITECT_LAB_HANDOFF_v1_0.md`
> **Evidence:** `RECON_stark-web-factory-scrapper-v1_phase1-baseline_2026-09-04.md` · `RUN_ANALYSIS_baseline-run-002_2026-09-05.md`
> **Director:** Tony Stark · **Architect:** Fable · **Engineer:** Claudy · **QA:** SOL
> **Pattern source:** Cyber Pharma Phase 3 sub-plan (BIM-000 → BIM-005). Proven. Reused.

---

## 1. Why this doc exists

The 9-Phase Plan says what Phase 1 proves. It does not say how we walk it. This map does. One module at a time. Each opens, builds, tests, closes. Then the next.

**Loop per module:** Fable brief + acceptance spec + Claudy prompt → SOL review → Director approves → Claudy Plan Mode → Director approves → build → tests green → SOL verdict → FIX loop if needed → Director merges → module closed → next.

Module folders freeze at Engineer handoff (L1). Only the current module's packet is written. Each later module is authored when its turn comes, from fresh evidence.

---

## 2. Naming

`web-factory-p1-bim000`, `web-factory-p1-bim001`, and so on. Project · phase · module type + number.
BIM = brownfield Python build. FIX = `web-factory-p1-fix001`. Prototype/scout = `web-factory-p1-proto001`.

---

## 3. The map

| Module | Name | What it proves | Exit gate (plain) | Status |
|---|---|---|---|---|
| **bim000** | Stage Prep + Controlled Upgrade | The repo is clean, current, honest, and the two halves talk | Crawl4AI upgraded to a chosen stable pin as an isolated step, C1 baseline re-green. Discovery output feeds the crawler directly, no manual copy. Status codes validated; a block page cannot count as success. Randomized inter-page pause. Real browser identity. Lying banner/docstring text fixed. `smart_discover.py` retired. Paths root-anchored. Doc drift corrected. Tests green. | **AUTHORED — awaiting SOL review / Director approval** |
| **bim001** | Raw HTML Capture | Every page's rendered HTML is saved untouched | Per-page HTML as captured, plus status and timing. Run manifest (command, pins, timestamps, pacing) and stage log. Typed absences list for anything that did not arrive. | Seeded |
| **bim002** | REST + SEO Stream | Per-route SEO is captured as first-class data | WP REST payload per page, full Yoast (titles, metas, canonical, OG/Twitter, JSON-LD, robots). Site-level REST route inventory and sitemap. Thrive Architect pages with empty `content.rendered` proven present in the HTML stream. | Seeded |
| **bim003** | Media Evidence Inventory | Every image is listed with provenance | Inventory per Plan §4A Phase 1. Nothing filtered. Staging-domain fossils recorded, not fixed (run-002 found 83 of them). Director screenshots slot created. | Seeded |
| **proto001** | Crawl4AI + Gemini Scout | Whether AI-assisted extraction earns its cost | See §3A. Runs after bim003, beside bim004, never blocking it. Throwaway unless it beats the deterministic path on evidence. | Reserved |
| **bim004** | The Full Run | Raw Recon Package v0 exists and is reproducible | Director runs one command on a fresh venv, twice, on cyberizegroup.com, polite rung (a). Same package structure both times. No required page silently missing. Smoke tests green. SOL reviews against "evidence survives interpretation." | Seeded |

**Docs only, no module number:** Site Access Protocol v0 · Phase 1 retrospective · Phase 2 Architect Lab handoff.

---

## 3A. Reserved experiment — Crawl4AI + Gemini assisted extraction (Director note, 2026-09-05)

**Default architecture stays deterministic-first:** browser crawl for rendered visitor-visible truth · WordPress REST for structured CMS/SEO/metadata truth · deterministic extraction where it does the job.

**The question the scout answers:** does Crawl4AI's LLM-assisted extraction (Gemini, paid access already held) materially improve quality, structure, reuse, or semantic understanding of collected site data versus the deterministic pipeline?

**Candidate tests:** true main-content region on messy pages · page-type classification · separating content from menus, popups, sidebars, ads · extracting reusable semantic sections (hero, CTA, FAQ, testimonial, services, team) · structured schemas from inconsistent legacy sites · AI-derived extraction patterns that deterministic code then reuses.

**Rules:** not in bim000, not forced into bim001. Runs only after the acquisition base is stable (post-bim003). Output must be tested head-to-head against the non-AI path. Fails → thrown away with evidence. Succeeds → candidate reusable Stark acquisition capability beyond the Web Factory. `GEMINI_API_KEY` placeholder is preserved for this (R-D); it is not authorization to integrate Gemini earlier.

---

## 4. Rulings — LOCKED 2026-09-05

| # | Ruling | Effect |
|---|---|---|
| F1 | **DEFER** | Empty `fit_markdown` untouched unless bim000 needs markdown. It does not. |
| F2 | **CONTROLLED UPGRADE in bim000** | Crawl4AI upgraded as an isolated, pinned, regression-gated step. Rabbit hole → stop, bring finding back. |
| F3 | **FIX** | No manual copy/rename between discovery and crawler. |
| F4 | **FIX** | Runtime messages tell the truth. |
| R-A | **TOLERATE** | LiteLLM acceptable as a Crawl4AI transitive. Never imported by Stark code. Not an architecture choice. |
| R-B | **RETIRE** | `smart_discover.py` removed, after recon confirms nothing depends on it. |
| R-C | **CONVENTION / KEEP** | `agent_docs/RESPONSES/OLD/` is Director housekeeping. Old responses stay there. New responses land in `agent_docs/RESPONSES/`. |
| R-D | **KEEP** | `.env.example` with `GEMINI_API_KEY` stays. Reserved for proto001. |
| Run-002 | **ACCEPTED** | Status validation · randomized inter-page pause · real UA/headers · no stealth. All in bim000. |
| Start | **bim000** | Numbering starts at 000. |

---

## 5. What may still move this map

- Crawl4AI upgrade outcome (bim000) may change bim001's capture approach.
- Environment ruling (Zorin vs Ubuntu LTS) lands before bim004.
- Stealth rung (b) stays out unless polite rung (a) fails on a required page.
- proto001 timing may shift if bim001–003 run long.

---

## 6. Explicitly not in Phase 1

Intelligence or classification in the production pipeline · `fit_markdown` quality · Prepare tooling · multi-site generality · media runtime · Hermes · Workbench · any skill folder. (proto001 is an experiment, not pipeline.)

---

## 7. Version history

| Version | Date | Changes |
|---|---|---|
| 0.1-DRAFT | 2026-09-05 | Map sketched from recon. Nine open rulings listed. |
| 0.2 | 2026-09-05 | All rulings locked. F2 moved into bim000 as controlled upgrade. Run-002 additions accepted. R-C/R-D flipped to KEEP. proto001 (Crawl4AI + Gemini scout) reserved in §3A. bim000 authored. |

---

*Map, not packet. Authored cold-start.*
