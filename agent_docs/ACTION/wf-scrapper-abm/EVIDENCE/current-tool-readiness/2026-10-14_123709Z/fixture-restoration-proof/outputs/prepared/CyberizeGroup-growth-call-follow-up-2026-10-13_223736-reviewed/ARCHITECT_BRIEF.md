# Architect follow-up — Growth Call

**Observed result:** one approved HTML page was captured successfully and prepared offline. The page reaches a **separate embedded booking widget**. Its parent HTML does not expose the widget's field labels or detailed offer text. This is a useful destination finding with incomplete booking-content coverage; no booking/form QA was performed.

## Source facts

- Requested/final URL: <https://cyberizegroup.com/growth-call/>; HTTP 200; saved 298,221 rendered-HTML bytes at 2026-10-13T16:38:43.362487+00:00.
- Document title: **Schedule Your Digital Growth Strategy Call Now**. This identifies a digital growth strategy call. The **main subtree** contains no standalone heading/paragraph text or link CTA; no form or label elements exist in the parent DOM. SEO description metadata invites the call and promises tailored solutions for online success; it is not visible form/offer copy. Other global anchors do not establish a main booking submit CTA. Do not transfer duration/price/guarantees from an assumption or title alone.
- Body classes identify a WordPress page (`page`, `page-id-8331`). It is a booking/consultation destination, not an editorial article despite the initial helper heuristic.
- The iframe source is [https://link.cyberizegroup.com/widget/booking/DGS01qOQAJzewOETHhPD](https://link.cyberizegroup.com/widget/booking/DGS01qOQAJzewOETHhPD), under `.tcb-post-content #tve_editor`. Its inline style declares visible/block display, full width and 785 px height. That does not prove the embedded form loaded completely or its fields were visible in a particular viewport.
- The captured parent document does not contain the **child iframe's DOM**. No visible field labels, submit-button wording, calendar slots, duration or booking availability can be reported from this saved evidence. No iframe label/title attribute was present either.
- Other parent iframe declarations include a tag-manager fallback and map embed; details are recorded in [EMBEDS_AND_FORM_LABELS.json](EMBEDS_AND_FORM_LABELS.json) with credential-like query values redacted. Those resources were not explicitly selected or separately harvested.

See [prepared page](pages/1919308e975782c911a6d794.md) and [SOURCE_INDEX.json](SOURCE_INDEX.json) for raw/metadata hashes, save time and exact extraction/iframe locations. Navigation/footer output is separate in [BOILERPLATE.md](BOILERPLATE.md); no meaningful repeated navigation/footer text was found in this page snapshot.

## Agent interpretation — implications for JARVIS

- The consultation CTA handoff leads to an embedded booking service, rather than an inline WordPress form. Treat **parent destination** and **embedded booking experience** as separate content/functionality boundaries.
- The document title supports “digital growth strategy call” as an observed offering label. Exact service promise, cost, duration and required visitor inputs remain unknown. Ask for evidence rather than inventing them.
- If the architect requires the actual fields or booking offer, a separately authorized widget-specific capture or owner-provided form specification is needed. This follow-up does not itself approve another host/page or booking interaction.
- The existing parent-HTML collector preserves iframe declarations but not nested document bodies. The limitation is visible in this result; it is not a reason to repeat the same page automatically or reopen the legacy controller.

## Collection versus preparation/coverage

One planned collection call completed, exit 0, original stop reason null, no reported cleanup error. Prepare ran offline, exit 0. The parent result is hash-valid. **Useful preparation is partial for inner booking content:** only the title, iframe declaration/style and explicit absences are established.

`--gap 5` was retained. With one planned call there is no completion-to-next-call interval to measure. Ordinary page/frame resources were additional browser traffic. No links were clicked, inputs filled, forms submitted, booking attempted, REST collected or media harvested. Images/hidden content remain unverified; this is one follow-up, not independent QA certification.

## Baseline status

Per Tony's current instruction, JARVIS accepted Prepare v0.1 for Home, Agency Services and Andromeda. That baseline, its three captures and prepared output remain unchanged. This follow-up adds separately saved evidence and does not reissue a baseline assessment. See [GAPS_AND_REQUESTS.md](GAPS_AND_REQUESTS.md) for the precise remaining questions; no further requests are executed.
