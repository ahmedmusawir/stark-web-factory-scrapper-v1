# Q1 readiness report — STOP: candidate not established

**Executor:** Claudy, independent QA Executor session · **Date:** 2026-10-15 12:12 (+06) / 06:12Z · **Reviewer requested:** new QA Lead (plan review), Tony (candidate/branch)
**Verdict: BLOCKED at candidate binding. Q1 cannot pin a candidate.** Safe inspection was completed; a candidate-unbound DRAFT test plan is attached for the QA Lead's early review. No tests were run, no external requests, no installs, no product/QAM repair, no Git mutation.

## 1. Readiness check — actual state (read-only)

| Check | Observed | Status |
|---|---|---|
| Branch | `wf-scrapper-abm` (checked out) | as expected |
| Full HEAD | `fb16b1b927a234d74a2c29c9044df33317ff8276` — "7oct2026 - starting to build the selection process", committed 2026-10-07 | **base HEAD only, not a candidate** |
| Ancestry | merge-base with `main` = `73f96dbcf307e22cd30f7bc8066015f5e5e3f1d4` (bim001 close); 5 commits ahead on branch | fine |
| Working tree | 68 dirty/untracked entries at session start (23 tracked modified, 45 untracked); 70 after this Q1 wrote its session log and handoff directory. No stash. | **uncommitted candidate work** |
| Intended QA branch `qa/wf-scrapper-abm` | Does not exist locally or on `origin`. Only historical `origin/qa/web-factory-p1-bim000` / `bim001`. | **BLOCKER** |
| Candidate commit | None. Engineering handoff, QAM MANIFEST and RECOVERY all say "PENDING Tony". | **BLOCKER** |
| Tested source vs committed HEAD | 52 tested files: **48 byte-identical to HEAD blobs, 2 modified vs HEAD** (`recon_pipeline/decide.py` +12/−3 lines: unfiltered `wp/v2/types` read, local type-property projection, generic/weak link-label guard; `tests/test_decide.py` +121/−2), **2 untracked** (`agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py`, its test). HEAD alone contains no Prepare helper and cannot reproduce the 97-test run. | **candidate ≠ HEAD** |
| Source52 identity | Recomputed independently with the engineer's method (sorted path→sha256 JSON, compact separators): `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` — matches the claim; worktree bytes equal tested bytes. | verified |
| Dependencies | `requirements.txt` `231e1d8f…5f46`, `requirements-lock.txt` `e6c3e1a9…594c`; unchanged vs HEAD. | verified |
| Environment | Python 3.12.3; crawl4ai 0.9.3; playwright 1.52.0; beautifulsoup4 4.13.4; pytest 8.3.5; markdown-it-py 4.2.0; pip 24.0; Playwright cache has chromium-1169/1234 + headless shells. Clean-install reproducibility NOT checked (no installs authorized). | recorded |
| Fixtures | Both retained archives present with matching SHA-256 (`d54bbaf0…cc63`, `fdf18de8…b4a8`); all **34 manifest files present on disk and hash-match**; archives contain 0 `.runtime` members. Verified read-only; nothing restored. | verified |
| QAM routing | README/STATE/MANIFEST/EXECUTION_INSTRUCTIONS each open with the 2026-10-14 current-tool pointer → `CURRENT_TOOL_SCOPE.md`, Shot2 report, FIXTURE_ACCESS. Write lane `QAM/HANDOFFS` (packaging rules in its README). Governing sources: CURRENT_TOOL_SCOPE crosswalk (48 AC / 24 T), DECIDE.md, COLLECTOR_SIMPLIFICATION.md, Prepare SKILL.md, canonical acceptance/QA plan/ledger. | routes correctly |
| Historical vs current | Director GO C1–C6→CHK→P1–P6→E1–E2, E-20/E-21, CHK/E2 live allocations and "ENGINEERING BLOCKED AT CHK" headers are preserved history. **Not executed.** The thin `QAM/AGENTS.md` and `QAM/CLAUDE.md` (2026-10-02) still state the old checkpoint without a current pointer; the README they point to carries it. | distinguished; minor doc gap |
| Referenced files missing | `/home/moose/Downloads/WebFactory_Engineering_Readiness_and_QA_Handoff_2026-10-14_183709.zip` (named in `handoff.json`, sha `0fd71c9b…b940`) is absent from Downloads. All its content exists in-repo. `agent_docs/KIP_REGISTRY.md` (root CLAUDE.md protocol file) does not exist. | non-blocking |

## 2. Blockers and owners

1. **No candidate commit** — Tony. The specimen QA must bind is "HEAD + 4 uncommitted source files + current docs". Per EXECUTION_INSTRUCTIONS Q1, base HEAD plus dirty changes is not a candidate identity.
2. **QA branch `qa/wf-scrapper-abm` not created** — Tony.
3. **Plan identity unbindable** — Executor/QA Lead, dependent on 1–2. The attached plan is a DRAFT; its hash becomes the plan identity only after the candidate SHA is inserted.
4. Non-blocking, owner Cody/JARVIS: QAM thin entries lack the current pointer; Downloads convenience ZIP missing; KIP registry absent.

Nothing here requires a product change. When Tony commits, the expected check is: the 52 source paths at the candidate SHA hash to source52 `39b9728a…8314`. If Tony commits a different selection, the Executor recomputes and all engineering evidence reuse must be re-decided.

## 3. Independent inspection of the implementation (recon, not verdicts)

**Entry points confirmed in code.** DECIDE `recon|import|list|select|export` (`recon_pipeline/decide.py`, 530 lines); COLLECT `collect|resume|add|refresh` (`recon_pipeline/collector.py`, 537 lines; `__main__` routes to it); PREPARE helper `prepare_saved.py` (171 lines) + agent SKILL.md. Defaults match docs: gap 5 s, collector max-requests 100 / max-seconds 1800 / max-bytes 100,000,000 / response cap 10 MiB post-receipt; HTML 90 s nav + 3 s delay, 120 s outer; REST 30 s; cleanup 10 s; recon 12 requests / 3 pages / depth 1 / 300 s. Exit codes: collector 0/2/3/130, DECIDE 2 on stop/cleanup/refusal, Prepare refusal 2.

**Observations worth binding as test cases (not findings; expected behaviour must be fixed by the QA Lead/JARVIS first):**

- O1 *Any* transport error (timeout, navigation failure) on one planned item is classified `browser_read_failed` and **stops all later planned calls**, same as a refusal. Docs say refusal/rate-limit/challenge stop; the code stops more broadly. Bind the expected result (T-05).
- O2 `--max-bytes` sums every file under the collection root via `rglob`, including the Crawl4AI `.runtime/` profile and `.writer.lock`. Browser-profile growth counts against the persistence budget (T-22).
- O3 `.runtime/` lives inside each saved collection (12 KB in the three fixture collections). Browser profiles can hold cookies/storage. Fixture archives exclude it (0 members), but any future ZIP of a collection directory must too (T-23).
- O4 Prepare helper derives the repo root from its own path (`parents[4]`) and refuses a collection outside that root. Relocation/portability of the skill is therefore constrained (T-19).
- O5 Prepare removes `header, footer, nav` *inside* the chosen main boundary. WordPress themes often wrap the H1 in `article > header`; such an H1 would move to BOILERPLATE.md. Not triggered by the four saved pages; needs a synthetic negative case (T-13/T-14).
- O6 DECIDE's generic-label guard strips `' .…›»>'` before matching; "Read more →" (arrow) would still be accepted as a title. Heuristic edge case (T-06).
- O7 Growth Call: helper hint `.tcb-post-content #tve_editor` → "article" is a known, unrepaired limitation; the reviewed package corrects the type and documents empty native main text + booking iframe. QA must verify both initial and reviewed packages independently (T-16/T-20).
- O8 Pacing tests use gaps of 0.05–0.15 s and assert the default constant; a native 5 s gap exists only in dated live logs (Oct 11: 5.0008 s / 5.0041 s). One loopback run with `gap=5` on two items would prove default pacing in QA (T-04).
- O9 Challenge detection: 401/403/429, `cf-mitigated: challenge`, challenge-platform markup, or title+phrase block page. JSON content-type skips document parsing (quoted markup is source). Heuristic, as documented (T-07).
- O10 Four historical findings (media 1,661/1,753; two unconfirmed late aborts; stopped-run bootstrap/route accounting; supervisor counters) are on the retired path; QA Lead decides disposition. Not current-tool defects.

## 4. Assessment of the "97 passing tests" claim

- JUnit confirms **97 cases, 0 failures/errors/skips, 19.65 s, host StarkZorin, 2026-10-14T18:47:37+06:00**, split 32 collector / 55 DECIDE / 10 Prepare. The count is accurate as pytest counts.
- Breadth is smaller than the count: **58 distinct test functions; 39 cases are parametrized variants** (26 of the 55 DECIDE cases are label/heading variants; 14 collector cases are refusal/coverage/scope variants).
- Real browser coverage is thin by design: **3 real-Chromium loopback cases** (collector HTML+REST pagination; 429 stop; DECIDE sitemap/types/metadata) and **1 saved-real-capture case** (Prepare three-page exact content). Everything else uses transport doubles. Loopback is enforced by a `fixture_only` route guard aborting non-127.0.0.1 traffic; `outside.invalid` appears only as fixture data.
- The run executed on **uncommitted bytes** in the engineer's own session, with the engineer's basetemp/evidence paths. It is engineering evidence, not QA.
- Not independently re-run in Q1 (Q1 is inspect-and-bind; execution starts in Q2).

**Proposed evidence reuse for the QA Lead's decision.** (a) Accept engineering JUnit/pytest/native timelines as *candidate-compatible reference* only if the committed candidate's 52 files hash to source52; (b) require an independent Q2 re-run of the same three modules on the candidate with a fresh basetemp (≈21 s, zero network) — cheap enough that reuse-as-PASS is unnecessary; (c) reuse `fixture-manifest.json` + `restore-fixtures.py` as the restoration *procedure*, with QA re-verifying hashes; (d) reuse the 9 offline accepted-package checks as a *checklist*, re-executed by QA against the same hashed inputs; (e) do **not** reuse dated live captures as evidence of current pacing/access; they remain preserved observations.

## 5. What was delivered and what is next

- This report, a candidate-unbound DRAFT plan (`Q1_PROPOSED_TEST_PLAN_DRAFT.md`), independent machine checks (`checks/`), and readable governing inputs, packaged under `QAM/HANDOFFS` with a Downloads copy.
- **Next:** Tony commits the candidate and creates `qa/wf-scrapper-abm`; the Executor re-pins (SHA, 52-file hash, fixture hashes, environment) and converts the draft into the candidate-bound plan; the QA Lead approves/amends before any Q2 execution. The QA Lead may review the draft now to shorten that loop.
- No certificate, PASS, or Q2 result exists. All 48 AC QA states remain NOT RUN.
