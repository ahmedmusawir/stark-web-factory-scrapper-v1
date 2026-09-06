# RUN ANALYSIS — baseline-run-002 — cyberizegroup.com — 2026-09-05

> Claudy, Engineer seat, Stark Web Factory Phase 1. Tony's brief 2026-09-05 (Parts A/B/C). Plan approved 09:4x, option (b): exact `smart_crawler.crawler` module, unchanged, driven through a status-observer wrapper living in the session scratchpad (outside the repo). No source edits. No installs. No git.
> Every line labeled **EVIDENCE** (observed on disk / in logs, cited) · **INFERENCE** (conclusion from evidence, basis stated) · **GAP** (expected, not found / not obtainable from this run).
> Companion: Part A request-behavior audit is in `agent_docs/RESPONSES/response_2026-09-05_094224_baseline-run-002-plan.md` and summarized in §0 below.
> Raw logs (scratchpad, not in repo): `discover.log`, `crawl.log`, `final10.txt`, `crawl_observer.py`.

---

## 0 — Request behavior recap (Part A, read-only)

- EVIDENCE — Crawler: sequential, one page at a time, no inter-request delay, 3 s forced post-load wait + wait-for-images, 90 s page timeout, no retry, cache bypassed. `smart_crawler/crawler.py:48-53, 164-166`.
- EVIDENCE — Crawler presents as headless: `headless=True` → `--headless=new`; truncated UA `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36` (no Chrome/Safari token) → crawl4ai emits an empty `sec-ch-ua`; no stealth, `navigator.webdriver` unpatched. `crawler.py:155-156`; crawl4ai `browser_manager.py:378, 744-750, 766-773`.
- EVIDENCE — crawl4ai's Playwright strategy never marks a 4xx/5xx as failure; `crawler.py:65-71` prints status only on failure → a soft 403/429 would be saved as a "successful" .md. This is why option (b) was needed to honor rule B.4.
- EVIDENCE — Discovery: plain `requests.get`, UA `python-requests/2.32.3`, 10 s timeout, no delay, no retry; sitemap-index children fetched back-to-back. `discover_site/sitemap_utils.py:10, 24-34`.
- INFERENCE — Burst: discovery is a 4-request burst in ~1 s; the crawler does not burst (≈1 page / 6-7 s) but has zero jitter. Basis: code above + timings in §2.

## 1 — Commands, timestamps, wall time (Part B)

| Step | Command (from repo root) | Start | End | Wall | Exit |
|---|---|---|---|---|---|
| B.1 Discover | `printf '1\n' \| venv/bin/python -m discover_site.discover https://cyberizegroup.com` | 2026-09-05 10:15:31 +06 | 10:15:40 | **8.2 s** | 0 |
| B.2 Trim | `venv/bin/python -c "import json;d=json.load(open('outputs/discovered_pages.json'))[:10];json.dump(d,open('outputs/discovered_pages_final.json','w'),indent=2)"` | 10:15:58 | 10:15:58 | <1 s | 0 |
| B.3 Crawl (attempt 1) | `printf 'y\n' \| venv/bin/python <scratchpad>/crawl_observer.py` | 10:15:58 | 10:15:59 | 0.9 s | 1 — `ModuleNotFoundError: No module named 'smart_crawler'`. **My wrapper's fault** (script dir, not repo root, on `sys.path`). Zero network requests made. Fixed by inserting CWD into `sys.path` inside the wrapper. |
| B.3 Crawl (attempt 2) | same | **10:16:19** | **10:17:31** | **72.1 s** | 0 |

- EVIDENCE — Discovery: sitemap index at `/sitemap.xml` → 3 children (`post-sitemap.xml`, `page-sitemap.xml`, `category-sitemap.xml`) → **194 URLs** written to `outputs/discovered_pages.json`. `discover.log`. Identical count to the 2026-09-02 run (RUN_NOTES §3).
- EVIDENCE — Discovery made **4 HTTP GETs** total (index + 3 children) in 8.2 s wall (includes Python startup and the interactive prompt). `discover.log`; `sitemap_utils.py:10,28`.
- EVIDENCE — All 194 discovered URLs are single-segment paths (`/slug/`); 0 contain `/category/`; the root `https://cyberizegroup.com/` is present. Computed from `discovered_pages.json`.
- GAP — Per-child-sitemap counts (how many of the 194 are posts vs pages vs categories) are not recoverable from this run: `sitemap_utils.py` flattens all children into one list. INFERENCE — the "category" sitemap yields URLs shaped like `/slug/` on this site (no `/category/` prefix), so category archive pages are indistinguishable from posts/pages in `discovered_pages.json`.
- EVIDENCE — First 10 URLs (sitemap order, `final10.txt`): `/blog/`, `/web-design-process/`, `/what-to-look-for-in-ppc-agency/`, `/our-covid-19-plan/`, `/5-foundational-principles-for-online-success/`, `/5-mistakes-real-estate-agents-make/`, `/covid-19-safety-tips-for-the-2020-pandemic/`, `/on-page-seo-audit/`, `/what-to-expect-from-a-ppc-agency/`, `/ppc-agency-checklist/`.
- EVIDENCE — **Pages attempted: 10. Succeeded: 10. Failed: 0.** `crawl.log` summary lines "✅ Successful: 10 / ❌ Failed: 0 / Success rate: 100.0%".
- EVIDENCE — Per-page elapsed (observer, wall around `arun`): 10.1 s (first page, includes browser warm-up), then 6.7 / 6.6 / 6.3 / 6.6 / 7.2 / 6.5 / 6.5 / 6.7 / 6.6 s. Mean of pages 2-10: **6.6 s**. `crawl.log` `[OBSERVER]` lines.
- INFERENCE — Of each ~6.6 s, 3.0 s is the fixed `delay_before_return_html`; the remainder is navigation + `wait_for_images` (which timed out on every page, see §3). Basis: `crawler.py:51-52` + the 10 "images failed to load within timeout" log lines.
- EVIDENCE — The first 5 URLs are the same 5 crawled on 2026-09-02; their `.md` files were **overwritten** (mtimes now 10:16:31-10:16:57). Sizes moved by a few bytes (e.g. blog 12,283 → 12,285; web-design-process 14,284 → 14,287; our-covid-19-plan 7,537 → 7,536). INFERENCE — byte drift is dynamic content (tracking pixel params / timestamps), not layout change. Pre-run `ls -la` vs post-run `stat`; RUN_NOTES §4 table.

## 2 — Status codes, retries, fallbacks

- EVIDENCE — **Every crawled page returned HTTP 200.** 10 × `[OBSERVER] status=200 success=True`. `crawl.log`.
- EVIDENCE — **No 403, no 429** anywhere in `discover.log` or `crawl.log` (`grep -E '\b(403|429)\b'` → 0 hits). Rule B.4 never triggered; run completed.
- EVIDENCE — Discovery: no HTTP errors printed (all 4 GETs succeeded; `raise_for_status()` did not fire). `discover.log`. GAP — discovery's `requests` calls do not surface status codes on success; "no error" is the only signal. INFERENCE — all four were 2xx (they returned parseable XML).
- EVIDENCE — **Retries: none** occurred and none are possible in this code path (no retry logic in `crawler.py`; crawl4ai's RateLimiter lives only in `arun_many`). `crawler.py:55-59`; crawl4ai `async_webcrawler.py:710-713`.
- EVIDENCE — **Fallback fired on 10 of 10 pages:** `fit_markdown` was empty on every page (`fit_md=0` in all observer lines; crawler printed "⚠️ fit_markdown empty, using raw_markdown" 10 times). Output is therefore `raw_markdown` for all 10 files. Reproduces the 2026-09-02 finding exactly.
- EVIDENCE — Per-page warning `[SCRAPE].. ◆ Some images failed to load within timeout` appeared **10 of 10** times. Non-fatal. INFERENCE — `wait_for_images=True` waits for lazy-loaded / third-party images (Jetpack pixel, staging-domain uploads, see §3) that never resolve within crawl4ai's internal image wait; it costs time and gains nothing here.
- EVIDENCE — crawl4ai's own `[FETCH]/[SCRAPE]/[COMPLETE]` lines showed a blank URL column on 2 of 10 pages (pages 5 and 7) while the observer line for the same page carried the full URL and status 200. INFERENCE — a display truncation quirk in crawl4ai's fixed-width logger for long URLs, not a fetch anomaly (both pages saved normally, 18,893 and 6,208 bytes).

## 3 — What the output files actually contain

**Format**
- EVIDENCE — All 10 files are **Markdown, not HTML.** Grep for `<html`, `<div`, `<script`, `<img` → 0 lines in every file. Markdown structure present in every file: headings (5-21 per file), `[text](url)` links (56-108 per file), list bullets (18-33 per file). `outputs/pages/*.md`.
- EVIDENCE — It is crawl4ai's **`raw_markdown`** (full-page conversion, §2), so each file = header nav + share buttons + article + sidebar CTAs + footer + subscribe modal, top to bottom.
- EVIDENCE — No file contains raw HTML and no file mixes formats.

**Inventory**

| File (`outputs/pages/`) | Bytes | Lines | First `#`/`##` heading at line | Boilerplate share* |
|---|---|---|---|---|
| cyberizegroup-com-blog.md | 12,285 | 116 | 15 | 10% |
| cyberizegroup-com-web-design-process.md | 14,287 | 140 | 23 | 23% |
| cyberizegroup-com-what-to-look-for-in-ppc-agency.md | 26,531 | 220 | 23 | 12% |
| cyberizegroup-com-our-covid-19-plan.md | 7,536 | 92 | 23 | 44% |
| cyberizegroup-com-5-foundational-principles-for-online-success.md | 18,893 | 192 | 39 | 18% |
| cyberizegroup-com-5-mistakes-real-estate-agents-make.md | 24,875 | 198 | 23 | 13% |
| cyberizegroup-com-covid-19-safety-tips-for-the-2020-pandemic.md | 6,208 | 83 | **none** | **53%** |
| cyberizegroup-com-on-page-seo-audit.md | 26,537 | 176 | 23 | 12% |
| cyberizegroup-com-what-to-expect-from-a-ppc-agency.md | 24,578 | 180 | 13% |
| cyberizegroup-com-ppc-agency-checklist.md | 29,382 | 199 | 23 | 11% |

\* EVIDENCE — "Boilerplate share" = bytes of lines that appear verbatim in ≥8 of the 10 files ÷ file bytes. 62 such shared lines exist (nav menu, footer, subscribe modal, social links, CTA blocks). Computed over `outputs/pages/*.md`. INFERENCE — the true non-article share is higher than this metric, because sidebar CTAs vary slightly per page (different `utm_source`, different images) and so escape the ≥8-file test; the "article starts at line 23" pattern across 8 files means ~22 lines of nav/share-buttons precede every article.

**Empty / thin content**
- EVIDENCE — **No file is empty** (min 6,208 bytes; 0 files under 500 bytes). No page tripped `crawler.py`'s own `< 500 chars` warning.
- EVIDENCE — **One page is content-thin:** `covid-19-safety-tips-for-the-2020-pandemic.md` has no `#`/`##` heading at all, 0 lines over 200 chars, and its article region (lines 22-23) is one sentence + one infographic image link; everything else in the file is nav, share buttons, sidebar CTAs (`#### New Course Reveals…`, `#### Get a Virtual Assistant…`, etc.), footer. 53% of its bytes are verbatim shared boilerplate. INFERENCE — the source post is an image-only infographic post; the crawl is faithful, the page just has almost no text.
- EVIDENCE — `our-covid-19-plan.md` (7,536 bytes, 44% boilerplate) is the second-thinnest; it does have a heading at line 23 and body text.
- EVIDENCE — `blog.md` is the blog index page, not an article: 108 links (most of any file), heading at line 15. INFERENCE — it is a listing of post teasers; useful as a link map, not as content.

**Noise inside the markdown**
- EVIDENCE — **206 of 667 links (31%) carry the site's own tracking query `?cat_source=direct&cat_medium=%28none%29`**, appended to nearly every internal nav link. `grep -o 'cat_source=direct' *.md | wc -l`.
- EVIDENCE — **87 `javascript:void(0)` pseudo-links** (share buttons "Share0 / Tweet0", modal close "x", "no, thanks."). Pure junk for downstream analysis.
- EVIDENCE — **Staging-domain leak:** 83 image URLs across all 10 files point to `https://cyberizegroup.mystagingwebsite.com/wp-content/uploads/…` while only 35 point to the live `https://cyberizegroup.com/wp-content/uploads/…`. INFERENCE — the site was migrated from a Pressable/WP.com-hosted staging environment and media URLs were never rewritten; this is a real defect on the client's live site, surfaced incidentally by the crawl. Worth flagging to whoever owns the client relationship; not our bug.
- EVIDENCE — Every file ends with the Jetpack stats pixel `![](https://pixel.wp.com/g.gif?…&post=<ID>…)`, which **leaks the WordPress post ID** of each page: blog=79, web-design-process=4952, what-to-look-for-in-ppc-agency=9134, our-covid-19-plan=6896, 5-foundational-principles=8740, 5-mistakes-real-estate=5086, covid-19-safety-tips=6865, on-page-seo-audit=9110, what-to-expect-from-a-ppc-agency=9127, ppc-agency-checklist=9055.
- EVIDENCE — `wp-content/uploads` appears in all 10 files (118 hits) → the site is **WordPress**; sitemap child names (`post-sitemap.xml`, `page-sitemap.xml`, `category-sitemap.xml`) are the **Yoast SEO** naming convention. INFERENCE — WordPress + Yoast + Jetpack, hosted on/migrated from Pressable (`mystagingwebsite.com` is Pressable's staging domain).

**Metadata the markdown does NOT carry**
- GAP — **No publish date** on any page: grep for `Month DD, YYYY` patterns → 0 hits; no "Posted on / Published" strings. The only years present are inside upload paths (`/2020/12/`, `/2023/04/`) — INFERENCE: upload-month, a weak proxy for publish date at best.
- GAP — **No author** ("by …", "author") on any page.
- GAP — **No categories/tags** rendered in the article region.
- GAP — **No post type** (post vs page vs category archive) — the URL shape is identical for all.
- GAP — **No canonical excerpt / SEO title / meta description** — raw_markdown drops `<head>`.
- GAP — **No modified date, no featured-image designation, no comment count.**

## 4 — What the WP REST API would give us that this run did not (NOT called — desk note only)

- INFERENCE (basis: WordPress + Yoast + Jetpack evidence in §3; WP core REST API is enabled by default since WP 4.7) — `GET /wp-json/wp/v2/posts?per_page=100&page=N` and `/wp-json/wp/v2/pages` would return, per item, in JSON, with **zero browser**: `id` (the same post IDs the Jetpack pixel leaked), `date`, `modified`, `slug`, `link`, `title.rendered`, `excerpt.rendered`, `content.rendered` (**article body only, no nav/sidebar/footer**), `author` (id → `/wp/v2/users/{id}` for name), `categories[]`, `tags[]`, `featured_media` (→ `/wp/v2/media/{id}` for URL/alt), `type`, `status`, `yoast_head_json` (if Yoast exposes it: SEO title, meta description, canonical, OG tags).
- INFERENCE — That closes **every GAP in §3**: dates, author, categories/tags, post-vs-page, excerpt, SEO metadata, featured image — and it eliminates the boilerplate problem outright because `content.rendered` is the article only.
- INFERENCE — Cost profile: ~2 paginated JSON requests per 100 posts vs 1 headless-browser page load (~6.6 s) per post. For 194 URLs: ~4-6 lightweight GETs vs ~21 min of browser time. It would also give `/wp/v2/categories` and `/wp/v2/tags` as first-class lists, resolving the "which of the 194 are category archives" GAP in §1.
- GAP — Whether cyberizegroup.com actually exposes `/wp-json/` (hosts and security plugins sometimes disable or auth-gate it), whether `yoast_head_json` is present, and whether `content.rendered` includes shortcode-expanded HTML: **unknown until called. Not called in this run per the brief.**
- INFERENCE — What REST would **not** give: the rendered sidebar CTAs, the nav structure, the exact rendered HTML a visitor sees, and JS-injected content — the things a headless crawl captures. The two are complementary, not substitutes: REST for content + metadata, crawl for "what does the page look like".

## 5 — Summary line

- EVIDENCE — 10/10 pages, all HTTP 200, 72.1 s wall, no 403/429, no retries, no failures, no empty files.
- EVIDENCE — Output is Markdown (raw_markdown) for all 10; `fit_markdown` empty on all 10; every file carries full-page nav/sidebar/footer boilerplate (10-53% verbatim-shared bytes) plus 206 tracking-param links, 87 `javascript:void` pseudo-links, and 83 staging-domain image URLs.
- GAP — No dates, authors, categories, post types, excerpts or SEO metadata in any output. The WP REST API (not called) is the documented source for all of them.

---

🛑 Run analysis complete. Source unchanged. Writes: this report, `outputs/*` run artifacts (gitignored), session log, RECOVERY.md. No git.
