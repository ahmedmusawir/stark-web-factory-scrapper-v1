# Redirect-identity repair — locally verified

**Done: the missing-predecessor gap is repaired and locally verified.** Both GET/HEAD out-of-scope cases are denied by product redirect controls before dispatch. Allowed redirects succeed with correct chains, counts and completion-based pacing. **192 engineering tests passed; the paired Capture comparison passed across 231 files.** No live website requests were made.

## What changed

Before incidental admission, an active operation's owned Network ID now requires redirect correlation. The collector holds the paused request for matching native evidence within existing operation/global bounds, validating session ownership, active operation, Network ID, frame, resource, method and previous-to-next transition. Missing/conflicting evidence produces `ambiguous_redirect_identity`.

Chrome's raw `predecessor` remains null when omitted. `resolved_predecessor` and `correlation_source` separately record the proven relationship. That relationship drives scope checks, hop/loop accounting, completion, pacing and dispatch counting, while preserving the native-parent path. Typed product admission errors now take precedence over the browser's generic abort `TypeError`.

Only five source/test files changed:

- `smart_crawler/browser_session.py`
- `tests/fixture_server.py`
- `tests/snapshot_compare.py`
- `tests/test_interception_boundary.py`
- `tests/test_redirect_identity.py`

The Document/Fetch/XHR patterns, final-resolution STOP/error handling, context guards, compact body script, bounds and transport are unchanged. No timeout/cap increase, pagination change, dependency change or domain exception.

## Proof and results

| Check | Result |
| --- | --- |
| Initial native scope/allowed redirect checks | 4 passed; exit 0 |
| Expanded focused controls | 29 passed; exit 0 |
| Full engineering regression, once on final candidate | **192 passed; exit 0**, 1,063.325s |
| Existing paired Capture comparison, same candidate | **231 files PASS; exit 0**, 116.542s |

- Native GET/HEAD scope cases require product `intentional_prevented` with `redirect_out_of_scope`; the fixture-only egress guard is explicitly excluded as the passing mechanism.
- Allowed cross-origin loopback redirects pass for GET/HEAD with Network evidence delivered before or after pause handling. Native nulls, separate resolved IDs, server timelines, chain/counts and ≥5s gaps are retained.
- Five deliberately missing/conflicting observation cases refuse explicitly: missing transition, wrong previous URL, frame, resource and method. Each aborts without target dispatch or any later intentional dispatch after STOP. These are labeled fixture faults, not unexplained native browser failures.
- Existing same-URL identity, native-parent redirects, loop/hop limits, refusal, budget, context, cancellation, cleanup and final-resolution STOP controls passed in the full suite.
- Complete 1.5 MB / 4 MB / 8 MB bodies retain exact hashes, including preceding page activity. The cap fixture retains the exact 10 MiB prefix and reports incomplete/`response_limit`. No partial body is promoted to a complete collection.

The existing denied-hop assertion now checks the separately resolved predecessor, while additionally requiring native null and no fixture-egress substitution. Capture pause-count expectations changed from 26 to 19 based on declared resource facts: 18 intentional operations plus 1 iframe. Six images still load; the excluded widget script remains blocked by the context guard. Server requests remain 24. Source bytes, object values, outcomes, counts, references and hashes retain their existing expectations; generated output was not adopted as a golden result.

Exact commands and phase evidence are in the checks JSON. Final commands:

```bash
venv/bin/python -m pytest -q -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/python tests/regen_fixtures.py --check --variant complete --stage capture --compare-to agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/redirect-identity/2026-10-04_063724Z/regression-controls/complete-raw
```

Both ran through the existing recorder with fresh local evidence paths. Native redirect evidence and the exact source/test diff are separate attachments.

## Identity, preservation and remaining limits

Checkout: `/home/moose/PYTHON/stark-web-factory-scrapper-v1`. Branch: `wf-scrapper-abm`. Base HEAD: `366f9830ba7b9bfb91f17b8655fd37467410123b`, plus preserved dirty/untracked work; this is not a new candidate commit.

The reviewed 66-file starting inventory matched exactly. Final **67-file** inventory, unchanged across focused/full/comparison checks:

`f52235202ce3fb546d436efa4b4b4a7a92025868edef20a939c25c81e0dcaa53`

All **11,333 prior evidence/output/report files** remain unchanged; original checkpoint text is preserved. No Git mutation, destructive action or deployment occurred.

**Still open:** homepage bootstrap/route accounting discrepancy; historical supervisor-finalization counter gap; CHK live completion and live posts-body qualification. These local results do not establish live-site reliability. Prepare remains **ON HOLD**; independent QA remains **NOT RUN**.

## Handoff

- Report: `agent_docs/RESPONSES/response_2026-10-04_130819_redirect-identity-repair.md`
- Exact source/test diff: `agent_docs/RESPONSES/response_2026-10-04_130819_redirect-identity-repair_source-test.diff.txt`
- Full updated controller: `agent_docs/RESPONSES/response_2026-10-04_130819_redirect-identity-repair_browser_session.py.txt`
- Final source inventory: `agent_docs/RESPONSES/response_2026-10-04_130819_redirect-identity-repair_source-inventory.json`
- Native redirect evidence: `agent_docs/RESPONSES/response_2026-10-04_130819_redirect-identity-repair_native-events.json`
- Commands, results and comparison proof: `agent_docs/RESPONSES/response_2026-10-04_130819_redirect-identity-repair_checks.json`
- Full evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/redirect-identity/2026-10-04_063724Z`
- Preservation proof: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/redirect-identity/2026-10-04_063724Z/preservation-result.json`

Engineering checkpoint, ledger, journal and session record updated. **Ready for JARVIS review; STOP. No live allocation is authorized.**
