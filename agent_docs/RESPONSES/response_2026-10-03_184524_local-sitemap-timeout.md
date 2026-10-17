# Local sitemap timeout — repair verified; live cause unresolved

## Verdict

**A local deadline/handoff defect was demonstrated and repaired.** With the preserved old reader, Chromium had consumed **2,048 bytes**, but Python returned **0** after timeout. The repaired reader returns those **2,048 bytes** and correctly reports failure. The delayed-setup supervised sitemap fixture now preserves its **64-byte** prefix instead of saving an empty response.

The original live run remains **INCOMPLETE**. Its supervisor enforced the advertised deadline; the reason live protocol events/result delivery arrived late remains unknown. No live request was made during this mission.

## What happened in the live run

Original source: `outputs/CyberizeGroup/runs/2026-10-03T11-46-34Z/stage_log.txt`. Times below are Python-observed seconds after sitemap operation start.

| Time | Retained observation | Log line |
|---|---|---|
| 0.000 | `op-3` starts; monotonic deadline `385132.118566`, approximately 30 seconds later | 1350 |
| +0.227 | Compiled script identity bound; exact setup/runScript start was not separately logged | 1355 |
| +0.266 | Pacing wait requested: 4.680 seconds | 1361 |
| +5.026 | Intentional sitemap dispatch | 1366 |
| +6.359 | Continuation command completed | 1368 |
| +27.903 / +28.037 | CDP / Playwright HTTP 200 observations | 1370–1371 |
| +30.076 | `operation_complete(error=null)` | 1372 |
| +30.898 / +31.206 | Native completion / Playwright request-finished callbacks delivered | 1373–1374 |
| +31.778 / +32.190 | Page closed / context-close error recorded | 1375–1377 |
| UTC 11:48:46 | Supervisor stop and finalization: **`operation_watchdog`** | 1378–1379 |

The native completion event contains browser timestamp `385118.687465`; its request-to-completion interval on the **browser clock** was 16.321 seconds. Browser timestamps and Python callback-arrival times are distinct observations. They do not prove when the body became available to Python. No sitemap body/result was archived. Exact signal arrival and the live Python cancellation exception were not separately logged.

**Why the null error was misleading:** the old `finally` block always emitted `operation_complete`, using only `op.error`. Timeout handling updated the session stop reason without necessarily setting that field; external `CancelledError` bypassed `except Exception`. The event was terminal bookkeeping, not proof of success. The parent’s SIGINT/cancellation path is consistent with the live sequence; the precise interleaving remains unobserved.

Full timeline and timer references: [live-timeline.json](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/sitemap-timeout/2026-10-03_121047Z/live-timeline.json) and [readable diagnosis](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/sitemap-timeout/2026-10-03_121047Z/diagnosis.md).

## Timer ownership and the bounded correction

Before repair, the parent’s operation deadline and Python’s approximately 30-second wait began before setup/pacing. The browser’s 29.9-second abort timer started **after** script setup. Delayed setup could put that abort beyond Python’s deadline, losing chunks already held in JavaScript. The native byte-counter proof confirms this mechanism locally.

The read now has one end boundary. For a normal **30-second** read, the cooperative browser cutoff is **29 seconds**, Python’s fallback is **29.75 seconds**, and the unchanged supervisor cutoff is **30 seconds**. Setup and pacing still consume the budget. The internal handoff reserves shrink for shorter remaining budgets. No limit was increased and no retry was added.

The JS timer uses a same-host absolute wall-clock cutoff; monotonic Python/supervisor limits remain authoritative. New setup/script/result observations and explicit **success / failure / cancelled** terminal outcomes improve correlation. Timeout/cancellation closes the existing page, and existing stop reasons remain sticky. The 90-second Crawl4AI navigation timeout applies to document capture, not the sitemap Fetch read.

Product change: [browser_session.py](/home/moose/python/stark-web-factory-scrapper-v1/smart_crawler/browser_session.py:746). The [supervisor](/home/moose/python/stark-web-factory-scrapper-v1/recon_pipeline/capture.py:251) is byte-for-byte unchanged. Identity, pacing, scope, redirects, refusal stops and byte caps remain covered by existing checks.

## Local proof and verification

| Check | Result |
|---|---|
| Browser-owned-byte proof, preserved old/current methods | Before: 2,048 consumed / 0 returned. After: 2,048 consumed / 2,048 returned. Both deadline failures. |
| Complete response within its available budget | Correct body returned; terminal success |
| Actual supervised stalled sitemap, ordinary and delayed setup | 64-byte prefix preserved; typed failure; no subsequent collection |
| Task cancellation and cleanup | Terminal cancelled; original stop reason and prior captured evidence retained |
| Affected controls | **55 passed**, exit 0 |
| Full engineering regression | **173 passed**, exit 0; 685.20 seconds recorder elapsed |
| Existing paired Capture comparison | **231 files PASS**, exit 0; 114.46 seconds |

The scheduling latency is explicitly injected; HTTP requests, streamed bodies and Chromium cancellation are real loopback behavior. It is not a claim to replay the original live timing. The final checks all used unchanged source inventory:

`f2aaab42fa6c64ef1cb621566ad7d4c8e606814e4d9f1caa5013979324b1a27b`

Exact child commands, wrapper context and evidence paths are in the checks JSON. Principal checks:

```bash
venv/bin/pytest -q tests/test_read_deadlines.py tests/test_interception_lifecycle.py tests/test_resolution_stop.py tests/test_browser_controls.py -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/pytest -q -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/python tests/regen_fixtures.py --check --variant complete --stage capture --compare-to /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/sitemap-timeout/2026-10-03_121047Z/regression-controls/complete-raw
```

Each ran through the existing recorder with a fresh evidence destination and `ABM_QUIET_LOG=1`; native proofs used `ABM_CONTROL_EVIDENCE`. Reproduction must use new destinations; never overwrite these records.

Pre-fix failures remain retained. An initial affected run had **8 passes then was interrupted** because an old native-abort helper’s literal replacement no longer matched. Its binding was corrected and guarded; all behavioral assertions remain. An extra proof’s first setup attempt lacked the archived controller’s relative lock-hash input; supplying an exact evidence snapshot corrected that setup without changing working dependencies. Neither failed attempt is counted as a pass.

## Source, preservation and checkpoint

Branch: **wf-scrapper-abm**. Initial HEAD: `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f`. HEAD advanced externally to **`366f9830ba7b9bfb91f17b8655fd37467410123b`**; no agent Git mutation occurred. The completed repair remains dirty/untracked, so HEAD alone does not identify it. The supplied inventory covers **62 files**, including untracked source.

Changed source files:

- `smart_crawler/browser_session.py` — bounded deadline coordination and terminal reporting.
- `tests/test_read_deadlines.py` — complete/stalled/supervised/cancellation checks.
- `tests/deadline_worker.py` — loopback-only setup-latency helper using the actual supervisor.
- `tests/fixture_server.py` — deterministic partial-stream fixtures.
- `tests/test_interception_lifecycle.py` — native-abort injection binding; assertions preserved.

All **7,204 pre-existing evidence/output/report files** are unchanged. Earlier live runs and failed local evidence remain intact. Recovery, campaign journal, engineering log, acceptance evidence and session checkpoint are updated. All **48 independent QA rows remain NOT RUN**. This is engineering verification, not QA certification.

## Handoff files

- [Report](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-03_184524_local-sitemap-timeout.md)
- [Focused source/test diff](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-03_184524_local-sitemap-timeout_source-test.diff.txt)
- [Checks, exact commands and evidence index](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-03_184524_local-sitemap-timeout_checks.json)
- [Complete source identity inventory](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-03_184524_local-sitemap-timeout_source-inventory.json)
- [Full current browser_session.py — read path](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-03_184524_local-sitemap-timeout_browser_session.py.txt)
- [Full current capture.py — supervisor path](/home/moose/python/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-03_184524_local-sitemap-timeout_capture.py.txt)
- [Current recovery checkpoint](/home/moose/python/stark-web-factory-scrapper-v1/RECOVERY.md)

## Remaining uncertainty and next action

The original live event/result delay is still unexplained; this local repair does not establish its root cause or full-crawl readiness. A severely unresponsive runtime can still reach the hard watchdog. **Missing final manifest dispatch/document/resource counters remain an unresolved finding**, with no unrelated reporting change made.

**Recommended next action: JARVIS reviews this local repair and the remaining live-handoff uncertainty before authorizing further work.** Live allocations remain consumed. Prepare is **ON HOLD** for the in-repo agent-skill amendment; no P1–P6/E1/E2. Independent QA **NOT RUN**. Stopped after this handoff.
