# Two-arm teardown experiment — COMPLETE; live verification not recommended yet

**Verdict:** The held GET stayed blocked in the normal-release control and then collected successfully. In the page-close arm, the server received that GET without any custom-controller continuation. Closing a paused page therefore cannot be treated as proof that its pending request was canceled. The exact wire-dispatch time and Chromium's internal release mechanism remain unknown.

## Results

| Arm | Held interval | Recorded intentional dispatches | Returned content | Process / duration |
|---|---|---:|---|---|
| A — normal release | 1.002 s; no target handler receipt | 2 | HTTP 200; complete 3,615 bytes; exact fixture match | exit 0 / 12.590 s |
| B — page close | 1.001 s before close; no target handler receipt | 1 (bootstrap only) | failure, `browser_page_closed`; zero returned body bytes | exit 0 / 7.660 s |

Each arm ran once, using the existing real Chromium/Crawl4AI capture/read path, one bootstrap and one intentional GET. Existing 5-second pacing, 10 MiB response cap, 30-second read limit, scope guards and 30-second finalization reserve remained in place. Neither 60-second/3-dispatch ceiling triggered. The bootstrap's ordinary POST and incidental 403 remained background events. Four local handler requests occurred per arm; only two were deliberately requested. No live target requests, retries, full-suite rerun or repair occurred.

Arm A's body SHA-256: `cd71a9553347bcb1e9452c426c874f3c8dd40979e456d1fb8caf35983aa5f4bd`. Its completion-to-next-controller-dispatch gap was 5.003493 seconds. Arm B's server received the held GET although the controller counted only bootstrap: **a dispatch-log count is not a teardown traffic guarantee**. Its server byte observation was 1.029622 seconds after bootstrap completion, before the next 5-second admission would have been eligible. This is an observed collection-control limitation, not successful second-operation admission.

## Decisive request timeline

Offsets are milliseconds from each worker's native pause observation. `O` denotes a line in that arm's `observations.jsonl`; `D` denotes `driver-protocol.jsonl`. Driver offsets are parent log-read observations, not calibrated command transmit times.

| Arm | Offset ms | Retained observation |
|---|---:|---|
| A | 0 / 0.047 / 0.168 | Pause → registration → fixture hold (O80–82) |
| A | 1001.802 / 1001.864 | No handler receipt during hold; release (O84–85) |
| A | 1001.974 / 4985.519 | Intentional classification; after pacing, Python continue attempt (O87, O92) |
| A | 4987.941 / 4988.481 | Custom-session continue SEND and successful reply (D39–40) |
| A | 4988.924 / 4993.265 | Routing-session pause, then its continue SEND (D41–42); context guard allows (O96–97) |
| A | 4994.970 / 5005.320 | Server reads GET bytes; complete exact body returned (O98, O110) |
| B | 0 / 0.057 / 0.100 | Pause → registration → fixture hold (O80–82) |
| B | 1001.593 / 1001.660 | No handler receipt during hold; page.close invoked (O84–85) |
| B | 1003.966 / 1004.705 | Target.closeTarget SEND and success reply (D39–40) |
| B | 1006.141 / 1007.385 / 1007.477 | Routing session detached; page closure observed; sticky STOP (D41, O86, O88) |
| B | 1008.302 / 1008.364 / 1008.541 | close returns; barrier releases; intentional classification (O89–92) |
| B | 1008.798 / 1009.207 | Python abort attempt; custom session detachment observed (O95, D42) |
| B | 1010.100 / 1013.269 | Server reads GET; Python abort raises TargetClosedError (O96, O102) |
| B | 1012.834 / 1104.052 | Failed read returns; cleanup finishes with original STOP preserved (O101, O108) |

Both reuse the bootstrap's existing server connection. Acceptance occurred long before the held read and proves no target transmission by itself. Earliest practical target-byte evidence is `recv_into` returning `GET /cleanup-held HTTP/1.1`; B's observation is 2.625 ms after STOP. This **does not locate wire dispatch relative to STOP**. No second custom continuation was attempted in B. No matching continuation or abort SEND, routing-layer pause, context-guard invocation, or Fetch.disable was retained for B's held GET. Its abort is a Python attempt/error, not a recorded CDP send.

## Identity, instrumentation and limits

- A: Network `1707616.4`; custom Fetch `interception-job-7.0` / CDP `C85CEB3610A43F491EFF221DDCDD65F1`; routing Fetch `interception-job-8.0` / CDP `51B34426FD477863647948E043EFCC20`. Both native pauses share the Network ID and frame `2A64933A9AB0C0132CBA32FD5AD6C2CF`.
- B: Network `1707806.4`; custom Fetch `interception-job-7.0` / CDP `3280E00130F1ED7E9B2BD470F36440B8`; routing CDP `30C24241AB2C9AD71B368B76D5E75C4F`; frame `3D026F63E2F5E9869347E280FB23B29E`. There is no retained routing Fetch ID for this GET. Native redirect predecessor remains absent.

Temporary subclasses wrap the existing fixture's socket reads, routing callbacks, CDP send calls, native registration and page-close calls without changing their decisions. Runtime: Chromium 136.0.7103.25 / installed headless_shell; existing product settings preserved. Detailed runtime identity is in each `result.json`.

Worker/server and parent observations use the same OS CLOCK_MONOTONIC, with thread/process scheduling latency. Chromium timestamps and driver UTC prefixes remain separate and uncalibrated. The installed driver's protocol logger precedes transport.send ([crConnection.js](../../venv/lib/python3.12/site-packages/playwright/driver/package/lib/server/chromium/crConnection.js#L55)); a SEND row records that outgoing path, while a matching reply corroborates delivery. This is not a transport-write-completion or packet trace. Four non-protocol/unparseable stderr lines per arm were counted but not retained; no trace cap triggered. Header/cookie/body fields are excluded from shared driver traces. Server instrumentation records request lines, byte counts and hashes, not raw headers.

## What this establishes / next move

**Proved:** custom STOP prevents its continuation, preserves an explicit failed read and attempts one abort. It does not guarantee the already-paused GET cannot reach the server during target closure. The normal control positively links both continuation layers to successful collection. The context guard allows A; it provides no observed decision for B's held GET.

**Still unknown:** Chromium's exact internal release path; wire time relative to STOP or fixture release; whether other teardown modes behave identically; whether a production closure would release an off-scope request. Production can hold requests during pacing, identity waits and cancellation, but the deliberate pre-classification fixture barrier is instrumentation, not a claim that every production event order matches this arm.

**Recommendation:** JARVIS should review a narrowly scoped pending-interception drain/confirmed-abort-before-planned-close repair with native proof before another live allocation. This experiment supports that repair direction, not its effectiveness or protection against unexpected external target loss. No implementation is authorized or performed here. Homepage route-accounting and historical supervisor-counter findings remain OPEN. Prepare remains ON HOLD; independent QA NOT RUN.

## Candidate and preservation

- Repository: `/home/moose/PYTHON/stark-web-factory-scrapper-v1`; branch `wf-scrapper-abm`.
- Base HEAD: `366f9830ba7b9bfb91f17b8655fd37467410123b` plus preserved dirty/untracked work; no completed-candidate commit claimed.
- Before **and** after 68-file inventory: `aaf883a8c59960ab825e5a58508772bb9c099b49f65187b248e1f2ed813dc622`.
- Seven monitored installed source files unchanged; dependency declarations/lock unchanged in the inventory.
- All 14,260 pre-existing output/evidence/report files are present with identical hashes. Product/test sources are unchanged. New instrumentation/evidence/handoff files and append-only checkpoint records are the only work from this mission.

## Handoff files

- **Report:** `response_2026-10-05_133438_two-arm-teardown.md`.
- **Compact results:** `response_2026-10-05_133438_two-arm-teardown_summary.json`.
- **Review bundle:** `response_2026-10-05_133438_two-arm-teardown.zip` — report, results, per-arm bounded traces, instrumentation, before/after inventories, preservation checks and file hashes.
- **Original evidence:** `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/two-arm-teardown/2026-10-05_072634Z/`.
- **Instrumented worker:** `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/two-arm-teardown/2026-10-05_072634Z/experiment_worker.py`.
- **Once-only launcher:** `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/two-arm-teardown/2026-10-05_072634Z/experiment_launcher.py`.
- **Detailed timeline:** `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/two-arm-teardown/2026-10-05_072634Z/request-timelines.json`.
- **Preservation checks:** `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/two-arm-teardown/2026-10-05_072634Z/preservation-result.json`.

**DONE — STOPPED for architectural review.** No live allocation was consumed by this local experiment.
