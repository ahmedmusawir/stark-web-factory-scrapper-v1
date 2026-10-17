# LEAD-02 retest — Independent QA execution report

**Status:** Retest executed and recorded. **Not a certificate.** JARVIS (QA Lead) adjudicates; Tony decides Gate Q, Git and release. No merge/deployment approval is declared here.
**Run:** LEAD-02 §6.3 preapproved retest of the repaired candidate, released by Tony's DIRECTOR GO (recorded verbatim in `g0-identity/DIRECTOR_GO_RETEST.txt`), 2026-10-16 18:06–18:40 +06.
**Executor:** Claudy, Independent QA Executor (Claude Code, **Claude Fable 5**; the Q2 baseline ran on Claude Opus 5.5 — the Director switched the model before this binding; same seat, outside engineering).

## Identities (all verified, `g0-identity/g0_retest_identity.json`)

| Item | Value / result |
|---|---|
| Released repaired candidate | `0f98bcf095781a3ac7a231c276199224dc531f11` = execution HEAD, branch `qa/wf-scrapper-abm` |
| Committed repair diff | exactly the 4 repaired product/test paths + 1 documentation record + engineering lane (adjudicated in `g0-identity/diff_adjudication.json`) |
| Four repaired file hashes | worktree = engineering after-hashes = candidate blobs (all equal) |
| Repaired source52 | `6f35cf8dacf3aeecc17a89b1c96e3558ea52e3c03edf63c2e402a766a1e986f4` on worktree AND fresh snapshot (matches GO) |
| Engineering ZIP | sha `151c15e6…b04666`, 116,748 B — matches GO; extracted read-only |
| Historical QA ZIP | sha `06f73841…d974df`, 499,912 B — matches GO; untouched |
| Approved plan | sha `4cf16738…52da2f` — matches GO; unchanged |
| Fixtures | 34/34 on worktree and snapshot; requirements/lock/fixture-ZIP hashes match plan §0 |
| Snapshot | fresh `git archive` of the repaired commit, scoped for the disk budget with fixtures restored from the hash-verified worktree (`g0-identity/snapshot_scoping.json`); the old pre-repair Q2 snapshot was never executed |

## Results

| Item | Result | Evidence |
|---|---|---|
| R1 title guard (T-06/O6) | **PASS** — arrow/decoration/emoji CTA variants declined for supply and replacement in both orders; informative Unicode titles byte-exact; stable IDs; UNDECIDED; provenance retained; no slug titles; full Q2 T-06/T-14 recheck clean with the arrow finding gone | `r1/` |
| R2 inert presentation (B1/B2, AC-043) | **PASS** — converter emits backslash-escaped literals in page and boilerplate; markdown-it-py 4.2.0 under commonmark/default, html on/off: 0 script elements, 0 active-scheme destinations, B1/B2 readable; headings/lists/emphasis/links/Unicode controls intact; raw bytes unchanged; B3 kept as untrusted JSON data | `r2/` |
| C1 final article heading (T-13) | **PASS** — initial helper output reproduces O5 and is preserved; NEW reviewed rendition restores the heading to main content with paragraph/CTA kept, nav/footer separated, index/hash/provenance updated; raw bytes unchanged. O5 itself stays OPEN (no helper change, by design) | `c1/` |
| C2 limit fixtures + O2 (T-22, AC-041/042) | **PASS** — max_requests=1 → `request_limit` with one persisted attempt; tiny deadline → in-flight cooperative cancellation (`request_error`/TimeoutError — stop-label OBSERVATION for the Lead; pre-dispatch guard → `time_limit`); small allowance → `persisted_byte_limit` post-receipt (size+body+65536 estimate; crossing body not persisted); O2 actual directory bytes incl. `.writer.lock` and `.runtime` (names/sizes only) recorded | `c2/` |
| C3 rich native REST (T-08/T-15) | **PASS** — no existing measurement satisfied the obligation (LEAD-02 §4); ONE controlled loopback native capture: deliberately formatted UTF-8 JSON (Unicode, embedded whitespace, content, yoast SEO, nested unknown keys) saved **byte-identical** to the served entity; no `_fields` anywhere; synthetic Set-Cookie excluded from metadata; exactly one loopback request; server owned and closed | `c3/` |
| T-23 completion | **PASS** — full Q2 instrument rerun on the repaired snapshot: happy path clean with B1/B2 escaped, 5/5 negatives refused (exit 2, no output, collections unchanged), 9/9 export-checker controls met (dir+zip), no matched values echoed | `regression/t23_retest_*` |
| Six-module regression (once, repaired candidate) | **144 passed, 0 failed/errors/skipped** — new regression tests included in actual totals (Q2 total was 97 current; not forced) | `regression/six-modules-*` |
| Supplemental matrix | 48 rows; historical measurements preserved verbatim; LEAD-02 baseline adjudications restated; reuse justified by the 4-path diff | `matrix/AC_EVIDENCE_MATRIX_RETEST.md` |
| T-20 | **REUSED, not repeated** — the consumer packet consists of the historical prepared packages, byte-unchanged on disk; the repair affects only newly prepared Markdown (added escapes; rendered text identical per engineering's historical-fixture check). No consumer content/structure/navigation change invalidates the accepted result (LEAD-02 §5) | matrix rows AC-034/035/038 |

## Observations and remaining gaps (unchanged by this retest)

1. **C2 stop-label observation:** in-flight deadline cancellation records `stop_reason=request_error` with item error `TimeoutError`, while the pre-dispatch guard records `time_limit`. The run stops at the deadline either way; labeling is for the Lead to weigh.
2. **O5 helper limitation OPEN** (final-output obligation closed via the reviewed rendition; helper intentionally unchanged).
3. **Explicitly untested, as before:** clean-venv install (AC-001), crash/cancellation breadth, broad hostile-viewer coverage, media/hidden/deferred/iframe completeness, external-site access, four historical controller findings. R1 generic set remains the five recorded phrases; R2 safety boundary is the converter output + markdown-it-py semantics, not every viewer.
4. **Disclosure:** the public Maps embed parameter ships only inside historical evidence/receipts, adjudicated at exact checker locations; it appears in no authored text of this retest.

## Instrument corrections (G3; runs preserved)

- R2 run 1: boundary scan matched the escaped literal (`\<script\>`) with a bare substring; corrected to unescaped-occurrence detection (`r2/*.run1.*`).
- C1 run 1: minimal subprocess env dropped HOME; crawl4ai import failed before any prepare logic; corrected to full env under `unshare -rn` (`c1/c1_corrections.json`).
- C2 runs 1–2: expectations aligned to observed deadline-cancellation semantics; byte allowance tuned around the fixed 65,536 overhead estimate (`c2/*.run1.*`, `c2/*.run2.*`).
- T-23 pre-run correction carried over from Q2 (refusal-message derivation) applied unchanged.

## Controls

- **Zero external requests:** Prepare runs inside `unshare -rn`; C2 used in-process doubles; C3 and the suites used 127.0.0.1 only; no other network activity initiated.
- **No product repairs, dependency changes or Git mutations.** Read-only git throughout.
- **Writer seat:** acquired 18:05:59 +06 after Cody's release and Tony's commit; single writer maintained; released to Tony at closeout (`WRITER_SEAT.md`).
- **Preserved:** both historical ZIPs (hashes re-verified), Q2 lane and scratch `/tmp/opencode/q2-scratch-20261016/`, engineering lane, raw collections and prepared packages. Nothing retained was deleted.
- **QA disk:** retest scratch ≈ 13 MB + lane; within the 500,000,000-byte budget.
- **Owned processes:** the C3 loopback server was closed in-instrument; collector Chromium exited with the CLI; no owned processes left running.

**Decision sought.** JARVIS to adjudicate this retest evidence (R1/R2 closure, C1–C3 completion, the C2 stop-label observation, T-20 reuse). Tony to decide acceptance, Git, and retain/delete for the QA scratches (`/tmp/opencode/q2-scratch-20261016/`, `/tmp/claudy-lead02-retest-20261016/`, engineering `/tmp/cody-lead02-2026-10-16_172752/`).

---

## Package receipt (outside the ZIP by design)

- **ZIP:** `/home/moose/Downloads/WebFactory_LEAD02_QA_Retest_2026-10-16_183150.zip`
- **SHA-256:** `b734010ad0430a26f8729451ca18bab889df46868729904f6e4577b041fab9d0`
- **Size / members:** 209,786 bytes / 65 members
- **Lane copy:** `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/RETEST_LEAD02_2026-10-16_180559/exports/WebFactory_LEAD02_QA_Retest_2026-10-16_183150.zip` (byte-identical, verified)
- **Checks:** CRC OK; paths confined and unique; checker PASS in dir mode (pre-zip), lane-zip and Downloads-zip modes; 1 exact-location adjudication (the T-23 instrument's own synthetic leak-control value, `exports/package_adjudication_rationale.md`); 0 prohibited members, 0 nested archives.
- **Receipts:** this report, `exports/retest_package_result.json` and the three checker reports stay OUTSIDE the ZIP (no self-inclusion).

## Closeout

- **Owned processes:** C3 loopback server closed in-instrument; collector Chromium exited with its CLI; nothing owned left running.
- **Writer seat:** released to Tony 18:42 +06 (lane `WRITER_SEAT.md`).
- **Retain/delete proposals (Tony decides; nothing deleted):** RETAIN the retest lane + both Downloads ZIPs (durable records). DISPOSABLE after Lead review: QA retest scratch `/tmp/claudy-lead02-retest-20261016/` (~13 MB), Q2 scratch `/tmp/opencode/q2-scratch-20261016/` (~29 MB), engineering scratch `/tmp/cody-lead02-2026-10-16_172752/` (~3 MB) — all reproducible from lane instruments.
- **Next:** JARVIS QA Lead adjudicates the returned evidence. Gate Q and merge/deployment remain Tony's and the Lead's calls; none is declared here.
