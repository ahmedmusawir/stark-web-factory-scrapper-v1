# Live Capture verification — Bounded Capture INCOMPLETE; collection stopped

## What collected

- **HTML:** 10 captured route outcomes, using 10 document slots. The bootstrap is also saved under `discovery/bootstrap.html`; matching reuse: https://cyberizegroup.com/. 11 HTML files on disk include that separate copy, not another navigation. Remaining route outcomes: `{'captured': 10, 'skipped': 184}`.
- **Discovery:** 4 saved sitemaps; 194 routes. Saved XML parse/hash results are in the summary; discovery stream `complete`.
- **Media pagination:** reached advertised end **True**; coverage complete **False**. These are separate verdicts. Missing totals/duplicate IDs are not filled or reinterpreted.
- **Media inventory:** 7,531 URLs, origin counts `{'items': 7531, 'internal': 7489, 'external': 13, 'staging_domain': 29}`. No separate media-file retrieval; `--no-media-head` skips in-scope HEAD and off-scope URLs remain untested. Normal rendering can load image subresources.

## REST collections — this run only

| Collection | Advertised records / pages | Fetched pages | Saved records | Unique IDs | Duplicate records | Short intermediate pages | Saved response bytes | Product status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| pages | 42 / 1 | 1 | 42 | 42 | 0 | 0 | 1459408 | complete |
| posts | 166 / 2 | 2 | 166 | 166 | 0 | 0 | 15862451 | complete |
| media | 1753 / 18 | 18 | 1661 | 1661 | 0 | 10 | 5812456 | partial |
| categories | 15 / 1 | 1 | 15 | 15 | 0 | 0 | 113505 | complete |
| tags | 56 / 1 | 1 | 56 | 56 | 0 | 0 | 351086 | complete |
| users | 6 / 1 | 1 | 6 | 6 | 0 | 0 | 5551 | complete |

- **pages:** advertised end True; coverage complete True; remaining advertised pages []; record gap 0; reasons none.
- **posts:** advertised end True; coverage complete True; remaining advertised pages []; record gap 0; reasons none.
- **media:** advertised end True; coverage complete False; remaining advertised pages []; record gap 92; reasons pagination_count_mismatch.
- **categories:** advertised end True; coverage complete True; remaining advertised pages []; record gap 0; reasons none.
- **tags:** advertised end True; coverage complete True; remaining advertised pages []; record gap 0; reasons none.
- **users:** advertised end True; coverage complete True; remaining advertised pages []; record gap 0; reasons none.

Short-page anomalies: `[{'collection': 'media', 'page': 3, 'records': 96, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 4, 'records': 96, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 5, 'records': 99, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 8, 'records': 98, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 9, 'records': 73, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 12, 'records': 89, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 13, 'records': 79, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 14, 'records': 92, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 15, 'records': 94, 'reason': 'short_intermediate_page'}, {'collection': 'media', 'page': 17, 'records': 98, 'reason': 'short_intermediate_page'}]`. Complete, valid short pages were followed according to headers. Every saved response's status, completeness, hash, headers and object count is retained in JSON. All fields use the existing production contract; no diagnostic field filter or pagination change.

## Exit, traffic and shutdown

Exit **2**; first stop reason **`interception_error:TargetClosedError`**. Recorder elapsed **386.098s**, from 2026-10-05T14:10:48.392990+00:00 to 2026-10-05T14:17:14.490631+00:00. Exactly one launch; this allocation is consumed.

Intentional dispatches **39 / 120**; redirect hops **0**. Minimum completion-to-next-dispatch gap **5.001167286070995s**; all observed gaps ≥5s: **True**; recorded intentional dispatches after first STOP: **0**. Browser resources are observed separately (1152 request events; 1096 response events).

Confirmed abort replies during shutdown: **0**. Unconfirmed cancellations: **2**. Original stop: `interception_error:TargetClosedError`. The retained `interception_command_complete` records follow successful CDP replies; command-intent logs alone are not acknowledgements. Completed continuations after shutdown start: 0. **These logs cannot establish zero teardown wire traffic.** No target-server telemetry or wire capture exists for this run. A missing/unconfirmed abort stays a finding.

All 39 intentional operations reported success before teardown. Stage-log lines 8179–8191 show initial drain with no pending losses, planned close, then two new XHR pauses (`interception-job-2384.0`, Network `8015BE005E2A8DA7757D7D3D60358F9E`; `interception-job-2385.0`, Network `1907199.2990`). Both belong to `page-cdp-1`, frame `85C6F3F81842A248F0DFD3C9F41385B9`, operation null, classification `shutdown_unclassified`. Both attempted `Fetch.failRequest` and returned `TargetClosedError`; neither abort received a successful reply. No failed intentional operation is inferred from adjacency to op-39. Full timestamped request-specific evidence is linked below; root cause and wire traffic remain unknown.

## Validation and preservation

Read-only raw reader/schema/reference/hash validation: **PASS**, 1995 files; raw unchanged by validation: True. Structural validity does not certify collection completeness. HTML usefulness was checked locally from saved markup:

- `html/cyberizegroup-com-5-foundational-principles-for-online-success.html`: 59 paragraphs ≥100 characters after excluding scripts/navigation/header/footer.
- `html/cyberizegroup-com-5-mistakes-real-estate-agents-make.html`: 82 paragraphs ≥100 characters after excluding scripts/navigation/header/footer.
- `html/cyberizegroup-com-blog.html`: 10 paragraphs ≥100 characters after excluding scripts/navigation/header/footer.

Repository `/home/moose/PYTHON/stark-web-factory-scrapper-v1`; branch `wf-scrapper-abm`; base HEAD `366f9830ba7b9bfb91f17b8655fd37467410123b` plus existing dirty/untracked work. Reviewed 69-file hash `f497011c908057d4a1fb447c8b83a83152cf783ba3f3d8f00ee954aac904c7d3` matched before/after and the run's source identity. All **16,504** pre-existing output/evidence/report files are hash-identical. No product/test edits or regression rerun.

The first preflight's uncompressed status projection exceeded the support reserve before network activity. It is preserved; gzip status/diff snapshots reduced the ready projection to 2,339,011 bytes without altering limits or source.

Budget accounting, including every newly persisted supporting file and checkpoint growth, is in the summary. Limits remain **97 MB raw + 3 MB supporting = 100 MB aggregate**, 1,800 seconds including finalization, 10 MiB response cap and existing deadlines.

## Evidence and next move

- **Report:** [response_2026-10-05_201927_planned-close-live-verification.md](response_2026-10-05_201927_planned-close-live-verification.md).
- **Compact summary:** [response_2026-10-05_201927_planned-close-live-verification_summary.json](response_2026-10-05_201927_planned-close-live-verification_summary.json).
- **Raw run:** [2026-10-05T14-10-49Z](/home/moose/PYTHON/stark-web-factory-scrapper-v1/outputs/CyberizeGroup/runs/2026-10-05T14-10-49Z).
- **Recorder result:** [result.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-05_140942Z/smoke/result.json).
- **Reader validation:** [reader-validation.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-05_140942Z/reader-validation.json).
- **File/hash inventory:** [raw-inventory.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-05_140942Z/raw-inventory.json).
- **Operation/pacing evidence:** [operation-and-pacing.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-05_140942Z/operation-and-pacing.json).
- **Shutdown request timeline:** [shutdown-request-timeline.json](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-live-capture/2026-10-05_140942Z/shutdown-request-timeline.json).
- **Full stage log:** [stage_log.txt](/home/moose/PYTHON/stark-web-factory-scrapper-v1/outputs/CyberizeGroup/runs/2026-10-05T14-10-49Z/stage_log.txt).
- **Checkpoint:** [RECOVERY.md](/home/moose/PYTHON/stark-web-factory-scrapper-v1/RECOVERY.md).

**Next move: JARVIS reviews actual coverage and shutdown results. STOPPED.** No repair or repeat authorized. Historical homepage stopped-path accounting and supervisor final-manifest counter findings remain OPEN. Prepare ON HOLD; independent QA NOT RUN. No Git mutations, dependency changes, deployment or recon work.

| Persisted bytes | Actual | Ceiling |
|---|---:|---:|
| Raw | 65,264,385 | 97,000,000 |
| Supporting incl checkpoints | 1,503,963 | 3,000,000 |
| Aggregate | 66,768,348 | 100,000,000 |
