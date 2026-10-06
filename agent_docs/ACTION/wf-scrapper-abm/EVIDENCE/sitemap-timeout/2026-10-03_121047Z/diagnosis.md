# Local diagnosis — confirmed handoff defect; original live delay remains unknown

The saved live run stopped because the **parent supervisor reached the advertised read-operation deadline**. HTTP 200 headers did not establish successful body handoff. A later native completion event exists, but no sitemap result/body was archived. The source and local reproduction establish a **separate deadline-coordination defect that can discard bytes already consumed by the browser**. They do not establish why the original live protocol events/result were delivered late.

## Decisive live timeline

Source: `outputs/CyberizeGroup/runs/2026-10-03T11-46-34Z/stage_log.txt`. Full selected rows and raw numeric clocks: `live-timeline.json` alongside this file.

| Relative to operation start | Observation | Stage-log line |
|---|---|---|
| 0.000 s | op-3 starts at monotonic 385102.118572; advertised deadline 385132.118566 | 1350 |
| +0.227 s | Isolated-world script identity bound; exact setup/runScript-call times were not separately recorded | 1355 |
| +0.266 s | Pacing wait requested 4.679592s after preceding completion | 1361 |
| +5.026 s | Intentional sitemap dispatch counted | 1366 |
| +5.156 s → +6.359 s | Fetch.continueRequest command attempted → completed | 1367–1368 |
| +27.903 s / +28.037 s | CDP / Playwright HTTP 200 response observations | 1370–1371 |
| +30.076 s | Unconditional operation_complete(error=null); not proof of success | 1372 |
| +30.898 s | Network.loadingFinished callback; native browser timestamp 385118.687465 retained | 1373 |
| +31.206 s | Playwright request-finished callback | 1374 |
| +31.778 s | Page closed | 1375 |
| +32.190 s | Context-close error, then browser_cleanup_error event | 1376–1377 |
| UTC 11:48:46 | Supervisor stop and finalization record **operation_watchdog** | 1378–1379 |

The parent signal/child Python cancellation were not independently timestamped in the old log. The active Python runtime converts SIGINT to main-task cancellation; that is consistent with the observed sequence, not a newly observed live exception. Native browser timestamps and Python callback-receipt times are retained separately. The native Network request/completion timestamp interval was 16.320907s; it must not be confused with result availability to Python. The delay's cause is unknown.

## Timer ownership before repair

- **Parent supervisor:** receives operation_start's monotonic deadline. It checks every roughly 0.1s and interrupts the entire worker process group on expiry; it retains the existing bounded shutdown/finalization path.
- **Python read:** wait_for wraps setup, compiled-script execution and result delivery, for another approximately 30s starting just after the advertised start. Setup and pacing consume this budget.
- **Browser abort:** the old 29.9s timer starts only when the compiled script executes. Setup therefore shifts its end later than the Python/supervisor deadline. With 0.6s injected setup latency, browser abort can occur after Python has discarded the awaitable.
- **Crawl4AI 90s page navigation:** applies to the bootstrap/document capture, not this CDP Runtime.runScript/window.fetch read. The three-second post-load delay and image wait similarly belong to document capture.
- **Global bound:** retains the 1800s ceiling and 30s finalization reserve; the local repair does not extend either or the per-read 30s bound.

The old finally block always emitted operation_complete using only op.error. Python TimeoutError updated stop_reason but not op.error; external CancelledError also bypassed except Exception. Either could leave a misleading null terminal error. Neither null nor the event name established a successful read.

## Local proof and correction

- Preserved pre-fix method, real Chromium, loopback, explicit 0.6s setup latency: a test-only JavaScript counter proved 2,048 bytes consumed by the reader; Python received 0. Repaired method: same 2,048 consumed and returned, still incomplete/read_deadline. See chunk-proof-before.json, chunk-proof-after.json and chunk-handoff-confirmed/result.json.
- Actual unmodified product supervisor and 30s read limit: the stalled sitemap fixture sends 64 bytes, then stalls 40s. Delayed setup previously saved an empty response; repair saves 64 bytes and retains a typed failure. Ordinary setup also passes. No HTTP/protocol failure was injected.
- Successful complete-response fixture and explicit task-cancellation fixture distinguish success/failure/cancelled, retain earlier document evidence, and preserve the existing stop reason. Native AbortController cancellation, identity, refusal, scope, redirects and byte caps are rechecked by the existing controls.

One operation end boundary now anchors the cooperative browser cutoff before setup, Python result deadline, and unchanged hard supervisor deadline. For a normal 30s read: browser abort at 29s; Python fallback at 29.75s; supervisor cutoff at 30s. Reserves shrink proportionally for shorter remaining budgets. These are internal allowances, not added time, retries or another transport. The JS cooperative clock uses same-host wall time; monotonic Python/supervisor deadlines remain authoritative even if that clock moves. A severely unresponsive runtime can still reach the hard watchdog; this repair does not promise retrieval of unreturned bytes after forced termination.

Read setup/script/result events and explicit terminal outcomes improve future correlation. Existing stop reasons stay sticky. Cancellation/timeout closes the existing page and cannot become success. The supervisor source is unchanged. No manifest-counter repair was made.

## Preserved gaps and test-history notes

- Original live body/result delivery delay and exact signal arrival are unresolved. No proven target refusal or controller root cause.
- Missing final dispatch/document/resource counters in the supervisor-finalized live manifest remain a finding only.
- The first affected run retained 8 passes then was interrupted: an older cancellation fixture's literal script replacement no longer matched. Only its injection binding was updated and guarded; behavioral assertions remain intact.
- The extra byte-counter proof's first attempt failed before capture because the archived controller lacked its relative lock-hash input. An exact lock snapshot supplied that input; working dependencies were untouched. The failed attempt remains preserved.
- HEAD advanced externally from 3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f to 366f9830ba7b9bfb91f17b8655fd37467410123b during this work. No agent Git mutation. Final evidence binds actual source bytes independently of HEAD.

Prepare remains ON HOLD. Independent QA NOT RUN. No live traffic is authorized or performed by this mission.
