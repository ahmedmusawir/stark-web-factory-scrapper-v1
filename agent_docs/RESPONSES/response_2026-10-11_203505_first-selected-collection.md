# Done — Tony’s first selected collection

**Completed: 3 of 3 selected HTML pages. Missing: none.** All returned HTTP200 and were saved before their checklist entries became complete. Collection exit 0; no stop reason and no reported cleanup error. No resume was needed.

**Andromeda’s actual article body was captured:** seven paragraphs, 15 list items and 1,903 characters in its identified article container, including the funnel, creative, scaling and weekly-routine sections. This establishes useful text in this rendered snapshot; hidden/deferred content completeness is not certified.

**Scope:** Tony approved only corrected-review rows 1, 3, 9. REST scope is **none**. Other 33 rows remain **UNDECIDED**. No recon, discovery, REST, additional article or media harvesting ran. Ordinary page-loaded resources are additional traffic.

## Saved pages

| Row | Page | HTTP | Saved HTML bytes | Observed content |
|---:|---|---:|---:|---|
| 1 | [B2B Digital Marketing Agency >> Cyberize Group](../../outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505/attempts/3a1a77925e47639b5f9fd201/989120207d124adf99a60c163e10552a/body) | 200 | 430,420 | Actual homepage: “We provide Digital Solutions for growing your business”; service and offering paragraphs present. |
| 3 | [Agency Services » Cyberize Group](../../outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505/attempts/ae3d8256cdd00e50ca26c1f2/a53bc0b7b9064888b1cdd491acc23000/body) | 200 | 573,516 | Actual Agency Services **category/article listing**, with its heading and article cards; it is not an individual service article. |
| 9 | [How to Regain Consistency with Facebook Ads After the Andromeda Update](../../outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505/attempts/76f31511d3acb8433bdb9d50/220f10a856624283ba03669128dffef9/body) | 200 | 389,468 | Actual article body:7 paragraphs / 15 list items; beginning, middle and concluding text present. |

Final URLs equal the three selected URLs; no main-document redirect predecessor was recorded. HTML is Crawl4AI’s UTF-8 rendered DOM snapshot, not original compressed HTTP bytes. Saved metadata retains body completeness, hashes, status and transport.

## Proof of useful article text

The article body is in `.tcb-post-content #tve_editor`; navigation, related cards and footer content were excluded from this inspection. Its exact heading is “How to Regain Consistency with Facebook Ads After the Andromeda Update.”

Two brief observed excerpts:

> Think of your ad strategy as a funnel with three campaigns.

> The Andromeda update made one thing clear: your creative does the targeting.

The saved body also includes “Your New Weekly Routine” and the concluding paragraph. UTF-8 punctuation is preserved. The earlier empty REST body for post11945 remains historical evidence; REST was not requested or changed in this batch.

## Decision binding and execution

- Corrected inventory: [inventory.json](response_2026-10-11_001956_label-cleanup-tony-choices_review/inventory.json). Content ID `64d54b52b28aa188e4d80a1eab97e1f7ebde293f294f39e6885b60991fb89392`; exact file SHA-256 `01adef99b6092cb57b089ff56e37298f36668ec11b7eb063df9d6be1d705f4c6`.
- Tony’s actual decision: [tony-decision.json](../../outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505/tony-decision.json); actor Tony Stark, `example_only=false`, HTML rows1/3/9, no REST/exclusions.
- Exported plan: [collector-plan.json](../../outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505/collector-plan.json); exactly three HTML URLs and `rest: []`.
- Fresh collection: `outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505`.
- Branch `wf-scrapper-abm`; full HEAD `fb16b1b927a234d74a2c29c9044df33317ff8276` plus preserved dirty/untracked work.
- Unchanged tested 50-file source inventory SHA-256: `609d3493a7f45bcb151c74c22275c35de171fc015886e40fb4547b6a020eb729`. No source/test/dependency edits or Git mutations.

Executed selection/export and capture commands:

```bash
venv/bin/python -m recon_pipeline.decide select --inventory agent_docs/RESPONSES/response_2026-10-11_001956_label-cleanup-tony-choices_review/inventory.json --include-html 1 --include-html 3 --include-html 9 --by 'Tony Stark' --out outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505/tony-decision.json
venv/bin/python -m recon_pipeline.decide export --inventory agent_docs/RESPONSES/response_2026-10-11_001956_label-cleanup-tony-choices_review/inventory.json --decision outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505/tony-decision.json --out outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505/collector-plan.json
venv/bin/python -m recon_pipeline collect --plan outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505/collector-plan.json --collection outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505 --gap 5 --max-requests 3 --max-seconds 480 --max-bytes 30000000
```

Collector work elapsed **37.426s**; command process elapsed39.226s. It made exactly **3 planned collection calls**, one attempt each. Completion→next-call gaps were **5.000830s** and **5.004110s**. No retries, refreshes or resume invocation.

Configured bounds:3 planned calls, 480 seconds of work, 30,000,000 bytes persistence check,10 MiB per-response retained cap. Actual HTML 1,393,404bytes; final collection directory 1,400,002bytes including library-local files. This simpler persistence check is not a hard aggregate wire/storage supervisor.

Passive observations recorded 355browser request events and 342response events, including scripts, images, styles, Fetch/XHR, fonts and other page traffic. This was **not** a three-HTTP-request test; the event counters are observations, not exhaustive wire accounting.

## Errors, validation and preservation

- **Collection:** complete for the selected HTML scope; exit 0; stop reason null; completed 3 / remaining 0.
- **Cleanup:** no raised/logged cleanup error; cleanup message list empty. This does not prove zero teardown traffic.
- **Warnings:** Crawl4AI reported some images did not load within its wait window on Home and Andromeda. The saved text is useful; no image/download or full resource completeness claim.
- **Saved-result checks:** existing collector `valid_result()` accepted all 3; each body’s byte count/SHA-256 and metadata reference SHA-256 match. This is selected-checklist validation, not historical raw-v2 or independent QA certification.
- **Preservation:** 43,613pre-existing output/evidence/report files hash-verified unchanged. Corrected inventory unchanged. Product/test source inventory unchanged before/after. Pre-existing dirty work preserved.
- **Historical findings:** previous media-count discrepancy, shutdown findings, homepage accounting and supervisor-counter findings remain open. This run’s totals do not combine previous runs.
- **Independent QA:** NOT RUN. Prepare not started.

## Handoff files

- [Collection summary](response_2026-10-11_203505_first-selected-collection_summary.json) — timing, three per-page results, content findings, source identity and hashes.
- [Checklist](response_2026-10-11_203505_first-selected-collection_checklist.json) — three complete items and durable saved-result references.
- [Evidence directory](../ACTION/wf-scrapper-abm/EVIDENCE/first-selected-collection/2026-10-11_143505Z) — preflight, command/logs, offline inspection, source and preservation proofs.
- [Home HTML](../../outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505/attempts/3a1a77925e47639b5f9fd201/989120207d124adf99a60c163e10552a/body).
- [Agency Services HTML](../../outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505/attempts/ae3d8256cdd00e50ca26c1f2/a53bc0b7b9064888b1cdd491acc23000/body).
- [Andromeda HTML](../../outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505/attempts/76f31511d3acb8433bdb9d50/220f10a856624283ba03669128dffef9/body).

**Next move:** review the three saved pages. Other rows remain undecided; any additions or REST scope require Tony’s explicit selection. This task stops here; no Prepare implementation or further collection.
