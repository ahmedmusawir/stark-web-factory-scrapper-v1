# Narrow custom interception — applied, qualification BLOCKED

**The resource boundary change works locally, but the candidate is not qualified.** Images, stylesheets and scripts load and remain observable without custom CDP pauses. A new GET/HEAD cross-host redirect check exposed an existing identity gap that also reproduces on the original all-resource controller. **Stopped at that control failure; no live requests or broader repair.**

## What changed

`smart_crawler/browser_session.py:286–292` now enables three request-stage patterns: `Document`, `Fetch`, `XHR`, each with `urlPattern: "*"`. No host exceptions. Only `created()` changed; an AST comparison confirms compact body delivery, identity, resolution/error handling, pacing, deadlines and STOP logic are unchanged. Context/popup/service-worker guards and passive Network/Playwright observers remain intact.

The other changes are deterministic fixture routes, four new boundary checks in `tests/test_interception_boundary.py`, and scoped assertions in `tests/test_request_identity.py`. Its stylesheet-triggered STOP test now triggers on incidental Fetch/XHR, retaining the same server-count, allocation and incidental-versus-intentional prevention assertions. Same-URL image/stylesheet checks now additionally require no custom classification; read-identity checks assert the actual native type pair. This is authorized by the current boundary-repair instruction; no historical result or expected snapshot was rewritten.

## What was proved

- **Before change:** the native loading test failed because Image, Stylesheet and Script entered custom interception. Script execution, CSS application and image decoding had succeeded. This failing baseline is preserved.
- **After change:** script execution, applied CSS and decoded PNG dimensions passed; server bodies and passive response events were observed, with no custom pauses for these types.
- **Native churn:** two partially delivered images were canceled by a subsequent product navigation. Their Network IDs never entered custom interception/resolution; capture and a later browser read succeeded.
- **Installed type behavior:** intentional GET/HEAD `window.fetch` is observed as **XHR in Fetch events, Fetch in Network events**. Both patterns remain necessary.
- **Identity:** same-URL incidental Fetch/XHR remain distinct; genuine duplicates, missing initiators and retained-type sticky STOP checks passed.
- **Byte handoff:** the small native body matched exact bytes and SHA-256. The prior large-body/cap proof remains historical; it was not rerun after the new scope failure.

## Concrete blocker

The fixture redirects `http://127.0.0.1:<port>/boundary-denied` to `http://localhost:<port>/never-boundary`. Both are local; the destination is outside the controller's allowed hostname set.

Expected: classify the next hop as intentional and deny it before dispatch with `redirect_out_of_scope`. Actual, for **GET and HEAD**:

1. The custom session pauses the next XHR hop, so wildcard URL coverage is intact.
2. Its Fetch event has no `redirectedRequestId`. Network evidence retains the same Network ID and redirect transition.
3. `admission_kind()` returns incidental at `browser_session.py:523–526` before redirect correlation/scope enforcement.
4. The **fixture-only** egress guard at `:571–577` aborts it. The destination receives no request; the read returns incomplete/`TypeError`, with no intentional scope-denial event.

The preserved original controller reproduces both failures under the same unchanged assertions. **This gap predates narrowing.** Code inspection shows that without the fixture-only guard, incidental handling reaches continuation at `:583–585`; this is a control gap, not proof that any live out-of-scope request occurred.

**Recommended next action:** JARVIS authorizes a separate, narrow missing-predecessor redirect-identity repair, with native pre-dispatch proof. Correlation using owned Network redirect evidence, or explicit ambiguity refusal, needs local proof before acceptance. No implementation of that mechanism was attempted here.

## Verification and limits

| Check | Result |
| --- | --- |
| Original resource-boundary baseline | 1 expected failure; exit 1 |
| Narrow boundary + request-identity checks | **14 passed, 2 failed; exit 1** |
| Original-controller GET/HEAD scope reproduction | Both reproduce; helper exit 0 confirms the gap, not a product PASS |
| Full engineering regression | **NOT RUN — required scope gate failed** |
| Existing Capture fixture comparison | **NOT RUN — no qualified final candidate** |

Exact commands, timing, source hashes and retained logs are in the checks JSON. The failed assertions were not relaxed. The full refusal/budget/context/redirect and large-body qualification matrix remains pending; unchanged source is not a substitute for testing. Earlier 179-test/231-file results are historical and do not certify this candidate.

Branch `wf-scrapper-abm`; base HEAD `366f9830ba7b9bfb91f17b8655fd37467410123b` plus preserved dirty/untracked work. Initial reviewed 65-file inventory matched exactly. Final **66-file** inventory:

`29315b06428a66896a5b23af3bbdfd25a0c7ed7fdd6bc3b0724d687a03187727`

All **11,209** prior evidence/output/report files are unchanged, including the latest failed live run. Original checkpoint contents remain preserved. Homepage bootstrap/route accounting and the historical supervisor-finalization counter gap remain **UNRESOLVED**. Prepare stays **ON HOLD**; independent QA **NOT RUN**. No dependency change, Git mutation, destructive action or deployment.

## Handoff files

- Report: `agent_docs/RESPONSES/response_2026-10-04_120350_narrow-interception.md`
- Exact source/test diff against intake: `agent_docs/RESPONSES/response_2026-10-04_120350_narrow-interception_source-test.diff.txt`
- Full current controller: `agent_docs/RESPONSES/response_2026-10-04_120350_narrow-interception_browser_session.py.txt`
- Final source inventory: `agent_docs/RESPONSES/response_2026-10-04_120350_narrow-interception_source-inventory.json`
- Native event evidence: `agent_docs/RESPONSES/response_2026-10-04_120350_narrow-interception_native-events.json`
- Commands, results and remaining gaps: `agent_docs/RESPONSES/response_2026-10-04_120350_narrow-interception_checks.json`
- Full local evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/interception-boundary/2026-10-04_055713Z`

Engineering checkpoint, journal, ledger and session record updated. **STOP — awaiting the scoped architectural decision.**
