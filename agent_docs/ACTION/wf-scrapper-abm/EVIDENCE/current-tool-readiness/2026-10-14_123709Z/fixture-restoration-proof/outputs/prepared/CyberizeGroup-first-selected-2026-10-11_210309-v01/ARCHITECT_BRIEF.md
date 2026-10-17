# Architect brief — Cyberize Group, three-page sample

Prepared offline from the **October 11, 2026** selected collection. Scope: Home, Agency Services and the Andromeda article only; **no REST was selected for that collection**. This is useful architect input from a small sample, not a whole-site assessment, functional test or independent QA certificate.

## Evidence and observed source facts

[Source index](SOURCE_INDEX.json) records URL, UTC save date, raw body/metadata hashes, CSS extraction location and derived-file hashes for every page. Main content is separated from [navigation/footer](BOILERPLATE.md). Raw captures remain unchanged. The Markdown preserves source wording rather than silently correcting copy, responsive duplicates or CTA destinations.

### Home — positioning and offerings

Source: [Home Markdown](pages/3a1a77925e47639b5f9fd201.md), source ID `3a1a77925e47639b5f9fd201`; extraction `#tcb_landing_page #tve_editor`, with `#thrive-header` and `#thrive-footer` separated. Captured 2026-10-11T14:36:05.278195+00:00.

**Observed:** the hero offers digital solutions for growing a business. It names three needs: more website visitors, website changes, and a new/rebuilt website. The business describes itself as a **B2B digital marketing agency**. Three solution headings are Website Design, Website Support and Website Traffic. More detailed blocks cover SEO, PPC, WordPress-based web design/development, and website support/maintenance. The source calls its care offering “WP Care.” A Supported Integrations section exists; the text says it is a sample, so no exhaustive integrations list is established.

**Observed CTAs:** design links to `/website-design/`; support to `/wordpress-support-options/`; SEO to `/seo-services/`; PPC to `/ppc/`. The traffic link is an in-page anchor. The ending sales section promotes a free website strategy call. Two “Book my strategy call” links have different saved destinations: `/growth-call/` and `/`. Both are retained; their click behavior is untested. The “hundreds of small businesses” statement is source marketing copy, not independently verified performance evidence.

**Observed content caveats:** the homepage repeats “Our Internet Marketing Services” in its markup; both headings are preserved. Its traffic copy refers to an area being on lock-down. These are actual source observations, not proof of responsive behavior or the last editorial update.

### Agency Services — category/article listing

Source: [Agency Services Markdown](pages/ae3d8256cdd00e50ca26c1f2.md), source ID `ae3d8256cdd00e50ca26c1f2`; extraction `#theme-content-section`. Captured 2026-10-11T14:36:16.998696+00:00. Its raw body includes `archive`, `category` and `category-agency-services` classes.

**Observed:** this URL is a **category/article listing**, not a detailed agency service page. Six cards cover garage-door PPC, dental SEO, digital marketing strategy, eLearning PPC, real-estate social media, and medical-supplies PPC. Each combines a heading, shortened excerpt and Read More link. Saved pagination text says **Page 1 of 7**. That is a UI indicator; only page1 was captured, and seven pages of article content were not downloaded. One empty SVG breadcrumb separator was removed; both meaningful breadcrumb entries and all article links remain.

### Andromeda — substantive article with conversion CTAs

Source: [Andromeda Markdown](pages/76f31511d3acb8433bdb9d50.md), source ID `76f31511d3acb8433bdb9d50`; extraction `.tcb-post-content #tve_editor`. Captured 2026-10-11T14:36:28.824399+00:00.

**Observed:** all **seven paragraphs, 15 list items and six headings** are present, in source order. Sections describe prospecting/remarketing/scaling, research and creative formats, bidding/cost control, a weekly operating routine, and a concluding invitation. The text is source advice; its effectiveness and correctness were not independently assessed.

**Observed CTAs:** Book My Call, get my strategy plan, start scaling smarter, and Book my call all resolve to the saved `/growth-call/` destination with the source tracking query retained. No clicking, scheduling or form submission was performed. Navigation, repeated signup/footer material and social-sharing UI outside the article subtree are not presented as article paragraphs.

## Separately dated REST context

- **October 7, 2026:** [saved post11945 REST body](../../collections/CyberizeGroup-selected-live-01/attempts/831c1e00b05bbdb42ea72413/86de34339bf54d5fb794cb0ffcc2cfdc/body), captured 2026-10-07T13:39:13.191607+00:00, HTTP200,33,839 bytes. It has ID11945, a populated title and the matching article link. `content.rendered` is **present and empty**, not missing/null. Its body hash is `dd04572fa0e4bf915a611d394dfa576dbcaa2a013eb33ea6b039d0ed0133bd2e`. The October11 HTML observation above remains independently substantive. The discrepancy does not establish a plugin, transport or root cause; no retry was attempted.
- **October 10, 2026:** [metadata reconnaissance summary](../../../agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recon-small-fixes/2026-10-10_135244Z/rest-live/result.json), interval 2026-10-10T13:56:06.445163+00:00 to 2026-10-10T13:56:22.281695+00:00. It describes **33 public types**. Pages advertised **42 records**, posts **166 records**; only **one projected metadata record per collection** was sampled. The projected responses did not request content. These advertised totals are not prepared/captured content counts and do not imply all exposed types can be collected.

## Agent interpretation — implications for JARVIS

These are recommendations to evaluate, not new source facts or approved implementation decisions.

- A starting information model could separate **service detail**, **category/listing**, **article** and **conversion destination**. Agency Services demonstrates why route names alone cannot identify those roles.
- A preliminary content hierarchy can reflect the three solution areas, then detailed SEO/PPC/design/support offerings. Service-detail captures are needed before treating that hierarchy as complete.
- The article pairs education with repeated consultation CTAs. `/growth-call/` is an important candidate for an explicit follow-up read; its form/function remains unknown.
- Shared navigation/footer can inform cross-page structure without contaminating the main article body. Image references, logos, maps and layout need separate review; this text package does not establish their completeness.
- Preserve HTML and REST as complementary evidence. An empty REST content string should become a named source gap, not an instruction to erase meaningful rendered content.
- Review the duplicate homepage heading, differently targeted CTA and lock-down phrasing before reusing the copy. Their cause and intended behavior are unknown.

## Limits

Only these three pages were prepared. Image completeness is **UNVERIFIED**, including eight Home and one article image references; some collection image waits timed out. No image bytes/OCR, hidden/deferred-content completeness, full service catalogue, full category pagination, CTA functionality or whole-site reliability is established. Historical capture/controller/media findings are not closed by this package. See [GAPS_AND_REQUESTS.md](GAPS_AND_REQUESTS.md) for specific next requests; none are executed automatically.
