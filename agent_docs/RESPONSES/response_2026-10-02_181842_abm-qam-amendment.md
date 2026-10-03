# Web Recon ABM/QAM amendment — DONE, awaiting JARVIS review

**Revision 1.1 is ready for JARVIS review. It is not cleared for build.** The extraction rulings and QAM workflow are applied; four material decisions remain explicit. No BUILD_READBACK, implementation, QA execution or live experiment occurred.

Director Tony Stark · Architect JARVIS · Engineer Cody. **Provenance: JARVIS Architect amendment under Tony’s delegated authority.** Date: 2026-10-02 (Asia/Dhaka).

## What changed and why

- Kept rendered Crawl4AI capture and browser-session discovery/REST; removed executable root REST enumeration and fallback-client assumptions. Preserved declared collections, pagination, all returned fields and available SEO, with demonstrated True image wait/90-second timeout/three-second delay/BYPASS/USER_AGENT source. [ABM_CONTRACTS.md](../ACTION/wf-scrapper-abm/ABM_CONTRACTS.md), line 45.
- Synchronized five-second completion-based operation pacing, zero retries/switching, first intentional refusal/challenge stop, scoped redirects and in-scope media HEAD. Background resources and normal POSTs are observed separately; no form actions. Old policies are retained as superseded history.
- Corrected collection-byte hashes versus serialized object derivatives, object→response/array-position provenance, complementary REST/rendered content, optional missing/null fields, one page outcome per route, invalid-versus-valid-partial handling and two-embed F-07 count. [ABM_CONTRACTS.md](../ACTION/wf-scrapper-abm/ABM_CONTRACTS.md), line 145; [ABM_CONTRACTS.md](../ACTION/wf-scrapper-abm/ABM_CONTRACTS.md), line 203; [ABM_ACCEPTANCE_SPEC.md](../ACTION/wf-scrapper-abm/ABM_ACCEPTANCE_SPEC.md), line 89.
- Added the minimal QAM lane and module Engineer entry; retained canonical acceptance/QA plan/ledger/journals. Separate Q1 Executor inspection → SOL plan decision → Q2 execution; explicit product-repair scope/re-pin; Tony cleanup accepted before final Gate Q; exact Lead certificate carried into JARVIS closeout. Independent cold-read, whole-app checks, Astra/fresh-Fable reviews and RRM remain. [QA/MASTER_QA_TEST_PLAN.md](../ACTION/wf-scrapper-abm/QA/MASTER_QA_TEST_PLAN.md), line 70 and [QAM entry](../ACTION/wf-scrapper-abm/QAM/README.md).

The packet retains **48 AC IDs, 24 QA groups and all build stages**. New E-05–E-12 use current delegated provenance; no earlier E-05–E-09 approval trail was found or invented. Historical R1–R8/E-01–E-04/CJ entries remain intact. [ABM_ACCEPTANCE_SPEC.md](../ACTION/wf-scrapper-abm/ABM_ACCEPTANCE_SPEC.md), line 158.

## Actual checkout and preservation

Repository: `/home/moose/python/stark-web-factory-scrapper-v1`  
Branch: `wf-scrapper-abm`  
Base HEAD: `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f`

This base SHA is **not** the completed implementation commit. Tony has not committed an ABM candidate; QA candidate/session/plan approvals and certificates remain PENDING. The ledger’s engineer/QA results remain NOT STARTED/NOT RUN.

Before this amendment, the tree already contained eleven historical response deletions with corresponding untracked files in OLD, plus untracked diagnostics/reports/ZIPs. I did not perform those moves/deletions or repair them. Exact initial status:

```text
 D agent_docs/RESPONSES/BIM001_GATE_Q_RECORD_2026-09-07.md
 D agent_docs/RESPONSES/BIM001_chunk1_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk2_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk3_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk4_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk5_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk6_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_closeout_2026-09-07.md
 D agent_docs/RESPONSES/BIM001_complete_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_handoff-read_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_plan_2026-09-06.md
?? agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/access-check/
?? agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/browser-check/
?? agent_docs/RESPONSES/OLD/BIM001_GATE_Q_RECORD_2026-09-07.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk1_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk2_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk3_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk4_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk5_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk6_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_closeout_2026-09-07.md
?? agent_docs/RESPONSES/OLD/BIM001_complete_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_handoff-read_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_plan_2026-09-06.md
?? agent_docs/RESPONSES/response_2026-10-01_204419_web-recon-architect-intake.md
?? agent_docs/RESPONSES/response_2026-10-01_210015_web-recon-access-check.md
?? agent_docs/RESPONSES/response_2026-10-01_213112_original-scraper-comparison.md
?? agent_docs/RESPONSES/response_2026-10-01_213112_original-scraper-comparison.zip
?? agent_docs/RESPONSES/response_2026-10-01_213421_original-scraper-comparison.md
?? agent_docs/RESPONSES/response_2026-10-01_213421_original-scraper-comparison.zip
?? agent_docs/RESPONSES/response_2026-10-01_220017_bim001-browser-reproduction.md
?? agent_docs/RESPONSES/response_2026-10-01_220017_bim001-browser-reproduction.zip
?? agent_docs/RESPONSES/response_2026-10-02_124310_useful-extraction.md
?? agent_docs/RESPONSES/response_2026-10-02_124310_useful-extraction.zip
?? agent_docs/RESPONSES/response_2026-10-02_132257_paced-article-batch.md
?? agent_docs/RESPONSES/response_2026-10-02_132257_paced-article-batch.zip
```

## Evidence incorporated — engineering observations, not certification

The October 1 intake/comparison and October 1–2 capture reports are preserved and included. The first browser attempt reached HTTP 200 but its wrapper interrupted a background POST. Corrected extraction verified nine blog article headings/links. One same-page Chromium `window.fetch` read returned post 11945 identity/title/link with empty content.rendered. Three paced browser article captures then contained substantive body text; no REST request was repeated.

**Article 2’s abrupt ending remains a caveat.** Hidden/deferred completeness, current sitemap success, full REST/Yoast fields, pagination/media coverage, full-site reliability and earlier 429 cause remain unknown. Five-second pacing is an adopted rule, not a proven cause of success. [ABM_AMENDMENT_1_1.md](../ACTION/wf-scrapper-abm/ABM_AMENDMENT_1_1.md), line 15 provides report and local evidence paths.

## Amendment → file → AC/test mapping

[ABM_AMENDMENT_1_1.md](../ACTION/wf-scrapper-abm/ABM_AMENDMENT_1_1.md), line 32 contains the full mapping. Summary:

| Amendment | Main files / sections | ACs | QA groups |
|---|---|---|---|
| E-05 pacing/stopping/background | Contracts §1.4/manifest; build C2–C5; fixtures/acceptance; QA | 005,006,010,013,016,017,040–042 | T-04,05,07,08,11,21,22 |
| E-06 transport/settings | Contracts §1.4/2.1–2.5; C1–C4; F-02/03; regression exceptions | 005,007,009,011–013,025,041 | T-04,06,07,08,15,22 |
| E-07 redirect/media scope | Contracts §1.4/2.6/2.7; C3/C5; QA | 005,015,018,028,041 | T-04,10,11,22 |
| E-08 response fidelity/content | Contracts §2.4/2.5/2.8/3.3–3.5; C4/P2/P3; F-02 | 011–014,021,024,025 | T-08,09,13,15 |
| E-09 route/partial validity | Contracts §2.8; CHK/P1/P6; F-10/12 | 008,016,019,020,023,029,038 | T-06,11,12,14,17,20 |
| E-10 forms/embeds | Contracts §3.6; AC-026/F-07; P4 | 026 | T-16 |
| E-11 readiness/history | Brief/build/rulings/recovery; open decisions | 001,039–042,047; open 038/044 | T-01,20,21,22,23 |
| E-12 QAM/authority | Entries/records/ledger/QA/QAM/journal | 021,035,036,045–048 | T-01,13,19,20,24; workflow covers all groups |

## Remaining decisions — one consolidated review

1. **M-01 installation:** Seven direct pins do not reproduce the 98-pin lock; P0 recorded 16 transitive drifts. Recommend making the existing `requirements-lock.txt` install the canonical AC-001/README path, followed by pip check and normalized freeze comparison, recording platform/Python/browser/lock identity. No dependency files changed.
2. **M-02 complete fixture:** F-09 derives from F-01’s 404 route, yet AC-038 requires complete. Recommend an explicitly complete F-09 variant; retain F-01 failure coverage and structurally valid F-12 losses. No criterion was quietly weakened.
3. **M-03 shared smoke allocation:** Historical P0 smoke never ran, while CHK requests a new integrated smoke. Recommend expressly allocating CHK’s existing limit-10 run to the smoke objective; retain two E2 full runs and let SOL decide QA reuse. No extra run granted.
4. **M-04 sentinel scan:** AC-044’s zero-hit scope includes governing text that deliberately names the fixture sentinel. Recommend a precise generated-artifact scan with only named fixture/governing-source exclusions and a negative control; no blanket report exclusion.

Exact conflicting text, recommendations, owners and blocked ACs are in [ABM_AMENDMENT_1_1.md](../ACTION/wf-scrapper-abm/ABM_AMENDMENT_1_1.md), line 49. Missing standalone park/old errata artifacts and unrecoverable older live outputs remain disclosed gaps. Runtime/browser transport controls still need future fixture proof; no current setup/regression checks were run.

## Existing authority and budgets

R1–R5/R8 still govern identity, donor lessons, single invocation/raw delivery, two full E2 runs, cold-read and output retirement. Old R6/P0/recovery executable sequences are superseded. CHK smoke and E2’s two full runs remain visible, **NOT RUN**; no budgets spent/enlarged. SOL decides candidate-bound reuse so QA does not automatically repeat engineering collections. [ABM_AMENDMENT_1_1.md](../ACTION/wf-scrapper-abm/ABM_AMENDMENT_1_1.md), line 62 contains the shared evidence/allocation register. Historical duration/storage estimates remain estimates.

## Documentation checks and changed files

Documentation checks only: 48 unique AC rows and 48 ledger rows; 24 groups cover all ACs and match the ledger; original task sequence retained; 113 current local Markdown links checked; all 7 contract JSON examples parse; manifest policy example matches the amendment; `git diff --check` clean. Historical R1–R8/E-01–E-04/CJ-007–CJ-014 text preserved. Active policy/ownership/cleanup wording reviewed; unresolved literal issues remain expressly blocked. **No product tests or independent QA were run.**

Baseline SHA-256 comparison: 1146 existing tracked/nonignored files checked; 1132 unchanged, 14 authorized documentation edits, zero newly missing files. Existing evidence and source-playbook files in that baseline are unchanged. Ignored caches/dependencies/bulk outputs are outside this hash count and were never opened for write. No product/test/dependency change, deletion, Git mutation, install, external request or deployment.

**Modified documentation (14):**

- `CHANGELOG.md`
- `CLAUDE.md`
- `RECOVERY.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_ACCEPTANCE_SPEC.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_BRIEF.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_BUILD_INSTRUCTIONS.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_CAMPAIGN_JOURNAL.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_CONTRACTS.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_EXECUTION_RECORDS.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_LEDGER.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_RULING_SHEET.md`
- `agent_docs/ACTION/wf-scrapper-abm/CLAUDE.md`
- `agent_docs/ACTION/wf-scrapper-abm/QA/MASTER_QA_TEST_PLAN.md`
- `agent_docs/ACTION/wf-scrapper-abm/QA/README.md`

**New documentation (10), plus this response and ZIP:**

- `agent_docs/ACTION/wf-scrapper-abm/ABM_AMENDMENT_1_1.md`
- `agent_docs/ACTION/wf-scrapper-abm/AGENTS.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/AGENTS.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/CLAUDE.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/EXECUTION_INSTRUCTIONS.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/README.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/MANIFEST.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/README.md`
- `agent_docs/ACTION/wf-scrapper-abm/QAM/STATE.md`
- `agent_docs/SESSIONS/session_2026-10-02.md`

## Package and next move

ZIP: `agent_docs/RESPONSES/response_2026-10-02_181842_abm-qam-amendment.zip`. It contains START_HERE, this response, complete revised ABM/QAM/QA governing documents, supporting instructions/reports and dependency declarations, a hash inventory, documentation-check results, scoped amendment diff and clearly marked pre-amendment document history (including RECOVERY). It excludes secrets/.env, cookies, dependencies/caches, raw capture bodies and bulky historical evidence. References to excluded raw evidence remain precise; missing files are not fabricated. Packaging is instruction-driven, not a claimed product exporter.

**Next: JARVIS reviews revision 1.1 and M-01–M-04. Stopped here. BUILD_READBACK and C1 were not performed.**
