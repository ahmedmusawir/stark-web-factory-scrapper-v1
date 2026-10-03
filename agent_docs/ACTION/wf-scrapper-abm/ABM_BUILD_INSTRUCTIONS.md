# wf-scrapper-abm — BUILD INSTRUCTIONS

## Director GO — implementation launch (2026-10-02)

Tony explicitly authorized the approved BUILD_READBACK campaign C1–C6 → CHK → P1–P6 → E1–E2; JARVIS approved the architecture with E-20/E-21 below. Current authority: **IMPLEMENTATION AUTHORIZED**; the active task and results are in RECOVERY.md and ENGINEERING_LOG.md. This supersedes prior readback-only/build-approval stops prospectively. Independent QA remains NOT RUN. No install, dependency change, fallback HTTP client, direct Playwright import, security bypass, Git mutation, destructive action or deployment.

**E-20 — redirect completion.** Use browser-observed predecessor request completion, correlated with the next intercepted redirect request. Hold the next hop before dispatch until ≥5 seconds after that completion; repeat scope, deadline and budget checks. Headers alone are insufficient. No requirement to retrieve a redirect body or prove delivery of server bytes the browser did not consume. Preserve delayed-response fixtures and exact browser/server timelines. Unproved completion/pre-dispatch control blocks live work. AC-005/006/010/016/041/042; T-04/05/07/11/22.

**E-21 — challenge evidence.** Retain `cf-mitigated` in the response-header allowlist with Content-Type, Location, Retry-After, X-ac, X-WP-Total, X-WP-TotalPages and Content-Length. Continue excluding cookies, credentials and authorization headers. Test positive and false-positive challenges. AC-005/010/011/016/017/041; T-04/07/08/11/22.

Provenance: **JARVIS Architect ruling under Tony's delegated authority**, recorded prospectively by Cody. Earlier approval/QA states remain historical. These mechanisms are approved for implementation and real Chromium loopback proof, not yet verified.

Conditional live allocation: one CHK Capture smoke (`--limit 10 --skip-prepare --no-media-head`), maximum 120 intentional dispatches, 1800 seconds, 100,000,000 persisted bytes and ten document slots including bootstrap. E2: two full attempts, each maximum 1200 intentional dispatches, 7200 seconds, 150,000,000 raw bytes and 500,000,000 aggregate run/pack/evidence bytes. B starts ≥1 hour after A finishes successfully. Count redirect hops; count background events separately; count bootstrap once and reuse matching capture. Retain BUILD_READBACK §6 per-operation 180s document/30s read limits, 10 MiB decoded cap and 30s finalization reserve within the ceiling. First intentional 403/429/challenge blocks all remaining live allocations. No retry/restart/extra diagnostic or increased budget. SOL decides candidate-bound QA reuse.

No per-task reapproval is required when prerequisites pass. Live work remains conditional on local gates. Maintain factual engineering evidence/source hashes, ledger/log and recovery; future tasks stay pending. Tony alone handles Git and deletion. Prior documentation-session claims below describe their historical pass, not current authority.

## Ordered future tasks, checks, surfaces, stop/resume and BUILD_READBACK

> **Version:** 1.2 · **Date:** 2026-10-02 · **Status:** rulings applied; BUILD_READBACK review/build approval pending; build NOT STARTED. JARVIS Architect amendment under Tony’s delegated authority.
> Read with `ABM_CONTRACTS.md` (what to build) and `ABM_ACCEPTANCE_SPEC.md` (how it is graded).
> **One approval, one campaign.** After review of the delivered BUILD_READBACK and Tony’s explicit build approval, Cody runs C1 → E2 without new chat instructions per task. Stop only on the conditions in §4.

---

## 1. Allowed surfaces (AC-041, R8)

**Create:** `recon_pipeline/` (package, `__main__.py`) · `prepare/` (package: `build.py`, `reader.py`, `rules/`, `twins.py`, `artifacts/*.py`) · `smart_crawler/validate.py` · `smart_crawler/rest_client.py` · `smart_crawler/browser_session.py` (narrow shared transport/policy component) · `smart_crawler/media_inventory.py` · `tests/fixture_server.py`, `tests/netblock.py`, `tests/regen_fixtures.py`, `tests/snapshot_compare.py`, `tests/fixtures/**`, new `tests/test_*.py` · `agent_docs/ACTION/wf-scrapper-abm/ENGINEERING_LOG.md`, `.../EVIDENCE/**`.
**Modify:** `smart_crawler/crawler.py` · `discover_site/discover.py`, `sitemap_utils.py` · existing `tests/test_crawler.py`, `test_discover.py`, `test_sitemap_utils.py` (only assertions enumerated in BUILD_READBACK §5 under E-01/E-05–E-09/E-13–E-19 and the preserved Contracts §1.1 identity binding, each with a docstring citing the applicable erratum; no other certified behavior weakened) · `README.md`, `RUN_NOTES.md`, `CHANGELOG.md`, `RECOVERY.md`, `agent_docs/SESSIONS/*` · `ABM_LEDGER.md` (engineer columns only).
**Do not touch:** `requirements.txt`, `requirements-lock.txt` (no new dependencies; stdlib + existing installed/pinned Crawl4AI/browser and beautifulsoup4; no requests/curl fallback for intentional discovery/REST) · `.env.example` · `agent_docs/ACTION/wf-scrapper-abm/` contract files (`CLAUDE.md`, `ABM_BRIEF.md`, `ABM_CONTRACTS.md`, `ABM_ACCEPTANCE_SPEC.md`, this file, `ABM_RULING_SHEET.md`) · `agent_docs/ACTION/web-factory-p1-bim00*/` · `agent_docs/RESPONSES/OLD/`, `RECON/OLD/` · `agent_docs/SKILLS/`.
**Forbidden:** stealth / `enable_stealth` / `use_undetected` / `magic` / `simulate_user` · any Playwright import in our code (a version metadata lookup is not an import, J-23) · any LLM or paid API call · `os.getenv` for secrets · mutating git · separate media-byte harvesting/saving (ordinary browser image loading remains allowed) · any network in tests except `127.0.0.1`.

## 2. Ordered tasks

Each approved implementation task ends with: `venv/bin/pytest -q` green for implemented/current tests (new-stage tests arrive with that stage; future acceptance remains NOT RUN) → engineering log entry → `RECOVERY.md` checkpoint → ledger rows updated to IMPLEMENTED with evidence path. Tony commits when he chooses; Cody lists uncommitted paths in each log entry.

### Stage C — Capture

| Task | Build | Done when |
|---|---|---|
| **C1** Raw v2 contract | `manifest.json` → `abm-raw-v2` per Contracts §2.2; relative paths only; `sha256`, `final_url`, `redirect_chain`, `retries`, `fetched_at` per page; `versions.tool_commit`; `wait_for_images=True`, timeout 90000 ms, post-load delay 3 s, BYPASS cache, existing USER_AGENT source; retire markdown + `run_summary.json`; `smart_crawler/validate.py` with every §2.8 check; stage-applicable rewrites from BUILD_READBACK §5 with cited docstrings; `CHANGELOG.md` entry citing R8/E-01. | Validator green on an independently authored three-route raw skeleton with static declared stream metadata (no dependency on future discovery/REST clients or Prepare); existing applicable regression green, stage-specific rewrites added with their implementation, never future checks marked PASS; no `outputs/pages`, no `run_summary.json` written. |
| **C2** Discovery | `--mode sitemap\|homepage` non-interactive (interactive prompt kept only when no flag and a TTY); `--out <dir>`; browser-session intentional reads and sitemap fallback order §2.3; no root enumeration or requests/curl substitution; `robots.txt` fetch + save; canonical_url + dedup + `routes.json` + `dropped`; `hosts_allowed` filter; shared five-second completion-based gap between intentional reads/hops; crawler gains `--routes <routes.json>` (default: latest `discovery/routes.json` under the run). | F-01 → exact expected `routes.json` (AC-007 test); fixture request log shows pauses. |
| **C3** Access policy | Pre-dispatch redirect policy §1.4 (`final_url`, chain, out-of-scope → unsupported without requesting destination, max five hops/loop → failed); zero retries, no transport/identity switching; SIGINT handler finalizes manifest/absences (`stopped_early`, exit 130); `--max-bytes` guard; first intentional 403/429/challenge stops all collection, no automatic restart; stage_log separates intentional reads/pacing/stops from public browser resource events; normal background POST permitted, no form actions; incidental resource failure alone is not document denial. | F-03 and F-04 tests green (AC-005, AC-006, AC-010, AC-017, AC-042). |
| **C4** REST stream | `rest_client.py`: browser-session declared collections §2.4 directly, pagination and no `_fields` filter, `users` single initial attempt; complete collection responses saved/hashed at declared browser boundary and value-preserving serialized object derivatives linked to response/array position; `map.json` per §2.5; `content_rendered_empty`; typed absences per object/collection; pause rule; `rest_ref`/`rest_outcome` on page records. **Before live use:** prove transport/body boundary and scoped redirect control on local fixtures. Compare observed optional fields with §2.5 and record missing/null separately; malformed identity/structure is explicit failure, never invented fields. October diagnostics are limited inputs, not a completed P0 or full SEO precondition. | F-02 tests green (AC-011, AC-012, AC-013, AC-014 raw half). |
| **C5** Media inventory | `media_inventory.py` scanning sources §2.6 across captured HTML + REST media; in-scope HEAD only under shared pacing/redirect/stop rules with `--no-media-head`; external/staging offscope URLs inventoried as skipped/untested, never probed; `origin` incl. `staging_domain`; provenance per item; counts. | F-05 test green (AC-015). |
| **C6** Screenshots slot + Capture pipeline / reader | Create minimal `prepare/reader.py` read-only validation adapter now: schema/hash/ref checks, typed accessors, accepts valid partial and rejects invalid. Wire discovery → capture → REST → media → validate; screenshots README and authored slot. `recon_pipeline --skip-prepare` completes Capture-only. Default full pipeline reports Prepare not yet implemented without pretending success until Stage P wires it. | AC-002, AC-003 Capture half, AC-008, AC-018 plus reader AC-019/020 raw-boundary checks. Fixture command explicitly `python -m recon_pipeline --project Fix --url http://127.0.0.1:<port> --skip-prepare`; valid raw and no pack expected. |

### Automatic engineering checkpoint (no Director step)

**CHK** Validate F-09-complete regenerated via Rulings 1.2 §3, reject each F-10, and exercise the minimal C6 reader against both; valid partial F-12 is accepted structurally. No pack construction required here. After all local transport controls prove safe and only under future live authorization, use the **single shared** integrated `--limit 10 --skip-prepare` Cyberize smoke. This satisfies the outstanding smoke objective; separate old-code P0 smoke retired. Save raw validation/reader evidence, no Prepare pack expected. First intentional refusal/challenge stops collection with no retry/restart. Unmet local proof/budgets block live work. Advance to internal Prepare **P1** only on recorded CHK completion. Optional absent fields are not schema contradictions.

### Stage P — Prepare

| Task | Build | Done when |
|---|---|---|
| **P1** Pack skeleton | Extend C6 read-only reader; `prepare.build`, NEW pack/raw copy or read-only symlink, envelope and pack inventory, explicit invalid-raw exit 3/failed folder. Wire default invocation into Prepare construction; remaining P tasks add required artifacts before declaring it complete. | AC-019/020 full checks; F-09 skeleton is an incomplete development milestone, never a complete Architect Data Pack. Source run unchanged; NEW raw copy hashes match. |
| **P2** Structure + content | `site_map.json/.md`, `content_inventory.json`, `disagreements.json` per §3.4; legacy thrive_signal heuristic with stated REST-empty/rendered-present basis; no plugin-cause assertion; main-content heuristic labeled `inferred` with `basis`. | AC-023, AC-024, AC-014 (pack half) tests green on F-01/F-02/F-06. |
| **P3** SEO | `seo_inventory.json` + `seo_summary.md` per §3.5; rendered `<head>` parser (bs4); JSON-LD parse-or-keep-string. | AC-025 test green (deep-equal vs `yoast_head_json`). |
| **P4** Forms/embeds + design | §3.6, §3.7 artifacts; single-value `function_status` enum; observed-only design with `absent` for unobservable. | AC-026, AC-027 tests green on F-07/F-08. |
| **P5** Media classification | `prepare/rules/media_rules.md` (numbered deterministic rules) + `media_classification.json` per §3.8; every item once; `basis` cites rule id. | AC-028, AC-030 tests green on F-05. |
| **P6** Loss ledger, brief, twins, reproducibility | Complete artifacts/losses/brief/B7/twins/link checks and reference-aware semdiff per Contracts §3.10/Rulings 1.2. Default Capture+Prepare path now produces the full pack; F-09 complete and F-12 partial remain distinct. | AC-021/022/029/031–034/038; exact fixture variants and snapshot negatives pass. E1 subsequently verifies whole default invocation. |

### Stage E — Integration, live, evidence

| Task | Build | Done when |
|---|---|---|
| **E1** Fixture e2e + hardening + docs | `tests/test_e2e_fixture.py` (AC-039); AC-043 hostile-string tests; AC-044 sentinel test; `tests/test_docs_commands.py` (AC-047); README (install, run, rerun, outputs, errors, Markdown-viewer caveat), RUN_NOTES ABM section, CHANGELOG. | Full suite green; count recorded in ledger; docs greps green. |
| **E2** Two full Cyberize runs | `python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com` twice, ≥1 h apart, within R4 limits; copy `manifest.json`, `absences.json`, `routes.json`, `rest/index.json`, `rest/map.json`, `media/inventory.json`, `pack.json`, `SITE_RECON_BRIEF.md`, `findings.md` of each into `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/live/<run_id>/` (HTML and REST objects stay in gitignored `outputs/`); `semdiff` between the two packs recorded. | AC-040, AC-042 evidence filed; ledger complete; **Engineering completion report** written (template in `ABM_EXECUTION_RECORDS.md`) recording base HEAD plus dirty changes; candidate SHA remains pending until Tony commits, then QA pins it. Use QAM handoff requirements. |

## 3. Engineer-owned checks that run inside the campaign

- `venv/bin/pytest -q` after every task (regression, AC-041).
- `python -m smart_crawler.validate` on every run folder the campaign produces.
- Surface greps at each stage close (J-23, L17): `grep -rn --include=*.py -E "enable_stealth|use_undetected|magic=|simulate_user|from playwright|import playwright|litellm|openai|google.genai" discover_site smart_crawler prepare recon_pipeline` → 0.
- Schema-bound filesystem-reference traversal/absolute/symlink checks over authored metadata, plus raw fidelity and generated-presentation escaping/advice checks (E-18); no blanket raw JSON/source grep.
- Record pip check plus normalized complete package comparison against existing requirements-lock.txt per approved E-13 at E1 close; requirements.txt is seven direct pins, not a complete lock. No installs/checks are performed in this documentation mission.

## 4. Stop conditions (everything else: continue)

Stop and write the reason into `RECOVERY.md` + engineering log, then end the session:
1. A real contract ambiguity beyond the explicit absence rules (CHK or E2). Missing optional content/Yoast alone is a recorded absence, not permission to invent a field or an automatic architecture stop.
2. Any action outside §1 surfaces would be required to proceed.
3. An intentional collection destination outside `hosts_allowed` (or local fixture host) would be required. Ordinary public browser resources are separately observed, not blanket-blocked or crawl authorization.
4. Any deletion/destructive cleanup would be required: inventory and propose it; Tony alone performs approved deletions, including inside outputs.
5. A mandatory AC cannot be met as bound (state which and why).
6. First intentional 403/429/challenge in any live stage — stop collection, preserve partial evidence and skipped work, report; no automatic restart and no claim of cause.

Not a stop: a failing test you can fix inside surfaces; a fixture you need to add; a session/context limit (checkpoint and resume); the Director being offline.

## 5. Resume rule

On any new session: read `agent_docs/ACTION/wf-scrapper-abm/CLAUDE.md`, then `RECOVERY.md`, then the last engineering log entry. Confirm disk matches (`git status --short`, `ls outputs/*/runs`). Continue only from an authorized, unblocked next task. A pending amendment review/BUILD_READBACK/build approval or a stopped live run is not resumed automatically. Never repeat a live Cyberize run to "make sure"; the evidence folder says whether it exists.

---

## 6. Preconditions and delivered BUILD_READBACK (documentation complete; build NOT STARTED)

P0 is **historically partial**, not passed: September 18 setup/regression succeeded after lock install, collections/smoke failed; September 19 recovery failed. Retain [P0 report](EVIDENCE/p0/P0_REPORT.md) and [recovery report](EVIDENCE/recovery/RECOVERY_REPORT.md) as immutable history. Their probe/root-enumeration/install/retry commands and the old “Run P1” kickoff are superseded, not executable instructions for this campaign. Completed October diagnostics are summarized in [amendment](ABM_AMENDMENT_1_1.md); no blanket P0 rerun is a build prerequisite.

Outstanding preconditions: M-01–M-04 are resolved by Rulings 1.2. Outstanding: BUILD_READBACK review and explicit Tony build approval; current environment/regression checks planned under that approval; fixture-bound browser response/redirect/pacing/stop proof before any authorized integrated live run; concrete live-budget allocation; no assumption of successful sitemap discovery or full REST/Yoast coverage. Do not reinstall a functioning runtime simply because the historical P0 script did so.

**BUILD_READBACK** is the network-free whole-campaign readback authorized and delivered by Cody in [BUILD_READBACK.md](BUILD_READBACK.md). It must map C1–C6, CHK, P1–P6, E1–E2 to files, ACs, fixtures and checks; name every planned regression rewrite/erratum; identify unresolved contract/environment/budget issues; describe the shared live-evidence register, stop policy and QAM handoff. It is distinct from Prepare P1 and does not renumber any build task. Stop for Tony’s build approval. This session is authorized to produce that readback only; it must not begin the build.

Once the build is approved, run the unblocked internal tasks continuously with factual engineering evidence. Future product/test surfaces above are **not authorization to change code during this readback pass**. Do not import Playwright directly or copy the diagnostic wrapper wholesale; implement required behaviors through available Crawl4AI hooks, declaring exact browser transport. QAM packaging is instruction-driven, not an existing exporter/validator.
