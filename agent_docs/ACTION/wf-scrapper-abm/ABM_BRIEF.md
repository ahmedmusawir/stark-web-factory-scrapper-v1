# Web Recon ABM — launch packet 1.2

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.


**Goal:** Capture → Raw Recon Package → Prepare → Architect Data Pack.

JARVIS Architect amendment under Tony’s delegated authority. Documentation/read-only pass, 2026-10-02. JARVIS approved M-01–M-04 and authorized BUILD_READBACK, now delivered; C1 remains unauthorized. Current state: AWAITING BUILD_READBACK REVIEW AND TONY'S BUILD APPROVAL. See [Rulings 1.2](ABM_RULINGS_1_2.md), [BUILD_READBACK](BUILD_READBACK.md) and retained [1.1 history](ABM_AMENDMENT_1_1.md).

## Identity and current state

Repo `/home/moose/python/stark-web-factory-scrapper-v1`; branch `wf-scrapper-abm`; observed base HEAD `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f`. The working tree was already dirty: eleven historical response deletions with corresponding untracked files in `RESPONSES/OLD/`, plus extraction evidence/reports. They are preserved. This base is **not a completed ABM implementation commit**. Tony alone commits and creates `qa/wf-scrapper-abm` later.

Director Tony Stark · Architect JARVIS · Engineer Cody · QA Lead SOL (existing assignment; actual session binding pending) · QA Executor separate session/persona, binding pending · independent reviewers Astra and fresh Fable. Historical Claudy/Fable/Cody seat labels describe their then-current work; current entry guidance controls this pilot.

## What exists and what is planned

Certified bim000/bim001 carry-ins remain: two-command flow, status validation, USER_AGENT single source, project validation, collision-safe per-run folders, HTML, manifest v1, absences and stage log. Historical suite: 54 tests; **not rerun for this amendment**. Current product still writes shared Markdown/run_summary and uses its older discovery/access policy. ABM v2, REST/media pipeline, Prepare and unified invocation remain unimplemented; minimal reader is planned in C6, packs in Stage P; ledger states remain NOT STARTED/NOT RUN.

October diagnostics demonstrated the existing `crawl_page` rendered path, nine blog headings/links, one same-page Chromium `window.fetch` post metadata response with empty content, and three substantive article captures. They did not certify the ABM or prove discovery/full-site reliability. Article 2 ends abruptly; hidden/deferred content completeness remains unknown. See the evidence register in the amendment.

## What this ABM adds

Capture: portable hashed raw v2; scoped browser-session discovery and declared REST collections with pagination/all returned fields; rendered Crawl4AI capture; media inventory and in-scope HEAD; screenshots slot; validator; one `recon_pipeline` invocation. No root REST enumeration. One intentional operation at a time, five seconds after completion, no retries or transport switching, first intentional refusal/challenge stops collection. Public browser background resources are observed separately.

Prepare: read-only raw ingestion, site map, content/SEO inventories, cross-stream differences, honest forms/embeds, design evidence, media classifications, typed losses, entry brief, existing JSON/Markdown twins and reproducibility. REST response bytes and parsed object derivatives have distinct provenance. No cleaned-article export is added. R8 retires old product Markdown/run_summary outputs; historical diagnostic Markdown remains evidence.

## Campaign and acceptance

Retain 48 ACs, 24 QA groups, C1–C6 → CHK → P1–P6 → E1–E2. BUILD_READBACK is the kickoff, **not Prepare task P1**. Current BUILD_READBACK review → Tony build approval → engineering campaign and factual handoff → Tony candidate commit/QA branch → Q1 independent Executor inspection and plan binding → SOL plan decision → Q2 approved continuous campaign → scoped repairs/re-pins → Tony cleanup and QA acceptance → final Gate Q certificate → independent Astra/fresh-Fable reviews, dispositions and any RRM/impact retest → Architect closeout carrying the exact certificate → Tony integration. See [QAM](QAM/README.md). No per-task approval loop is introduced.

P0 remains historically partial/failed. Current setup/regression readiness is planned, not presumed. Integrated CHK smoke and E2 two full runs remain obligations within existing authority; budgets are not spent or enlarged here. SOL decides evidence reuse. One shared CHK `--limit 10 --skip-prepare` smoke satisfies the outstanding objective; old-code P0 smoke retired. Proposed concrete limits await build approval; no live run authorized now.

## Scope and risks

No deployment, frontend/viewport QA, redesign, LLM/Gemini, stealth, proxy/identity switching, new dependencies or separate media-byte harvesting. Rendering browsers may load images. Main-content and media-class heuristics remain labeled inferred. Yoast/full REST availability, discovery, pagination and whole-site completeness are unconfirmed. Earlier 429 cause and any causal benefit of five-second pacing remain unknown. Independent review involvement/model identities must be declared, not assumed.

**Exit:** every mandatory AC supported by candidate-bound evidence; cleanup accepted before final Gate Q; SOL certificate, cold-read, whole-app review, Astra/fresh-Fable dispositions and any RRM/retests complete; JARVIS closeout; Tony integration. Product verdict and QAM pilot verdict are separate.
