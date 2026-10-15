# Shot 1 complete — current tool completion plan

**Recommendation: prepare this working tool for independent QA; do not start another feature build.** The agreed DECIDE → COLLECT → PREPARE capabilities exist and have dated engineering evidence. No required missing product feature was established by this read-only inspection. The remaining work is a current-scope acceptance/QA binding, final engineering readiness verification and a reproducible candidate handoff. Growth Call's preliminary helper classification is wrong, but the required agent inspection corrected the delivered package; it does not justify automatic iframe capture.

**State:** closeout assessment/playbook remain interim drafts; adoption and closeout deferred. This report proposes the next bounded pass, not permission to execute it. No product tests or live requests ran today; independent QA remains **NOT RUN**.

## Practical definition of done

Tony can choose explicit sitemap/default discovery, inspect a source-linked numbered inventory, record exact HTML/REST choices against that immutable version, and export a plan without collecting anything. COLLECT saves those approved responses durably, accounts honestly for failures/partial coverage, skips valid completed results on resume, and accepts explicit additions or refreshes without losing originals. PREPARE is an offline **agent skill**: validate hashes, inspect extraction, preserve useful content, then author source-linked architect facts, interpretation and gaps. Unavailable child content remains a gap. Release additionally needs candidate-bound independent QA and its owner decision.

Requirements are the [October 7 collector direction](../ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md), lines 5–12/26–34; [DECIDE contract](../ACTION/wf-scrapper-abm/DECIDE.md), lines 20–50; and [Prepare skill](../SKILLS/web-recon-prepare/SKILL.md), lines 12–38, plus Tony's subsequent accepted selections/follow-up and this Shot 1 instruction. These establish a selected sample tool, not exhaustive site coverage or form testing.

## Capability assessment

**Supported** below means dated engineering evidence, not independent QA PASS. Source/tests were inspected today, not executed.

| Capability | Current classification and evidence |
|---|---|
| Sitemap/default discovery, bounds and deduplication | **Implemented/supported locally.** [decide.py](../../recon_pipeline/decide.py), lines 149–175/236–279; [tests](../../tests/test_decide.py), lines 70–131/241–253. Saved default recon produced 36 document URLs. Current simplified sitemap access to the live site is **unverified**, not needed to prove parsing/queue controls locally. |
| Review labels, metadata, WordPress types/counts | **Implemented/supported.** [decide.py](../../recon_pipeline/decide.py), lines 60–115/281–352; [tests](../../tests/test_decide.py), lines 301–388. October 10: 33 type descriptions, 42 pages / 166 posts advertised, one metadata record each. October 11: nine labels match actual saved headings exactly. Unknown titles stay unknown; link labels are not verified destination titles. [Label correction](response_2026-10-11_001956_label-cleanup-tony-choices.md), lines 5–33. |
| Exact human selection and separate plan export | **Implemented/supported.** [decide.py](../../recon_pipeline/decide.py), lines 118–127/442–494; [tests](../../tests/test_decide.py), lines 152–190. Inventory/file hashes bind row choices to stable IDs; unknown/conflicting choices fail; one REST item does not authorize a collection. Tony's rows 1 / 3 / 9 exported with REST NONE. [Selected collection](response_2026-10-11_203505_first-selected-collection.md), lines 1–17. Approval is a recorded assertion, not CLI authentication. |
| Selected HTML and browser REST capture | **Implemented/supported.** [collector.py](../../recon_pipeline/collector.py), lines 54–86/260–338. October 7 blog + REST post 11945 saved; REST content was present-empty. October 11 three selected HTML pages saved; Andromeda has seven paragraphs / 15 list items. No full-content task is satisfied by recon metadata. [Two-item live check](response_2026-10-07_194146_selected-collector-live.md), lines 3–5/28–50. |
| Planned pacing, refusal stops and honest cleanup | **Implemented/supported.** [collector.py](../../recon_pipeline/collector.py), lines 347–474; [tests](../../tests/test_selected_collector.py), lines 56–81/161–190/257–266. Planned calls are sequential with configurable five-second default gaps; refusal preserves progress and stops later calls. Collection and cleanup outcomes differ. Redirect/background traffic adds requests and is not independently paced. |
| Durable checklist, resume, add and explicit refresh | **Implemented; engineering evidence exists, native interruption breadth insufficiently verified.** [collector.py](../../recon_pipeline/collector.py), lines 128–178/395–400/487–529; [tests](../../tests/test_selected_collector.py), lines 84–120/305–329. Interrupted/missing/corrupt/add/refresh cases use local transport doubles. Native success and dated live no-op resume prove byte acquisition and zero-browser skip, not every crash/filesystem failure. Existing focused checks support readiness; QA must assess those boundaries. |
| Opt-in REST pagination/count discrepancies | **Implemented/supported locally, current live broad coverage unverified.** [collector.py](../../recon_pipeline/collector.py), lines 187–243; [tests](../../tests/test_selected_collector.py), lines 127–158/236–255. Nonempty short pages continue to valid advertised end within approval bounds; missing headers/duplicates/count mismatches remain partial. Catching up the historical media library is outside this tool's selected scope. |
| Offline extraction, source index, architect brief/gaps | **Implemented/supported.** [helper](../SKILLS/web-recon-prepare/scripts/prepare_saved.py), lines 69–153, plus mandatory agent work in skill lines 25–38. [Tests](../SKILLS/web-recon-prepare/tests/test_prepare_saved.py), lines 42–134, cover content fidelity, corruption and preservation. October 11 three-page package: 20 references checked; October 13 reviewed follow-up: nine. The helper alone does not finish PREPARE. [Prepare results](response_2026-10-11_210309_prepare-v01.md), lines 3–27. |
| Preliminary embedded-page classification | **Defective helper hint; delivered agent-reviewed outcome supported.** Helper lines 52–66 treats `.tcb-post-content #tve_editor` as article; Growth Call disproves that rule. No dedicated iframe-focused regression is present. Required source inspection and a new reviewed package handle the gap; see decision below. |
| Release/independent QA readiness | **Missing current binding, not a missing feature.** [QAM state](../ACTION/wf-scrapper-abm/QAM/STATE.md), lines 3–9, still pins an October 2 blocker/source. [QA instructions](../ACTION/wf-scrapper-abm/QAM/EXECUTION_INSTRUCTIONS.md), lines 7–13, demand the old 48-AC / 24-group controller controls. They cannot govern this candidate unchanged. |

**Historical verification:** October 7 collector slice reported 59 checks (32 collector + 27 older checks); October 11 final DECIDE 55 checks and Prepare 10 checks. These separate runs are not one final-candidate regression or independent certification. Raw logs/JUnit identities are indexed in this package.

**Retired/outside active scope:** custom CDP interception/cancellation proof, per-redirect-hop pacing, bootstrap/global route accounting, old exact aggregate supervisor, mandatory six REST collections/media harvest and programmed P1–P6/E1/E2 packs. Automatic iframe collection, booking/forms, embedded AI, deployment and exhaustive visual/SEO/content completeness are also outside scope. The historical findings remain open; retirement is not a pass/waiver. [Interim assessment](response_2026-10-14_134641_abm-closeout_assessment-draft.md), unresolved-findings section, is reused unchanged.

## Growth Call decision

**The existing agent-review requirement adequately handles the agreed v0.1 scope.** Skill lines 27–30 explicitly require inspecting raw boundaries, classifying actual source and recording unvisited embeds. The unchanged helper produced an article / empty marker; agent inspection preserved that output and created a new booking-container package with the iframe and missing child content documented. [Actual follow-up](response_2026-10-13_223736_growth-call-follow-up.md), lines5–7/25–31.

Recommend no helper repair as a completion prerequisite. Make the saved Growth Call case an explicit QA review check: recognize the preliminary error, inspect the parent, report no native form labels/main copy, preserve the booking destination, and label authored headings and unknown child content. Do not accept helper exit0 as package readiness. If JARVIS instead requires reliable automatic type hints or machine-detected embed gaps, that is a small separately scoped helper/test repair; currently no such requirement exists. Never collect the iframe automatically or claim the helper was repaired.

## One bounded next pass — readiness, not another build

All steps below are **PROPOSED / NOT RUN** in Shot 1.

1. **Bind current scope prospectively.** JARVIS approves this definition of done and treatment of the preliminary Growth hint. Cody then synchronizes current README/root/module entries, DECIDE/COLLECT/skill status and QA/QAM pointers once, keeping dated historical text. Reconcile the existing canonical acceptance/master-plan mappings with the selected tool; retain the 48 IDs / 24 groups and explicitly seek dispositions for superseded obligations, never silently pass/waive them or create a competing QA plan. Acceptance: active entry points lead to the three current stages; no instruction resurrects the retired controller or requires the unfinished old Prepare build. No final playbook work.
2. **Verify the final engineering candidate locally once.** Run the existing three focused modules together in fresh evidence paths; no broad historical suite, new framework or live check. Acceptance: explicit modes/bounds, projected metadata/label fidelity, immutable selections, native loopback HTML/REST bytes, five-second default plus measured configured pacing,429 stop, durable completion, interruption/hash-invalid resume, addition-only capture and honest pagination gaps. Preserve unexpected failures; scope any necessary repair through JARVIS rather than inventing changes now.

   Proposed command (fresh paths required; not executed):

   ```bash
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q \
     tests/test_selected_collector.py tests/test_decide.py \
     agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py \
     -p no:cacheprovider --basetemp outputs/verification/NEW_TOOL_CANDIDATE/fixtures \
     --junitxml outputs/verification/NEW_TOOL_CANDIDATE/junit.xml
   ```

3. **Complete the factual handoff offline.** Recheck saved selections/checklists/index hashes; review the three-page content against raw sources and Growth Call's corrected classification/child-content gap. Acceptance: exact Andromeda 7paragraphs / 15items/6headings, Agency listing, navigation separation, source-resolving briefs, dated empty REST content and unknown images; no fabricated fields or changed originals. Export exact commands/results, fixture identities, limitations and source inventory, including untracked skill files. Existing packages supply the evidence; no new capture is justified.
4. **Tony commits; independent QA follows.** Tony alone stages the agreed files/creates the QA branch. Executor pins that actual commit, inspects it in Q1 and binds the canonical plan; **SOL decides the plan and evidence reuse before Q2**. Cody's checks remain engineering evidence. QA executes approved current-scope checks, adjudicates findings and any authorized repair/retest; required cleanup/closeout responsibilities remain explicit owner decisions. Final playbook adoption waits until tool/QA completion.

## Prerequisites, candidate and open decisions

- Actual checkout: `/home/moose/PYTHON/stark-web-factory-scrapper-v1`; branch `wf-scrapper-abm`; **full HEAD `fb16b1b927a234d74a2c29c9044df33317ff8276` plus dirty/untracked work**, not a completed candidate commit. 52-file source inventory `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` matches the interim checkpoint; no additional active Python files were found. Full pre-existing status and hashes are in [preflight](response_2026-10-14_173927_current-tool-completion-plan_review/preflight.json) and [source inventory](response_2026-10-14_173927_current-tool-completion-plan_review/source-inventory.json).
- Observed installed Python 3.12.3, Crawl4AI 0.9.3, Playwright 1.52.0, BeautifulSoup 4.13.4, pytest 8.3.5, markdown-it-py 4.2.0. Dated collection records report Chromium 136.0.7103.25; no browser was started today. Lock SHA `e6c3e1a9a89f6cd8f5dfb71694c74d54d6b34237929f06a0ce3aa519b89a594c`. Clean-environment install, `pip check`, complete normalized lock comparison and launch identity remain unexecuted readiness checks, not evidence of an environment defect. Keep existing lock/direct declarations unchanged. [Install binding](../../README.md), lines 29–77.
- The real three-page Prepare test hardcodes an ignored saved collection ([test](../SKILLS/web-recon-prepare/tests/test_prepare_saved.py), line 100). Source checkout alone will not supply it. Bind/provision its checklist, metadata and bodies read-only for QA; the retained first-page Prepare review ZIP contains those inputs. Growth review has its own saved bundle. Do not make QA depend on unavailable chat or a moved Downloads copy.
- **JARVIS/Tony decision needed:** current acceptance/QA scope and prospective dispositions of retired requirements; no product expansion. **SOL decision needed later:** candidate-bound plan/reuse; actual Executor session pending. No active requirement establishes automatic iframe extraction, exhaustive custom-type recon or whole-site media coverage.
- **Proposed live scope: zero calls.** Existing saved live results plus native loopback controls are sufficient for the readiness pass. Any later QA access check needs a concrete uncovered criterion, explicit URLs/bounds and Tony's separate allocation. Historical media 1,661 / 1,753, two unconfirmed shutdown aborts, stopped-run bootstrap/route mismatch and supervisor-counter gap stay open; no new repair obligation is inferred.

## Handoff

- **`response_2026-10-14_173927_current-tool-completion-plan.md`** — the completion plan.
- **`START_HERE.md`** — ZIP entry point and requested reviewer decision.
- **[preflight.json](response_2026-10-14_173927_current-tool-completion-plan_review/preflight.json)** — branch, full HEAD, existing dirty paths and installed versions.
- **[source-inventory.json](response_2026-10-14_173927_current-tool-completion-plan_review/source-inventory.json)** — the unchanged 52-file source identity.
- **[supporting-material.json](response_2026-10-14_173927_current-tool-completion-plan_review/supporting-material.json)** — supporting files with sizes and hashes.
- **[historical-observations.json](response_2026-10-14_173927_current-tool-completion-plan_review/historical-observations.json)** — dated collection outcomes, kept separate from today's inspection.
- **[inspection-checks.json](response_2026-10-14_173927_current-tool-completion-plan_review/inspection-checks.json)** — preservation and document-link checks.
- **`FILE_HASH_INVENTORY.json`** — ZIP member hashes.

Relevant current source/tests/skill and small prior result records are included for review; the ZIP is not a runnable full environment.

This pass writes only the report/review metadata and normal recovery/session/changelog checkpoint. Source, tests, dependency files, captures, prior drafts and evidence are preserved. Raw bodies, runtime caches, dependencies, secrets and bulky historical evidence are excluded; precise paths/hashes remain in the source indexes. **STOP: awaiting review/authorization of readiness work; implementation and independent QA have not begun in this pass.**
