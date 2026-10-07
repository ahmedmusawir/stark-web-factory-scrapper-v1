# DONE — DECIDE: recon and human selection

**Implemented and locally verified. 84 tests passed; no new live site traffic. The working collector is unchanged. Independent QA NOT RUN.**

DECIDE now discovers a bounded review inventory in an explicit sitemap or default-link mode, reads projected WordPress types/counts/metadata, saves Tony's explicit row/ID choices, and exports a plan for the existing collector. Discovery and plan export never start full collection. Prepare remains a separate future skill.

## Repository and preservation

- Branch: `wf-scrapper-abm`.
- Full HEAD: `2824afb773d02bb4e0e7387710f1e7917858be8e` plus preserved dirty/untracked work; no Git mutations.
- Final 50-file code/test inventory: `ebc6e8310ce4aab49a93ec6cc3c2011fbddeb404642362a6fc442a71ae77b864`.
- All prior 48 code/test files remain byte-identical, including the working collector, its entry point, offline inventory adapter, raw reader and existing tests. Prior identity remains `f031eb90585599a276d10a920746d4fd0286a3c260e8be4e6d4e5bc776b7d009`. Only two code/test files were added.
- **27,568 existing output/evidence/report files hash-verified unchanged.** Existing document text is retained verbatim with prospective checkpoint additions. [Preservation proof](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/preservation-final.json).
- Existing dirty work was already present from Part A, collector simplification and the two-item live check; exact starting status is retained in [git-status-before.txt](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/git-status-before.txt). No staged files, commits, branches, dependency changes, live traffic or deployment.

## Delivered behavior

| Area | Implementation |
|---|---|
| Explicit mode | `--mode sitemap` follows supplied or robots-declared sitemaps; `--mode default` reads pages and same-origin links. No mode fallback. |
| Bounded discovery | Shared request/time/pacing budget; configurable discovery page/depth and candidate bounds. Default mode downloads some HTML and ordinary resources. |
| Review | JSON plus numbered Markdown; stable IDs, URLs, available title/MIME/WordPress type/dates, source hashes, unknowns and limits. |
| WordPress | Projected public types and pages/posts/custom-type metadata; advertised counts distinct from enumerated IDs and review rows; no media enumeration/full-content request. |
| Human choice | HTML/REST inclusions and explicit exclusions by exact-version row or stable ID; unknown/conflicting selections rejected. |
| Scope export | One selected post exports its item endpoint with pagination false. A collection row requires explicit maximum pages. No automatic collection. |
| Known gaps | Optional validated saved collection carries historical empty-content warnings; post11945 remains flagged for HTML review if selected. No retry. |

The new command reuses **unchanged `BrowserTransport`** for rendering and browser-response bytes, the existing sitemap parser, and the offline inventory's stable-ID, formatting and raw-import functions. It does not instantiate the custom interception controller. New recon evidence is separate from collector output: no collector checklist is created, and exported capture items start pending even when recon metadata was saved.

## Exact usage commands

Full mode/bounds examples and collector add/resume integration: [DECIDE.md](../ACTION/wf-scrapper-abm/DECIDE.md).

The following is the **proposed small live check**, not executed or authorized by this local task:

```bash
venv/bin/python -m recon_pipeline.decide recon \
  --mode default --url https://cyberizegroup.com/blog/ \
  --out outputs/recon/CyberizeGroup-default-01 \
  --gap 5 --max-requests 4 --max-pages 1 --max-depth 0 \
  --max-rest-pages 1 --per-page 1 --max-candidates 100 --max-seconds 180 \
  --known-collection outputs/collections/CyberizeGroup-selected-live-01
```

Explicit sitemap alternative, also **not executed**:

```bash
venv/bin/python -m recon_pipeline.decide recon \
  --mode sitemap --url https://cyberizegroup.com/ \
  --sitemap https://cyberizegroup.com/sitemap_index.xml \
  --out outputs/recon/CyberizeGroup-sitemap-01 \
  --gap 5 --max-requests 8 --max-pages 2 --max-depth 1 \
  --max-rest-pages 1 --per-page 1 --max-candidates 500 --max-seconds 180
```

Offline import/list/select/export flow (only the separately recorded illustrative sample commands were run):

```bash
venv/bin/python -m recon_pipeline.decide import \
  --collection outputs/collections/CyberizeGroup-selected-live-01 \
  --out outputs/reviews/CyberizeGroup-imported-01

venv/bin/python -m recon_pipeline.decide list \
  --inventory outputs/reviews/CyberizeGroup-imported-01/inventory.json

# Substitute rows/IDs only after Tony reviews that exact inventory.
venv/bin/python -m recon_pipeline.decide select \
  --inventory outputs/reviews/CyberizeGroup-imported-01/inventory.json \
  --include-html ROW_OR_ID --include-rest ROW_OR_ID \
  --exclude OTHER_ROW_OR_ID --by Tony \
  --out outputs/reviews/CyberizeGroup-decision-01.json

venv/bin/python -m recon_pipeline.decide export \
  --inventory outputs/reviews/CyberizeGroup-imported-01/inventory.json \
  --decision outputs/reviews/CyberizeGroup-decision-01.json \
  --out outputs/reviews/CyberizeGroup-approved-plan-01.json
```

For the older raw-v2 input, substitute `import --raw outputs/CyberizeGroup/runs/2026-10-05T14-10-49Z --out NEW_DIRECTORY`. Every inventory/decision/export uses fresh paths. Human decisions store IDs plus inventory content ID and exact file SHA-256; reordering/reformatting cannot silently remap an old choice. Decision revisions are new files with the desired full set of choices; there is no implicit merge.

After a later authorized decision, the plan can feed the unchanged `recon_pipeline collect`, or `add --plan ...` followed by explicit `resume` on an existing collection. This task executed neither.

## Saved-data demonstration — illustrative, not Tony approval

The small sample is **IMPORTED_CAPTURE_INVENTORY**, ten candidates from the previously saved blog and REST11945 responses. It is not fresh recon. Its first four numbered rows are:

| Row | Observed title | Stable ID |
|---:|---|---|
| 1 | Digital Marketing Blog by Cyberize Group | `doc-0ddf88c0a3873299185f` |
| 2 | Boost Your Dental Practice with a Professional SEO Company | `doc-9c9f20df006630a8e5c2` |
| 3 | How to Regain Consistency with Facebook Ads After the Andromeda Update | `doc-c6b9265b51bf57660bb4` |
| 4 | Garage Door Repair PPC Agency – Get More Leads & Sales Now! | `doc-64e397f98cf595d53e06` |

The illustrative decision chooses HTML row **3**, chooses the same stable ID as a **single REST item**, and excludes row1 solely to demonstrate exclusion syntax. This is **not a recommendation or actual Tony decision**. The decision is marked example-only; every original inventory row remains UNDECIDED.

Resulting illustrative collector plan:

```json
{
  "pages": [
    "https://cyberizegroup.com/facebook-ads-andromeda-update/"
  ],
  "rest": [
    {
      "url": "https://cyberizegroup.com/wp-json/wp/v2/posts/11945",
      "paginate": false
    }
  ]
}
```

This contains no `_fields` projection and does not authorize all posts. Its separate review sidecar preserves `rest_content_rendered_empty` and `needs_HTML_review_if_selected`. The old REST content remains empty. No HTML article capture was triggered.

A second read-only import through the existing RawRun adapter produced **217** historical candidates. The old media count is still **1,661 unique versus 1,753 advertised** (92 missing), with all earlier partial/shutdown findings retained. These historical counts are not fresh-recon totals. **229 unique referenced source files** across the imports were hash-verified.

## Focused verification

**Final: 84 passed in 36.71 seconds; exit 0** — 25 DECIDE checks plus 59 unchanged collector/REST/raw-reader/offline-inventory checks. No independent QA campaign was run.

Exact recorded command (use fresh evidence paths for any future authorized rerun):

```bash
PYTHONDONTWRITEBYTECODE=1 DECIDE_EVIDENCE=agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/verified-final SELECTED_COLLECTOR_EVIDENCE=agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/verified-final venv/bin/python -m pytest -q tests/test_decide.py tests/test_selected_collector.py tests/test_rest_client.py tests/test_raw_reader.py tests/test_offline_inventory.py --basetemp=agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/verified-final/fixtures
```

Checks establish explicit modes/no fallback; same-origin candidate deduplication; request/page/depth/candidate limits; pacing and refusal stops; projected metadata/custom types/media exclusion; short-page continuation; unknown/changing totals, duplicate/count discrepancies and malformed metadata; exact row/ID/version mapping; unknown/conflicting-choice rejection; explicit whole-collection scope; single-item plan export; and recon/full-capture separation.

Native Chromium fixture: **4 planned calls** (sitemap, types, projected posts metadata and projected custom-book metadata), minimum completion gap **0.050621s** for a configured 0.05s fixture delay; no stop or reported cleanup error. The posts fixture advertises166 records but enumerates1, correctly remaining partial. The new recon runner defaults to five seconds; shortened fixture gaps verify its completion-based pacing without unnecessary waits.

The first native check hit a **test setup-order failure** because constructing the library before the runner created its fresh directory created that directory early. The fixture now creates the real browser at the runner's normal start point; the fresh-output guard remains. The initial failure and every later run are preserved. No existing assertion, expected snapshot or collector source was rewritten to get green.

## Limits and next move

- Same-origin applies to scheduled discovery and inventory URLs; ordinary browser redirects/resources can cause additional traffic. Off-origin final redirects stop further recon after observation. There is no old custom pre-dispatch redirect/cancellation proof.
- WordPress availability is bounded by the public types endpoint under the standard API mount (or explicit `--wp-base`). No root enumeration, namespace guessing, admin-only access or exhaustive type guarantee. Missing namespace metadata uses the standard wp/v2 convention.
- The server may ignore `_fields`; that response is retained as unexpected recon evidence, flagged partial and not paginated further. Metadata-only recon does not establish article-body availability, Yoast coverage or full-capture completion.
- Unknown HTTP MIME is distinct from a known WordPress type. Link labels can supply a candidate title without proving the destination title. Content/deferred-widget completeness remains unknown.
- Five-second pacing is for planned calls, including pagination; the numeric request cap is not a browser-resource/redirect cap. Response cap is post-receipt, not a streaming wire/memory bound; cleanup has a separate ten-second async timeout.
- No recon resume mechanism, automatic exclusion/ranking, embedded AI or Prepare skill was added. Existing collector add/resume is unchanged. Human approval is recorded, not authenticated by this CLI.

**Proposed next move:** Tony reviews the four-request default-mode check above. It reads the blog once, then projected public types and at most two exposed content-type metadata pages (pages/posts prioritized), one record each, five-second gaps, 180-second collection deadline, no media/content fields and no automatic collection. Browser subresources are additional traffic. **Not executed.**

## Changed files

- [recon_pipeline/decide.py](../../recon_pipeline/decide.py)
- [tests/test_decide.py](../../tests/test_decide.py)
- [README.md](../../README.md)
- [RECOVERY.md](../../RECOVERY.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [agent_docs/ACTION/wf-scrapper-abm/AGENTS.md](../ACTION/wf-scrapper-abm/AGENTS.md)
- [agent_docs/ACTION/wf-scrapper-abm/CLAUDE.md](../ACTION/wf-scrapper-abm/CLAUDE.md)
- [agent_docs/ACTION/wf-scrapper-abm/ABM_CAMPAIGN_JOURNAL.md](../ACTION/wf-scrapper-abm/ABM_CAMPAIGN_JOURNAL.md)
- [agent_docs/ACTION/wf-scrapper-abm/ABM_LEDGER.md](../ACTION/wf-scrapper-abm/ABM_LEDGER.md)
- [agent_docs/ACTION/wf-scrapper-abm/ENGINEERING_LOG.md](../ACTION/wf-scrapper-abm/ENGINEERING_LOG.md)
- [agent_docs/SESSIONS/session_2026-10-07.md](../SESSIONS/session_2026-10-07.md)
- [agent_docs/ACTION/wf-scrapper-abm/DECIDE.md](../ACTION/wf-scrapper-abm/DECIDE.md)

Generated report, checks, sample artifacts and evidence are additional files. No existing product/test file changed.

## Review handoff

- [Report — response_2026-10-07_201138_decide-recon-selection.md](response_2026-10-07_201138_decide-recon-selection.md)
- [Checks — response_2026-10-07_201138_decide-recon-selection_checks.json](response_2026-10-07_201138_decide-recon-selection_checks.json)
- [Exact new source/test diff — source-test.diff.txt](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/source-test.diff.txt)
- [DECIDE implementation — decide.py](../../recon_pipeline/decide.py)
- [Focused tests — test_decide.py](../../tests/test_decide.py)
- [Source inventory — source-inventory-final.json](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/source-inventory-final.json)
- [Numbered sample — INVENTORY.md](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/sample-final/review/INVENTORY.md)
- [Machine-readable sample — inventory.json](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/sample-final/review/inventory.json)
- [Illustrative choices — EXAMPLE_ONLY_decision.json](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/sample-final/EXAMPLE_ONLY_decision.json)
- [Illustrative plan — EXAMPLE_ONLY_collector-plan.json](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/sample-final/EXAMPLE_ONLY_collector-plan.json)
- [Executed offline demonstration commands — commands.json](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/sample-final/commands.json)
- [Final test output — pytest.log](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/verified-final/pytest.log)
- [Native loopback evidence — native-result.json](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/verified-final/native-result.json)
- [Preservation proof — preservation-final.json](../ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07_135659Z/preservation-final.json)

Stopped after the local handoff. **Independent QA NOT RUN.**
