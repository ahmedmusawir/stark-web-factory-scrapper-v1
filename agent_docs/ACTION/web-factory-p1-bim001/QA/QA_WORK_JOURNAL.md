# BIM001 QA work journal

Append-only provenance record started during repaired-candidate retest on 2026-09-06, after receipt and complete reading of `INPUTS/WEB_FACTORY_P1_DOCTRINE_JOURNAL.md` J-13. Earlier QA work is already documented in the recon/offline reports and their command evidence; this journal does not rewrite those historical records.

Candidate: `eee039a2c06cc1aeaa3e9dfb52e17db9d3ddb20a`.

| Artifact / family | Purpose / QA question | Retention | State mutation / restoration |
|---|---|---|---|
| `retest_driver.py` | Independent AC-32/71/82 source checks, persisted port probe, affected tests, dual-CWD regression and integrity | QA helper retained with evidence | Output roots/temp/cache/JUnit destinations isolated under retest evidence; process-local stubs only; no persistent implementation/environment changes |
| `evidence/retest_eee039a/*.command.json`, `*.stdout.txt`, `*.stderr.txt` | Exact command/context/output/exit evidence for repaired specimen | Permanent execution evidence | File creation only inside QA lane |
| `evidence/retest_eee039a/source_verification.json`, `FakeCrawler_*.txt` | Prove restored class body, only a/b/c baseline amendments, retained assertions, hostname behavior | Permanent evidence | Read-only source/git inspection; in-process fake helper execution only |
| `evidence/retest_eee039a/port_case/**`, `port_verified.json` | Re-run previous port-bearing QA probe through actual main/capture/manifest path | Permanent controlled fixtures/artifacts | Browser stub, output constants and pacing substituted only in subprocess; socket attempts denied; no production outputs touched |
| `evidence/retest_eee039a/{targeted,root,foreign}.xml`, `baseline_passing.json` | Per-case proof, especially all 14 BIM000 tests | Permanent evidence | Existing tests unchanged; bytecode and pytest cache writes disabled; temp paths contained |
| `evidence/retest_eee039a/tmp*` | Isolated pytest/local temporary artifacts | Retained QA helper data | Inside QA lane; no cleanup of prior evidence or caches |
| `evidence/retest_eee039a/outputs_*.json`, `integrity.json` | Production output and pinned-HEAD no-drift proof | Permanent evidence | Snapshots only; nothing to restore |
| `QA_ERRATA_BIM001_2026-09-06.md` | Record supplied AC-20/35/90/92 rulings without rewriting contract | Permanent adjudication provenance | New QA record only; frozen AC files unchanged |
| `QA_RETEST_BIM001_*.md`, retest `ac_statuses.json`, `context_intake.json` | Repaired-candidate results, inherited evidence boundaries, context paths/hashes and live readiness | Permanent QA report/evidence | QA lane only; no live smoke or Gate Q |

No git mutation, package installation, cache deletion, implementation fix or existing-test edit by Cody. Tony retains git authority; SOL owns adjudication and live-smoke authorization.

## 2026-09-07 — SOL-authorized final live QA

Authorization: Director-supplied SOL authorization in the final-live-QA instruction, restricted to one CyberizeGroup crawl with limit 10 on `eee039a2c06cc1aeaa3e9dfb52e17db9d3ddb20a`. No unrelated network probes or retries are authorized by this evidence workflow.

| Artifact / family | Purpose / QA question | Retention | State mutation / restoration |
|---|---|---|---|
| `live_qa.py` | Preserve pre-state, invoke exact existing crawler subprocess once, inspect live artifacts and historical integrity | QA helper | No application/library patch; existing venv; bytecode disabled; process TMPDIR in evidence lane |
| `evidence/live_2026-09-07_eee039a/pre_*`, `discovered_pages.before.json`, `runtime.json` | Pin SHA/input/194-URL target and preserve prior run hashes/mtimes plus exact legacy bytes | Permanent evidence | Copies and snapshots only; no prior run deletion |
| `evidence/live_2026-09-07_eee039a/live*`, `tmp/` | Exact command, UTC timing, exits, stdout/stderr and browser temporary files | Permanent evidence / isolated runtime temporary data | One authorized capped live subprocess; crawler may write a fresh run and overwrite legacy summary/markdown by its existing contract |
| `evidence/live_2026-09-07_eee039a/*checks*`, `*integrity*`, `*snapshot*`, `per_page_artifacts.json`, `*classification*` | AC-21 live size comparison, AC-74 artifact truth, no historical-run overwrite | Permanent evidence | Read-only artifact inspection; fresh artifacts copied byte-for-byte into QA lane; originals preserved |
| `QA_LIVE_BIM001_*.md`, live `ac_statuses.json` | Final 52-AC evidence status and recommendation to SOL | Permanent QA report | No Gate Q issued; no implementation, tests, dependencies, frozen contracts or git state mutated |

Legacy root `outputs/run_summary.json` and matching `outputs/pages/*.md` are expected runtime writes; their exact pre-live bytes are preserved under `pre_legacy/`. Historical per-run artifacts must remain unchanged. Runtime output restoration would erase the final live specimen and is not performed.
