# Default-mode recon — useful candidates; REST reconnaissance incomplete

**Done:** one authorized run produced **36 same-site candidate URLs**, including **nine article headings/links** corroborated in the actual blog listing. Every item remains **UNDECIDED**. No selection, plan export or full collection occurred.

**Gap:** projected WordPress types returned HTTP 200 with the complete two-byte JSON body `[]`. That is valid JSON but the wrong structure for the expected types map (`malformed_wp_types`). No pages/posts/custom-type metadata reads followed. Their advertised counts remain **unknown**, and **zero REST selection records** were enumerated. Field projection cannot be verified from an empty array. No cause is established.

**Next move:** Tony reviews [the numbered choices](response_2026-10-07_205421_default-recon-live_review/CANDIDATES.md) and supplies inclusions/exclusions by row or stable ID. Any further REST investigation needs a separate authorization. This allocation is finished.

## What the one run actually read

| Planned call | Status / final URL | Saved bytes | Result |
|---|---|---:|---|
| Blog listing | 200; `https://cyberizegroup.com/blog/` | 591,675 | Real rendered blog, title “Digital Marketing Blog by Cyberize Group”; nine article heading/link pairs. |
| Projected types | 200; same requested types URL | 2 | `[]`; no usable type map, counts or endpoint inventory. |
| Pages metadata | Not attempted | 0 | No usable types map. Advertised total unknown. |
| Posts metadata | Not attempted | 0 | Same reason. Advertised total unknown. |

Custom content types were not established or enumerated. Media enumeration was outside scope. The 36 document candidates came from one blog’s same-site links, not REST records or a whole-site inventory. Only the blog was read; 35 candidate destinations were not fetched. All dates and 35 MIME types remain unknown. Many inventory article titles are the last observed “Read Post” anchor label; the separate numbered review shows the heading labels corroborated in the saved blog without altering the inventory version.

Useful examples in that listing:

- Row **9**: “How to Regain Consistency with Facebook Ads After the Andromeda Update.”
- Row **12**: “Garage Door Repair PPC Agency – Get More Leads & Sales Now!”
- Row **7**: “Boost Your Dental Practice with a Professional SEO Company.”

Row9 retains the **historical** post11945 `content.rendered` empty warning from the validated saved collection. It is flagged for HTML review if selected. This recon requested no post body, and cannot establish why that earlier body was empty. The sample does not establish destination content quality, publication dates, full-site coverage or other exposed REST types.

## Human review — recommendations, not decisions

- Service and case-study rows **3–5, 8, 11, 18, 20–21, 24–25, 29–32, 34, 36** appear useful for understanding the business’s offers; this is an inference from their link labels.
- Article rows **7, 9, 12, 14, 15, 26–28, 33** provide topical candidates. The destination article bodies were not inspected in this run.
- Policy/legal rows **13, 16, 22–23** may be lower value for marketing analysis, but could matter for compliance. Rows **30/32** might overlap; matching labels do not prove duplicate content. No automatic exclusions were made.

## Execution, limits and cleanup

- **Exactly two planned calls** out of the maximum four; two unused. This was not a request-limit stop: `stop_reason=null`; the WordPress structure gap prevented metadata enumeration.
- **CLI exit 0**; this does not mean WordPress recon succeeded. `cleanup_error=null`; no cleanup error reported. The library warned that some images did not load within its timeout.
- Started **2026-10-07T14:50:35.182694+00:00**; finished **2026-10-07T14:50:52.849362+00:00**; process elapsed **17.666690s**, below the 180s configured collection deadline. No supervisor action.
- Blog call took **8.921760s**; types call **1.362446s**. Completion-to-next-planned-call gap **5.001124091s**, meeting five seconds. These measurements share the runner’s Python monotonic clock; they are planned-call timing, not wire-dispatch timestamps.
- **134 passive browser request events** were observed, with statuses/resources in `requests.json`. Background resources and ordinary redirects were additional traffic; two planned calls is not two HTTP requests. Planned final URLs stayed unchanged; the browser counters also recorded one incidental/ordinary 301 whose chain is not identified here.
- Saved response bytes **591,677**; output directory **680,101 bytes**. No retry, alternative mode/client, pagination, extra probe or automatic collection.

## Source and offline validation

Branch **`wf-scrapper-abm`**, full HEAD **`fb16b1b927a234d74a2c29c9044df33317ff8276`**; starting working tree **clean**. The current commit differs from the prior implementation report’s historical HEAD, but all reviewed source bytes match.

Reviewed and final **50-file inventory SHA-256**: `ebc6e8310ce4aab49a93ec6cc3c2011fbddeb404642362a6fc442a71ae77b864`. Product/test source remained unchanged. No tests or extra browser checks were run for this task.

Offline inspection verified inventory content binding, 36 unique stable IDs, all rows UNDECIDED, both body lengths/hashes, and all referenced source hashes including the earlier REST warning. **42,650 pre-existing output/evidence/report files hash-verified unchanged**. New checkpoint entries preserve historical text. Independent QA **NOT RUN**; Prepare not started. Historical media discrepancy, shutdown/accounting and supervisor findings remain open.

## Exact command and retained evidence

```bash
venv/bin/python -m recon_pipeline.decide recon --mode default --url https://cyberizegroup.com/blog/ --out outputs/recon/CyberizeGroup-default-01 --gap 5 --max-requests 4 --max-pages 1 --max-depth 0 --max-rest-pages 1 --per-page 1 --max-candidates 100 --max-seconds 180 --known-collection outputs/collections/CyberizeGroup-selected-live-01
```

- Original output: `outputs/recon/CyberizeGroup-default-01/`.
- Run log, preflight, execution, source and preservation proofs: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/default-recon-live/2026-10-07_145034Z/`.
- Blog evidence: `outputs/recon/CyberizeGroup-default-01/evidence/0001.body`; SHA-256 `0867a82223dfb0f3c6781062ebbf6894586200468521074c740e02bbdc3271ab`.
- Types evidence: `outputs/recon/CyberizeGroup-default-01/evidence/0002.body`; SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.

## Handoff files

- [CANDIDATES.md](response_2026-10-07_205421_default-recon-live_review/CANDIDATES.md) — easy numbered review, with supplemental article labels and recommendations.
- [INVENTORY.md](response_2026-10-07_205421_default-recon-live_review/INVENTORY.md) — unchanged canonical numbered inventory.
- [inventory.json](response_2026-10-07_205421_default-recon-live_review/inventory.json) — byte-identical machine inventory; version `b6bbf6e41195988cab053457c81bd91fed8d9560a84953add657c54d8bbcf291`; file SHA-256 `2ee9e4ac53dfb9fd630d06a7f86e43b2e9539ca07481b066bf657c37f1a7ee44`.
- [response_2026-10-07_205421_default-recon-live_summary.json](response_2026-10-07_205421_default-recon-live_summary.json) — compact results, limits, unknowns and cleanup outcome.
- [checks.json](response_2026-10-07_205421_default-recon-live_review/checks.json) — offline hashes, source references and preservation checks.

Raw rendered HTML and historical capture bodies remain in the repository; shared packaging contains their precise locations/hashes, the small types response and sanitized metadata. No cookies, credentials, dependencies or bulk historical output are included. **STOP: no further live call, selection, capture or repair.**
