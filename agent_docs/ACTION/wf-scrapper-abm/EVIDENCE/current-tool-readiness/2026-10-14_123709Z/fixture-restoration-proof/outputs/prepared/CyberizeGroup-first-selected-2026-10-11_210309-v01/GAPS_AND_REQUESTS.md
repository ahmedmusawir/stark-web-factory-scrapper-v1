# Gaps and proposed requests — no automatic fetching

This is a **three-page sample**. The proposals below are for JARVIS/Tony to review, not approved selection or live allocation. Current collection/recon remain unchanged.

## Known gaps and unknowns

- **Images: UNVERIFIED.** Main-source references include eight Home images and one article image; listing thumbnails/background images may live outside the text subtree. Collection logs report image-wait warnings. No image-byte completeness or visual/layout/alt-text audit is claimed.
- **Service details are not captured.** Home describes offering families; Agency Services is an article category listing. Do not confuse its six cards with a complete service catalogue.
- **Category pagination is incomplete by scope.** The UI says Page 1 of 7, but only the selected first page was read. Card excerpts are intentionally truncated in the source; they are not the linked article bodies.
- **REST discrepancy remains:** the separately dated October7 post11945 response has `content.rendered: ""`; October11 rendered HTML has seven article paragraphs and 15 list items. No cause is established and no retry is justified automatically.
- **Counts are not content:** October10 types returned 33 descriptions; pages 42 / posts 166 were advertised, with one projected metadata record each. Metadata did not request content. Other types' readability, SEO-field availability and site-wide coverage are unknown.
- **CTAs/forms/embeds are untested.** The same Home CTA label targets `/growth-call/` and `/`; intended behavior is unknown. The footer includes a consent-blocked map message; no consent or form interaction occurred.
- **Source copy needs editorial review:** repeated Home heading and lock-down wording are preserved, not silently repaired. Published/modified dates are not established for every selected page; capture time is not publication time.
- **Hidden/deferred content and responsive variants are unknown.** This conversion preserves the identified saved DOM subtree; it cannot certify content absent from the capture.

## Specific proposed next reads

The HTML destinations below were observed in saved links. The conditional REST item URL is proposed from the exposed pages endpoint and observed ID9067; it was not fetched. Request the exact scope Tony approves; none imply discovery, pagination, media harvesting or an entire WordPress collection.

| Priority | Proposed item | Reason | Evidenced source |
|---|---|---|---|
| 1 | HTML `https://cyberizegroup.com/growth-call/` | Understand the primary consultation destination, offer and form labels; capture does not authorize submitting it. | Home and Andromeda CTA links |
| 2 | HTML `https://cyberizegroup.com/seo-services/` | Establish actual SEO service detail, audience and CTA rather than assuming the category listing supplies it. | Home SEO link |
| 2 | HTML `https://cyberizegroup.com/ppc/` | Establish the PPC service/process detail and source claims. | Home PPC link |
| 3 | HTML `https://cyberizegroup.com/website-design/` | Clarify web-design/development scope, deliverables and proof. | Two Home design links |
| 3 | HTML `https://cyberizegroup.com/wordpress-support-options/` | Clarify WP Care/support terms and boundaries. | Home support links |
| Optional | HTML `https://cyberizegroup.com/agency-services/page/2/` | Sample category continuation only if additional content themes matter; preserve bounds and do not infer all seven pages are approved. | Saved category Next/page2 link (tracking query recorded in source index) |
| Conditional | Single REST item `https://cyberizegroup.com/wp-json/wp/v2/pages/9067` | If Full SEO Audit is selected later, enrich identity/metadata for its evidenced page9067. The current snapshot contains metadata only; full-content/SEO availability is not established. | October10 sampled page ID and exposed pages endpoint; proposed item route |

## Requests to people, not the scraper

- Ask Tony which service destinations or consultation page belong in the next batch. All other review rows remain UNDECIDED.
- Ask the content owner to clarify the differently targeted strategy-call links and whether lock-down phrasing is still intended.
- Ask JARVIS whether image/visual evidence and deeper category coverage are needed for the intended architecture deliverable; then define a separate bounded collection request.
- Use the already-saved post11945 REST body for the known empty-content comparison. **Do not propose an automatic repeat of that same read** solely because it was empty.
