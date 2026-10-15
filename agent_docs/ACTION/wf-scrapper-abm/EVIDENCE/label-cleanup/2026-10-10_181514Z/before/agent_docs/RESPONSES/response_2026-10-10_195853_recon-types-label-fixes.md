# Recon fixes complete — REST verification succeeded

**Done:** type discovery now reads `/wp-json/wp/v2/types` without `_fields` and extracts the required properties locally. Later generic labels no longer overwrite informative candidate headings. The existing collector is unchanged.

**Proof:** eight pre-fix behavioral failures were retained; all **35 focused checks passed** afterward, including native localhost Chromium with a realistic WordPress type-map filter. The one authorized live check made **three planned REST calls**, all HTTP200: **33 type descriptions**, **42 advertised pages / one sampled page record**, and **166 advertised posts / one sampled post record**. No cleanup error was reported. No blog was refetched, pagination followed, custom-type collection read, media enumeration, full content request or retry performed.

**Next move:** JARVIS reviews the diff/results; Tony reviews the preserved candidate choices. No human choices, approved plan or full collection were created. Independent QA **NOT RUN**; Prepare remains outside scope.

## What changed and why

- `recon_pipeline/decide.py`: removes `_fields` only from the types URL; locally extracts `name`, `slug`, `rest_base`, `rest_namespace`. Full type response bytes remain evidence. Pages/posts metadata still use the existing nine projected fields.
- Candidate labels: normalized generic Read Post/Read More/Continue Reading/Learn More/View Post links cannot replace an informative label. An informative heading can replace an earlier generic label. Every source locator is preserved; these are labels observed on a referring page, not verified destination titles.
- `tests/test_decide.py`: the types fixture now filters the **type-name map**, returning `[]` for the old property-only filter and supporting explicitly type-rooted selectors. The native fixture uses it. The old assertion requiring `_fields` on every REST URL changed to require no query on types and exact projection on collection metadata. Other selection/scope/pacing/refusal/import assertions remain.
- `DECIDE.md`: current types and label rules plus the scoped follow-up authority. Checkpoint records below add factual observations while retaining previous text.

Exact scoped source/test/instruction diff: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/source-test-doc.diff.txt`. Full changed source snapshots: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/source-final`. No collector, dependency, custom controller or other product source changed.

## Live results — complete responses, limited enumeration

| Call | HTTP | Saved bytes | Advertised totals/pages | Actually sampled |
|---|---:|---:|---|---|
| wp_types | 200 | 25,278 | 33 type descriptions; no content records | not a collection |
| wp_metadata:page | 200 | 276 | 42 records / 42 pages | 1 record / first page only |
| wp_metadata:post | 200 | 363 | 166 records / 166 pages | 1 record / first page only |

All final URLs matched their exact requested URLs; no redirect chain was recorded for these planned responses. The three JSON bodies were complete and their length/SHA-256 checks matched. Both metadata samples contained exactly `id, link, title, type, slug, date, date_gmt, modified, modified_gmt`; neither contained `content`. Projection was honored for these two objects. Full-content availability was **not tested**.

- Page **9067**: “Full SEO Audit”, `https://cyberizegroup.com/full-seo-audit/`.
- Post **11945**: “How to Regain Consistency with Facebook Ads After the Andromeda Update”, `https://cyberizegroup.com/facebook-ads-andromeda-update/`.

The posts sample is the previously flagged post11945. Its historical empty `content.rendered` evidence remains unchanged; this metadata-only request cannot confirm or resolve that content gap. Advertised X-WP totals are server claims, not 42/166 records captured by this check. X-WP-TotalPages is 42/166 **for per_page=1**. Only page1 was fetched; no whole-collection coverage claim.

Exact live URLs:

- `https://cyberizegroup.com/wp-json/wp/v2/types`
- `https://cyberizegroup.com/wp-json/wp/v2/pages?per_page=1&page=1&_fields=id%2Clink%2Ctitle%2Ctype%2Cslug%2Cdate%2Cdate_gmt%2Cmodified%2Cmodified_gmt`
- `https://cyberizegroup.com/wp-json/wp/v2/posts?per_page=1&page=1&_fields=id%2Clink%2Ctitle%2Ctype%2Cslug%2Cdate%2Cdate_gmt%2Cmodified%2Cmodified_gmt`

Transport: existing **Crawl4AI Chromium navigation**, using `after_goto Response.body()` decoded entity bytes. No separate Python HTTP client. Work elapsed **15.836579s**; recorder process elapsed **17.833129s**; exit **0**, `stop_reason=null`, `cleanup_error=null`; supervisor did nothing. Completion-to-next-planned-call gaps **5.000741117s** and **5.003063887s**, both at least five seconds. The 180-second work budget, existing 30-second REST deadline, response cap and ten-second cleanup timeout were retained. Passive counters observed three document requests/three HTTP200 responses; planned-call counts are not a universal browser-resource guarantee.

## Type names returned by the public description endpoint

- `attachment`
- `feedback`
- `jetpack_form`
- `jp_act_log_event`
- `jp_pay_order`
- `jp_pay_product`
- `jp_search_overlay`
- `nav_menu_item`
- `page`
- `post`
- `tcb_symbol`
- `thrive_layout`
- `thrive_section`
- `thrive_template`
- `tvd_content_set`
- `tve_cond_display`
- `tve_global_cond_set`
- `tve_lead_shortcode`
- `tve_notifications`
- `tve_saved_lp`
- `tve_user_template`
- `tve_video_data`
- `tvo_capture`
- `tvo_capture_post`
- `tvo_display`
- `tvo_display_post`
- `wp_block`
- `wp_font_face`
- `wp_font_family`
- `wp_global_styles`
- `wp_navigation`
- `wp_template`
- `wp_template_part`

These are **33 exposed type descriptions**, not proof that all corresponding collections permit anonymous reads. Attachment/media and every non-page/post collection were left unrequested; their totals and content remain unknown. No namespace guessing was used for the live samples: `wp/v2/pages` and `wp/v2/posts` came from the returned descriptions.

## Meaningful labels — offline proof from saved HTML

All nine original “Read Post” article rows retain the actual informative heading labels when the saved blog is replayed through the repaired discovery path:

- Old row **7**: `Read Post` → ....
- Old row **9**: `Read Post` → ....
- Old row **12**: `Read Post` → ....

The proof retains all original HTML source locators and the same stable IDs across all36 URLs. It is explicitly **IMPORTED_SAVED_HTML_REPLAY**, not a fresh recon run. No destination article was read. The generic-label list is deliberately small; it is not semantic title ranking or AI selection.

Original inventory version `b6bbf6e41195988cab053457c81bd91fed8d9560a84953add657c54d8bbcf291` and exact file SHA-256 `2ee9e4ac53dfb9fd630d06a7f86e43b2e9539ca07481b066bf657c37f1a7ee44` remain unchanged. All original rows stay UNDECIDED. The October7 filtered-types `[]` response, old captures, inventories and selections were preserved; **42,686 existing output/evidence/report files hash-verified unchanged**.

## Focused checks and source identity

Pre-fix: **8 failed / 27 deselected**, exit1, retained in `pre-fix-checks.log`. Final: **35 passed**, zero failures/errors/skips, pytest7.59s, exit0. No broad controller campaign or independent QA suite was rerun. Exact final command:

```bash
DECIDE_EVIDENCE=agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/focused-final PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q tests/test_decide.py --basetemp=/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/focused-final/fixtures -p no:cacheprovider --junitxml=/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/focused-final/junit.xml
```

Branch **`wf-scrapper-abm`**; full HEAD **`fb16b1b927a234d74a2c29c9044df33317ff8276`**. Starting work tree already contained the October7 checkpoint changes and recon report/evidence (exact `git-status-before.txt` retained); that work was preserved. No Git mutation was performed.

Before: 50-file source `ebc6e8310ce4aab49a93ec6cc3c2011fbddeb404642362a6fc442a71ae77b864`. Tested/live/final unchanged candidate: **50-file SHA-256 `32cbd7e9f47137afb754b4954bc402ddae7319f2153895f8c16e092e82b91f2f`**. Inventory procedure: hash all files under smart_crawler/recon_pipeline/prepare/discover_site/tests excluding `__pycache__`, then SHA-256 the sorted compact JSON path→hash map. Only `recon_pipeline/decide.py` and `tests/test_decide.py` differ in that inventory; every collector/helper/legacy product file is unchanged.

## Changed files

- `recon_pipeline/decide.py`
- `tests/test_decide.py`
- `agent_docs/ACTION/wf-scrapper-abm/DECIDE.md`
- `RECOVERY.md`
- `agent_docs/ACTION/wf-scrapper-abm/ENGINEERING_LOG.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_CAMPAIGN_JOURNAL.md`
- `agent_docs/ACTION/wf-scrapper-abm/ABM_LEDGER.md`
- `agent_docs/SESSIONS/session_2026-10-10.md`

Fresh report/evidence paths are additional artifacts. Checkpoint changes are appended or prepended; historical records were not rewritten into passes. Historical accounting/media/shutdown/supervisor findings remain open.

## Handoff files

- Report: `agent_docs/RESPONSES/response_2026-10-10_195853_recon-types-label-fixes.md`.
- Compact results: `agent_docs/RESPONSES/response_2026-10-10_195853_recon-types-label-fixes_summary.json`.
- Exact diff: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/source-test-doc.diff.txt`.
- Focused checks/log/JUnit/native fixture evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/focused-final`.
- REST result metadata and three small bodies: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/rest-live`.
- Label/provenance proof: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/saved-label-proof.json`.
- Final source/preservation checks: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/source-final.json`, `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/preservation-final.json`.

A single review ZIP includes the report, exact diff, changed source snapshots, focused results, small REST bodies and preserved historical `[]` reference. It excludes dependencies, caches and bulky saved blog/capture bodies. No cookies, credentials or private headers are included. **STOP after this handoff.**
