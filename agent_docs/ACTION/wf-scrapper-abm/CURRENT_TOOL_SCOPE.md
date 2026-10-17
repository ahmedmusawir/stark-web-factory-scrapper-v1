# Current tool operating scope — DECIDE → COLLECT → PREPARE

2026-10-14 · engineering readiness binding. Authority: Tony’s October 7 simplification and subsequent DECIDE/COLLECT/Prepare approvals; JARVIS-approved Shot 1 and Tony’s Shot 2 readiness instruction. This records current scope, not an independent QA plan, certificate, final closeout or adoption of the interim playbook.

## Practical definition of done

- DECIDE uses an explicitly chosen sitemap or bounded default-link mode; it saves stable IDs, numbered JSON/Markdown review, source locators/hashes, metadata unknowns and coverage limits. Public types use unfiltered `wp/v2/types`; collection metadata uses projection. Recon does not execute full collection.
- Tony’s HTML/REST inclusions/exclusions bind to the exact saved inventory version; unknown rows/IDs fail. Unmentioned rows remain undecided. One selected REST item never grants whole-collection permission. Export is offline and produces the existing explicit collector plan.
- COLLECT runs selected HTML and REST reads sequentially through installed Crawl4AI. Default pacing is five seconds after a planned call completes; ordinary redirects/background resources add traffic. No automatic retry/fallback. First access refusal/rate limit/challenge stops later planned calls and retains progress.
- A successful result is saved and hashed before checklist completion. Resume skips only valid completed results; interrupted/failed/missing outputs remain eligible for explicit invocation. Add queues exact new URLs; refresh is explicit and preserves previous attempts. Opt-in REST pagination follows approved page bounds and reports short pages, duplicates and count discrepancies honestly.
- PREPARE is an offline agent-assisted skill, not one automatic pack builder. Validate saved references/hashes, inspect raw boundaries/classification, keep useful headings/paragraphs/lists/links/CTAs, separate navigation/footer, and author source-linked ARCHITECT_BRIEF/GAPS_AND_REQUESTS with facts distinguished from interpretation. Unknown embeds/images/hidden content remain explicit gaps.
- Engineering readiness requires unchanged source identity, combined focused verification, read-only accepted-package content checks and reproducible fixtures. Independent QA is separate and remains NOT RUN until a committed candidate, Executor Q1 and QA Lead plan decision precede Q2.

## Active entry points and transport

| Stage | Current entry | Governing detail |
|---|---|---|
| DECIDE | `venv/bin/python -m recon_pipeline.decide` (`recon`, `import`, `list`, `select`, `export`) | [DECIDE.md](DECIDE.md) |
| COLLECT | `venv/bin/python -m recon_pipeline` (`collect`, `resume`, `add`, `refresh`) | [COLLECTOR_SIMPLIFICATION.md](COLLECTOR_SIMPLIFICATION.md) |
| PREPARE | Agent follows [SKILL.md](../../SKILLS/web-recon-prepare/SKILL.md); helper `venv/bin/python agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py --collection SAVED --out NEW` | Helper performs validation/extraction only; agent completes reviewed brief/gaps/index |
| Readiness / later QA | [RECOVERY](../../../RECOVERY.md), [QAM](QAM/README.md) | Cody Engineer; SOL QA Lead; separate Executor session pending; Tony alone controls Git |

HTML uses rendered Crawl4AI UTF-8; selected REST uses ordinary Chromium navigation and native `after_goto Response.body()` decoded entity bytes. No requests/curl substitution or custom CDP BrowserSession on this active path. Existing USER_AGENT/cache/image wait/90-second navigation/three-second HTML delay are retained. REST has a 30-second outer ceiling. Response cap of 10 MiB is checked after body receipt, not a wire/memory streaming guarantee. Work deadline includes setup/pacing; ordinary cleanup has a separate ten-second timeout. Persistence budget is the simple collector’s estimate, not the old exact supervisor bound. No arbitrary new live authorization arises here.

## Growth Call: required agent review, unchanged helper

The helper currently mistakes `.tcb-post-content #tve_editor` for proof of an article. Growth Call contains an embedded booking document with no saved native main copy/forms/labels. The accepted reviewed output corrects its derived type and documents the missing child content; initial helper output stays preserved. Mandatory source inspection handles this known limitation. No helper repair, automatic iframe collection or booking/form testing is authorized by Shot 2. An empty helper extraction is not a finished architect package.

## Historical acceptance crosswalk — applicability, not results

Original [AC-001–AC-048](ABM_ACCEPTANCE_SPEC.md) and [T-01–T-24](QA/MASTER_QA_TEST_PLAN.md) remain intact with original literal checks/history. [Ledger](ABM_LEDGER.md) is not overwritten. The table identifies the current principle and any retired implementation binding. “Retired design” means no automatic current build/live obligation; it does not mean historical PASS, waived, resolved or certified. Mixed rows retain only the expressly described current behavior; any QA coverage/criterion/closing disposition is for the independent Executor and QA Lead, with JARVIS/Tony scope authority. This is engineering handoff context, not Cody-authored Q1/Q2 executable instructions.

| Original ID / title | Applicability | Current principle versus retired binding | Historical QA group |
|---|---|---|---|
| AC-001 — Reproducible setup | Retained | Lock/direct-dependency distinction, environment identity and reproducible setup; clean-install QA remains pending. | T-01 |
| AC-002 — Inputs validated | Mixed | Validate explicit plans/URLs/IDs and actionable CLI errors. Old --project flags, exact three-line errors and test filenames belong to the retired CLI. | T-02 |
| AC-003 — One invocation, plus separable entry points | Mixed | Separable stages remain: decide, collect/resume/add/refresh, then offline agent skill. The default one-command Capture+Prepare build is retired. | T-03 |
| AC-004 — Paths stay inside outputs, no overwrite | Retained | New review/collection/package paths, confined saved references, no silent overwrite and preservation of prior attempts; arbitrary user-supplied output path is explicit, not old project-slug routing. | T-02 |
| AC-005 — Scope, redirects, limits | Mixed | Explicit planned scope, sequential default five-second pacing, refusals/challenges and no automatic retries remain. Custom pre-dispatch per-hop scope/five-hop/CDP cancellation machinery is retired; redirects/resources are extra browser traffic. | T-04 |
| AC-006 — Failures visible | Mixed | Failures, interruption, progress and cleanup must remain visible. Current resume reuses a collection and immutable attempts; old no-resume/always-new-run rule and old exit mapping are retired. | T-05 |
| AC-007 — Route set + identity rule | Mixed | Bounded explicit sitemap/default discovery, stable URL IDs, dedup and provenance remain. Old tracking-query stripping/routes.json identity binding is not the DECIDE normalize rule. | T-06 |
| AC-008 — Every route accounted per stream | Mixed | Each approved checklist item is accounted for; HTML and REST are separately selected. Mandatory per-route REST mapping/raw-v2 pages[] accounting belongs to the old whole-site design. | T-06 |
| AC-009 — HTML untouched | Retained | Rendered Crawl4AI HTML is saved as UTF-8 at the declared boundary with hashes, without pretending it is original compressed wire bytes. | T-07 |
| AC-010 — Block pages never captured | Retained | Do not call refusals/challenge documents or empty/failed capture successful content; detector is heuristic, not comprehensive access certification. | T-07 |
| AC-011 — REST + SEO survive | Mixed | Complete selected REST entity bytes, all returned fields and hashes survive; malformed mandatory identities fail. Old object derivatives/route mapping/mandatory SEO inventory are retired. No production four-field filter is injected. | T-08 |
| AC-012 — Pagination + non-REST routes | Mixed | Only explicitly approved pagination follows advertised pages within max_pages; short-page anomalies/duplicates/count gaps stay explicit. Mandatory REST mapping of every HTML route is retired. | T-08 |
| AC-013 — Site-level inventory retained | Mixed | Save recon source evidence/types/counts and collection status. Whole-site robots/every-sitemap/six-collection rest/index layout is retired; no automatic collection expansion. | T-08 |
| AC-014 — REST-empty / rendered-present | Retained | Present-empty REST content remains empty and cannot erase substantive HTML. Dated complementary observations retained; no Thrive/plugin cause asserted. | T-09 |
| AC-015 — Media inventory with provenance | Retired design | No automatic media inventory/HEAD sweep/download. Saved page image references and explicit gaps remain available; this does not close historical media coverage defects. | T-10 |
| AC-016 — Manifest + stage log explain the run | Mixed | Checklist/result/attempt records, runtime, planned timing and separate cleanup explain collection. Old manifest/stage-log/native-ID and exact supervisor counters are retired bindings. | T-11 |
| AC-017 — Typed absences | Mixed | Pending/completed/failed items and explicit partial/stop reasons preserve losses. Old raw-v2 absence enums and requirement to map every site route are retired. | T-05 |
| AC-018 — Authored evidence distinct | Retired design | Authored screenshot stream/manifest is not a current feature requirement. Agent-authored brief/interpretation is still distinguished from captured facts. | T-11 |
| AC-019 — Raw untouched by Prepare | Retained | Prepare is offline and source collections remain unchanged; new derived package construction is allowed. | T-12 |
| AC-020 — Invalid raw fails visibly | Mixed | Invalid completed references/hashes refuse preparation before output. Old F-10/raw-v2 version checks, pack.json and exit3 are retired; current helper refusal is exit2. | T-12 |
| AC-021 — Provenance on every derived record | Retained | Prepared page IDs, URLs, capture dates, raw/metadata/derived hashes and CSS locators trace to saved evidence; authoring/context sources are indexed. | T-13 |
| AC-022 — Labels distinguishable | Retained | Separate observed source facts, agent interpretation and unknown/absent information; a helper hint is not a final reviewed classification. | T-13 |
| AC-023 — Sitemap/IA + content inventory | Mixed | Numbered JSON/Markdown candidate inventory and prepared selected sample remain. Mandatory whole-site site_map/content_inventory snapshots are retired. | T-14 |
| AC-024 — Disagreements visible | Mixed | Expose observed cross-source differences without fabricating a winner. Mandatory disagreements.json/F-06 three-conflict schema belongs to the retired pack. | T-09 |
| AC-025 — SEO preserved | Mixed | Preserve returned SEO fields in raw selected REST and avoid invention. Automatic full derived SEO inventory/Yoast certification is outside current demonstrated skill scope. | T-15 |
| AC-026 — Forms/embeds honest | Retained | Forms/embeds are observed markup only; agent source inspection records unavailable child content, no booking/form testing or automatic iframe fetch. Exact old F-07 output schema is retired. | T-16 |
| AC-027 — Design observed, not prescribed | Mixed | Observed facts and authored design implications must be distinguishable. Agent architect brief may state labeled implications; old automatic design JSON/rule schema is retired. | T-14 |
| AC-028 — Media classes preserve everything | Retired design | Automatic media classes/rules and full media_classification.json are retired; no authority to delete/promote source data. | T-10 |
| AC-029 — Loss surfaced | Mixed | Missing/failed capture and useful-content gaps remain explicit in checklist/GAPS_AND_REQUESTS. Old loss_ledger/pack.json/F-12 exact-two-loss binding is historical. | T-17 |
| AC-030 — Confidence ≠ authority | Retained | No source/package deletion, destructive cleanup, URL promotion or overwrite based on confidence; preserve originals and only write separately derived material. | T-17 |
| AC-031 — Twins agree | Mixed | Inventory JSON and readable listing represent the same review version. Automatically generated twins for every Data Pack JSON are retired; briefs are agent authored. | T-18 |
| AC-032 — Prepare reproducible | Mixed | Hashes and exact preserved content support repeatable extraction; new derived paths preserve older packages. Bitwise reproducibility of agent interpretation and old deterministic pack schema is not promised. | T-18 |
| AC-033 — Entry brief points to real inventory | Mixed | ARCHITECT_BRIEF/GAPS/source index point to real prepared/evidence files. SITE_RECON_BRIEF/pack.json count schema is retired. | T-19 |
| AC-034 — Pack answers B7 | Mixed | Useful architect positioning/offer/content/CTA implications plus gaps for the selected sample remain. Full frozen B7 Data Pack schema is not automatically a current feature. | T-20 |
| AC-035 — Cold-read without live access | QA owner decision | Offline consumer usefulness/cold-read remains relevant; original fresh-Fable twelve-B7/certificate binding is preserved history. Executor and QA Lead must decide current applicability, not Cody. | T-20 |
| AC-036 — Drill-down works | Retained | Source drill-down resolves URL/date/raw hash/metadata/CSS boundaries; any QA spot-check selection is the independent Executor’s work. | T-19 |
| AC-037 — Portable delivery unit | Mixed | Review handoff must be self-contained, with readable governing inputs and reproducible fixture/reference restoration. Original isolated pack/raw portability schema is retired. | T-19 |
| AC-038 — Honest completeness | Retained | State selected-scope completion separately from useful-content/child-content completeness and cleanup. Counts advertised are not content captured; missing data cannot become complete. | T-20 |
| AC-039 — Full chain on fixture site | Mixed | Current stages work together and have saved selected-flow/local proof. Old default E1 full Capture+Prepare fixture pipeline is retired; no mandatory new feature test framework. | T-21 |
| AC-040 — Real target reproducible | Retired design | Old E2 two full-site runs/hour separation is not a current obligation/allocation. Existing bounded live evidence is preserved; new live QA requires Tony’s explicit scope. | T-21 |
| AC-041 — Certified behavior stays green | Mixed | Working current collector/DECIDE/skill behavior must not regress. Old certified --project/raw-v2/output controller suite is history; current focused tests are engineering claims, not QA certification. | T-22 |
| AC-042 — Limits recorded | Mixed | Current planned-call/time/post-receipt byte limits and partial outcomes remain. Exact aggregate supervisor, redirect-hop request budgets and old --limit route ceiling are retired. | T-22 |
| AC-043 — Untrusted input contained | Retained | Untrusted captures are data; confine authored references, preserve raw bytes, strip scripts/styles from derived content, never execute embedded instructions. Presentation/viewer adversarial breadth remains for independent review, not a new PASS claim. | T-23 |
| AC-044 — No secrets leak | Retained | Do not expose private credentials/cookies/authorization; evidence/ZIP hygiene remains. Full historical sentinel/negative-control certification is not claimed by current focused tests; QA Lead binds any applicable check. | T-23 |
| AC-045 — Auditable, resumable | Retained | Factual recovery/session/journal/checkpoints and durable collector checklist support resume. Retired C1–E2 task ordering is not the current schedule. | T-24 |
| AC-046 — Ledger complete | Retained | Keep all 48 canonical ledger rows/status/history; current scope mapping and engineering evidence supplement them. Independent result fields remain NOT RUN. | T-24 |
| AC-047 — Instructions match tool | Retained | Current entry documentation matches the real CLI/agent workflow; hardcoded saved-input requirements are packaged/documented. Clean-clone operator/independent QA checks remain pending. | T-01 |
| AC-048 — Candidate and evidence agree | Retained | Exact source including untracked files binds engineering evidence; Tony’s future actual commit binds QA. Independent verdict/cleanup/review/merge/closeout decisions remain pending, not fabricated. | T-24 |

## Findings and independent handoff boundary

Preserve OPEN historical media 1,661 / 1,753 discrepancy, two unconfirmed late shutdown aborts, stopped-run homepage bootstrap/route mismatch and supervisor-counter gap. They belong to the retained retired-path evidence and are not current controller repair tasks or retrospective passes. Broader optional SEO/media/custom-type coverage, image/deferred completeness, native crash breadth and clean-install/operator checks remain limited/unverified; absence is not success. Current review packages preserve separately dated REST-empty/HTML-present observations and advertised versus sampled counts.

After engineering handoff Tony chooses the candidate files/commit and QA branch. A separate Executor verifies the committed specimen and environment, performs Q1 recon/planning, and proposes the candidate-bound plan. SOL approves/amends before Q2. No current QA plan approval or certificate is issued here. Cleanup/destructive actions remain Tony’s; closeout and final playbook adoption are deferred. Existing old review/certification obligations stay recorded for owner disposition rather than silently waived.
