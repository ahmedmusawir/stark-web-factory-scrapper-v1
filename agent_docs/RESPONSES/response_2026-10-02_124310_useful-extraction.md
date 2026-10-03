# Useful extraction — DONE

**Cody / Engineer · JARVIS / Architect · Tony / Director**

**Blog extraction: SUCCESS. REST extraction: PARTIAL — one real post’s metadata returned, but its rendered content is empty.** No refusal/challenge was observed, and no retry or alternate route was used.

## 1. Blog: useful content verified

The existing `smart_crawler.crawler.crawl_page` completed successfully for `https://cyberizegroup.com/blog/`, independently of discovery.

| Evidence | Result |
|---|---|
| Main-document status | HTTP 200 |
| Title | Digital Marketing Blog by Cyberize Group |
| Saved HTML | **600,962 bytes** |
| Saved Markdown | **15,380 characters / 15,394 UTF-8 bytes** |
| Article verification | **Nine distinct article headings and links found in both HTML and Markdown** |

Examples, with tracking query parameters omitted here:

- **How to Regain Consistency with Facebook Ads After the Andromeda Update** — `https://cyberizegroup.com/facebook-ads-andromeda-update/`
- **Garage Door Repair PPC Agency – Get More Leads & Sales Now!** — `https://cyberizegroup.com/garage-door-repair-ppc-agency-get-more-leads-sales-now/`
- **Boost Your Dental Practice with a Professional SEO Company** — `https://cyberizegroup.com/boost-your-dental-practice-with-a-professional-seo-company/`

Verification required linked HTML headings, excluding navigation/category/pagination links, with matching heading text and URL in saved Markdown. All nine are recorded in `article-verification.json`. No article links were followed. The final observed URL retained `/blog/` with tracking query parameters; no main-document redirect was observed.

## 2. REST: metadata obtained; post body missing in substance

After successful article verification, the wrapper waited **5.000596 seconds**, then made exactly one targeted read:

`GET https://cyberizegroup.com/wp-json/wp/v2/posts?per_page=1&_fields=id,link,title,content`

**Transport:** JavaScript `window.fetch`, invoked through `page.evaluate` in the **same Chromium page and BrowserContext** used by `crawl_page`. This was not requests, curl or a separate Python HTTP client. Fetch used `redirect: 'error'`, a 30-second timeout and no retry.

| Response check | Result |
|---|---|
| Status / type / body size | **200 / application/json / 222 bytes** |
| Collection | One record; **not an empty collection** |
| ID | **11945**, positive integer |
| Link | `https://cyberizegroup.com/facebook-ads-andromeda-update/` |
| Title | How to Regain Consistency with Facebook Ads After the Andromeda Update |
| Content | `content.rendered` is a string equal to **`""`**: zero characters before and after stripping markup |
| Missing / null requested fields | None / none |

The REST title/link match an article extracted from the blog. Thus post identity and metadata are corroborated, but **useful REST post-body extraction did not succeed**. The helper’s `failed_validation_or_stopped` label means failed content validation here: its stop state is null. The reason for empty content remains unknown; this one record cannot establish site-wide REST behavior.

## 3. Execution and boundaries

Run: **2026-10-02 06:41:39–06:41:56 UTC**; supervised process duration **18.63 seconds**. Observed **135 browser request events and 133 responses**, including normal background traffic. Ten background POSTs were allowed: five fetches, four XHRs and one ping. No clicking, filling or form-submission action was performed. No refusals, detected challenges or diagnostic request aborts occurred.

The blanket non-GET/HEAD shutdown was removed in a **new wrapper**. Existing capture settings remained unchanged: headless Chromium, project USER_AGENT, bypass cache, image wait, 90-second page timeout and three-second delay. Runtime: Python **3.12.3**, Crawl4AI **0.9.3**, Playwright **1.52.0**, actual Chromium **136.0.7103.25**. Request instrumentation remains a difference from an uninstrumented run; routing can affect browser HTTP caching.

One blog navigation and one targeted REST read occurred. No discovery, `/wp-json/` enumeration, pagination, explicit media fetching or alternate route was attempted. Browser-loaded subresources are included in the event counts. This does not establish a root cause for earlier failures or full-crawl readiness.

## 4. Evidence and preservation

Evidence directory: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/browser-check/2026-10-02_063951Z/`.

**Local payloads:** `returned.html`, `returned.md`, `rest-response.body`. **Shared proof:** wrapper, article verification, page/REST results, actual configuration, sanitized browser events, supervisor and preservation records. Captured payloads, raw framework logs, runtime profiles/caches, cookies and credentials are excluded from the ZIP.

Branch remains `wf-scrapper-abm`; HEAD remains `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f`. All **1,086 hashed pre-existing files** retained their bytes. Only this new evidence directory, this report and its sibling ZIP were added. No product edits, dependency changes, Git mutations or deployment occurred.

**Next decision:** JARVIS can use the demonstrated blog extraction. The empty REST content needs separate investigation if full post bodies are required. No further requests were made.
