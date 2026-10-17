# Part A — Offline imported Capture inventory and human selection

Status: first engineering slice; independent QA NOT RUN. Prepare ON HOLD.

## What this command does

`recon_pipeline.offline_inventory` validates saved input using `prepare.reader.RawRun`, then creates a NEW review directory. Its numbered Markdown listing and JSON describe the same document candidates. This is **IMPORTED_CAPTURE_INVENTORY**, not a fresh lightweight recon run or a current access test.

Candidate universe: saved discovery routes UNION saved WordPress pages/posts links, merged only by exact URL equality. Taxonomy/user/media collections remain coverage context. Their records are not automatically promoted to document-capture targets; no inclusion/exclusion decision is made. A taxonomy URL already present in discovery remains a document candidate. Unknown titles/types stay unknown; slugs and taxonomy labels are not invented as page titles.

Stable IDs are `doc-` plus the first 20 hex digits of SHA-256 over the exact UTF-8 URL. Export refuses an ID collision. Numbers are display positions only. Titles, dates, WordPress types, captured HTML and collection-response/object references retain their source locators and file hashes. WordPress type is not an asserted HTTP MIME type. Empty REST content stays recorded as empty; meaningful HTML is not erased.

The inventory carries the raw snapshot hash and a semantic binding over its context/items sorted by stable ID. Reordering rows keeps that binding; changing evidence metadata requires a new inventory and explicit reselection. Inventory creation timestamps do not define selection identity. These hashes detect mismatches; they are not independent certification.

## Current preserved input

- Raw: `outputs/CyberizeGroup/runs/2026-10-05T14-10-49Z`.
- Original capture source: 69 files, SHA-256 `f497011c908057d4a1fb447c8b83a83152cf783ba3f3d8f00ee954aac904c7d3`; historical base HEAD `366f9830ba7b9bfb91f17b8655fd37467410123b` plus then-reviewed dirty source.
- Actual checkout at Part A start: branch `wf-scrapper-abm`, HEAD `2824afb773d02bb4e0e7387710f1e7917858be8e`, clean; original 69 source records still match.
- Capture remains INCOMPLETE, exit **2**. All 39 intentional operations succeeded; media fetched pages 1–18 but returned **1,661 unique / 1,753 advertised**, gap **92**, with ten short intermediate pages. Two new shutdown XHR aborts remained unconfirmed. The original results are unchanged.
- Existing imported review: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/review/inventory.json` and `INVENTORY.md`. All **217** candidates are **UNDECIDED**. No real choice file has been authored.

## Usage — existing installed venv, repository root

Create a separate NEW export (the directory must not already exist):

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m recon_pipeline.offline_inventory import \
  --raw outputs/CyberizeGroup/runs/2026-10-05T14-10-49Z \
  --out agent_docs/RESPONSES/CyberizeGroup_imported_review_NEW
```

Read the already generated listing:

```bash
venv/bin/python -m recon_pipeline.offline_inventory list \
  --inventory agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/review/inventory.json
```

After Tony explicitly supplies IDs, save choices in a NEW file. This syntax example was **not executed against the real review inventory**; replace the placeholders with his choices:

```bash
venv/bin/python -m recon_pipeline.offline_inventory choose \
  --inventory agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/review/inventory.json \
  --include <INCLUDE_STABLE_ID> --exclude <EXCLUDE_STABLE_ID> \
  --note 'Tony explicit selection' --out agent_docs/RESPONSES/CyberizeGroup_choices_v1.json
```

Quote substituted IDs as ordinary shell arguments; angle-bracket placeholders are not runnable shell input. Either include or exclude is sufficient; flags may repeat. Unknown IDs, conflicting include/exclude in one command, empty decisions, an existing output path, or any output within the original raw directory are refused. Unspecified IDs remain UNDECIDED. Metadata can be read and ranked conversationally; no embedded model integration is needed.

Reopen saved choices:

```bash
venv/bin/python -m recon_pipeline.offline_inventory list \
  --inventory agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/offline-selection/2026-10-06_025607Z/review/inventory.json \
  --choices agent_docs/RESPONSES/CyberizeGroup_choices_v1.json
```

For revised explicit decisions, use `choose --previous <v1-file> --out <NEW-v2-file>` plus new include/exclude flags. Prior choices persist unless explicitly revised; v1 and the imported inventory remain untouched. Choice files store the inventory/source bindings; reopening against changed inventory content is refused. Choices never start capture.

## Verification and limitations

Focused engineering checks cover actual RawRun input, source-file/object traceability, stable IDs under reorder, include/exclude persistence after reopen, immutable revisions, unknown-ID refusal, raw/output overwrite refusal, visible missing metadata and partial-state context, and escaped presentation of source text. Synthetic choices are marked as test data and are not Tony decisions. Actual-input verification also hashes every referenced file, verifies each saved WordPress ID/link, forbids socket connections in its process and compares all raw bytes before/after.

Missing metadata is not fetched or guessed. Exact URL equality can leave slash/alias variants separate; conversational review should inspect their provenance before making choices. Media/taxonomy/user coverage is context, not yet an independently selectable media asset catalog. The retained capture is not a fresh/current site inventory. No Prepare package is constructed.

## Proposed next slice — requires separate live authorization

JARVIS should bind a dedicated lightweight recon entry whose default is sitemap discovery. It should use the approved browser-owned session/identity/scope/pacing/stop controls, save robots and sitemap evidence and a route inventory, and label those future results FRESH_LIGHTWEIGHT_RECON. Propose **20 intentional dispatches**, **300 seconds including finalization**, **10 MB persisted aggregate**, existing 10 MiB per-response cap and existing operation deadlines; no HTML/REST/media collection in that slice. Ceilings are proposed, not granted or implemented.

No automatic homepage fallback on refusal or missing sitemap; record the outcome and let Tony decide a separately bounded alternative. Before another live allocation, JARVIS must assess the two unconfirmed shutdown requests. Current Capture CLI is still Capture, not that proposed lightweight entry. Homepage stopped-path accounting and historical supervisor final-manifest counter findings remain OPEN. STOP after this offline handoff.
