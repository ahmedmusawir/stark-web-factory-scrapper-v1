# Label cleanup done — Tony’s choices ready

**Done:** punctuation/empty/generic CTA labels no longer overwrite meaningful labels. Missing meaningful titles remain unknown; no slug-based titles. Unicode text, stable IDs and every source locator are preserved. The collector and accepted WordPress types fix remain unchanged.

**Verified:** **55 focused DECIDE checks passed** (pytest8.75s, exit0), including both heading → `...` → Read Post and reverse order, weak-only unknown titles, Unicode text and the unchanged native localhost browser fixture. All **nine** actual saved blog labels now **exactly match their independently extracted h2 text**. No live target requests ran.

**Correction:** my October10 nine-label success claim was wrong. The old proof accepted `...` because its oracle only checked “not Read Post.” That proof stays intact; an explicit correction was appended to the earlier report and checkpoint records. The accepted REST results were preserved and not repeated.

**Next move:** Tony reviews the numbered candidates and chooses HTML/REST scope separately. Recommended first HTML batch: **1 Home, 3 Agency Services, 9 Andromeda article**—positioning, offering, then one article. Recommendations are not selections. Every row remains **UNDECIDED**.

## Corrected nine labels

These are headings observed in the saved blog listing, not verified destination-page titles.

| Row | Exact saved heading = replayed label |
|---:|---|
| 7 | Boost Your Dental Practice with a Professional SEO Company |
| 9 | How to Regain Consistency with Facebook Ads After the Andromeda Update |
| 12 | Garage Door Repair PPC Agency – Get More Leads & Sales Now! |
| 14 | How to Rank High on Google: A Step-by-Step Guide |
| 15 | How to Write SEO-Friendly Content: A Step-by-Step Guide |
| 26 | The Essential Guide to Developing a Winning Digital Marketing Strategy |
| 27 | The Ultimate Guide to Acquiring More Pizza Shop Customers |
| 28 | Unlocking the Power of SEO Copywriting: What You Need to Know |
| 33 | What is a Sitemap and How to Create One for Your Website |

## Immutable review and historical REST snapshot

[TONY_CHOICES.md](response_2026-10-11_001956_label-cleanup-tony-choices_review/TONY_CHOICES.md) shows all36 numbered URLs, readable labels, stable IDs, provenance and gaps. [inventory.json](response_2026-10-11_001956_label-cleanup-tony-choices_review/inventory.json) and [INVENTORY.md](response_2026-10-11_001956_label-cleanup-tony-choices_review/INVENTORY.md) are the new canonical version. The same36 document URLs/IDs/row numbers remain; original inventory and selections were not changed. New version `64d54b52b28aa188e4d80a1eab97e1f7ebde293f294f39e6885b60991fb89392`; exact file SHA-256 `01adef99b6092cb57b089ff56e37298f36668ec11b7eb063df9d6be1d705f4c6`.

The saved October10 REST snapshot describes **33 types**. Pages advertised **42 records / 42 pages at per_page1**, but **one metadata record** was sampled (9067). Posts advertised **166 records / 166 pages**, but **one metadata record** was sampled (11945). These are historical samples, not new collection totals. Other type counts/readability are unknown. Metadata did not request full content.

Row9 keeps post11945’s earlier empty-content warning. Its evidenced single-post REST endpoint is available for a separate explicit choice. Row11 has the saved single-page metadata mapping. HTML selection does not approve an entire REST collection. Home/Services and the article bodies were not fetched by this task.

## Source, checks and preservation

Branch `wf-scrapper-abm`; full HEAD `fb16b1b927a234d74a2c29c9044df33317ff8276` plus preserved pre-existing dirty source/checkpoint/evidence. Only `recon_pipeline/decide.py` and `tests/test_decide.py` changed in the50-file source inventory. Tested/final identity: `609d3493a7f45bcb151c74c22275c35de171fc015886e40fb4547b6a020eb729`.

Exact focused command:

```bash
PYTHONDONTWRITEBYTECODE=1 DECIDE_EVIDENCE=agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/label-cleanup/2026-10-10_181514Z/focused-final venv/bin/python -m pytest -q tests/test_decide.py --basetemp=/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/label-cleanup/2026-10-10_181514Z/focused-final/fixtures -p no:cacheprovider --junitxml=/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/label-cleanup/2026-10-10_181514Z/focused-final/junit.xml
```

Before-fix failures are retained. The new Unicode fixture declares UTF-8 explicitly; exact expected-heading assertions remain. No broad engineering campaign or independent QA was rerun. **43,112 existing output/evidence/report files hash-verified unchanged**; the one authorized earlier-report correction is append-only and preserves every earlier byte. Old `[]`, nine-ellipsis proof, REST responses, captures, inventories, selections and ZIPs remain unchanged.

## Handoff files

- [Numbered choices](response_2026-10-11_001956_label-cleanup-tony-choices_review/TONY_CHOICES.md) — all36 UNDECIDED rows, recommendations and separate REST scope.
- [Corrected nine labels](response_2026-10-11_001956_label-cleanup-tony-choices_review/corrected-nine-labels.json) — expected/actual exact strings with hashes and source locators.
- [response_2026-10-11_001956_label-cleanup-tony-choices_checks.json](response_2026-10-11_001956_label-cleanup-tony-choices_checks.json) — focused results, source and preservation checks.
- Exact source/test/instruction diff: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/label-cleanup/2026-10-10_181514Z/scoped.diff.txt`.
- Evidence: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/label-cleanup/2026-10-10_181514Z`.

No live requests, human choice, approved export, collection, Git mutation, dependencies or Prepare implementation. Independent QA **NOT RUN**. Historical accounting/media/shutdown/supervisor findings remain open. STOP after handoff.
