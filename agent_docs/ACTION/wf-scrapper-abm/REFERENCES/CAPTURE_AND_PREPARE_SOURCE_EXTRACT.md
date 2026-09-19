# Scoped product-plan extract: Capture and Prepare

Source: STARK_WEB_FACTORY_9_PHASE_PLAN_v1.0.md (2026-09-04), sections 5 and 6, verbatim below. Historical baseline versions are not current repo facts. The Director has compressed execution into one ABM; the source text is retained for product requirements. The wider program is not campaign scope.

## 5. PHASE 1 — Prove the Base

### Goal
Prove that the cleaned Stark Web Recon base actually works on real client hosting, and let a real run define what a Raw Recon Package is.

### Why This Phase Exists
The repo was cleaned, not proven. One discovery run and six smoke tests are not a product. Ditto died at Pressable's wall; our defensible claim is "ours works on real client hosting." That claim must be earned before anything is built on top.

### Starting Inputs
C1-baseline repo · four open C1 findings · Pressable wall map from Run 001 (403 on headless, 429 on bursts, calm HTTP 200, REST open) · Director rulings: pyenv+venv+pip, no Playwright, Ubuntu LTS for automation, polite ladder.

### Scope
- Disposition the four C1 findings (fix, defer, or accept) before new work.
- Crawl4AI 0.7 upgrade decision and, if taken, re-green the smoke tests.
- First real collection on cyberizegroup.com through the polite ladder: sitemap + paced rendered crawl + WP REST, no headless fingerprint.
- Let the run define the **Raw Recon Package v0**: per-page rendered capture, REST payload (full Yoast/SEO), media evidence inventory with provenance (§4A Phase 1), Director-supplied screenshots slot, run manifest and stage log, typed absences for anything blocked or skipped.
- Prove the Thrive Architect finding: pages whose REST `content.rendered` is empty are captured by the rendered stream.
- Draft **Site Access Protocol v0** from the Pressable experience.
- Fix the discovery-to-crawler handoff contract; the two halves must speak one format.

### Key Deliverables
`STARK_WEB_RECON` repo at a tagged Phase-1 state · `RAW_RECON_PACKAGE` v0 for cyberizegroup.com (name tentative) · `SITE_ACCESS_PROTOCOL` v0 (tentative) · Phase 1 retrospective.

### Validation / Exit Gate
The Director runs one command on a fresh venv and gets a Raw Recon Package for cyberizegroup.com. Same command run twice yields the same package structure. Package contains the SEO payload per page, the rendered HTML per page, the media evidence inventory, a stage log, and a typed absences list. Required Cyberize collection completes through the approved polite access path; blocked or unsupported evidence is typed and surfaced; no required page is silently missing. Smoke tests green. SOL reviews the package against the "evidence survives interpretation" bar.

### Dependencies
Phase 2 needs a real, stable Raw Package to derive from. Nothing about its format is guessed before this gate.

### Explicitly Deferred
Any intelligence or classification · content-quality fixes to `fit_markdown` beyond what the run needs · stealth/full-profile browser (ladder rung b) unless the polite rung fails · multi-site generality · Hermes.

### Lessons That May Amend Later Phases
Whether the polite rung suffices on Pressable decides how much of the ladder the Site Access Protocol must operationalize. What the run cannot capture defines Phase 2's absence taxonomy. Whether REST alone is ever sufficient decides Prepare's stream-reconciliation rules.

---

## 6. PHASE 2 — Web Recon Prepare

### Goal
Turn the Raw Recon Package into an Architect Data Pack that an Architect can read cold, without touching the raw package or the live site.

### Why This Phase Exists
This is Tony's "skill 1 runs the tool, skill 2 builds the data pack." It is where the Angle A lessons pay out. Raw evidence is untouched; derived intelligence lives beside it with its uncertainty attached.

### Starting Inputs
Phase 1 Raw Package · Angle A patterns (loss ledger, typed absences, authored-plus-computed evidence, confidence separate from action, dual twins) · Angle B lesson: embed inventory with function status; per-route SEO as contract.

### Scope
- Define the **Architect Data Pack** contract from what the Architect actually needs to write a Site Brief (Phase 3 co-designs; Phase 2 ships).
- Derive: site map and IA as-is · content inventory per page with authored-vs-rendered disagreement recorded · **per-route SEO payload preserved, not synthesized** · **embed and form inventory with function status** (third-party, iframe, form handler, script-driven) · descriptive design evidence (palette, type, spacing, section vocabulary) marked as *observed, not prescribed* · **classified media evidence** per §4A Phase 2 (evidence inventory, not production inventory; apparently-unused is a class, not a deletion) · loss ledger and typed absences.
- JSON + Markdown twins only where both a machine contract and a human/agent narrative are needed (recon summary, SEO summary, findings/absence report); generate both from one source object where practical. A raw asset list does not need a prose twin.
- Author `SITE_RECON_BRIEF` (tentative name) as the human-readable entry point.
- Preserve lineage: page identity and source references survive every derivation.

### Key Deliverables
`ARCHITECT_DATA_PACK` v0 for Cyberize (tentative; file names inside TBD by Architect and SOL) · `SITE_RECON_BRIEF` v0 · Prepare tooling in the Web Recon repo, or a sibling, per packet decision · retrospective.

### Validation / Exit Gate
**Cold-read test.** Fable, with the Data Pack as primary intake, drafts the skeleton of a Site Brief and lists every question the pack could not answer without drilling into raw evidence. SOL checks that no derived artifact overwrote or mutated raw evidence, that every absence is typed, and that per-route SEO in the pack matches the raw REST payload one-for-one. Director approves the pack format as the Recon-to-Architect contract.

### Dependencies
Phase 3 consumes the Data Pack as its primary intake surface; raw Recon evidence remains available for targeted drill-down when the Brief exposes uncertainty or contradiction. No derivation becomes an irreversible bottleneck. Phase 6 QA uses the SEO payload as its parity baseline. Phase 4 Designer consumes the descriptive design evidence.

### Explicitly Deferred
Confidence-scored classification of sections (record what is observed; do not act on it) · breakpoint discovery machinery · any codegen · Hermes in this seat (candidate #1, decided in Phase 9).

### Lessons That May Amend Later Phases
The questions the cold-read cannot answer become Phase 1 evolution items or Phase 3 questionnaire items. If the Designer needs evidence the pack does not carry, the pack contract grows here, not in the Designer's hands.

---

