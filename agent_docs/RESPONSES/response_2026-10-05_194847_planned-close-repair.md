# Planned-close repair — ENGINEERING VERIFIED; STOP for review

**Planned collector shutdown now aborts registered pending requests before closing the browser.** Real localhost Chromium proves successful abort replies before target closure, no continuation/duplicate command for those IDs, and no held target GET at the server. This repairs the collector-initiated close path; it does not guarantee cancellation after an externally closed/crashed browser has already lost control.

## What changed

- **`smart_crawler/browser_session.py`:** one shared shutdown task immediately fences operations and continuation, aborts owned pending IDs using the existing resolver, awaits already-resolving entries, denies newly arriving pauses, and then calls Crawl4AI cleanup. Evidence-write failure, document caps/refusal, read cancellation/timeouts and normal context exit use it. The context-route guard also denies continuation while closing.
- **Confirmation:** `abort_confirmed` becomes true only on a successful `Fetch.failRequest` reply. Failed, canceled, closed-target or unresolved commands remain unconfirmed; no stale-ID retry or replacement HTTP request occurs. The first STOP and partial evidence remain intact. The prior narrowly eligible incidental closed-target cleanup remains nonfatal but explicitly unconfirmed.
- **Bound:** shutdown stays within `min(run start + max seconds, shutdown start + existing finalization reserve)`. Closure time is reserved inside that budget. A bounded 50 ms quiet observation checks queued pauses; it does not assert permanent silence. Unconfirmed findings are retained; no timeout, cap, transport, pagination or dependency settings changed.
- **Tests/helpers:** `tests/test_planned_shutdown.py` adds 22 native/defensive and comparator checks. `tests/snapshot_compare.py` validates shutdown deadline/order, completion and zero-loss complete-fixture facts before projecting only the two new volatile fields `drain_deadline` and `finished`. This follows the existing E-14 fact-bound comparison rule. No prior assertion or expected Capture output was removed or rewritten. The [closure audit](../../agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/planned-shutdown/2026-10-05_123946Z/closure-audit.md) lists each inspected path and library/supervisor boundaries.

## Local proof

| Native case | Confirmed aborts before close | Held GET handler receipts | Preserved result |
|---|---:|---:|---|
| Normal pre-classification hold | 1 | 0 | Interrupted read fails `collector_shutdown` |
| STOP during that hold | 1 | 0 | Original refusal retained |
| Normal actual product pacing | 1 | 0 | No second intentional dispatch |
| STOP during product pacing | 1 | 0 | Original refusal retained |
| Evidence-write failure during pacing | 1 | 0 | `evidence_write_limit` retained |
| New pause arriving during shutdown | 2 | 0 | Both IDs aborted once |
| Abort already resolving | 1 | 0 | Waits for existing resolution; no duplicate |

**Eight native abort SEND/reply pairs across seven cases** precede `Target.closeTarget` in the retained driver sequence. The [native evidence](response_2026-10-05_194847_planned-close-repair_native-evidence.json) includes raw session/Fetch/Network/frame identifiers, matched protocol replies, closure commands and server observations. Actual product pacing cases wait in the existing `gap()`; they do not use the artificial pre-classification barrier.

Normal successful read remains byte-exact with completion-to-next-dispatch pacing ≥5 seconds. The external-close negative control remains an explicit `browser_page_closed` failure with **one held GET received**, no confirmed abort and no successful body returned. Error/hung-abort/already-continuing doubles verify explicit unconfirmed findings, preserved first STOP and bounded cleanup; those injections are not native failure reproduction.

## Checks run on the final unchanged candidate

| Check | Result | Exit | Recorder elapsed |
|---|---|---:|---:|
| Final focused native/resolution/lifecycle/comparator | 68 passed | 0 | 208.324s |
| One full regression on final candidate | 235 passed | 0 | 1169.905s |
| Existing paired Capture comparison | PASS, 231 files | 0 | 116.329s |

Earlier 21/58 focused checks and a 225-test regression passed on preceding candidates. The first paired comparison FAILED because its normalizer did not recognize the two new clock fields; the retained exact diff contains only those fields and their derived log byte count. Content, hashes, references, outcomes and counts were unchanged. Bounded validation and ten positive/negative comparator controls were added, requiring fresh verification of the final source. The earlier failed comparison and passing evidence are intact. The table above binds `f497011c908057d4a1fb447c8b83a83152cf783ba3f3d8f00ee954aac904c7d3`. No test run today is independent QA certification.

Exact commands, from the repository root (recorder adds the fresh `ABM_CONTROL_EVIDENCE` destination; focused proof uses `DEBUG=pw:protocol`):

```bash
venv/bin/python -m pytest -q -s tests/test_planned_shutdown.py tests/test_resolution_stop.py tests/test_bounded_capture_repair.py tests/test_interception_lifecycle.py -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/python -m pytest -q -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/python tests/regen_fixtures.py --check --variant complete --stage capture --compare-to /home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/planned-shutdown/2026-10-05_123946Z/regression-final-controls/complete-raw
```

Evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/planned-shutdown/2026-10-05_123946Z/{focused-bound,regression-final,comparison-final}/result.json` and `command.log`; full native fixture records in matching `*-controls/`. Bounded driver proof has zero parse gaps. The fact-bound Capture comparison retains all checks of bytes, hashes, references, outcomes/counts and actual pacing; expected output was not accepted blindly.

Environment: installed Python 3.12.3, Crawl4AI 0.9.3, Playwright 1.52.0, pytest 8.3.5; Chromium 136.0.7103.25 headless_shell. Exact platform, browser/lock hashes and retained capture settings are in the checks JSON. No installation or version change occurred.

## Limits and open findings

- Planned abort success describes registered paused IDs, not cancellation of previously dispatched stream bytes or every browser resource. A continuation already in progress is never duplicated or retried; its cancellation can remain unconfirmed.
- Pauses arriving while shutdown still owns a usable session are denied. Pauses arriving during actual target loss can remain unconfirmed and are reported; the quiet observation is not a guarantee against late traffic.
- The existing supervisor can SIGINT then force-kill after its separate 5-second grace. An exhausted finalization budget or forced process loss can prevent confirmation. The controller records that limitation; this repair does not increase the supervisor or operation budgets.
- Closed-target errors and detachment are not abort acknowledgements. Worker/server monotonic clocks are shared; driver timestamps are parent observations of logs, not wire timing. Matched protocol replies substantiate the successful aborts. No wire-dispatch time is inferred from handler receipt.
- Original two-arm failing evidence is preserved. Historical homepage route-accounting and supervisor final-manifest counter findings remain **OPEN**.

No broader transport change was needed for the proved planned-close cases. **Next move: JARVIS reviews this candidate and its remaining teardown boundaries.** No live allocation is authorized or used here. Prepare remains ON HOLD; independent QA NOT RUN.

## Source identity and preservation

- Repository: `/home/moose/PYTHON/stark-web-factory-scrapper-v1`; branch `wf-scrapper-abm`.
- Base HEAD: `366f9830ba7b9bfb91f17b8655fd37467410123b` plus preserved dirty/untracked source. This is not a newly committed candidate.
- Starting 68-file inventory matched `aaf883a8c59960ab825e5a58508772bb9c099b49f65187b248e1f2ed813dc622`.
- Final 69-file inventory: `f497011c908057d4a1fb447c8b83a83152cf783ba3f3d8f00ee954aac904c7d3`. Controller and its affected comparison helper changed; one test file was added. All other intake source records and both dependency files match.
- All **14,285** pre-existing output/evidence/report files remain present and hash-identical. Seven monitored installed source files are unchanged. Current checkpoint/journal/ledger/session/changelog updates preserve their prior contents.

## Handoff — one file per item

- **Report:** [response_2026-10-05_194847_planned-close-repair.md](response_2026-10-05_194847_planned-close-repair.md).
- **Exact source/test diff:** [response_2026-10-05_194847_planned-close-repair_source-test.diff.txt](response_2026-10-05_194847_planned-close-repair_source-test.diff.txt).
- **Full controller:** [response_2026-10-05_194847_planned-close-repair_browser_session.py.txt](response_2026-10-05_194847_planned-close-repair_browser_session.py.txt).
- **Full added tests:** [response_2026-10-05_194847_planned-close-repair_test_planned_shutdown.py.txt](response_2026-10-05_194847_planned-close-repair_test_planned_shutdown.py.txt).
- **Full comparison helper:** [response_2026-10-05_194847_planned-close-repair_snapshot_compare.py.txt](response_2026-10-05_194847_planned-close-repair_snapshot_compare.py.txt).
- **Final source inventory:** [response_2026-10-05_194847_planned-close-repair_source-inventory.json](response_2026-10-05_194847_planned-close-repair_source-inventory.json).
- **Native command/server proof:** [response_2026-10-05_194847_planned-close-repair_native-evidence.json](response_2026-10-05_194847_planned-close-repair_native-evidence.json).
- **Commands, results and preservation checks:** [response_2026-10-05_194847_planned-close-repair_checks.json](response_2026-10-05_194847_planned-close-repair_checks.json).

**DONE — STOPPED after local engineering handoff.** No live traffic, Git mutation, dependency change, deletion, recon/Prepare work or deployment.
