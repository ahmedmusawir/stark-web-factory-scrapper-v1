# Web Factory scraper — LEAD-04 technical QA acceptance

QA Lead: JARVIS. Date: 2026-10-17 (Asia/Dhaka).

**Decision: TECHNICAL QA ACCEPTED for the approved DECIDE → COLLECT → offline agent-assisted PREPARE scope. All LEAD-02 repairs and LEAD-03 evidence conditions are closed. No further product repair, evidence addendum, broad QA run or test-plan approval is required on the reviewed evidence.**

**Final Gate Q remains pending the existing module cleanup verification and Lead cleanup acceptance.** This is the cleanup condition already stated in the original approved plan and LEAD-03, not another test campaign. Git, destructive cleanup and integration remain Tony's decisions. This document does not assert that cleanup happened, the working tree is clean, the ABM has merged, or a deployed/live-site check passed.

## 1. Exact candidate and evidence binding

| Item | Identity |
|---|---|
| Repaired product candidate | `0f98bcf095781a3ac7a231c276199224dc531f11` |
| Repaired source52 | `6f35cf8dacf3aeecc17a89b1c96e3558ea52e3c03edf63c2e402a766a1e986f4` |
| Original approved plan SHA-256 | `4cf1673851f5a170391af4e3e3fa418069732108ff1828e9fead6e062b52da2f` |
| LEAD-02 decision SHA-256 | `1622ac029633f957efc5a2a79d32c82ca244e70c85517ade078de2ce9b4c187b` |
| LEAD-03 decision SHA-256 | `357a7eb3f0a73b9c2e5b579a4cbe2e7d9ebca32bfefcd4c3e6a9e51a7bd4c1f7` |
| Historical QA ZIP | `WebFactory_QA_Q2_Package_2026-10-16_155121.zip` — SHA-256 `06f73841cc678badd30d56bfb4c41614c376b16abe7254ea1e374a96c1d974df` |
| Engineering repair ZIP | `WebFactory_LEAD02_Engineering_Rework_2026-10-16_173633.zip` — SHA-256 `151c15e61ee2d723f4b62fab96e12be3b7706af87641d9bb7eee9931f2b04666` |
| Independent retest ZIP | `WebFactory_LEAD02_QA_Retest_2026-10-16_183150.zip` — SHA-256 `b734010ad0430a26f8729451ca18bab889df46868729904f6e4577b041fab9d0` |
| Reviewed addendum ZIP | `WebFactory_LEAD03_Evidence_Addendum_2026-10-16_192729.zip` — SHA-256 `023057c1b6334fa1b75d35e8b4a1f9422c9dfcf5f8670655a1014d88fae4913f` |
| Addendum size / membership | 46,785 bytes / 35 file members; 34 indexed members plus the manifest |

The supplied addendum identity recheck records the candidate unchanged, matching source52 on the worktree and retained snapshot, no changed product paths and the retest ZIP unchanged. This acceptance is bound to those exact product bytes and evidence. It does not approve an unseen later product change.

## 2. Lead verification and closure

The Lead independently recomputed the addendum ZIP SHA/size, checked CRC, unique confined paths, exact manifest membership and all indexed sizes/hashes. A review-time file-only export scan passes for all 35 members without content-hit exemptions, prohibited files or nested archives. The A1/A2/A3 instrument hashes match their packaged source. Product tests were not rerun by the Lead and no new VM inspection is claimed.

### A1 / C1 — CLOSED

The original raw body, result metadata, checklist, initial output and reviewed-v1 output are now included. The Lead independently verified the checklist → metadata → body digest chain; raw body is 247 bytes, SHA-256 `d4251ec9f8acfb1e6ae0b66710adf0147cd1aa66555601bad70e702ea30c59c0`, matching the original synthetic fixture.

Reviewed-v1's stale heading/boilerplate metadata is preserved as history. The new `qa-c1-article-reviewed-v2` index accurately records the final main heading, one source paragraph, zero list items, and global header/footer locations, while labeling the initial extraction metadata separately. Its page and boilerplate hashes, checklist/raw/metadata references and authored paths resolve against the exported files. The final main content preserves `Meaningful Page Title`, the body paragraph and `Book a Call` targeting `https://example.test/book`; genuine global navigation/footer remain separate.

All file-bearing provenance entries are covered by the addendum's external manifest, including the SOURCE_INDEX itself and the reference to preserved reviewed-v1. A self-reference in the change history is not required to contain an impossible self-inclusive file digest. The active prepared-file pointer correctly targets v2.

The A1 result's `paragraph_count_final: 4` comes from counting blank-line separators in the instrument, not semantic source paragraphs. Exclude that spacing diagnostic from the paragraph acceptance claim. The raw `<p>` content and final index correctly establish one source paragraph; the linked CTA is preserved separately. This annotation resolves the reporting imprecision without another executor round or product change.

### A2 / C3 — CLOSED

The Lead independently verified the original exported checklist → result metadata → saved body chain. The original saved response is 1,104 bytes, SHA-256 `743103072c2e8e88f682b11c4a6fa8f671b9cbf00202c66e29d1965697f83525`.

The Lead reconstructed the expected bytes from the prior retest instrument's independent `RICH` fixture and the recorded loopback origin. Those bytes match both the original saved capture and the clearly labeled reconstructed reference exactly. Metadata records HTTP 200, complete body and matching length/hash; the selected REST URL has no `_fields`, the saved header set is limited to content type/length, and the synthetic cookie value is absent. No recapture was needed or performed for this addendum.

### A3 / O2 — CLOSED within the approved estimate semantics

The retained native collection has zero runtime regular files; the listed two child directories plus `.runtime` itself explain the report's three-directory description. Its exported non-runtime files sum independently to 4,370 bytes, matching the recorded sizing total; the real writer lock is zero bytes.

The separate synthetic clone records a 1,337-byte sentinel under `.runtime/`: the recorded sizing-expression result increases from 12,536 to 13,873, with matching independent `os.walk` sums. The Lead verified the sentinel's independently defined bytes/hash and arithmetic. The named collector module digest matches the unchanged collector recorded in the candidate-bound retest.

Precisely stated, this is a probe reproducing the reported inline product sizing expression with hash/line provenance, not a new end-to-end collection with a populated native browser profile. Combined with the already accepted byte-limit-trigger measurement, it satisfies the required demonstration that runtime regular-file bytes fall within the sizing expression's domain. It does not demonstrate live profile growth under collection, an exact aggregate persisted-byte ceiling, directory-block accounting, wire/memory bounds or instantaneous cancellation. The `du` interpretation correction is retained without expanding those claims.

### Previously accepted results — retained

- R1 generic-title repair and R2 inert-presentation repair remain CLOSED under LEAD-03.
- The 144 unique passing tests across the six required modules remain accepted, with zero failures/errors/skips.
- Controlled in-flight `request_error` / `TimeoutError` and pre-dispatch `time_limit` semantics remain accepted as previously adjudicated; the label distinction stays recorded.
- T-20 reuse remains accepted for the unchanged historical consumer packet; no new cold-read requirement is added for the small synthetic C1 metadata correction.
- The nine export-checker controls and bounded refusal/integrity measurements remain accepted within their demonstrated scope.

## 3. Existing cleanup condition — concrete disposition

Accept the addendum's retain/delete classification with these bounds:

**Retain:** all durable QAM/engineering/QA lanes, the four bound evidence ZIPs in §1, their manifests/receipts, decisions, original saved product collections/prepared packages, response/session/recovery/changelog history and the corrected C1/C3 specimens now exported in the addendum. Keep evidence permanent even when disposable execution scratch is removed.

**Eligible for deletion after Tony's explicit release, after verifying durable copies and exact targets:**

1. `/tmp/claudy-lead02-retest-20261016/`
2. `/tmp/opencode/q2-scratch-20261016/`
3. `/tmp/cody-lead02-2026-10-16_172752/`

This is approval of the cleanup classification, not a claim that deletion is authorized or completed. Tony can release these exact targets together. A deliberate Director retain decision can instead preserve a named scratch tree outside the durable repository, with its purpose, path and resulting recovery pointers recorded; retained scratch must not be mislabeled deleted.

The executor's cleanup pass should verify the durable archive hashes/CRC first, preserve any still-needed measurement record, validate that each root is the intended QA-owned directory (no unexpected root symlink), close only owned processes if any, perform only Director-released cleanup, update current routing/recovery pointers to durable records and return one verification report. Retain all historical entries. No product change, test rerun, dependency install, Git mutation or broad filesystem cleanup is needed.

The report must state exact deleted/retained/absent paths, source/candidate identity, owned-process status, durable archive hashes and remaining Git status. Pending QA record changes are not product drift and must not be called a clean working tree. Tony handles commits and integration. Final Gate Q can then be adjudicated from that cleanup verification under the existing module rule.

## 4. Scope and known limitations preserved

This acceptance covers DECIDE → COLLECT → offline agent-assisted PREPARE under the approved current-scope crosswalk. It does not claim every original retired acceptance behavior passed or that all 48 rows are unrestricted PASS.

Keep explicit: clean-venv install reproducibility untested; native crash/cancellation breadth and broad hostile-viewer coverage unproved; media/hidden/deferred/image/iframe-child completeness and current external-site access unverified. O5 remains an initial-helper limitation handled by the evidenced agent review. Four historical controller findings remain OPEN and retired controller/full-site designs remain retired.

The PREPARE skill's source-versus-interpretation, meaningful-content preservation, dated REST/HTML context, evidence references and explicit gaps remain the agreed Architect-handoff workflow. New factory orchestration/WBM/starter-kit/deployment skills and a manual live-site walkthrough are outside this technical certification claim. No merge, deployment or broader Web Factory completion is declared here.
