# wf-scrapper-abm — RULING SHEET

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.

## Revision 1.2 — current authority and retained ruling history

2026-10-02 — JARVIS Architect amendment under Tony’s delegated authority. The table below preserves the September 18 decisions verbatim. It is **historical provenance**, not permission to execute superseded probes/setup/retry policies. Active contracts, prospective E-13–E-19 and [Rulings 1.2](ABM_RULINGS_1_2.md) govern; E-05–E-12/[amendment record](ABM_AMENDMENT_1_1.md) remain retained history. R6's old root/client/3-second probe and R7's old executable P0 sequence are retired; R7’s outstanding smoke objective is now allocated to CHK only by E-15; separate old-code P0 smoke retired. No new live budget is granted here.

## Consolidated historical Director rulings, 2026-09-18

| # | Question | Ruling | Effect |
|---|---|---|---|
| R1 | Module identity and branch | `wf-scrapper-abm`, keep existing branch `wf-scrapper-abm`, no rename. Scrapper ABM is one component of the wider Web Factory. | Phase map v0.4 records absorption of bim002/003/004 + Phase 2 Prepare. Pack folder `agent_docs/ACTION/wf-scrapper-abm/`. |
| R2 | Ditto extraction reports | Not on disk; bind donor lessons from Plan §6. Reconcile later reports through errata. | Contracts §3 built from §6 lessons (loss ledger, typed absences, authored+computed, confidence ≠ action, twins, embeds with function status, per-route SEO as contract). |
| R3 | Prepare location and CLI | Same repo, `prepare/` beside `smart_crawler/`; `python -m prepare.build --project X --run <run_id>`; single invocation for the whole flow retained. | `recon_pipeline` package owns the single invocation. |
| R4 | Live runs, environment, retention, delivery | Zorin, `~/python/stark-web-factory-scrapper-v1`. Two full Cyberize runs approved within campaign limits. `outputs/` gitignored. Pack delivered with its raw evidence so links resolve after copy. Runtime/storage figures are estimates. | Contracts §1.4 budgets, §3.1 `raw/` copy default; E2 task. |
| R5 | Cold-read owner | Fresh Fable session, during QA, before Gate Q. SOL judges. Later code reviews stay separate. | AC-035 binding; Erratum E-03. |
| R6 | REST probe | Approved: three GETs, 3 s apart, global `requests 2.31` acceptable for this probe only; record version. | P0 part D. |
| R7 | Task zero | Approved: rebuild pinned venv per README, run 54-test regression, then one `--limit 10` smoke. Report regression failure before smoke. Skip tag. Git stays with Director. | P0 parts A–C. |
| R8 | Contract break | Approved: `abm-raw-v2`; retire generated markdown and `run_summary.json`; Prepare derives from HTML + approved raw evidence; preserve historical evidence; document contract changes behind test updates; preserve all other certified behavior. | Erratum E-01; C1 task; AC-041 no-break list. |

**Historical Architect bindings (superseded where noted below; not active execution instructions):** `wait_for_images=False` (J-24) · one retry on exception with 10 s pause · robots recorded-not-enforced (E-02) · media HEAD-only (E-04) · `hosts_allowed` = apex + www · sitemap fallback order · `--max-bytes` default 500 MB · tracking-param strip list.


## Active amendment rulings (not retroactive Director rulings)

- Tony Director; JARVIS Architect; Cody Engineer. SOL remains QA Lead; independent Executor session binding pending.
- E-05/E-06 replace the historical pacing/retry/False-image-wait and requests/root assumptions with browser-session reads, five seconds after completion, no retries/switching, first intentional refusal stop, True image wait and demonstrated settings.
- E-07 qualifies E-04: in-scope HEAD only; external/staging inventory remains, no explicit offscope probes. Browser images/background traffic are distinct from media harvesting.
- E-08/E-09 fix response fidelity, complementary sources, route accounting and valid-partial versus invalid packages. E-10 corrects the mailto embed count.
- E-11 preserves partial P0 and existing integrated obligations; the then-unresolved dependency/fixture/budget/sentinel decisions are now prospectively approved by E-13–E-16. E-12 adopts QAM, separate QA seats and cleanup before final Gate Q.
- R1–R5/R8 retain module identity, donor lessons, single invocation, raw delivery, two full-run obligation, cold-read and product-output retirement. No build, live work or QA execution is authorized by this documentation amendment.

## Prospective JARVIS ruling — revision 1.2

2026-10-02 · **JARVIS Architect ruling under Tony's delegated authority.** M-01–M-04 APPROVED; E-13–E-16 apply lock baseline, distinct fixture variants, shared CHK smoke and precise leak scan. E-17 moves minimal reader to C6; C6/CHK Capture-only --skip-prepare, packs in Stage P. E-18 scopes path/escaping/immutability/advice checks to authored boundaries. E-19 corrects the nonexistent soft-block flag binding using installed-source evidence; implementation controls remain unproven until fixtures. See [ruling dispositions](ABM_RULINGS_1_2.md) and [BUILD_READBACK](BUILD_READBACK.md). Earlier R1–R8/E-01–E-12 history remains. AWAITING BUILD_READBACK REVIEW AND TONY'S BUILD APPROVAL. No build/live authorization.
