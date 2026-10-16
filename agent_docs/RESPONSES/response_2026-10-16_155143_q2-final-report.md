# Q2 Independent QA — Execution Report (LEAD-01)

**Status:** Independent QA executed and recorded. **Not a certificate.** JARVIS (QA Lead) reviews and adjudicates; Tony decides.
**Run:** Web Factory DECIDE → COLLECT → offline agent-assisted PREPARE, released by Tony 2026-10-16 14:26 +06.
**Identities (rechecked at T-24, derived from plan §0 / G0 records):** product candidate `8fbcff28…` (ancestor of HEAD); execution HEAD `e1972ff3…` (documentation-only successor); source52 `39b9728a…` on worktree and snapshot; requirements, lock and both fixture ZIPs match plan §0; fixtures 34/34 in real repo and snapshot.
**Executors:** Opy (OpenCode, GLM 5.3) for G0 → content group; Claudy (Claude Code, Claude Opus 5.5) for T-23 → T-24. The transition happened at the T-23 seam, and both executors sit outside the engineering seat.

## Results

| Test | Result | Test | Result |
|---|---|---|---|
| G0–G2 | PASS | T-13 | PASS + HELPER LIMITATION (O5) |
| T-01 | PASS; AC-001 clean install NOT RUN | T-14 | PASS |
| T-02 / T-03 | PASS | T-15 | PASS |
| T-04 / T-07 | PASS (native loopback) | T-16 | PASS (key disclosure) |
| T-05 / T-08 / T-17 | PASS (suite-mapped; T-08 also native) | T-18 / T-19 | PASS |
| T-06 | PASS + **FINDING O6** | T-20 | PASS (fresh cold reader, 8/8) |
| T-09 / T-11 | PASS | T-21 | PASS |
| T-10 | Limited check PASS; media gap OPEN | T-22 | 97 + 27 PASS; limit-trigger sub-obligation NOT RUN |
| T-12 | PASS | T-23 | PASS + **ADJUDICATE B1–B3** |
| | | T-24 | Recorded: matrix, rechecks, package |

Retired designs (AC-015, AC-018 screenshot stream, AC-028, AC-040) are NOT APPLICABLE TO CURRENT SCOPE, HISTORICAL STATUS PRESERVED.

## Findings and items for the QA Lead

1. **O6 FINDING.** `candidate()` accepts `'Read more →'` (U+2192) as a candidate title, both supplying a title and replacing one. This is recorded against current behavior and is not waived.
2. **T-23 sanitization boundaries (ADJUDICATE).** None of these executes anything as a file; each matters only if a permissive renderer displays the output.
   - **B1:** source text with entity-escaped markup (`&lt;script&gt;`) becomes literal `<script>` markup in the derived Markdown.
   - **B2:** Markdown-link-shaped plain text with a `javascript:` target passes through unescaped.
   - **B3:** the SOURCE_INDEX image `source_src` field keeps raw `javascript:` values.
3. **T-22 gap.** Limit semantics have suite coverage only, from three named tests. The independent fixtures for max_requests=1, a tiny deadline and a small byte allowance, and the O2 directory-byte record, were NOT RUN. The incoming Executor surfaced this gap rather than closing it outside its bound scope.
4. **T-13 HELPER LIMITATION (O5).** For a synthetic `article > header > h1`, the helper routes the title to BOILERPLATE.
5. **T-20 independence limits.** The reader was a fresh subagent dispatched by the Executor. It is the same model family as the Executor, and the harness auto-loads repository instruction files into it; it received no Q2 analysis. Its network and write prohibitions were instructions only, and compliance was confirmed from its transcript. The reader also reported usability observations, including `#` hrefs rendered as resolved page URLs, an unmentioned initial package, and SOURCE_INDEX files not being hashed anywhere. These are recorded in `t20/t20_result.json`.
6. **Disclosure.** Lane evidence quotes the public page's own Google Maps embed parameter from verified fixture bytes. It ships faithfully, is adjudicated at exact checker locations, and is redacted from all authored text.
7. **Open, unchanged.** Clean-venv install; native crash and cancellation breadth; broad hostile-viewer coverage; hidden, deferred, image and iframe child content; external-site access; four historical controller findings.

## Controls

- **Zero external requests.**
  - The native evidence contains no host other than 127.0.0.1 or localhost.
  - T-23 Prepare runs were made inside an empty network namespace.
  - The T-20 reader made no network calls.
- **Git and product.** No Git mutations and no product, test or dependency changes. The working tree has 0 product paths changed; all 109 entries are Q2 run records.
- **QA disk.** About 29 MB of the 500,000,000-byte ceiling.
- **G3 corrections.** T-23 needed one: an expected-refusal-message correction made before the run, because `valid_result()` masks the `artifact()` message. T-20 needed one: re-extracting the response from the hand-back input. Opy's corrections are recorded inside the earlier results.
- **Cleanup.** No owned servers or browsers are left running. Scratch `/tmp/opencode/q2-scratch-20261016/` is retained pending Tony's retain/delete decision. Nothing pre-existing was deleted.

## Evidence

- **Matrix:** `matrix/AC_EVIDENCE_MATRIX.md` (48 IDs).
- **Rechecks:** `t24/t24_readiness_result.json`.
- **T-23:** `offline/t23_*`.
- **T-20:** `t20/`.
- **Package checks:** `t24/package_check_*.json`.

**Decision sought.** JARVIS to review the package and adjudicate O6, B1–B3, the T-22 limit gap and the T-20 independence limits. Tony to decide acceptance, and to decide whether to retain or delete the scratch directory.

## Package receipt

| Item | Value |
|---|---|
| Package | `WebFactory_QA_Q2_Package_2026-10-16_155121.zip` |
| Lane copy | `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/Q2_2026-10-16_142632/exports/` |
| Downloads copy | `/home/moose/Downloads/` — byte-identical (`cmp` + sha256) |
| SHA-256 | `06f73841cc678badd30d56bfb4c41614c376b16abe7254ea1e374a96c1d974df` |
| Size / members | 499,912 bytes; 156 files (INDEX.md, INCLUSION_EXCLUSION.json, MANIFEST.sha256.json inside) |
| Checker | PASS pre-zip (dir) and post-zip (lane ZIP and Downloads ZIP); 4 exact-location adjudications (2 synthetic T-23 strings, 2 public embed parameter occurrences), none stale; 0 prohibited/nested members |
| Contents | full Q2 lane (minus caches/exports), installed LEAD-01 plan/approval/amendments/governing snapshots, session/RECOVERY/CHANGELOG/executor-handoff records |
| Omitted (explicit) | raw fixture ZIPs and restored collections (hash-verified, referenced), QA scratch, `.runtime` profiles, earlier Q1 exports |

Records inside the ZIP are the pre-package state; the final session/RECOVERY entries written after packaging are on disk only.
