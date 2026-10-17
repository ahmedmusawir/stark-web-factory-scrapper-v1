# Web Factory scraper — LEAD-03 retest adjudication

QA Lead: JARVIS. Date: 2026-10-16 (Asia/Dhaka).

**Decision: R1 and R2 CLOSED for the tested scope; deadline semantics ACCEPTED; T-20 reuse ACCEPTED. Final certification remains withheld pending ONE bounded evidence addendum for C1, O2 and C3.**

No additional product repair is required by this review. Preserve the completed measurements. Do not restart reconnaissance, repeat the unchanged test-plan approval, rerun the six-module suite, or repeat the cold reader merely to supply this addendum.

## 1. Exact binding and review checks

| Item | Identity |
|---|---|
| Retest package | `WebFactory_LEAD02_QA_Retest_2026-10-16_183150.zip` |
| Retest SHA-256 | `b734010ad0430a26f8729451ca18bab889df46868729904f6e4577b041fab9d0` |
| Size / members | 209,786 bytes / 65 files |
| Repaired candidate | `0f98bcf095781a3ac7a231c276199224dc531f11` |
| Repaired source52 | `6f35cf8dacf3aeecc17a89b1c96e3558ea52e3c03edf63c2e402a766a1e986f4` |
| Engineering package SHA-256 | `151c15e61ee2d723f4b62fab96e12be3b7706af87641d9bb7eee9931f2b04666` |
| Historical QA package SHA-256 | `06f73841cc678badd30d56bfb4c41614c376b16abe7254ea1e374a96c1d974df` |
| Original plan SHA-256 | `4cf1673851f5a170391af4e3e3fa418069732108ff1828e9fead6e062b52da2f` |
| LEAD-02 decision SHA-256 | `1622ac029633f957efc5a2a79d32c82ca244e70c85517ade078de2ce9b4c187b` |

Reviewed the supplied retest, the engineering rework package, the historical QA package, LEAD-02, and the governing scope/plan snapshots. Evidence paths below are relative to `RETEST_LEAD02_2026-10-16_180559/` in the retest ZIP unless otherwise identified.

The Lead independently verified:

- Retest ZIP SHA, bytes, CRC, unique confined member names and exact membership; all 64 indexed member sizes/hashes match.
- Engineering ZIP SHA and all 81 indexed member digests; reviewed its four-path product/test patch and renderer evidence.
- JUnit contains 144 unique cases across the exact six required modules, with zero failures, errors or skips: collector 32, DECIDE 74, Prepare 11, REST client 10, raw reader 6, offline inventory 11.
- All six checked identity/R1/R2/C1/C2/C3 instrument hashes match their packaged source.
- C3's independent `RICH` fixture definition, with its recorded loopback origin substituted, reconstructs to 1,104 bytes and SHA-256 `743103072c2e8e88f682b11c4a6fa8f671b9cbf00202c66e29d1965697f83525`.
- The review-time archive/export check passes with exactly one adjudicated synthetic control at `helpers/t23_untrusted_privacy_retest.py`, line 304, pattern `credential_assignment`. No broad exemption or unexpected hit is accepted.
- The retest's copy of LEAD-02 is byte-identical to the issued decision.

Identity/environment/source/fixture records support execution against the repaired candidate. The six-module command records execution from the verified repaired worktree, while the focused instruments use the fresh repaired snapshot. Accept these candidate-bound regression measurements; retain the actual locations in the record. This is evidence review, not a new VM inspection or a Lead rerun of product tests.

## 2. Adjudications

| Item | Decision | Basis / limit |
|---|---|---|
| R1 / O6 / T-06 | CLOSED, PASS | Exact arrow-label supply and replacement cases now decline generic titles; both discovery orders, informative Unicode controls, stable identity, UNDECIDED state and preserved source locators are evidenced. The complete saved-title recheck reports no remaining arrow finding. This is bounded to the documented generic-label set and tested decoration handling. |
| R2 / B1–B2 | CLOSED, PASS | The repair escapes source-text presentation syntax while preserving useful formatting. Independent retest examines converter output plus markdown-it-py 4.2.0 commonmark/default with HTML on/off, page and boilerplate, readable literal payloads and positive controls. Engineering supplies actual before/after derived/rendered artifacts. No broad hostile-viewer or browser-exploit certification follows. |
| B3 | Existing acceptance retained | A raw image source string remains untrusted JSON provenance; its mere presence is not execution. No new image fetch or data erasure is required. |
| C1 | Supported measurement; final evidence acceptance PENDING | The reported reviewed main content contains the recovered heading and preserves paragraph/CTA, but the actual initial/reviewed files and SOURCE_INDEX are omitted. Final index consistency is not fully checked by the instrument. See A1. |
| C2 request limit | PASS | One dispatch, one saved attempt, second item pending, visible `request_limit`, partial exit 2, and transport closed. |
| C2 deadline cases | ACCEPT, PASS for the controlled-double semantics | See the specific reasoning below. No label-only product repair or new deadline campaign is required. |
| C2 persisted-byte trigger | PASS for tested estimate semantics | First response persists; second is received but refused before persistence, with `persisted_byte_limit`, partial exit 2 and retained evidence. This does not prove an exact hard aggregate, wire, memory or redirect-hop cap. |
| O2 runtime overhead | NOT DEMONSTRATED | Every reported runtime list is empty. A zero-byte `.writer.lock` is legitimate, but counting it and body/checklist bytes does not demonstrate inclusion of runtime file bytes. See A3. |
| C3 | Method and reported result ACCEPTED; saved-byte evidence PENDING | The fixture reconstructs independently and the report records one loopback request, byte equality and excluded synthetic Set-Cookie. The actual saved body/result/checklist chain is absent from the ZIP. See A2. No recapture is requested. |
| T-20 reuse | ACCEPT | The historical consumer packet is unchanged, its references are rechecked, and the repair diff does not change that packet's content/structure/navigation. The engineering comparison also records unchanged rendered text/headings/links for the historical sample after fresh extraction. That engineering result supports impact analysis; it is not substituted for independent retest. Reuse remains a bounded consumer-usefulness check of the historical packet, not a cold read of every future rendition or a security certificate. |
| T-23 / export controls | ACCEPT within tested scope | Retest records the negative/refusal cases and all nine checker-control expectations. Preserve source-data and presentation-safety dispositions separately from export privacy. |

### Deadline assertion correction

The approved scope requires bounded work, visible failure/partial outcomes, recorded limits and safe exit. It does not require every deadline path to use the literal label `time_limit`. Plan T-05 expressly accepts a visible conservative timeout stop and partial exit 2; T-22 requires actual limit/partial semantics without an instantaneous-cancellation claim. CURRENT_TOOL_SCOPE and COLLECTOR_SIMPLIFICATION describe a work deadline including setup/pacing and separate cleanup.

`case_b_tiny_deadline` reports a one-second work limit with a 1.4-second transport double. The request is cancelled at about one second; the item records `TimeoutError`, no attempt is persisted, the outcome is partial, exit is 2, and the transport closes once. `case_b2_predispatch_deadline` refuses a second operation whose five-second pacing gap would exceed the two-second budget, records `time_limit`, and preserves the first attempt. It can stop before the deadline rather than wait until expiration; that is conservative and acceptable.

The corrected assertion is accepted because these measurements satisfy the governing semantic requirement. Changing an expectation to match an observation is not, by itself, a valid general QA correction. Preserve the failed initial assertions and the disclosed correction. Retain the labeling distinction as an observation: `request_error` plus item `TimeoutError` in flight, `time_limit` before dispatch. This does not establish native Chromium crash/teardown or hard cancellation behavior.

## 3. ONE addendum from retained scratch

Independent QA may finish this within the existing authorized lane and limits. Reacquire the single writer seat, verify candidate identity and unchanged repaired source52, and preserve all original packages and scratch. If HEAD is a documentation-only successor, record the complete relevant diff and prove product/test/config/dependency bytes unchanged. No product edits, Git mutations, dependency installs or external traffic are authorized.

Retained snapshot:
`/tmp/claudy-lead02-retest-20261016/snapshot-repaired/`

### A1 — Supply actual C1 artifacts and check final index consistency

Export the retained files, preserving their snapshot-relative layout:

- `outputs/collections/qa-c1-article/`: checklist and referenced saved body/result metadata; exclude runtime/lock material.
- `outputs/prepared/qa-c1-article-initial/`: the actual initial page Markdown, BOILERPLATE and SOURCE_INDEX, unchanged.
- `outputs/prepared/qa-c1-article-reviewed/`: the actual reviewed page Markdown, BOILERPLATE and SOURCE_INDEX, unchanged as the submitted measurement specimen.

Recompute and record the complete checklist → result → raw-body hash chain and every final index file/hash reference. Compare final main heading order, paragraph/list counts, link/CTA labels and destinations, boilerplate locations, and provenance against the actual reviewed files and raw fixture. Verify the CTA's destination, not only the presence of its label. Show the raw and initial outputs remain unchanged.

The C1 helper changes `title`, prepared file/hash, boilerplate file/hash and review provenance, but does not update `content.headings` or `boilerplate_locations`; its boolean checks therefore do not establish that those fields describe the final rendition. Inspect the actual index. If those fields still describe the initial extraction, either clearly preserve them as initial-extraction metadata and add accurate final-reviewed metadata, or produce a NEW `qa-c1-article-reviewed-v2/` with a consistent final index. Preserve the prior reviewed directory; do not silently overwrite it. Index authored file references with verifiable hashes and label their review provenance. This is correction of QA-authored derived material under the approved skill, not a product-code repair.

Include any new rendition's files, index, before/after maps and verification results in this same addendum. Do not rerun Prepare, the full suite or a cold reader merely to correct and verify this small synthetic reviewed package.

### A2 — Supply C3's original saved response chain

From retained `outputs/collections/qa-c3-rich-rest/`, include:

- The actual `checklist.json`.
- The saved result metadata referenced by its selected item.
- The original saved body at `attempts/888f03b3ef21b8a7489f6f69/a60f27da84384661be9ba942499d99b0/body`.

Resolve the result path from the actual checklist rather than guessing it. Verify the checklist's metadata digest, metadata/body length and SHA, `body_complete`, status/scope, selected URL without `_fields`, allowed headers and exclusion of the synthetic cookie value from saved metadata. Compare the actual saved body byte-for-byte to the independently reconstructed served fixture using recorded origin `http://127.0.0.1:37785`.

The expected body is 1,104 bytes with the SHA recorded in §1. Label a reconstructed reference as reconstructed; never substitute it for the original saved capture. Include verifier commands, cwd, exits and output. Do not restart the server, browser or C3 capture.

### A3 — Complete only O2's runtime accounting proof

First inspect the retained C3 native collection's `.runtime` tree. Report names, file sizes, file/directory counts, runtime-file subtotal, writer-lock size, other-file subtotal, total and the actual sizing routine used by the collector's persistence check. Do not read or export real runtime/profile/cookie contents. A zero-byte lock or empty runtime tree is a valid observation, not evidence of nonzero runtime overhead.

If retained native runtime has no regular files, use a SEPARATE disposable QA clone of an existing synthetic collection. Add one known-size non-secret sentinel under `.runtime/` in that clone and measure the actual product sizing routine before/after. Record the routine's module path/hash and demonstrate that its total increases by exactly the sentinel's bytes while independent per-file sums agree; keep the real writer-lock entry in the accounting. No native browsing or full limit-fixture rerun is needed. Do not change the maintained collector or tests, original collection, or real browser state. Export only the measurement report and the synthetic sentinel's size/hash definition, not `.runtime` itself.

The current O2 note also says `du -sb` exceeds the file sum, while the recorded numbers are equal. Correct that interpretation in a separate addendum note. Distinguish product per-file apparent-size accounting from directory/filesystem overhead and describe the actual results; do not claim an exact persisted-byte ceiling.

### Addendum delivery and stop rule

Deliver ONE new file:
`/home/moose/Downloads/WebFactory_LEAD03_Evidence_Addendum_<actual-local-timestamp>.zip`

Include A1/A2 safe artifacts, A3 measurement, exact inclusion/hash/size manifest, candidate/source identity recheck, resolved verification commands/exits/output, and a supplemental matrix note qualifying the earlier C1/C2/C3 PASS claims. Preserve the original retest ZIP and completed results. Verify CRC, unique confined paths, exact membership, hashes and export hygiene. Keep final ZIP hash receipts outside the ZIP; exclude runtime profiles, cookies/auth storage, credentials, dependencies and nested historical ZIPs.

Include one concise report and an inventory proposing which original/retest/engineering scratch trees and durable QA records to retain or delete. Tony retains Git and cleanup decisions; no deletion or merge is granted here. This inventory is the existing closeout preparation, not another test-plan gate.

If retained bytes are missing or have changed, report the exact path and mismatch; do not regenerate them and present them as original evidence. Complete unaffected addendum items and return the consolidated result. Genuine new product drift or a newly observed product failure must remain visible.

## 4. Certification boundary and preserved scope

Final certification is withheld until the actual C1/C3 artifacts and accurate final index are verified and O2 is demonstrated. The existing module cleanup/acceptance requirement remains before final Gate Q; the addendum should prepare the retain/delete inventory now. No new product defect or additional broad campaign is imposed by this ruling.

Keep DECIDE → COLLECT → offline agent-assisted PREPARE, zero external requests and the existing disk bound. Preserve O5 as an initial-helper limitation handled by agent review. Preserve the explicitly untested clean-venv install, native crash/cancellation breadth, broad hostile-viewer coverage, hidden/deferred/image/iframe-child completeness and current external-site access. The four historical controller findings remain OPEN and retired designs remain retired. Accepted T-20 reuse does not certify whole-site completeness or the broader Web Factory pipeline. Git, destructive cleanup, integration and deployment remain Tony's decisions.

## 5. Copy to the independent QA executor

```text
Independent QA — JARVIS LEAD-03 accepts R1/R2 closure, the controlled
deadline semantics and T-20 reuse on candidate
0f98bcf095781a3ac7a231c276199224dc531f11.

Read WebFactory_QA_LEAD03_Retest_Decision_2026-10-16.md.
Complete its ONE bounded evidence addendum from retained scratch:
A1: export original C1 raw/initial/reviewed artifacts and verify the
    final SOURCE_INDEX against final content; preserve originals and
    use a new rendition if QA-authored index corrections are needed.
A2: export C3's original checklist, saved result metadata and body;
    verify the hash chain and exact independent 1,104-byte fixture.
A3: demonstrate runtime-byte inclusion in the actual product sizing
    routine; measure existing native runtime first, and use a known
    non-secret sentinel in a separate synthetic QA clone if necessary.

Do not rerun general recon, the 144-case suite, the cold reader,
Prepare or C3 capture merely to supply this evidence. No new product
repair is requested. Preserve historical results and packages.

Verify unchanged candidate/source identity, maintain one writer,
follow the existing offline/privacy/storage bounds, and deliver one
indexed addendum ZIP in Downloads with a concise report and proposed
retain/delete inventory. Tony retains Git and destructive cleanup.
No further approval of the unchanged test plan is needed.
```
