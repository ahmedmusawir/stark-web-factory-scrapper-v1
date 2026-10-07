# DONE — simpler COLLECT slice implemented

**59 local engineering checks passed. No live website requests. Independent QA NOT RUN.**

Tony can now supply selected page URLs and explicit WordPress REST scope, collect them, resume safely, and add URLs without refetching valid completed items. The active path uses installed Crawl4AI's ordinary browser lifecycle. The custom CDP interception controller remains preserved in the historical pipeline; it is not constructed by the new collector. DECIDE automation and the PREPARE skill were not built.

## Repository and preservation

- Actual checkout: `/home/moose/PYTHON/stark-web-factory-scrapper-v1` (uppercase path; configured lowercase path was unavailable).
- Branch: `wf-scrapper-abm`.
- Full HEAD: `2824afb773d02bb4e0e7387710f1e7917858be8e` — plus dirty/untracked work, **not a newly committed implementation**.
- Final 48-file code/test inventory SHA-256: `f031eb90585599a276d10a920746d4fd0286a3c260e8be4e6d4e5bc776b7d009`. This inventory covers code/test files; it is not comparable to historical inventories that also included governing documents. Procedure and every file hash are in [source-inventory-final.json](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/source-inventory-final.json).
- Pre-existing work included modified CHANGELOG, RECOVERY, campaign journal, acceptance ledger and engineering log; untracked Part A source/test, inventory evidence, reports and October 6 session record. Full starting status: [git-status-before.txt](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/git-status-before.txt).
- **18,552 pre-existing output/evidence/report files hash-verified unchanged.** Old product/test files were unchanged except the deliberately switched `recon_pipeline/__main__.py` entry. Existing document text was retained verbatim, with prospective entry/checkpoint additions. Source/test bytes match the final tested candidate. [Preservation proof](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/preservation-final.json).
- October 5 capture still **INCOMPLETE / exit 2**: 1,661 unique media records versus 1,753 advertised; two unconfirmed shutdown aborts. Homepage route accounting and historical supervisor-counter findings remain OPEN. No past failure has been rewritten.

## Keep / simplify / retire

| Keep | Simplify | Retire from the new active path |
|---|---|---|
| Crawl4AI, existing USER_AGENT, rendered HTML, full REST fields/bytes, hashes | Ordinary `start → arun → close`; native response hook for REST | Custom CDP Fetch interception, correlation/drain state machines and supervisor |
| Sequential planned requests and refusal stop | Configurable five-second completion delay, including pagination and resume | Claims of per-resource/per-redirect pacing or guaranteed cancellation |
| Original results and explicit partial coverage | Immutable attempt files plus a small atomic checklist | Mandatory discovery, whole-site expansion and all-collection/media download |

Inspected historical path: `recon_pipeline.capture → BrowserSession → crawl_page → AsyncWebCrawler.arun`. Crawl4AI supplies rendering; the controller added operation identity, interception, fetch streaming, budgets and shutdown proof machinery. Browser-based REST does not require those pieces for this slice: the installed `after_goto` hook supplies native `Response.body()` bytes after ordinary Chromium navigation. That exact path was demonstrated on localhost. This is **different from historical same-page window.fetch**, and its target-site access remains untested.

The superseded experimental requirements, installed API references, output format and full usage are recorded in [COLLECTOR_SIMPLIFICATION.md](../ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md). The legacy raw-v2 reader and 48-AC/24-group campaign remain historical; new engineering results do not certify them.

## What works now

- **Explicit scope:** JSON page list, or `pages` plus `rest` selections. Pagination requires `paginate: true` and explicit `max_pages`. No link crawling, discovery, root REST enumeration or automatic media collection.
- **Pacing and stop:** default five seconds after a planned response completes; configurable. 401/403/429 or explicit challenge stops subsequent planned calls. Retry-After is retained. No automatic retry/fallback.
- **Save/resume:** body and metadata are saved before completion is recorded. Resume checks both hashes, skips valid results, and retries eligible failed/interrupted/missing results only on that explicit invocation. An empty resume starts no browser.
- **Add/refresh:** `add` queues explicit URLs offline; resume collects only unfinished items. `refresh` queues a page/individual endpoint into a new attempt without overwriting the original. Refresh an entire paginated collection into a **new collection directory** to avoid mixing page generations.
- **Honest REST:** nonempty short pages continue when valid headers advertise more pages. Missing/changing headers, limits, total mismatches and duplicate IDs remain partial. Non-paginated endpoints claim only the selected response, never whole-collection coverage.
- **Cleanup:** collection outcome and cleanup error are separate. Both raised errors and context-close errors logged internally by Crawl4AI are retained. A cleanup error cannot erase saved content or manufacture collection success.

## Commands — selected capture, resume, add

These are usage examples for Tony's review. **No public-site command below was executed.** The supplied initial plan selects `/blog/` and REST post `11945` only.

```bash
# Collect a NEW, explicit selection.
venv/bin/python -m recon_pipeline collect \
  --plan agent_docs/RESPONSES/response_2026-10-07_192033_simple-collector_plan.json \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --gap 5 --max-requests 2 --max-seconds 300 --max-bytes 20000000

# Resume; completed results with valid hashes are skipped.
venv/bin/python -m recon_pipeline resume \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --gap 5 --max-requests 2 --max-seconds 300 --max-bytes 20000000

# Queue one approved additional URL, without network activity.
venv/bin/python -m recon_pipeline add \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --plan agent_docs/RESPONSES/response_2026-10-07_192033_simple-collector_additions.json

# Collect the addition without repeating valid completed items.
venv/bin/python -m recon_pipeline resume \
  --collection outputs/collections/CyberizeGroup-selected-01 \
  --gap 5 --max-requests 1 --max-seconds 180 --max-bytes 20000000
```

For explicit refresh, use `venv/bin/python -m recon_pipeline refresh --collection outputs/collections/CyberizeGroup-selected-01 --id ITEM_ID`, then resume with approved bounds. Read the actual stable ID from `checklist.json`; unknown IDs are rejected. Bodies live at `attempts/<stable-id>/<attempt-id>/body`; their status, final URL, approved response headers and hashes are in adjacent `result.json`.

## Verification and evidence

**Final result: 59 passed in 29.33 seconds, exit 0.** This comprises 32 new collector checks and 27 existing offline REST/reader/inventory checks. Two collector cases used real Chromium on loopback; state/failure cases used transport doubles. Fast fixture gaps exercise the configurable delay; the default value of five seconds is asserted separately.

```bash
PYTHONDONTWRITEBYTECODE=1 \
SELECTED_COLLECTOR_EVIDENCE=agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/check-03 \
venv/bin/python -m pytest -q \
  tests/test_selected_collector.py tests/test_rest_client.py \
  tests/test_raw_reader.py tests/test_offline_inventory.py \
  --basetemp=agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/check-03/fixtures
```

This is the **recorded command**, not an instruction to reuse its evidence directory. Future verification must use a fresh directory.

| Behavior | Observed evidence |
|---|---|
| Only selected items | Native server received selected HTML and two explicitly approved REST pages; linked `/unselected` was not fetched |
| Browser REST fidelity | Unicode/full unknown fields preserved; returned bytes and SHA-256 exactly equal fixture responses |
| Pacing and pagination | Native minimum completion gap 0.150811s with configured 0.15s; short page 1 continued to page 2; three unique records matched advertised total |
| Stop on refusal | Native 429 produced one planned/server request; next selected page remained pending |
| Resume/add/missing output | Completed item skipped after interruption; missing/corrupt output refetched; one addition fetched alone |
| Cross-invocation pacing | Before-fix local failure retained; completion timestamp persistence now passes the resume/addition check |
| Partial REST | Missing/changing headers, empty intermediate page, count mismatch, duplicate IDs and explicit page limit all remain partial |
| Cleanup vs collection | Raised cleanup error and library-logged cleanup error stay visible; earlier 429 reason is preserved |
| Existing data behavior | Existing REST fidelity, raw-reader and Part A offline checks passed without changing those sources/tests |

Installed runtime recorded by native checks: Python 3.12.3, Crawl4AI 0.9.3, Playwright 1.52.0, Chromium 136.0.7103.25. No installation or upgrade. Earlier 26-pass and 58-pass runs, plus the subsequently discovered pacing failure, remain preserved; the final result is bound to the final source inventory.

## Limits and next move

This is a smaller collection contract. Ordinary redirects/background resources can generate additional HTTP traffic; the planned-call bound is **not** an all-HTTP-request bound. The 10 MiB cap is checked after browser delivery, not a streaming memory/wire cap. The persistence check reserves metadata space before saving; it is not the previous hard aggregate supervisor. Collection time includes setup/pacing; cleanup has a separate ten-second asynchronous timeout. No old low-level teardown guarantee is claimed.

New `selected-collection-v1` output is not a raw-v2 package and is not yet an input to the old RawRun reader. The future Prepare skill needs its own adapter/contract. Large-body behavior, target-site access through the new REST navigation, hidden/deferred content completeness and a broad production campaign remain unverified. This is not independent QA certification.

**Proposed next check — await Tony:** one new collection with exactly these two planned GET navigations:

1. `https://cyberizegroup.com/blog/`
2. `https://cyberizegroup.com/wp-json/wp/v2/posts/11945`

Use the first command above: maximum two planned calls, five-second gap, 300-second collection budget plus ten-second async cleanup timeout, 20 MB configured persistence check, 10 MiB retained-response cap. No pagination/discovery/media/retry or alternate client. Browser redirects/resources are additional traffic. Inspect real article content and complete REST bytes separately; empty REST content remains an honest absence. **Not executed; no live allocation assumed.**

## Changed files — this task only

- [recon_pipeline/__main__.py](../../recon_pipeline/__main__.py)
- [recon_pipeline/collector.py](../../recon_pipeline/collector.py)
- [tests/test_selected_collector.py](../../tests/test_selected_collector.py)
- [README.md](../../README.md)
- [CLAUDE.md](../../CLAUDE.md)
- [RECOVERY.md](../../RECOVERY.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [agent_docs/ACTION/wf-scrapper-abm/AGENTS.md](../ACTION/wf-scrapper-abm/AGENTS.md)
- [agent_docs/ACTION/wf-scrapper-abm/CLAUDE.md](../ACTION/wf-scrapper-abm/CLAUDE.md)
- [agent_docs/ACTION/wf-scrapper-abm/ABM_CAMPAIGN_JOURNAL.md](../ACTION/wf-scrapper-abm/ABM_CAMPAIGN_JOURNAL.md)
- [agent_docs/ACTION/wf-scrapper-abm/ABM_LEDGER.md](../ACTION/wf-scrapper-abm/ABM_LEDGER.md)
- [agent_docs/ACTION/wf-scrapper-abm/ENGINEERING_LOG.md](../ACTION/wf-scrapper-abm/ENGINEERING_LOG.md)
- [agent_docs/ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md](../ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md)
- [agent_docs/SESSIONS/session_2026-10-07.md](../SESSIONS/session_2026-10-07.md)

Generated report, checks JSON, two example plans and evidence are additional handoff artifacts. The pre-existing offline inventory source/test, old controller, old raw reader and dependency files are unchanged.

## Handoff files

- [Report — response_2026-10-07_192033_simple-collector.md](response_2026-10-07_192033_simple-collector.md)
- [Checks summary — response_2026-10-07_192033_simple-collector_checks.json](response_2026-10-07_192033_simple-collector_checks.json)
- [Usage and superseded requirements — COLLECTOR_SIMPLIFICATION.md](../ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md)
- [Initial proposed selection — response_2026-10-07_192033_simple-collector_plan.json](response_2026-10-07_192033_simple-collector_plan.json)
- [Proposed one-URL addition — response_2026-10-07_192033_simple-collector_additions.json](response_2026-10-07_192033_simple-collector_additions.json)
- [Exact source/test diff — source-test-final.diff.txt](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/source-test-final.diff.txt)
- [Final code/test inventory — source-inventory-final.json](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/source-inventory-final.json)
- [Final test log — pytest.log](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/check-03/pytest.log)
- [Native successful collection — timeline.json](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/check-03/native-success/timeline.json)
- [Native refusal stop — timeline.json](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/check-03/native-denial/timeline.json)
- [Retained pacing failure — resume-pacing-before.log](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/resume-pacing-before.log)
- [Preservation checks — preservation-final.json](../ACTION/wf-scrapper-abm/EVIDENCE/simple-collector/2026-10-07_130939Z/preservation-final.json)
- [Current engineering checkpoint — RECOVERY.md](../../RECOVERY.md)

**STOPPED AFTER HANDOFF.** No live target traffic, Git mutations, dependency changes, deployment, further recon work or Prepare skill. Independent QA NOT RUN.
