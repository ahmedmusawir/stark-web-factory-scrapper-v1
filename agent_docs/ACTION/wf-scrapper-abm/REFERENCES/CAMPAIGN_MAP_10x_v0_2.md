# Web Recon ABM — Campaign Map

Version: 0.2 | 2026-09-17 | Current block: 1, Architect authoring

## Fixed outcome

One approved website collection produces preserved raw evidence plus a processed pack that a chat-based Architect can understand and inspect. Source references, disagreements, missing data, and uncertainty survive processing. Completion is tested against the master spec, not document volume.

## Five long blocks

| Block | Lead | Work bundled into the block | Exit / next handoff |
|---|---|---|---|
| 1. Package | Existing Fable Architect + Tony | Consolidated recon, source reconciliation, donor-pattern mapping, contract/schema decisions, acceptance bindings, internal task ordering, Claudy Plan Mode readback | Tony approves one executable ABM and build plan |
| 2. Build | Claudy / Fable | Remaining Capture tasks → raw contract validation → Prepare tasks → end-to-end checks → completion report; log work throughout | One committed candidate, one acceptance ledger, one engineering handoff |
| 3. QA and repair | SOL Lead + Cody executor; Claudy repairs | QA recon and plan binding → full test campaign → defect batch → repairs → retest/regression → Gate Q → QA Cleanup | Certified candidate and durable evidence ready for reviews |
| 4. Review | Astra + Fable in separate sessions | Two broad reviews on the same candidate; keep reports separate until both finish; Architect consolidates findings, Tony rules | One disposition ledger and approved RRM scope, or explicit no-repair ruling |
| 5. RRM and close | Architect → Claudy → SOL/Cody → Astra → Tony | One consolidated repair build; independent repair tests/regression; targeted final Astra review; certification, cleanup, Architect closeout, Director merge | Certified Recon + Prepare candidate and short experiment retrospective |

There is no extra mandatory Astra plan review inserted between blocks 1 and 2. The approved Factory Plan Mode readback remains. Director-requested specialist advice can be obtained for an actual unresolved issue without creating a standing new gate.

## Internal build stages

**Stage C — Capture:** finish collection of rendered HTML, REST/SEO, site route/sitemap evidence, media inventory, provenance, and typed absences; preserve certified base behavior.

**Automatic engineering checkpoint:** validate the real raw package against the approved contract, reconcile all input routes, exercise failure fixtures, and prove the Prepare reader can consume it. Advance directly when green. If real evidence contradicts the approved contract, record the precise conflict and escalate only that decision; never invent a schema change.

**Stage P — Prepare:** derive current site structure, content/SEO/media/form/embed inventories, observed design evidence, disagreements, loss/absence records, and the human entry brief with provenance links. Validate the complete pipeline.

These stages may contain multiple internal BIM tasks. They do not require separate independent QA campaigns. Existing certified BIMs become the no-break baseline; recon determines which remaining work is actually needed.

## Branch and seat rules

- Suggested campaign identity: web-recon-abm001, subject to the Architect checking existing names once.
- Director flow: approved main baseline → ABM engineering branch → qa/<ABM> → certified merge to main. Director controls commits/pushes/merges; agents use read-only git unless explicitly authorized otherwise.
- Claudy and Cody use the forward QA line sequentially during repair loops. Pin a new candidate SHA before each retest. Neither edits product code while the other is testing it.
- Reviewers use the same frozen post-QA candidate; review outputs live outside their read-only product specimen. Record input identity and any prior involvement.
- If repairs are accepted, use the existing RRM lifecycle: main → RRM engineering branch → qa/<RRM> → main. One consolidated RRM is the target; split only for a concrete dependency or rollback constraint that the Architect explains to Tony.
- Fable's fresh review session offers a separate review pass, but using the same model as Engineer is not full model independence. Astra supplies the different-model assessment.
- QA certificates identify implementation SHA; evidence/closeout commits and merges are recorded separately. Cleanup cannot hide product changes.

## Authoring bindings to resolve in one pass

| Binding | Required fact before build launch |
|---|---|
| B1 — Specimen | Repo path, branch/SHA, clean/dirty state, certified modules and current regression command |
| B2 — Interface | Exact collection, Prepare, and combined run commands; project/output ownership; fresh-environment instructions |
| B3 — Contracts | Raw and derived schema versions, required fields, URL identity and source-link rules, run association and failure semantics |
| B4 — Evidence cases | Named fixtures for stream disagreement, REST-empty rendered pages, SEO absence, media classes, missing data, malformed inputs, partial runs |
| B5 — Access and cost | Approved target/route set, scope/redirect policy, request and retry limits, pacing, time/disk limits, permitted live probes and output retention |
| B6 — Processing | Which deterministic rules implement each donor lesson; any unsupported inference explicitly labeled; no mandatory LLM or paid API dependency |
| B7 — Consumer check | Required pack questions and which fields must be answerable without live access; actual reading/verification owner |
| B8 — Authority | Writable paths, protected surfaces, approved dependencies, git/cloud owner, live-run permissions |

Unfilled bindings mean AUTHORING, not ready to launch. They are implementation facts for the main Architect to settle, not an invitation to reconsider the already-directed product scope. QA independently binds commands and probes in its own plan before Cody executes.

## Experiment exception record

The Director explicitly requested compression into long steps on 2026-09-17. For this ABM, routine per-BIM/per-stage independent QA is replaced by one whole-product QA campaign. Engineering checks, stable acceptance, independent QA verdicts, role separation, evidence, cleanup, and Director authority remain. No automatic change to unrelated Factory projects.

Stop for a real contract/scope conflict, unauthorized external action, destructive operation, or inability to meet mandatory requirements. Otherwise continue approved work. At context/session limits, checkpoint and resume; no new product approval merely because a session restarted.

## Finish and measure

Close only after mandatory acceptance is verified, required manual/cold-read checks are complete, reviews are dispositioned, accepted RRM work is verified, and final certification/cleanup/closeout is recorded. Report remaining limitations honestly; no deployment claim.

Track build time, QA time, review/RRM time, Director interventions, session resumptions, defect/rework rounds, and measured provider usage if available. Compare to Experiment B as operational learning, not a controlled performance benchmark.
