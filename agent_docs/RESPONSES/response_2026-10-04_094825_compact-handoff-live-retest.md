# Compact-handoff live retest — INCOMPLETE; stopped

**One attempt ran, exited 2, and stopped on `interception_error:Error`.** It retained four complete sitemaps, 194 discovered routes, eight successful route HTML captures plus a separate homepage bootstrap, and 197 media URLs. **REST was never reached.** This attempt provides no live verdict on the repaired posts-body handoff.

The allocation is consumed. No retry, alternate client, probe or repair followed. **Next move: JARVIS reviews the controller failure. Prepare remains ON HOLD; independent QA remains NOT RUN.**

## Identity and execution

No post-correction live retest existed before this attempt: existing manifests, recorder results and checkpoint records ended at the earlier deadline-repair run. Actual checkout is `/home/moose/PYTHON/stark-web-factory-scrapper-v1`; branch `wf-scrapper-abm`; HEAD `366f9830ba7b9bfb91f17b8655fd37467410123b` plus preserved dirty/untracked work.

All 65 reviewed source entries matched before execution and remained unchanged afterward:

`4166482e389d46c7680e18ae11a0406ebe893c3a28631a9f7e04d455614a5afe`

Exact command, executed once through the existing recorder with its locator changed to the fresh evidence directory:

```bash
venv/bin/python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com --limit 10 --skip-prepare --no-media-head --max-operations 120 --max-seconds 1800 --max-bytes 100000000 --max-aggregate-bytes 100000000
```

Start `2026-10-04T03:42:08.770043+00:00`; finish `2026-10-04T03:44:48.750513+00:00`; **159.980s including teardown/finalization**. Recorder exit 2; command log ceiling was not reached. Installed runtime: Python 3.12.3, Crawl4AI 0.9.3, Playwright 1.52.0, Chromium 136.0.7103.25. Full identity and settings remain in the raw manifest. Existing `ignore_https_errors=True` was unchanged; no security/configuration changes were made.

## Actual collection

Four complete XML sitemap bodies, **102,866 bytes**, parse successfully and match their recorded hashes. Robots.txt was also complete at 175 bytes. Discovery found 194 routes: 167 post, 18 page and 9 category entries.

| Sitemap | Bytes | Entries |
| --- | ---: | ---: |
| `sitemap_index.xml` | 662 | 3 |
| `post-sitemap.xml` | 93,198 | 167 |
| `page-sitemap.xml` | 7,353 | 18 |
| `category-sitemap.xml` | 1,653 | 9 |

Eight route HTML files contain usable saved content. Paragraph counts below are inspection aids after excluding script/style/navigation/header/footer and selecting article/main when available; they do not prove completeness of hidden/deferred content. The blog is an index.

| Captured route | HTML bytes | Paragraphs ≥90 characters |
| --- | ---: | ---: |
| `/blog/` | 600,754 | 1 |
| `/web-design-process/` | 380,939 | 33 |
| `/what-to-look-for-in-ppc-agency/` | 455, 182 | 100 |
| `/our-covid-19-plan/` | 378,914 | 5 |
| `/5-foundational-principles-for-online-success/` | 426,888 | 65 |
| `/5-mistakes-real-estate-agents-make/` | 400,433 | 82 |
| `/covid-19-safety-tips-for-the-2020-pandemic/` | 394,549 | 4 |
| `/on-page-seo-audit/` | 424,565 | 74 |

The homepage bootstrap separately succeeded and is saved as `discovery/bootstrap.html` (**410,002 bytes**). Thus nine successful document bodies exist, while manifest route accounting reports **8 captured,1 failed, 185 skipped**. **Finding:** the homepage route itself is marked skipped after the stop, although its bootstrap evidence exists. These are disclosed separately rather than inflating captured-route counts. The failed tenth slot was `/what-to-expect-from-a-ppc-agency/`: HTTP 200 was observed, but it has no successful saved HTML file.

**REST:** pages/posts/media/categories/tags/users were all skipped after the controller stop. Posts bytes 0, objects 0, no response file, no observed pagination totals and no pagination attempted. This is **not an empty successful collection or a capped response**. The configured `per_page=100`, complete-field policy and 10 MiB cap were unchanged. No response reached that cap in this attempt. The prior run’s 42 REST pages remain preserved; they are not counted as this run's results.

**Media:** 197 inventoried URLs: 169 internal,10 external, 18 staging. In-scope HEAD reads were disabled by `--no-media-head`; off-scope URLs remained unprobed. No separate media-byte harvesting occurred. Browser rendering generated ordinary background resource traffic. The media stream is marked skipped for retrieval, despite the populated inventory.

## Failed operation and request-specific evidence

Op-15 was the intentional document. Its navigation received200 headers and a CDP loadingFinished event. An **incidental Image** request to `www.googletagmanager.com/td` (tracking query omitted) then produced:

`CDPSession.send: Protocol error (Fetch.continueRequest): Invalid InterceptionId.`

- Operation: `op-15`; session: `page-cdp-1`.
- Fetch ID: `interception-job-2132.0`.
- Network ID: `935232.2634`.
- Frame: `44951AED282F00EE2F45BA81D139F343`; redirect predecessor: null.
- Classification: `incidental`; resolution state: `error`.
- At failure: `confirmed_canceled=false`, `supported_incidental=false`.

Three earlier Invalid InterceptionId errors were recorded as confirmed incidental cancellations and did not stop collection. This fourth error was not supported as safe cancellation, and the controller retained its explicit stop. **Why this request's interception ID was invalid remains unknown.** No cause is assigned to an adjacent log event. No intentional 403/429 or explicit challenge was observed.

Offsets below start at op-15 monotonic 442472.171708513. Its advertised 180s document deadline was 442652.171699103. This was not a deadline failure or a REST result-serialization failure.

| Observed event | Offset | Full stage-log line |
| --- | ---: | ---: |
| operation_start | +0.000s | 9546 |
| intentional_intercepted | +0.084s | 9557 |
| pause | +0.085s | 9558 |
| intentional_dispatch | +5.002s | 9579 |
| cdp_response_headers | +5.081s | 9584 |
| interception_command | +5.168s | 9599 |
| cdp_loading_finished | +5.526s | 9723 |
| interception_command_error | +5.528s | 9725 |
| stop | +5.529s | 9726 |
| operation_complete | +10.883s | 9964 |
| interception_page_closed | +25.652s | 9966 |

There is no REST script/result handoff to assess: collection stopped beforehand. `operation_complete` correctly reports failure with the original stop reason. Page closure occurred during cleanup; finalization retained `interception_error:Error` at line 9967. No supervisor watchdog action was recorded. Browser-loaded background redirects are separate from intentional redirect accounting.

## Validation, limits and preservation

- Raw-reader validation: **PASS**, 23 files with references/hashes verified; validation left all raw bytes unchanged. This is a structurally valid **partial** package.
- Intentional dispatches: **15/120**, zero intentional redirect hops. **10/10 document slots**, including bootstrap and failed document.
- All 14 completion-to-dispatch gaps were at least 5s; minimum **5.001487s**. Zero intentional dispatches after STOP.
- Browser observations separately: 1,080 request events and 977 response events. These are not additional coordinator operations.
- Time: **159.980/1,800s**. Existing 30s reads, 180s document operations, 90s navigation, 10 MiB decoded cap and finalization reserve were retained.
- Persisted bytes: **8,208,742/97,000,000 raw**, **1,330,136/3,000,000 supporting**, **9,538,878/100,000,000 aggregate**. Supporting accounting includes new reports, metadata, recorder files and checkpoint growth.
- All **11,161 prior evidence/output/report files** unchanged, including the previous live run. Original checkpoint text preserved. No product/test/dependency edits, Git mutation, destructive action or deployment.

Current final-manifest counters are present. The earlier supervisor-finalization counter gap remains an unresolved historical finding; this normal-finalization run does not establish that path repaired. No regression suite was rerun during this live-only mission, and no independent QA result is claimed.

## Handoff files

- Report: `agent_docs/RESPONSES/response_2026-10-04_094825_compact-handoff-live-retest.md`
- Compact JSON summary: `agent_docs/RESPONSES/response_2026-10-04_094825_compact-handoff-live-retest_summary.json`
- Raw run: `outputs/CyberizeGroup/runs/2026-10-04T03-42-09Z`
- Recorder result: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/smoke/result.json`
- Failed-operation timeline: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/failed-operation-timeline.json`
- Sanitized interception excerpt: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/interception-excerpt.json`
- Collection inspection: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/collected-results.json`
- Pacing evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/operation-and-pacing.json`
- Reader/hash validation: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/reader-validation.json`
- Raw file inventory: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/raw-inventory.json`
- Preservation proof: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/preservation-result.json`
- Byte accounting: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/budget-accounting.json`
- Unchanged source inventory: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-04_034156Z/source-final.json`

RECOVERY, engineering log, campaign journal, acceptance evidence and session checkpoint are updated. **STOP — no remaining live allocation; no automatic repair.**
