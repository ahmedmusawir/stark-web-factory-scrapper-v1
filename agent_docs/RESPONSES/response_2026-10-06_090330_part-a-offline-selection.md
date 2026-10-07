# Part A offline Recon/Selection — DONE; ready for engineering review

**217 document candidates are available for conversational review, all UNDECIDED.** This is an imported Capture inventory, not a fresh lightweight recon run. No inclusion/exclusion decision or live request was made.

**Capture remains INCOMPLETE:** original exit **2**, all 39 intentional operations successful, media **1,661 unique / 1,753 advertised** despite all 18 pages fetched, and **two unconfirmed shutdown aborts**. Those source results are untouched; this work does not certify the checkpoint or repair the controller.

## What changed

- **New `recon_pipeline/offline_inventory.py`:** separate offline import/list/choose entry. Uses the existing RawRun validator, merges only exact URLs from discovery routes and saved REST pages/posts, records titles/types/dates/locators and hashes, and preserves gaps. Capture's current entry point and existing source are unchanged.
- **New `tests/test_offline_inventory.py`:** focused behavioral proof for source tracing, stable IDs/reordering, saved choices/reopening, immutable revisions, unknown-ID/conflict/empty-choice refusal, output/raw protection, missing metadata and safe presentation. Network socket connections are forbidden in these tests.
- **New `PART_A_OFFLINE.md`:** usage, current limitations and a proposed next discovery slice. Mutable engineering checkpoints/journals/ledger/session/changelog were appended; old records retained. No frozen contract, dependency or existing product/test file was edited.

## Inventory and sample

194 routes plus 208 distinct page/post links become 217 candidates: 185 exact URL matches, nine route-only candidates and 23 REST-only candidates. Media/taxonomy/users remain coverage context; they are not automatic exclusion decisions. A taxonomy URL already discovered remains a document candidate. Nine titles and nine WordPress types are unavailable and explicitly unknown; available dates retain their source kind, including sitemap lastmod.

IDs derive from exact UTF-8 URLs and are independent of row number. Collision checking refuses an export. Source snapshot and inventory bindings prevent reopening choices against changed evidence metadata; row reordering preserves the binding. Titles can come from saved REST or HTML and are presentation derivatives; no source body is mutated or plugin cause inferred.

| Stable ID | Saved title | WordPress type | URL |
|---|---|---|---|
| `doc-22d2072cb4418c53d3e9` | Home – New | page | https://cyberizegroup.com/ |
| `doc-196c4e1aca79a5e74c21` | 10 Essential Small Business Marketing Strategies for 2024 | post | https://cyberizegroup.com/10-essential-small-business-marketing-strategies-for-2024/ |
| `doc-1c060484d78bdcd07f14` | \[title unknown\] | unknown | https://cyberizegroup.com/agency-locations/ |

This sample contains **no proposed choices**. No actual choice file was created. The retained choice/reorder example is synthetic fixture evidence only.

## Usage

Read the generated listing:

```bash
venv/bin/python -m recon_pipeline.offline_inventory list \
  --inventory agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/review/inventory.json
```

After Tony supplies explicit IDs, `choose` saves includes/excludes in a NEW file; `list --choices` reopens it. Use `--previous` plus a NEW output filename for revisions. Unknown IDs and an ID included and excluded in one command are refused. Unspecified IDs remain UNDECIDED. The imported inventory and previous choice files are never overwritten; output within the original raw directory is refused. The [usage guide](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/PART_A_OFFLINE.md) gives exact command forms. No embedded GLM/Ollama integration is added; conversational ranking is the intended next review action.

## Offline verification

- **17 tests passed, exit 0**, in the recorded focused run: new offline tests plus existing raw-reader checks. Exact command and result are in [checks JSON](response_2026-10-06_090330_part-a-offline-selection_checks.json) and [focused log](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/focused-checks.log). Test/code hashes match the final files; the subsequent addition was usage documentation only. No full regression or independent QA campaign was run.
- Real imported input: **1,216 source-reference hash checks** and **208 WordPress ID/link checks** passed; RawRun schema/reference/hash/mapping checks passed. Actual-input verification ran with socket connections forbidden.
- Reordering preserved IDs and inventory binding. Synthetic included/excluded choices survived reopening and reorder; revised choices kept the prior file unchanged. Negative checks refused unknown IDs, overwrite attempts and mismatched evidence binding.
- Media gap **92**, short-page anomalies and two unconfirmed aborts are visible in JSON and the numbered listing. Missing metadata remains marked unknown.
- All **1,995 raw files** and **18,527 pre-existing output/evidence/report files** remain hash-identical. All original 69 source records are unchanged.

## Identity and staging proposal

Branch `wf-scrapper-abm`, actual HEAD `2824afb773d02bb4e0e7387710f1e7917858be8e`; clean at intake. Tony committed the earlier checkpoint: its 69 source records still hash to `f497011c908057d4a1fb447c8b83a83152cf783ba3f3d8f00ee954aac904c7d3`. This is distinct from the capture's historical base HEAD `366f9830ba7b9bfb91f17b8655fd37467410123b`.

Final 72-file source inventory: `f4f6842735c0185d0dc6b03687b55ba2aca31bb2ad2d641110f8b0b37b7d8168` (three new source/test/usage files; no old source overwritten). Changes remain uncommitted; Tony alone controls Git. [Proposed selective staging list](response_2026-10-06_090330_part-a-offline-selection_proposed-staging.txt) has one path per line, with no add-all command. No staging, commit or branch operation was performed.

## Next move and remaining limits

Tony/JARVIS can now review and rank the numbered inventory conversationally, then provide explicit stable-ID inclusions/exclusions. Next implementation proposal: a dedicated **sitemap-default lightweight recon** entry using approved browser-owned identity/scope/pacing/stop controls, saving discovery evidence and routes without HTML/REST/media collection. Proposed ceilings: 20 intentional dispatches, 300 seconds including finalization, 10 MB aggregate, existing response/operation caps. These are **proposals, not live authorization**. No automatic homepage fallback; report missing/refused sitemap and seek a separately authorized alternative. JARVIS must assess the unconfirmed teardown finding before another live allocation.

Exact URL/alias variants remain separately identified; hidden/deferred content completeness and current accessibility are unknown. The media discrepancy is not resolved by this inventory. Historical homepage stopped-path accounting and supervisor final-manifest counter findings remain OPEN. Prepare ON HOLD; independent QA NOT RUN.

## Handoff files

- **Numbered inventory:** [INVENTORY.md](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/review/INVENTORY.md).
- **Machine inventory:** [inventory.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/review/inventory.json).
- **Usage instructions:** [PART_A_OFFLINE.md](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/PART_A_OFFLINE.md).
- **Report:** [response_2026-10-06_090330_part-a-offline-selection.md](response_2026-10-06_090330_part-a-offline-selection.md).
- **Checks:** [response_2026-10-06_090330_part-a-offline-selection_checks.json](response_2026-10-06_090330_part-a-offline-selection_checks.json).
- **Exact new-source diff:** [response_2026-10-06_090330_part-a-offline-selection_source.diff.txt](response_2026-10-06_090330_part-a-offline-selection_source.diff.txt).
- **Tony's proposed staging list:** [response_2026-10-06_090330_part-a-offline-selection_proposed-staging.txt](response_2026-10-06_090330_part-a-offline-selection_proposed-staging.txt).
- **Actual-input traceability:** [actual-input-verification.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/actual-input-verification.json).
- **Final source inventory:** [source-final.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/source-final.json).

**DONE — STOPPED after offline handoff.** No live traffic, controller repair, Git mutation, dependency change, deployment or Prepare work.
