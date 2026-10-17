**DONE — both bounded repairs verified locally. No live scrape ran.**

The media collector now follows valid `X-WP-TotalPages` past a nonempty short intermediate page. Normal shutdown no longer becomes a collection failure solely because an incidental abort reaches an already closed target. Unexpected closure, uncertain classification, intentional failures, and unrelated protocol errors still fail.

**What changed**

- `smart_crawler/rest_client.py`: records `short_intermediate_page` on the saved response and continues advertised pagination. Empty intermediate pages, malformed/incomplete responses, missing/changing totals, refusal and exhausted limits retain explicit partial/stop behavior. Duplicate IDs are retained as separate derivatives and reported; duplicate IDs or a final count mismatch prevent a complete verdict. Advertised totals and source bytes are unchanged.
- `smart_crawler/browser_session.py`: only `Fetch.failRequest` + cleanup already underway + no active operation + incidental classification + `TargetClosedError` + the owned page confirming closure qualifies for `interception_cleanup_closed`. The diagnostic error remains visible; the entry becomes terminal `closed`, returns false, and cannot be resolved again. Earlier stop reasons remain intact. No continuation, retry, transport change or limit increase was added.
- `tests/test_bounded_capture_repair.py`: new offline pagination cases, recording-CDP boundary checks, native loopback cleanup reproduction, and native unexpected active-read closure proof. No existing test assertions or expected Capture outputs were changed.

**Evidence and results**

The preserved live media responses contain 100, 100 and 96 records while advertising 1,753 records / 18 pages. Their bytes and hashes are unchanged. The repair does not alter the earlier run or claim that its missing media records were collected.

| Phase | Result | Exit | Seconds |
|---|---|---:|---:|
| before | 8 failed, 12 passed in 34.49s | 1 | 35.530 |
| focused | 1 failed, 54 passed in 156.22s (0:02:36) | 1 | 156.915 |
| focused-final | 56 passed in 162.13s (0:02:42) | 0 | 163.048 |
| regression | 213 passed in 1122.70s (0:18:42) | 0 | 1123.633 |
| comparison | PASS F-09 complete Capture facts, source bytes, references, inventory and actual pacing | 0 | 115.875 |

The pre-fix failures include a real Chromium closed-target abort, not an injected native error. The first post-fix focused run had one failure in the *new fixture*: it incorrectly assumed closing CDP guarantees zero incidental server traffic. Its trace showed otherwise. The corrected fixture preserves that observation, checks one abort attempt and prevented controller continuation, and forbids reissue/extra intentional dispatch. The successful focused run and full regression use the same final source as the Capture comparison.

Native unexpected closure during an active read still returns failure with `browser_page_closed`; no controller intentional-dispatch event follows STOP. **Additional finding:** in that controlled native closure fixture, the loopback server received the held read about 5–8 ms after STOP. Server receipt does not establish wire dispatch time, and absence of a controller event does not prove zero teardown traffic. The candidate must not be described as proving that stronger guarantee. See the retained native timeline; no broader repair was made. Existing cancellation, identity, redirect, pacing, refusal, byte-cap, deadline and budget checks remain covered by regression. The 231-file Capture comparison passed and checks authored fixture facts and the complete canonical package; generated output was not accepted as a new expected result.

**Source identity and preservation**

Branch `wf-scrapper-abm`; base HEAD `366f9830ba7b9bfb91f17b8655fd37467410123b` plus existing dirty/untracked work. These repairs were not committed. The initial 67-file inventory matched `f52235202ce3fb546d436efa4b4b4a7a92025868edef20a939c25c81e0dcaa53`; final 68-file inventory:

`aaf883a8c59960ab825e5a58508772bb9c099b49f65187b248e1f2ed813dc622`

Exactly the three source/test paths listed above differ from intake. All 13,083 pre-existing evidence/output/report files retain their hashes. The focused diff is against the preserved intake bytes, not against an assumed clean checkout. No Git mutations, dependencies, deletion, deployment, recon/selection or Prepare implementation.

**Handoff files**

- [Exact source/test diff](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-04_221510_bounded-capture-repair_source-test.diff.txt)
- [Full updated browser controller](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-04_221510_bounded-capture-repair_browser_session.py.txt)
- [Full updated REST collector](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-04_221510_bounded-capture-repair_rest_client.py.txt)
- [Final source inventory](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-04_221510_bounded-capture-repair_source-inventory.json)
- [Checks, exact commands, exits and source hashes](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/RESPONSES/response_2026-10-04_221510_bounded-capture-repair_checks.json)
- [Native cleanup before/after evidence](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-capture-repair/2026-10-04_154542Z/cleanup-before-after.json)
- [Native unexpected active-read closure — focused run](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-capture-repair/2026-10-04_154542Z/focused-final-controls/native-unexpected-close-active-read.json)
- [Native unexpected active-read closure — full regression](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-capture-repair/2026-10-04_154542Z/regression-controls/native-unexpected-close-active-read.json)
- [Saved live media response review](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-capture-repair/2026-10-04_154542Z/saved-media-review.json)
- [Full regression log](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-capture-repair/2026-10-04_154542Z/regression/command.log)
- [Capture comparison log](/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/bounded-capture-repair/2026-10-04_154542Z/comparison/command.log)
- [Engineering checkpoint](/home/moose/PYTHON/stark-web-factory-scrapper-v1/RECOVERY.md)

**Proposed bounded live verification — NOT executed**

After Tony explicitly allocates a new attempt, verify this final inventory and use the existing bounded recorder with fresh evidence/output paths around:

```bash
venv/bin/python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com --limit 10 --skip-prepare --no-media-head --max-operations 120 --max-seconds 1800 --max-bytes 100000000 --max-aggregate-bytes 100000000
```

Retain 10 document slots including bootstrap, 120 intentional dispatches including redirects, five-second completion pacing, 1,800 seconds including finalization reserve, 97 MB raw + 3 MB supporting evidence, the existing 10 MiB response cap/deadlines/scope/redirect/refusal controls, and no retry or restart. These are ceilings, not proof that every advertised media page will fit. Verify final pages/objects/unique IDs and shutdown outcome independently.

**Remaining limits / next move**

JARVIS reviews this repair and the unexpected-closure traffic finding before recommending another live allocation; Tony decides any allocation. Historical stopped-path homepage route accounting and supervisor counter gaps remain **OPEN**. This local proof cannot guarantee live media totals or eliminate unrelated shutdown failures. The earlier live run remains incomplete. Prepare remains **ON HOLD**; independent QA **NOT RUN**. **STOP after handoff.**
