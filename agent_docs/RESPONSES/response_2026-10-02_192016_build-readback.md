# ABM rulings + BUILD_READBACK — DONE

**Final state: AWAITING BUILD_READBACK REVIEW AND TONY'S BUILD APPROVAL.**

Applied JARVIS’s rulings prospectively as packet **1.2**, added **E-13–E-19**, and completed the whole-campaign [BUILD_READBACK](../ACTION/wf-scrapper-abm/BUILD_READBACK.md). Build/independent QA remain **NOT STARTED / NOT RUN**. No implementation, product tests, installations, browser launches, live requests, Git mutations or destructive actions occurred.

Director Tony Stark · Architect JARVIS · Engineer Cody. Provenance: **JARVIS Architect ruling under Tony's delegated authority**.

## Decisions applied

| Decision | Applied change |
|---|---|
| M-01 / E-13 | Canonical lock install → pip check → normalized full package comparison, with only explicitly unlocked pip/setuptools/wheel exclusions. Python/platform/browser/lock identity recorded. Dependency files unchanged; clean-environment QA unexecuted |
| M-02 / E-14 | Complete F-09 variant separated from F-01’s required404 and F-02 fault cases; valid F-12 retains two required losses. Inputs/expected facts and integrity-first snapshot normalization explicitly bound |
| M-03 / E-15 | CHK owns the single shared limit-10 Capture smoke; old-code P0 smoke retired. E2 retains two full runs ≥1h apart; SOL decides candidate-bound reuse, extra volume requires Tony |
| M-04 / E-16 | Generated runs/packs/evidence/logs/reports scanned with exact source exemptions, isolated leak-detection control, no sentinel echoed. Checks NOT RUN |
| E-17 | Minimal read-only reader/validation adapter moved to C6; C6/CHK --skip-prepare; pack construction Stage P, default whole pipeline verified E1/E2 |
| E-18 | Path/escaping/advice checks target authored boundaries; raw evidence preserved and NEW pack/raw copy authorized; source mutation still forbidden |
| E-19 | Corrected assumed soft-block flag using installed-source inspection; exact signals and negative cases planned without claiming implementation proof |

Exact dispositions, fixture consumers, snapshot/comparison/scan boundaries: [ABM_RULINGS_1_2.md](../ACTION/wf-scrapper-abm/ABM_RULINGS_1_2.md), line 7. Earlier E-01–E-12/R1–R8 and journal events retain their historical text/state; the old 1.1 report/ZIP remain untouched.

## What source inspection established

Existing crawl_page/BrowserConfig settings remain the starting point. The readback names installed hooks, page/context/response methods and Chromium Fetch interception APIs with source paths/lines. Ordinary page.route cannot guard every redirect; redirect bodies are unavailable through Fetch.getResponseBody. Crawl4AI supplies is_blocked tuple/error/crawl_stats, not a dedicated result flag, and its near-empty heuristic cannot be treated as explicit refusal.

**Still unproven:** redirect completion plus pacing, pre-dispatch coverage, same-origin/session bootstrap and service-worker/CORS handling, bounded decoded-byte reads and soft-block precision. Local positive/negative fixtures must prove these before any live stage. No fallback client/security change is proposed. [BUILD_READBACK.md](../ACTION/wf-scrapper-abm/BUILD_READBACK.md), line 17 and [BUILD_READBACK.md](../ACTION/wf-scrapper-abm/BUILD_READBACK.md), line 45.

The plan maps every C/CHK/P/E task to files/dependencies/ACs/fixtures/checks/evidence, inventories **34 intended rewrites among 53 existing test functions inspected**, and preserves other certified invariants. It defines exact precommit source hashes/modes → Tony commit → independent QA identity attestation → SOL reuse, followed by separate Q1 → SOL plan decision → Q2. [BUILD_READBACK.md](../ACTION/wf-scrapper-abm/BUILD_READBACK.md), line 66 through §8.

## Proposed limits — review required, no live authorization

CHK: 120 intentional dispatches, 1800 seconds, 100 MB persisted evidence, ten document slots including proposed origin bootstrap; --skip-prepare and --no-media-head. Each E2: 1200 dispatches, 7200 seconds, 150 MB raw and 500 MB aggregate run/pack/evidence cap; two allocations ≥1h apart. Redirect hops count; browser resource events remain separate. Transfer/deadline/byte/stop enforcement and shortcomings are detailed in [BUILD_READBACK.md](../ACTION/wf-scrapper-abm/BUILD_READBACK.md), line 155. These are proposed ceilings, not historical estimates or permission to execute.

## Checkout, validation and preservation

- Repo `/home/moose/python/stark-web-factory-scrapper-v1`; branch **wf-scrapper-abm**; unchanged base HEAD **3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f**. This is not a completed implementation SHA.
- Pre-existing state included amendment dirty docs, diagnostic evidence/reports/ZIPs, eleven response deletions and matching untracked OLD files. Exact initial status is in `PRE_EXISTING_STATUS.txt`; no repair/move/deletion performed.
- **48 AC rows / 24 QA groups retained and mapped; all ledger results unchanged.** C1–C6 → CHK → P1–P6 → E1–E2 retained. 154 current local links resolve; 7 contract JSON examples parse; setup snippet parses without execution; git diff --check clean.
- Hashed **1158** existing tracked/nonignored files: **1133 unchanged**, **25 authorized documentation edits**, zero newly missing files. Product/tests/dependency declarations/evidence/previous reports/ZIPs unchanged. Ignored caches/dependencies/bulk outputs are outside that count and were not opened for write.
- Added only two governing documents before this report/package: ABM_RULINGS_1_2.md and BUILD_READBACK.md. Complete changed-path inventory, scoped diff versus the start of this pass, documentation-check results and source inspection hashes/excerpts are in the ZIP. Documentation validation is not product or independent QA PASS.

## Review package and next move

ZIP: `agent_docs/RESPONSES/response_2026-10-02_192016_build-readback.zip`. Includes START_HERE, this report, updated ABM/QA/QAM/root instructions, BUILD_READBACK, dispositions/errata, scoped diff, check results and file/hash inventory. Historical reports/playbooks are labeled context; no dependency trees, secrets/.env, cookies, caches or raw capture dumps included. Missing older park/errata/raw artifacts remain disclosed historical gaps, not fabricated replacements.

**Next: JARVIS reviews BUILD_READBACK—including unproven controls and proposed ceilings—then Tony decides build approval. STOPPED.**
