# CHK controller repair — local verification complete

**Done:** the same-URL request classification defect is repaired and locally verified. **37 affected controls passed; the full suite passed 143 tests; the paired Capture comparison passed all 231 files.** Independent QA remains **NOT RUN**.

**Next move:** JARVIS reviews this handoff; Tony decides any replacement live allocation. **No live website requests were made.** The earlier failed CHK smoke remains incomplete and preserved. Prepare/E1/E2 have not resumed.

## Reproduction and repair

Before changing product code, real Chromium reproduced the original failure: the document and its generated stylesheet used the same URL/method; the document dispatched once, then the stylesheet triggered `ambiguous_intentional_request`. `E/before-fix-real/result.json` records **1 expected failure, 3 deselected, exit 1**; `E/before-fix-real-controls/same-url-stylesheet.json` retains the failing trace. An earlier sandbox socket denial is separately retained and is not claimed as reproduction.

`smart_crawler/browser_session.py:334,354,392` now joins paused Fetch requests to native Network evidence and checks expected resource/frame identity. Initial document admission requires a main-frame Document request with its native navigation loader/request correlation. Redirect predecessor/Network identity, scope, five-hop bound, five-second completion-based pacing, duplicate guards, refusal stops and budgets remain enforced.

For intentional GET/HEAD reads, `browser_session.py:544,568` compiles the coordinator's Fetch script in a **same-frame isolated execution context**, with **universal access explicitly false**. Chromium's initiating script ID must match that compiled script; the resulting Network ID is joined to the intercepted Fetch ID. A sourceURL label is not trusted as identity. Page-generated Fetch/XHR with matching URL/method/frame—even a spoofed sourceURL—stays incidental. No HTTP headers/query identifiers, new client, dependency or browser security setting was introduced. Reads still use same-page Chromium `window.fetch` and bounded `Response.body.getReader`, with normal origin/CORS rules; the existing CORS-failure control passes.

Installed Chromium reports native Fetch as **XHR at interception / Fetch in the Network event**. The controller retains both observations and checks that evidenced pairing. CDP admission IDs now also govern response/refusal/error observation (`browser_session.py:287`); the public browser Request observer supplies statistics only because it exposes no public CDP request ID. Prevented events distinguish `intentional_prevented`, `incidental_prevented` and unresolved identity. Incidental events never increment intentional dispatches.

## What the local checks prove

- Same-URL stylesheet, image, Fetch and XHR during document capture: successful capture, one intentional dispatch; background requests reach the loopback server.
- Page-generated Fetch/XHR versus coordinator GET/HEAD: an incidental **403** does not impersonate or block the separately correlated coordinator read, which returns 200; two intentional dispatches total including bootstrap. Matching sourceURL cannot forge script identity.
- Genuine second document / duplicate compiled-script Fetch: prevented; no second intentional dispatch. Missing initiator identity: explicit stop before read dispatch. The latter is a documented injected-observation-loss control on real browser traffic.
- Redirects for documents/Fetch/HEAD, completion pacing, scope, refusal/challenge positives and negatives, byte/request/time limits and partial preservation remain covered by the passing affected and full suites. Sticky-stop prevention reports incidental resources separately.
- Capture comparison validates source bytes, hashes, values, references, outcomes and counts before normalizing volatile times/protocol IDs. The helper now also validates and preserves frame/script/request associations. No generated output was accepted as a new expected result.

Evidence root **E**: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/controller-repair/2026-10-03_051020Z`. Exact executed commands (retained per-command environment uses `ABM_CONTROL_EVIDENCE=E/<stage>-controls`, bounded recorder and exclusive new evidence folders):

```text
venv/bin/pytest -q tests/test_request_identity.py tests/test_browser_controls.py -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/pytest -q -o tmp_path_retention_count=1000000 -o tmp_path_retention_policy=all
venv/bin/python tests/regen_fixtures.py --check --variant complete --stage capture --compare-to /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/controller-repair/2026-10-03_051020Z/regression-final-controls/complete-raw
```

| Check | Result | UTC on October 3 | Evidence |
|---|---|---|---|
| Affected real-browser controls | 37 passed, exit 0; 283.17s pytest time | 05:53:11–05:57:54 | `E/affected-final/` |
| Full engineering regression | 143 passed, exit 0; 469.95s pytest time | 05:57:55–06:05:45 | `E/regression-final/` |
| Paired complete Capture fixture | 231-file canonical comparison PASS, exit 0 | 06:05:45–06:07:40 | `E/snapshot-final/`, `E/snapshot-final-controls/F09-complete-_8xgc50i/full-comparison.json` |

Earlier failing development checks remain retained: an initial Fetch/XHR event-type mismatch, then the helper's obsolete prevention-event expectation. The final source fixes those findings. These are local engineering outcomes, not independent QA or current live-access results.

## Source identity, scope and remaining gates

Repository `/home/moose/python/stark-web-factory-scrapper-v1`; branch `wf-scrapper-abm`; unchanged base HEAD `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f` plus preserved dirty/untracked work. **No implementation candidate commit exists.** All three final checks have identical before/after source inventory SHA-256:

`3e629379a1295ca0a76c636ab2dc361ffdb449fdf2bdc9ae10ebc5a43af6e2d5`

Actual environment: Python3.12.3, Crawl4AI0.9.3, Playwright1.52.0, Chromium136.0.7103.25; installed API/browser/lock hashes and per-file source hashes are in the checks companion and source inventories. No installation, dependency changes, Git mutations, cleanup or deployment. Existing capture settings, USER_AGENT and TLS configuration are unchanged.

The focused diff contains only `smart_crawler/browser_session.py`, `tests/fixture_server.py`, `tests/test_browser_controls.py`, new `tests/test_request_identity.py`, and `tests/snapshot_compare.py`. RECOVERY, ledger, engineering log, journal and October3 session record were updated separately. All 5,357 baseline files remain present; 5,349 are byte-unchanged, with all differences confined to authorized source/records. Prior live evidence, reports, dependency files and the earlier certified-test files are unchanged. All48 AC rows remain; independent QA is NOT RUN throughout.

AC-005/T-04 and AC-016/T-11 have local repair proof; AC-041/T-22 has the new full regression, with E1 still pending. AC-039/T-21 and AC-042/T-22 remain blocked on the uncompleted live/build obligations. The shared allocation is unchanged: **no replacement smoke or E2 attempt was spent or authorized here**. Real-site behavior with this repair is untested; no root cause for historical429s or full-crawl readiness is claimed. Future QA must bind Tony's actual committed tree to these source hashes; SOL decides evidence reuse.

## Handoff files

- **Repair report:** [response_2026-10-03_124643_chk-controller-repair.md](response_2026-10-03_124643_chk-controller-repair.md)

- **Focused source/test diff:** [response_2026-10-03_124643_chk-controller-repair_source-test.diff.txt](response_2026-10-03_124643_chk-controller-repair_source-test.diff.txt)

- **Sanitized evidence excerpt:** [response_2026-10-03_124643_chk-controller-repair_evidence.json](response_2026-10-03_124643_chk-controller-repair_evidence.json)

- **Commands, results and source hashes:** [response_2026-10-03_124643_chk-controller-repair_checks.json](response_2026-10-03_124643_chk-controller-repair_checks.json)

- **Preservation check:** [preservation-final.json](../ACTION/wf-scrapper-abm/EVIDENCE/controller-repair/2026-10-03_051020Z/preservation-final.json)

- **Current checkpoint:** [RECOVERY.md](../../RECOVERY.md)

The diff compares against the pre-repair working tree. The evidence excerpt contains no response bodies, cookies or sensitive headers; its event indices and hashes identify the full preserved traces. Missing fields in old events remain missing. An active operation ID on an incidental event does not make that traffic intentional.

Full traces and source inventories remain under E. No ZIP was created for this lightweight handoff.

**STOPPED — LOCAL REPAIR VERIFIED; AWAITING REVIEW AND TONY'S REPLACEMENT LIVE-ALLOCATION DECISION.**
