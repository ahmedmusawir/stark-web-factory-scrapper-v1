# Web Factory scraper — QA Lead decision LEAD-02

Reviewer: JARVIS, QA Lead. Date: 2026-10-16 (Asia/Dhaka).

**Decision: RETURN FOR BOUNDED REWORK AND QA COMPLETION. Gate Q is not granted.**

The planned QA execution has returned useful independent results. This is the conditional rework stage of the two-shot process. Do not restart reconnaissance or create another general test-plan approval round. Preserve accepted evidence, repair the two product behaviors below, and close the specified QA gaps in one coordinated pass. A repaired candidate still needs independent verification before certification.

## 1. Exact review binding

| Item | Identity |
|---|---|
| Reviewed evidence ZIP | `WebFactory_QA_Q2_Package_2026-10-16_155121.zip` |
| ZIP SHA-256 | `06f73841cc678badd30d56bfb4c41614c376b16abe7254ea1e374a96c1d974df` |
| ZIP size / file members | 499,912 bytes / 156 |
| Approved original plan SHA-256 | `4cf1673851f5a170391af4e3e3fa418069732108ff1828e9fead6e062b52da2f` |
| Original product candidate | `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4` |
| Reported execution HEAD | `e1972ff3a80bf67a321461a743d0097e97cd069a` |
| Rechecked source52 | `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` |
| Current scope | DECIDE → COLLECT → offline agent-assisted PREPARE |

Evidence paths below are relative to `Q2_2026-10-16_142632/` inside the reviewed ZIP unless stated otherwise. This decision supplements the approved plan; it does not edit that plan or retroactively change its hash.

## 2. What the Lead independently verified

- ZIP SHA, size, member count, CRC, unique names and confined paths.
- All 155 members indexed by `MANIFEST.sha256.json` match their recorded sizes and SHA-256 hashes; there are no extra or missing files.
- The packaged approved plan has exactly the approved SHA above.
- Current JUnit has 97 unique cases; retained JUnit has 27. All 124 passed, with zero failures, errors or skips. All 124 collected node IDs reconcile with JUnit; none are missing or added.
- Reviewed the QA export checker's source and ran its file-only check against the delivered archive at review time, including the manifest itself. Result: PASS, 156 members, no unadjudicated hits, prohibited members or nested archives; four exact-location adjudications retained.
- The untouched cold-reader response matches its recorded SHA. The consumer packet manifest includes the SOURCE_INDEX files themselves; the reader's observation that their hashes were absent from the material it saw is not evidence that they are absent from the recorded packet manifest.

These are archive/evidence checks. The Lead did not rerun product QA, access Tony's VM, inspect omitted raw fixture bytes, or independently prove the complete network activity of the original run. Candidate ancestry, environment, unchanged source/fixtures, zero external requests and process cleanup are supported by the supplied execution records, not a new live inspection.

The original pre/post-packaging checker reports named in the execution report are absent from this ZIP. `t24/t24_package_run.txt` contains only its heading. The packaging helper writes those reports after copying the lane to staging, which explains their omission. My review-time archive check establishes the delivered archive's present integrity and bounded export hygiene; it does not recreate those historical receipts or prove the VM Downloads copy. Include existing receipts in the next evidence handoff without rebuilding this historical ZIP.

## 3. Required product repairs — Architect to bound, Cody to implement

### R1 — Generic CTA replaces or supplies a title: FAIL

Evidence: `offline/t06_t14_result.json`, `label_guard_cases`.

`Read more →` is accepted as a candidate title and overwrites `Informative Title Kept`. This violates the explicit DECIDE title rule and plan T-06/O6. A successful reproduction of a defect is not an acceptance PASS. Retain the successful inventory and exact-nine-heading checks separately; mark the title-guard obligation FAIL in the supplemental matrix.

Required behavior:

1. A generic CTA with the tested arrow/punctuation variants cannot supply an otherwise unknown title or replace an informative title.
2. Preserve the raw source locator and label as provenance; do not guess a title from the slug.
3. Keep informative controls, Unicode text, stable IDs and explicit selection behavior intact.

Add regression cases for both supply and replacement, including the exact `Read more →` reproduction and the existing control variants. Scope the implementation to title acceptance/normalization and its directly affected tests.

### R2 — Source text becomes executable-looking presentation syntax: FAIL for B1/B2

Evidence: `offline/t23_adjudication.json` and `offline/t23_untrusted_privacy_result.json`, `part_a.happy`.

- **B1:** entity-escaped source text becomes literal `<script>…</script>` in derived Markdown.
- **B2:** source text shaped like `[click me](javascript:…)` survives as Markdown link syntax.

These demonstrate source-text-to-presentation promotion at the conversion boundary. They fail the inert derived-presentation obligation in plan T-23. No script execution or exploitable browser XSS was demonstrated; do not describe either as proved. The absence of execution during a file converter run does not satisfy the presentation requirement.

Required behavior:

1. Preserve these source-text examples as readable inert text in derived output; do not turn them into active raw HTML or active URL-bearing Markdown.
2. Preserve legitimate headings, lists, emphasis and allowed links. Do not solve this by discarding meaningful content or escaping the entire document indiscriminately.
3. Leave raw collection bytes and historical prepared packages unchanged. New runs use new output directories.
4. Verify both examples at the derived Markdown boundary and with a declared local Markdown rendering/parsing configuration. Inspect the resulting markup for active elements/destinations; no execution of public captures is needed. Record renderer settings and the actual safety boundary instead of claiming universal viewer safety.

Architect should locate and bound the conversion fix and tests using the reproductions already supplied. This ruling does not prescribe an uninspected implementation or authorize a general sanitization rewrite.

**B3: ACCEPT AS UNTRUSTED SOURCE DATA, not an execution defect.** A raw image `source_src` inside SOURCE_INDEX JSON is provenance. Retaining `javascript:` in that data field does not execute it, and removing it would erase source evidence. It must remain data, never an automatically trusted rendering destination. No B3 product repair or arbitrary image fetching is required by this ruling. This acceptance does not extend to an unsafe value being emitted as an active Markdown/HTML destination.

## 4. QA completion — already within the approved test scope

### C1 — Finish agent review of the synthetic article heading

Evidence: `offline/t13_result.json`, `synthetic_article_header_h1`.

The evidence explicitly records `title_in_final_main_content: false` and `title_in_boilerplate: true`. No separately reviewed rendition demonstrating recovery is supplied. **T-13's meaningful-heading acceptance obligation is FAIL as delivered.** Reference-resolution checks remain accepted. Calling this only a helper limitation does not close the final-output obligation.

The approved skill allows agent-assisted correction of derived output. Complete that stage in a NEW reviewed rendition: restore the meaningful article title to main content, preserve paragraphs and CTA, keep genuine global navigation/footer separate, update the index/hash/provenance to the reviewed file, and preserve initial helper output and raw collection bytes. Verify the final content, its index, references and before/after raw hashes. A helper code change is not required if this prescribed agent stage succeeds; do not expand the repair merely to automate it.

### C2 — Complete the three independent limit-trigger fixtures and O2 measurement

Evidence: `attempts/t22/` and matrix AC-041/AC-042. The report correctly discloses that these were NOT RUN.

Run controlled cases for `max_requests=1`, a bounded tiny work deadline, and a small persisted-byte allowance. Record fixture definitions, actual settings, request starts/completions, stop reasons, partial outcomes, preserved attempts and cleanup. Measure actual directory bytes including `.runtime` and writer-lock overhead for O2.

Assess the documented estimate and post-receipt semantics. Do not invent exact wire-byte, redirect-hop, streaming-memory or instantaneous-cancellation guarantees. Independent fixtures may use approved doubles where the plan permits them; do not expand into an external-site campaign. Suite PASS is retained but does not replace these explicit cases. These cases were already approved; the executor handoff seam was not a reason to omit them.

### C3 — Close the controlled native REST full-field evidence gap

Plan T-08/T-15 requires a controlled native response with Unicode, whitespace, optional SEO and nested/unknown fields, compared byte-for-byte with the served entity.

The supplied T-21 native case proves exact retention of a simple 143-byte object. Its fixture in `helpers/t21_flow.py` constructs ID/link/title/type/date only. Historical post11945 establishes preservation of that hashed saved payload, and the suites add valuable coverage; neither establishes this specific native rich-payload obligation. **That sub-obligation is NOT DEMONSTRATED in the supplied handoff.** Do not reject the native checks that did pass or call this a proved product failure.

First identify any existing exact measurement from this run that actually satisfies the requirement and include its fixture/assertions/results. If none exists, execute one additional loopback native capture with a deliberately formatted UTF-8 JSON body containing non-ASCII text, `content`, optional SEO and nested unknown keys. Compare complete saved bytes to the independently defined served bytes, verify the selected URL has no collector-injected `_fields`, and verify synthetic Set-Cookie is excluded from result metadata. This is completion of the existing plan, not a new feature or a live SEO certification.

## 5. Accepted adjudications and retained limits

| Item | Lead disposition |
|---|---|
| T-20 cold reader | Accept as the bounded consumer-usefulness check. A fresh context is evidenced, no QA analysis was supplied, and the audited tool list shows packet reads and no network/write commands. Same model family and harness-loaded instructions alone do not invalidate this test; the plan did not require a different model or OS enforcement. Do not reuse this as security or code certification. |
| Reader usability notes | Preserve. Fragment-only links resolving to a page URL do not establish a working CTA; source markup can disambiguate them. If producing a new reviewed consumer packet, explain the initial Growth Call package as a reference and avoid overstating distinct CTA destinations. These observations do not require a new menu, UI, crawler or separate approval round. |
| O5 helper observation | Keep as a real initial-helper limitation; C1 still must demonstrate the final reviewed content. |
| Growth Call helper classification | Accepted bounded behavior when the final agent-reviewed package correctly identifies the booking container and marks iframe child content/form function unknown. |
| T-09 keyword hits | Do not classify nine keyword matches as nine unsupported conclusions. Recorded examples include CSS selectors, cited source facts and explicitly labeled interpretations. No unsupported plugin/root-cause conclusion is established by that keyword counter. |
| T-23 privacy controls | Accept the clean, leak, corruption, nested-archive and exact-location false-positive controls within their demonstrated scope. Keep AC-044/export hygiene separate from the B1/B2 failure in AC-043. |
| Public embed parameter | The four checker adjudications are two synthetic control locations plus two occurrences reported from saved public page markup. Accept the documented classification for this reviewed export; do not reproduce the value in authored prose or infer private authentication from its shape. This is not a general exemption for credentials. |
| Executor transition | Opy → Claudy is recorded as one QA run. Both are represented as outside Cody's engineering seat. Do not restart the campaign because its executor changed. Preserve that independence during rework. |
| Clean install and other known limits | Remain explicitly untested/unverified: clean-venv reproducibility, crash/cancellation breadth, broad hostile-viewer coverage, hidden/deferred/image/iframe-child completeness and current external-site access. No new work on these is added by this ruling. |
| Retired implementation | Remains retired; four historical controller findings remain OPEN. No old controller/CDP/full-site design is revived or certified. |

## 6. One coordinated repair-and-verification pass

1. **Architect routes R1/R2 to Cody in the Engineer seat**, using these exact acceptance outcomes. No general recon or plan restart. The attached evidence is the reproduction source.
2. **Cody implements the bounded fixes and regression tests**, preserves existing evidence and reports changed paths and validation. Director retains Git; no agent commits, pulls, switches branches or resets under this instruction.
3. **After Tony commits/releases the repaired candidate, independent QA runs the preapproved retest scope in one run:** verify new identity/diff; execute R1/R2 regressions, T-06, affected Prepare content/provenance checks including C1, T-23, C2 and C3; run all six required regression modules once against the repaired candidate; refresh the 48-row QA matrix, recheck source/fixtures, verify exports, close owned processes and deliver one ZIP. Include new tests rather than forcing the total to stay 124. Ordinary failures continue through unaffected safe checks.
4. **JARVIS reviews that returned evidence for the final QA verdict.** Reuse valid, unaffected earlier measurements with explicit candidate/diff justification. Repeat T-20 only if consumer content, structure or navigation changed enough to invalidate its result; no automatic new cold-read round. Keep final cleanup/merge readiness truthful and separate from a test PASS.

C1–C3 can be prepared within the QA lane while engineering works, but maintain one active writer in the shared checkout. A QA executor must not repair product code or certify its own output. This review provides the retest scope now; no separate retest-plan approval is needed for these unchanged bounds. A different product scope or genuinely new blocker returns for a decision.

Retain the existing QA scratch until the remaining checks and evidence capture are complete. Closing owned processes is routine authorized hygiene. Destruction of existing retained material and Git remain Tony's decisions; do not delete evidence merely to make the working tree look clean. The next handoff should propose an explicit retain/delete list and identify durable records without blanket `git add -A` advice.

For new execution records, capture resolved interpreter, arguments, cwd, start/end, exit code and retained output; avoid placeholder commands. Include existing package-check receipts as companion evidence and avoid recursive self-inclusion of the ZIP/hash receipt. Preserve the historical ZIP unchanged.

## 7. Copy to the Architect

```text
Architect — JARVIS has reviewed the completed scraper QA evidence.

Read WebFactory_QA_Lead_Decision_2026-10-16.md (LEAD-02) and the existing
WebFactory_QA_Q2_Package_2026-10-16_155121.zip.

Gate Q is withheld. Route ONE bounded repair pass to Cody as Engineer:
R1: generic CTA labels must not supply or replace candidate titles.
R2: source text must remain inert through derived Markdown conversion
    for the exact B1/B2 reproductions, while preserving useful content.

Use LEAD-02's acceptance outcomes to produce the actionable engineering
handoff directly; do not restart general recon or seek another approval
of the unchanged QA plan. Keep unrelated features and retired designs out.

Keep Opy/Claudy in the independent QA seat. Their completion/retest scope
is already specified in LEAD-02: C1 final article heading, C2 limit triggers
and directory bytes, C3 rich native REST fidelity, affected regressions
and one complete run of the six required modules after repair.

Tony retains Git and releases the repaired committed candidate to QA.
Preserve all historical evidence and follow one-active-writer ownership.
Return a concrete repair handoff for Cody with exact paths, reproduction
references, acceptance checks and the QA handback location.
```

This is a QA Lead adjudication of the bound evidence package, not approval of an unseen patch, a certificate, a merge authorization or a deployment decision.
