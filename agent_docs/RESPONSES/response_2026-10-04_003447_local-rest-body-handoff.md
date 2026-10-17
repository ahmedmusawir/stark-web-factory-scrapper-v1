# Local REST body handoff — repair verified

**Confirmed:** returning millions of numeric byte values through CDP imposes substantial local result-delivery overhead. A bounded base64 representation removes most of that measured cost while preserving bytes and existing controls. **The original live op-17 failure remains unexplained.** No live request was made during this mission.

**Verification complete:** 179 engineering tests passed; the existing Capture comparison passed across 231 files. Both used the same unchanged final source. CHK remains incomplete; Prepare stays ON HOLD; independent QA remains NOT RUN.

## What the evidence establishes

Preserved live run: `outputs/CyberizeGroup/runs/2026-10-03T17-35-57Z`. Its op-17 observed 200 headers and Network.loadingFinished at +12.977s, but no Python result receipt before read_deadline at +29.758s. The saved posts body is zero bytes. This does not establish how many bytes JavaScript consumed or the live payload's size. The original late callback/cleanup delay was not reproduced locally.

The original reader used `Array.from(...)`, then `Runtime.runScript(returnByValue=True)`. Installed Playwright forwards the CDP result and recursively traverses returned lists before resolving the Python callback (`_connection.py:400,502–512`); its pipe transport uses JSON. Source hashes are in `inspection-sources.json`. These observations support the representation mechanism; individual browser, driver and Python costs were not separately profiled.

The native fixtures serve 100 REST-shaped objects with all declared sample fields, unknown fields, large integers, escaped strings and literal UTF-8 Unicode. Expected bytes/hashes come from deterministic fixture inputs. They use the existing browser-owned read path, real Chromium, existing fixture server, and actual Capture supervisor. One case precedes the read with three product page captures, each generating ordinary Fetch/XHR/image/POST traffic. This is not an exact replay of the live site's background workload.

| Payload / sequence | Original number arrays | Compact comparison | Fidelity |
| --- | ---: | ---: | --- |
| 1,500,000 bytes | 1.855s | 0.056s | Exact bytes/hash |
| 4,000,000 bytes | 5.638s | 0.193s | Exact bytes/hash |
| 4,000,000 bytes after 3 captures | 5.041s | 0.185s | Exact bytes/hash |
| 8,000,000 bytes | 12.385s | 0.593s | Exact bytes/hash |
| 10,489,856 bytes | 19.493s | 0.694s | Exact bytes/hash |

Times measure **delivery of the browser's result-prepared marker to Python result receipt**. Marker delivery can itself be delayed. Browser performance/wall timestamps, independent server body-send, CDP network completion, body consumption, result preparation, Python receipt and cleanup are retained in `timing-matrix.json` and per-case logs. JavaScript encoding remained subsecond; most observed improvement was after result preparation. The encoding-only comparison and original baseline both passed all six assertions—**no missing-body timeout was manufactured or reproduced**.

The 10,489,856-byte source crosses the existing 10 MiB cap. Both versions returned the exact 10,485,760-byte prefix, labeled incomplete with `response_limit`; it is not a complete JSON collection. Corrected actual-supervisor checks also proved full 1.5 MB / 4 MB / 8 MB response fidelity and cap-prefix preservation, with no post objects invented and no later media collection after the cap stop.

## Small correction and scope

- `smart_crawler/browser_session.py:779–818`: encode byte views into base64 blocks of at most 32 KiB, decode strictly in Python, then retain the existing bytes/hash/provenance processing. Only this product file changed.
- `tests/fixture_server.py`: optional deterministic body responses and a loopback activity page; existing fixture defaults preserved.
- `tests/handoff_probe.py`: payload facts and bounded browser/Python timing instrumentation.
- `tests/handoff_worker.py`: existing Capture supervisor with measurement hooks, fixture-only.
- `tests/test_read_body_handoff.py`: exact byte/hash/Unicode, prior-activity, cap and actual-supervisor assertions.

No REST field filtering, pagination, timeout/cap increase, retry, alternate client, dependency change, direct Playwright import or security setting change. Native identity, redirects, pacing, refusals, final-resolution STOP and cancellation behavior remain unchanged. No certified-test assertion was weakened. The full result is still returned through CDP; this is compact encoding, not streamed IPC.

## Engineering checks

| Check | Result | Recorder elapsed |
| --- | --- | ---: |
| Original reader baseline | 6 passed; exit 0|223.62s|
| Encoding-only compact comparison | 6 passed; exit 0|172.86s|
| Affected reader/deadline/cancellation/redirect controls | 16 passed; exit 0|366.80s|
| Supplemental actual-supervisor sizes/cap | 3 cases passed; helper exit 0|214.56s|
| Full engineering regression |**179 passed; exit 0**|888.41s|
| Existing paired Capture comparison |**231 files PASS; exit 0**|115.28s|

The individual cap fixture correctly exits 2 with `response_limit`; its verification passes. Raw-reader reference/hash checks distinguish complete responses from valid partial packages. Exact commands, phase identities and evidence paths are in the results JSON and `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/rest-handoff/2026-10-03_175254Z/exact-check-commands.json`. Primary final commands were:

```bash
venv/bin/python -m pytest -q -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/python tests/regen_fixtures.py --check --variant complete --stage capture --compare-to agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/rest-handoff/2026-10-03_175254Z/regression-controls/complete-raw
```

Each ran through the existing recorder with fresh evidence paths. The module invocation avoids the installed pytest script's stale lowercase-checkout shebang; nothing was reinstalled. Earlier setup issues are retained: a refused existing recorder-directory label, a supplemental-helper import failure before browser startup, and correction of a newly added fixture's egress-event assertion. The strengthened assertion ran in the final full suite. Existing expectations were not replaced.

## Identity, preservation and limits

- Checkout: `/home/moose/PYTHON/stark-web-factory-scrapper-v1`
- Branch: `wf-scrapper-abm`
- Base HEAD: `366f9830ba7b9bfb91f17b8655fd37467410123b` plus dirty/untracked work; not a completed implementation commit.
- Final 65-file inventory SHA-256: `4166482e389d46c7680e18ae11a0406ebe893c3a28631a9f7e04d455614a5afe`
- Initial reviewed 62-file inventory: `f2aaab42fa6c64ef1cb621566ad7d4c8e606814e4d9f1caa5013979324b1a27b`
- All **8,157 prior evidence/output/report files** unchanged. Original checkpoint contents preserved; only the five listed source/test paths differ from the intake source.

The original direct over-cap read took 32.337s through terminal processing: the by-value result arrived within its wait budget, with later Python processing outside that await. This is not proof of a 30s end-to-end bound. The hard supervisor is unchanged; the corrected cap case was verified through it. The earlier supervisor-finalization manifest-counter gap remains outside this repair.

Single local comparisons establish a substantial representation cost, not complete-site reliability or the cause of the live timeout. Hidden live workload, actual posts body size, detailed serialization sub-costs and the live cleanup delay remain uncertain. **Recommended next action: JARVIS reviews this scoped change and proof before any further authorization.**

## Handoff

- Report: `agent_docs/RESPONSES/response_2026-10-04_003447_local-rest-body-handoff.md`
- Compact results: `agent_docs/RESPONSES/response_2026-10-04_003447_local-rest-body-handoff_results.json`
- Exact source/test diff against intake: `agent_docs/RESPONSES/response_2026-10-04_003447_local-rest-body-handoff_source-test.diff.txt`
- Final source inventory: `agent_docs/RESPONSES/response_2026-10-04_003447_local-rest-body-handoff_source-inventory.json`
- Evidence root: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/rest-handoff/2026-10-03_175254Z/`
- Timelines: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/rest-handoff/2026-10-03_175254Z/timing-matrix.json`
- Preservation proof: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/rest-handoff/2026-10-03_175254Z/preservation-result.json`
- Final Capture comparison: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/rest-handoff/2026-10-03_175254Z/comparison-controls/F09-complete-l3kywy4n/full-comparison.json`

RECOVERY, campaign journal, engineering log, acceptance evidence and session records are updated. No live traffic, Git mutation, destructive action, deployment or Prepare implementation. **STOP — awaiting JARVIS review.**
