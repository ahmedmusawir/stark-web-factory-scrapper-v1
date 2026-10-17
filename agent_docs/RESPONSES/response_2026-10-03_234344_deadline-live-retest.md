# Web Recon — deadline-repair live retest

**Outcome: useful evidence collected, but CHK remains INCOMPLETE.** The single authorized attempt exited **2** on **`read_deadline`** at the first posts REST read. No retry or repair followed. Allocation consumed; STOP.

- **Collected:** ten usable HTML captures,194 discovered routes, 42 REST page objects, 242 media URLs.
- **Sitemap repair retest:** all four sitemap bodies returned completely and parse as sitemap XML.
- **Still missing:** posts body/objects and the remaining REST collections. Posts200 headers and a network completion event did not yield a returned body.
- **Next move:** JARVIS reviews that retained handoff gap before further authorization. Prepare remains ON HOLD; independent QA NOT RUN.

## Identity and execution

Actual checkout: `/home/moose/PYTHON/stark-web-factory-scrapper-v1`. The prior lowercase `/home/moose/python/` location is absent. The uppercase checkout matches branch `wf-scrapper-abm`, HEAD `366f9830ba7b9bfb91f17b8655fd37467410123b`, and all 62 reviewed inventory entries:

`f2aaab42fa6c64ef1cb621566ad7d4c8e606814e4d9f1caa5013979324b1a27b`

Source stayed unchanged before, during and after this attempt. Pre-existing dirty work: eight tracked modifications (five checkpoint records plus browser_session.py and two test files) and 837 untracked paths, including the prior repair/evidence. Full status is preserved in `smoke/git-status.txt`; no product/test/dependency or Git mutation was performed.

Exact command, run once through the existing recorder:

```bash
venv/bin/python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com --limit 10 --skip-prepare --no-media-head --max-operations 120 --max-seconds 1800 --max-bytes 100000000 --max-aggregate-bytes 100000000
```

Recorder: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/recorder.py` with the `smoke` label and exact command above; only its locator path was changed. `ABM_QUIET_LOG=1` suppressed raw console output. Start `2026-10-03T17:35:56.151057+00:00`; finish `2026-10-03T17:39:40.941469+00:00`; **224.790 seconds**, including teardown/finalization. Python 3.12.3, Crawl4AI 0.9.3, Playwright 1.52.0, Chromium 136.0.7103.25; full runtime identity in raw manifest. No regression tests were rerun for this live-only mission.

## Collected content

All ten saved pages returned 200 and successful HTML capture. Counts below are inspection aids: paragraphs of at least 90 characters after removing script/style/navigation/header/footer, using the first article/main container when available. They do not certify hidden/deferred content completeness. The blog is an index, not a full article.

| Page path | HTML bytes | Substantive paragraphs |
| --- | ---: | ---: |
| `/blog/` | 570,243 | 1 |
| `/web-design-process/` | 380,935 | 33 |
| `/what-to-look-for-in-ppc-agency/` | 455,150 | 100 |
| `/our-covid-19-plan/` | 378,908 | 5 |
| `/5-foundational-principles-for-online-success/` | 426,887 | 65 |
| `/5-mistakes-real-estate-agents-make/` | 400,427 | 82 |
| `/covid-19-safety-tips-for-the-2020-pandemic/` | 394,542 | 4 |
| `/on-page-seo-audit/` | 424,101 | 74 |
| `/what-to-expect-from-a-ppc-agency/` | 424,460 | 81 |
| `/` | 441,333 | 1 |

The homepage bootstrap was reused, not navigated twice. Useful content includes the web-design process, PPC agency guidance and on-page SEO instructions. Exact files, titles, hashes and headings are in `collected-results.json`. Of 194 known routes, 184 were skipped under the ten-document allocation; the HTML stream remains partial for site coverage.

| Saved sitemap | Body bytes | Entries | Validation |
| --- | ---: | --- | --- |
| `discovery/sitemap_index.xml` | 662 | 3 children | Complete; XML valid |
| `discovery/post-sitemap.xml` | 93,198 | 167 routes | Complete; XML valid |
| `discovery/page-sitemap.xml` | 7,353 | 18 routes | Complete; XML valid |
| `discovery/category-sitemap.xml` | 1,653 | 9 routes | Complete; XML valid |

Sitemap total **102,866 bytes**; robots.txt complete at 175 bytes. Discovery counts 194 routes: 167 post-sitemap entries, 18 page-sitemap entries, 9 category routes. All four bodies have successful read-result receipts, saved hashes and valid XML; none is a retained partial body.

REST uses **Chromium same-page window.fetch / Response.body.getReader**, at the browser-decoded entity-byte boundary. `/wp-json/wp/v2/pages?per_page=100&page=1` returned a complete 1,459,408-byte JSON collection: 42 objects, matching its advertised 42/one page. Every sampled page object has yoast_head(string) and yoast_head_json(object); 40 have nonempty rendered content, 2 empty. These are observations of this collection only. Raw response and 42 serialized derivatives retain their linkage and hashes.

`/wp-json/wp/v2/posts?per_page=100&page=1` returned 200 headers advertising 166 objects/two pages, but **zero body bytes were handed back and saved**. It is explicitly incomplete, not an empty successful collection; zero usable post objects. The 167 sitemap entries versus 166 advertised REST posts is an observed difference, not a proven defect or cause. Media/categories/tags/users REST were skipped after stop. Nineteen route-to-REST mappings exist; this does not imply19 HTML captures.

Media inventory contains **242 URLs** from received HTML/REST: 201 internal, 12 external, 29 staging. Internal HEAD checks were disabled; 41 off-scope URLs remain untested. No separate media-byte harvesting occurred. The rendering browser did load ordinary image/background resources.

## Posts timeout — decisive timeline

All offsets are Python-observed monotonic seconds from op-17 start (`406135.267747896`, UTC 17:38:44 at one-second log precision). Setup and pacing consume the existing 30-second operation ceiling.

| Event | Offset | Stage-log line |
| --- | ---: | ---: |
| Operation starts; hard deadline 406165.267744910 | 0.000 |10674|
| Setup starts / identity bound / script submitted |0.003 /0.022 /0.023|10676–10678|
| Shared pacing wait begins; planned 4.714504s |0.038|10682|
| Intentional dispatch |4.760|10683|
| HTTP200 headers |8.637|10687|
| CDP Network.loadingFinished observed |12.977|10689|
| Scheduled cooperative abort boundary; execution not separately logged |29.000|10675|
| Python deadline STOP |29.758|10690|
| operation_complete: **failure/read_deadline** |29.760|10691|
| Browser requestfinished callback / page closed |54.261 /54.369|10692 /10706|

**No `read_result_received` event exists for op-17.** Native loadingFinished timestamp 406145.996278 is retained separately from its Python observation time. That event does not prove JS chunk processing or CDP result serialization completed. The repaired Python cutoff is 29.75s, inside the unchanged 30s hard limit; the observed stop matches that path. No supervisor watchdog stop or signal action is recorded. Finalization retained `read_deadline` (line 10711), not a successful/null-error terminal outcome. Why result handoff failed and why the later callback/closure took about 24.6s after STOP remain unknown. No cause is assigned to incidental interception events.

Request identity: op-17; Fetch `interception-job-2369.0`; Network `644661.2921`; frame `06C7C5B730C5F422D1152AF7C797D54C`; session label `page-cdp-1`. Intentional continueRequest completed normally at line 10685. Six separate Invalid InterceptionId events were logged as confirmed canceled **incidental** traffic (lines 521, 7686, 7692, 7705, 7713, 7715). Four failRequest cleanup errors followed closure (10707–10710); the original stop reason remained intact. Full recorded IDs/classifications and cancellation evidence are in `interception-excerpt.json`. No same-URL ambiguity, 403/429 or explicit challenge was observed.

## Validation and budgets

- **Raw reader:** exit 0, 69 files, 194 route outcomes; references/hashes valid; all raw hashes unchanged by validation. This establishes a structurally valid **partial** package.
- **Traffic:** 17/120 intentional dispatches,zero intentional redirects, 10/10 document slots. All 16 measured completion gaps >= 5s; minimum 5.001886s. Zero intentional dispatches after STOP. Separately, 1,148 browser request events and 1,085 response events were observed; these are not 1,148 intentional operations.
- **Time:**224.790/1,800s. Existing30s read, 180s document, 90s navigation, 10MiB decoded-response cap and 30s finalization reserve retained.
- **Persisted bytes:** raw **12,418,353/97,000,000**; all new supporting files/checkpoint growth **674,504/3,000,000**; aggregate **13,092,857/100,000,000**. Supporting accounting includes recorder, metadata, report/JSON, inventories and audit growth; runtime files 0 bytes.
- **Preservation:** all 8,062 prior evidence/output/report files unchanged; original checkpoint contents retained. Product/test source inventory unchanged.

The current final manifest includes dispatch/document/resource/status counters. The previously reported missing-counter gap in the older supervisor-finalized package remains a historical unresolved finding; this attempt does not prove that path repaired. Current transport settings include the existing `ignore_https_errors=True`; no security setting was changed. Source inventory hash in the raw manifest uses a different JSON representation; its per-file identities match the reviewed 62-file inventory. No full-crawl readiness or QA certificate is claimed.

## Handoff files

- Report: `agent_docs/RESPONSES/response_2026-10-03_234344_deadline-live-retest.md`
- Small JSON summary: `agent_docs/RESPONSES/response_2026-10-03_234344_deadline-live-retest_summary.json`
- Execution result: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/smoke/result.json`
- Timeout timeline: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/timeout-timeline.json`
- Interception evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/interception-excerpt.json`
- Operation/pacing evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/operation-and-pacing.json`
- Collected-content inspection: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/collected-results.json`
- Raw-reader result: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/reader-validation.json`
- Raw file hashes: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/raw-inventory.json`
- Preservation proof: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/preservation-result.json`
- Byte accounting: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/budget-accounting.json`
- Source inventory: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-03_173535Z/source-final.json`
- Raw manifest: `outputs/CyberizeGroup/runs/2026-10-03T17-35-57Z/manifest.json`
- Full retained stage log: `outputs/CyberizeGroup/runs/2026-10-03T17-35-57Z/stage_log.txt`

RECOVERY, campaign journal, engineering log, acceptance evidence and today's session record are updated. No Prepare/P1–P6/E1/E2, additional request, repair, install, deployment or Git mutation followed. **STOP — awaiting JARVIS review.**
