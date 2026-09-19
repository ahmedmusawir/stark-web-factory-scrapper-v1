# wf-scrapper-abm — BUILD INSTRUCTIONS
## Ordered tasks, checks, surfaces, stop/resume, and the two Director-facing prompts

> **Version:** 1.0 · **Date:** 2026-09-18 · **Status:** frozen at Engineer handoff
> Read with `ABM_CONTRACTS.md` (what to build) and `ABM_ACCEPTANCE_SPEC.md` (how it is graded).
> **One approval, one campaign.** After P1 readback approval, Claudy runs C1 → E2 without new chat instructions per task. Stop only on the conditions in §4.

---

## 1. Allowed surfaces (AC-041, R8)

**Create:** `recon_pipeline/` (package, `__main__.py`) · `prepare/` (package: `build.py`, `reader.py`, `rules/`, `twins.py`, `artifacts/*.py`) · `smart_crawler/validate.py` · `smart_crawler/rest_client.py` · `smart_crawler/media_inventory.py` · `tests/fixture_server.py`, `tests/netblock.py`, `tests/regen_fixtures.py`, `tests/fixtures/**`, new `tests/test_*.py` · `agent_docs/ACTION/wf-scrapper-abm/ENGINEERING_LOG.md`, `.../EVIDENCE/**`.
**Modify:** `smart_crawler/crawler.py` · `discover_site/discover.py`, `sitemap_utils.py` · existing `tests/test_crawler.py`, `test_discover.py`, `test_sitemap_utils.py` (only assertions named in Erratum E-01, each with a docstring citing E-01) · `README.md`, `RUN_NOTES.md`, `CHANGELOG.md`, `RECOVERY.md`, `agent_docs/SESSIONS/*` · `ABM_LEDGER.md` (engineer columns only).
**Do not touch:** `requirements.txt`, `requirements-lock.txt` (no new dependencies; stdlib + already-pinned `requests`, `beautifulsoup4` only) · `.env.example` · `agent_docs/ACTION/wf-scrapper-abm/` contract files (`CLAUDE.md`, `ABM_BRIEF.md`, `ABM_CONTRACTS.md`, `ABM_ACCEPTANCE_SPEC.md`, this file, `ABM_RULING_SHEET.md`) · `agent_docs/ACTION/web-factory-p1-bim00*/` · `agent_docs/RESPONSES/OLD/`, `RECON/OLD/` · `agent_docs/SKILLS/`.
**Forbidden:** stealth / `enable_stealth` / `use_undetected` / `magic` / `simulate_user` · any Playwright import in our code (a version metadata lookup is not an import, J-23) · any LLM or paid API call · `os.getenv` for secrets · mutating git · downloading media bytes · any network in tests except `127.0.0.1`.

## 2. Ordered tasks

Each task ends with: `venv/bin/pytest -q` green → engineering log entry → `RECOVERY.md` checkpoint → ledger rows updated to IMPLEMENTED with evidence path. Tony commits when he chooses; Claudy lists uncommitted paths in each log entry.

### Stage C — Capture

| Task | Build | Done when |
|---|---|---|
| **C1** Raw v2 contract | `manifest.json` → `abm-raw-v2` per Contracts §2.2; relative paths only; `sha256`, `final_url`, `redirect_chain`, `retries`, `fetched_at` per page; `versions.tool_commit`; `wait_for_images=False`; retire markdown + `run_summary.json`; `smart_crawler/validate.py` with every §2.8 check; E-01 test rewrites with docstrings; `CHANGELOG.md` entry citing R8/E-01. | Validator green on a fresh `--limit 3` run against F-01 (F-01 built in this task, minimal); all prior tests green or rewritten under E-01; no `outputs/pages`, no `run_summary.json` written. |
| **C2** Discovery | `--mode sitemap\|homepage` non-interactive (interactive prompt kept only when no flag and a TTY); `--out <dir>`; sitemap fallback order §2.3; `robots.txt` fetch + save; canonical_url + dedup + `routes.json` + `dropped`; `hosts_allowed` filter; pause rule between sitemap children; crawler gains `--routes <routes.json>` (default: latest `discovery/routes.json` under the run). | F-01 → exact expected `routes.json` (AC-007 test); fixture request log shows pauses. |
| **C3** Access policy | Redirect policy §1.4 (`final_url`, chain, out-of-scope → unsupported, loop → failed); one retry on exception/timeout with 10 s pause; SIGINT handler finalizes manifest/absences (`stopped_early`, exit 130); `--max-bytes` guard; stop rule unchanged; stage_log lines for every request/pause/retry/stop. | F-03 and F-04 tests green (AC-005, AC-006, AC-010, AC-017, AC-042). |
| **C4** REST stream | `rest_client.py`: root, collections §2.4 with pagination, no `_fields` filter, `users` single attempt; objects saved byte-for-byte; `map.json` per §2.5; `content_rendered_empty`; typed absences per object/collection; pause rule; `rest_ref`/`rest_outcome` on page records. **Before coding:** compare the P0 Part B probe output to Contracts §2.5; any field-name difference → log it, stop, request erratum. | F-02 tests green (AC-011, AC-012, AC-013, AC-014 raw half). |
| **C5** Media inventory | `media_inventory.py` scanning sources §2.6 across captured HTML + REST media; HEAD probe under pacing with `--no-media-head`; `origin` incl. `staging_domain`; provenance per item; counts. | F-05 test green (AC-015). |
| **C6** Screenshots slot + pipeline | `screenshots/README.md` fixed text; manifest `streams.screenshots`; `recon_pipeline` single invocation: create run folder → discovery into `discovery/` → crawl → rest → media → validate → (unless `--skip-prepare`) prepare; three-line actionable errors (J-17) on every CLI; `versions.tool_commit`. | AC-002, AC-003 (first half), AC-018 tests green; `python -m recon_pipeline --project Fix --url <fixture>` end-to-end produces a validator-green raw run. |

### Automatic engineering checkpoint (no Director step)

**CHK** Run the validator on: F-09 regenerated (`tests/regen_fixtures.py`, diff empty), F-10 each case rejected, and the real P0 smoke run re-captured on the new code (`--limit 10` Cyberize, one run, within R4 limits). Confirm `prepare/reader.py` (stub from C1: loads a run folder, verifies schema+hashes, exposes typed accessors) consumes all three without error. Log the three results. **Advance to P1 when green.** If real Cyberize evidence contradicts a contract field (e.g. Yoast key missing site-wide), record the precise conflict in the log and `RECOVERY.md`, and stop for an Architect erratum; do not change the schema.

### Stage P — Prepare

| Task | Build | Done when |
|---|---|---|
| **P1** Pack skeleton | `prepare.build` CLI; `reader.py` read-only guard; `pack.json`; `raw/` copy (or symlink with `--no-copy-raw`); exit 3 on invalid raw with named check; `.failed` folder rule; record envelope §3.3 helper. | AC-019, AC-020 tests green; F-09 → empty pack with `completeness` computed. |
| **P2** Structure + content | `site_map.json/.md`, `content_inventory.json`, `disagreements.json` per §3.4; Thrive signal; main-content heuristic labeled `inferred` with `basis`. | AC-023, AC-024, AC-014 (pack half) tests green on F-01/F-02/F-06. |
| **P3** SEO | `seo_inventory.json` + `seo_summary.md` per §3.5; rendered `<head>` parser (bs4); JSON-LD parse-or-keep-string. | AC-025 test green (deep-equal vs `yoast_head_json`). |
| **P4** Forms/embeds + design | §3.6, §3.7 artifacts; single-value `function_status` enum; observed-only design with `absent` for unobservable. | AC-026, AC-027 tests green on F-07/F-08. |
| **P5** Media classification | `prepare/rules/media_rules.md` (numbered deterministic rules) + `media_classification.json` per §3.8; every item once; `basis` cites rule id. | AC-028, AC-030 tests green on F-05. |
| **P6** Loss ledger, brief, twins, reproducibility | `loss_ledger.json`, `findings.md`, `SITE_RECON_BRIEF.md` §3.9 incl. §11 B7 map; `twins.py`; semantic-diff tool `prepare/semdiff.py` per §3.10; link checker. | AC-021, AC-022, AC-029, AC-031 to AC-034, AC-038 tests green; two Prepare runs on F-09 semantically equal. |

### Stage E — Integration, live, evidence

| Task | Build | Done when |
|---|---|---|
| **E1** Fixture e2e + hardening + docs | `tests/test_e2e_fixture.py` (AC-039); AC-043 hostile-string tests; AC-044 sentinel test; `tests/test_docs_commands.py` (AC-047); README (install, run, rerun, outputs, errors, Markdown-viewer caveat), RUN_NOTES ABM section, CHANGELOG. | Full suite green; count recorded in ledger; docs greps green. |
| **E2** Two full Cyberize runs | `python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com` twice, ≥1 h apart, within R4 limits; copy `manifest.json`, `absences.json`, `routes.json`, `rest/index.json`, `rest/map.json`, `media/inventory.json`, `pack.json`, `SITE_RECON_BRIEF.md`, `findings.md` of each into `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/live/<run_id>/` (HTML and REST objects stay in gitignored `outputs/`); `semdiff` between the two packs recorded. | AC-040, AC-042 evidence filed; ledger complete; **Engineering completion report** written (template in `ABM_EXECUTION_RECORDS.md`) naming the candidate SHA once Tony commits. |

## 3. Engineer-owned checks that run inside the campaign

- `venv/bin/pytest -q` after every task (regression, AC-041).
- `python -m smart_crawler.validate` on every run folder the campaign produces.
- Surface greps at each stage close (J-23, L17): `grep -rn --include=*.py -E "enable_stealth|use_undetected|magic=|simulate_user|from playwright|import playwright|litellm|openai|google.genai" discover_site smart_crawler prepare recon_pipeline` → 0.
- Absolute-path grep over every JSON in `outputs/` produced by tests → 0.
- `pip freeze` == lock at E1 close.

## 4. Stop conditions (everything else: continue)

Stop and write the reason into `RECOVERY.md` + engineering log, then end the session:
1. A real-evidence conflict with a contract field (CHK rule, or during E2).
2. Any action outside §1 surfaces would be required to proceed.
3. Any network action outside `hosts_allowed` + `127.0.0.1` would be required.
4. A destructive operation on anything outside `outputs/` would be required.
5. A mandatory AC cannot be met as bound (state which and why).
6. Two consecutive stop-rule exits on Cyberize during E2 (Pressable changed posture) — report, do not retry.

Not a stop: a failing test you can fix inside surfaces; a fixture you need to add; a session/context limit (checkpoint and resume); the Director being offline.

## 5. Resume rule

On any new session: read `agent_docs/ACTION/wf-scrapper-abm/CLAUDE.md`, then `RECOVERY.md`, then the last engineering log entry. Confirm disk matches (`git status --short`, `ls outputs/*/runs`). Continue from "next task". Never repeat a live Cyberize run to "make sure"; the evidence folder says whether it exists.

---

## 6. Prompts

### P0 — Task zero: environment, regression, smoke, REST probe (R6, R7). Paste before authoring review.

```
You are Claudy, Engineer seat, wf-scrapper-abm, Task zero (P0). Branch wf-scrapper-abm (confirm read-only). Director has approved installs for this task only, and the three REST GETs below.

A. Environment (R7): follow README §Install exactly on this clone (pyenv 3.12.3, venv, pip install -r requirements.txt, playwright install chromium). Prove: venv/bin/pip freeze sorted == requirements-lock.txt sorted; pip check clean; playwright install --dry-run chromium shows the build present.
B. Regression: venv/bin/pytest -q. Expect 54 passed. If not, STOP and report before C.
C. Smoke: printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com ; venv/bin/python -m smart_crawler.crawler --project CyberizeGroup --limit 10. Expect 10/10 200. Copy the run's manifest.json, absences.json, stage_log.txt into agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/p0/<run_id>/ (not the HTML).
D. REST probe (R6): with the pyenv-global requests (record its version), USER_AGENT from discover_site.sitemap_utils, 3 s apart:
   GET https://cyberizegroup.com/wp-json/
   GET https://cyberizegroup.com/wp-json/wp/v2/pages?per_page=1
   GET https://cyberizegroup.com/wp-json/wp/v2/posts?per_page=1
   Save the three bodies + headers to agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/p0/rest_probe/. Report: status codes; namespaces list; X-WP-Total / X-WP-TotalPages; whether yoast_head_json and yoast_head are present; top-level keys of one page object; whether content.rendered is empty on the sampled objects; whether these keys exist: id,type,link,slug,status,date,modified,title,excerpt,content,author,featured_media,categories,tags.
E. Compare D against ABM_CONTRACTS.md §2.5. List every mismatch (missing key, different name, different shape). No code changes.
Write agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/p0/P0_REPORT.md. Print the path and stop. No mutating git.
```

### P1 — Whole-campaign Plan Mode readback (Director approves once)

```
You are Claudy, Engineer seat, wf-scrapper-abm. Branch wf-scrapper-abm. P0 is complete and its report is at agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/p0/P0_REPORT.md.

Read, in order: agent_docs/ACTION/wf-scrapper-abm/CLAUDE.md, ABM_BRIEF.md, ABM_RULING_SHEET.md, ABM_CONTRACTS.md, ABM_ACCEPTANCE_SPEC.md, ABM_BUILD_INSTRUCTIONS.md, ABM_LEDGER.md, and the P0 report.

PLAN MODE. Produce one readback of the entire campaign, then stop for a single Director approval. The readback must contain:
1. Scope restated in your words: what Capture adds, what Prepare produces, what is out.
2. Per task C1…C6, CHK, P1…P6, E1, E2: the files you will create/modify, the tests you will add, the AC IDs each task closes, and the check that proves it. Keep it to a table plus short notes.
3. Every place the contracts or spec are ambiguous, underspecified, or conflict with repo reality or the P0 evidence. For each: your proposed reading. These become errata if the Director accepts them (J-21) — do not silently choose.
4. Every E-01 test rewrite you expect, by test name, with the contract reason.
5. Fixture plan: how tests/fixture_server.py serves F-01…F-14, how regen_fixtures.py keeps F-09 honest.
6. Live-run plan for CHK smoke and E2, with the budget you will enforce.
7. Your stop conditions restated, and your checkpoint cadence.
8. Anything in ABM_BUILD_INSTRUCTIONS.md §1 surfaces you believe is missing and why.

Do not write code. Do not start C1. End with: "Readback complete. Awaiting Director build approval."
```

After approval: Claudy proceeds C1 → E2 per §2, logging per `ABM_EXECUTION_RECORDS.md`, stopping only per §4. Director trigger to start is one line: "Build approved. Go."
