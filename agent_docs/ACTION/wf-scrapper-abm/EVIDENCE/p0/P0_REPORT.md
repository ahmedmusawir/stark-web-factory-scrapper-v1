# wf-scrapper-abm — P0 REPORT (task zero)

**Seat:** Claudy (Engineer) · **Date:** 2026-09-18 · **Branch:** `wf-scrapper-abm` @ `9162873` "18sep2026 - ready for our first abm" (read-only confirmed) · **Authority:** R6 (REST probe), R7 (venv, regression, smoke)
**No code changes. No mutating git. No retries against the live site.**

## Verdict in one screen

| Part | Result |
|---|---|
| A. Environment | **DONE, with two findings.** Python 3.12.3 had to be built (`pyenv install 3.12.3`). `pip install -r requirements.txt` gave freeze **≠** lock (16 transitive drifts); `pip install -r requirements-lock.txt` (README's documented byte-for-byte path) gave freeze == lock, 98 lines. `pip check` clean. Chromium 1169 installed. |
| B. Regression | **PASS — 54 passed** in 9.26 s (48 + 3 + 3), on the locked environment. |
| C. Smoke | **NOT COMPLETED — blocked.** Discovery's single GET to `/sitemap.xml` returned **429**. No `discovered_pages.json`, so the `--limit 10` crawl had no input and was not started. No run folder exists; nothing to copy. Not retried. |
| D. REST probe | **PARTIAL.** `GET /wp-json/` → **200**. `GET /wp/v2/pages?per_page=1` → **429**. `GET /wp/v2/posts?per_page=1` → **429**. Exactly three GETs made, 3 s apart. No page/post object was obtained. |
| E. Compare vs Contracts §2.5 | **§2.5 field names are UNCONFIRMED** — the one open binding in the contracts is still open. Rate-limit behaviour observed here conflicts with the §1.4 pacing assumption for REST. Details in §E. |

**Headline for the Director:** the host rate-limited this machine during P0. Second request of the probe was already refused at 3 s spacing, and the refusal was still in force 12 minutes later for a different path (`/sitemap.xml`). Until a collection object is fetched, C4's precondition ("compare the P0 Part B probe output to Contracts §2.5") cannot be met. **P1 readback can still be written** — it does not need the network — but it would carry §2.5 as an open item. Decisions needed are listed at the end.

**Sequence disclosure:** I ran Part D *before* Part C (the prompt lists C then D), using the dead time while Python compiled. The first 429 occurred inside D itself (request 2), so the reorder did not cause it; but D's three requests came 12 minutes before the discovery GET and may have contributed to the penalty that blocked C. With the listed order, the smoke would have gone first.

---

## A. Environment (R7)

README §Setup followed on this clone. Commands and results, in order:

| # | Command | Result |
|---|---|---|
| 1 | `python -m venv venv` (first attempt) | **FAIL** — `pyenv: version '3.12.3' is not installed (set by .python-version)`. pyenv on this machine had only `system`, 3.12.11, 3.12.13. (The 3.12.3 I reported in the pre-ABM recon was `/usr/bin/python3`, the system interpreter — same version number, not a pyenv build.) |
| 2 | `pyenv install 3.12.3` (README line 1, "once, if missing") | exit 0, 2 m 53 s, installed to `~/.pyenv/versions/3.12.3` |
| 3 | `python -m venv venv` → `venv/bin/python --version` | `Python 3.12.3` |
| 4 | `venv/bin/pip install -r requirements.txt` | exit 0, 8 m 08 s |
| 5 | `venv/bin/pip freeze \| sort` vs `sort requirements-lock.txt` | **NOT EQUAL.** 98 vs 98 lines, **16 packages differ**, all transitive, all newer than the lock: anyio 4.15.0→4.15.1 · filelock 3.32.5→**4.0.0** · greenlet 3.5.5→3.5.6 · httpcore2 2.12.0→2.13.0 · httpx2 2.12.0→2.13.0 · huggingface_hub 1.30.0→1.32.0 · idna 3.19→3.20 · jiter 0.16.0→0.17.0 · multidict 6.7.1→6.9.0 · numpy 2.5.2→2.5.3 · openai 3.8.0→**3.15.0** · propcache 0.5.2→0.5.4 · regex 2026.9.3→2026.9.10 · tqdm 4.70.0→4.70.1 · urllib3 2.7.0→2.8.0 · yarl 1.24.5→1.25.1. All 7 top-level pins matched. Diff: `env/freeze_vs_lock_drift.diff`. |
| 6 | `venv/bin/pip install -r requirements-lock.txt` (README §Setup, "reproduce the environment byte-for-byte") | exit 0 |
| 7 | freeze sorted vs lock sorted, again | **EQUAL — diff empty, 98 lines.** `env/freeze_after_lock.sorted.txt` |
| 8 | `venv/bin/pip check` | `No broken requirements found.` exit 0 (also clean after step 4) |
| 9 | `venv/bin/playwright install --dry-run chromium` | names chromium **136.0.7103.25**, build **1169**, at `~/.cache/ms-playwright/chromium-1169`. Before install that directory did **not** exist (only `chromium-1234`, from another project). |
| 10 | `venv/bin/playwright install chromium` | exit 0, 31 s. `~/.cache/ms-playwright/` now has `chromium-1169`, `chromium_headless_shell-1169`, `ffmpeg-1011` (plus the pre-existing 1234 pair). |
| 11 | `cp .env.example .env` | done (gitignored; contains only the empty `GEMINI_API_KEY=` placeholder) |

Installed: crawl4ai 0.9.3 · playwright 1.52.0 · requests 2.32.3 · beautifulsoup4 4.13.4 · pytest 8.3.5 (venv). Global/system: requests 2.31.0 (used for D only).

**Finding A-1 (affects AC-001 as bound).** AC-001 says: install with `pip install -r requirements.txt`, then `pip freeze == requirements-lock.txt`. That check failed today on a clean clone, 13 days after the lock was cut, and will fail more over time — `requirements.txt` pins 7 top-level packages and leaves ~91 transitives floating. It is only satisfiable via the lock file. Proposed reading for P1 (erratum-eligible, not decided here): AC-001's install step becomes `venv/bin/pip install -r requirements-lock.txt`, README §Setup makes that the primary command. This needs no change to `requirements.txt` or the lock (both are do-not-touch).
**Finding A-2.** AC-001 quotes `pyenv local 3.12.3`; README's actual text is `pyenv install 3.12.3  # once, if missing` and relies on the tracked `.python-version`. Wording mismatch only; E1 docs task can align it.
**Finding A-3.** A clean machine needs a ~3 min Python source build and ~8 min pip install before anything runs. Worth a line in README for Cody's T-01.

## B. Regression

```
$ venv/bin/pytest -q
......................................................                   [100%]
54 passed in 9.26s
```
Exit 0. Collected per file: `tests/test_crawler.py` 48 · `tests/test_discover.py` 3 · `tests/test_sitemap_utils.py` 3. Matches the certified count (14 bim000 + 40 bim001). Run on the lock-exact environment (after step 7).

## C. Smoke — blocked at discovery

```
$ printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com      # 2026-09-18T14:27:19Z
[INFO] Checking sitemap at https://cyberizegroup.com/sitemap.xml
[WARNING] Failed to fetch sitemap: 429 Client Error: Too Many Requests for url: https://cyberizegroup.com/sitemap.xml
[WARNING] Sitemap unavailable or empty.
```
Exit **0** (certified behaviour: discovery never exits non-zero on a handled failure). One GET made. `outputs/` still holds only `.gitkeep`. The crawler command was **not run** — with no `outputs/discovered_pages.json` it would only print "File not found" and exit 1. Transcript: `smoke/discover.stdout.txt`, `smoke/discover.stderr.txt` (empty).

Expected "10/10 200" → **not observed; nothing attempted at the page level.** No `manifest.json` / `absences.json` / `stage_log.txt` exist to copy.

Why not retried: spec §0.3 ("a stop → report, no retry … without Director word"), Brief §7 ("report, don't force"), and the P0 approval covered one discovery + one smoke, not a polling loop against a host that is actively refusing us.

## D. REST probe (R6)

Client: system `/usr/bin/python3` 3.12.3, **`requests` 2.31.0** (pyenv-global = system). UA = `discover_site.sitemap_utils.USER_AGENT` (Chrome/140 Windows string). `timeout=30`, 3 s sleep between requests, no retries. Script kept beside the evidence: `rest_probe/rest_probe.py`; summary `rest_probe/probe_meta.json`.

| # | URL | At (UTC) | Status | Content-Type | Bytes | X-WP-Total | X-WP-TotalPages | Files |
|---|---|---|---|---|---:|---|---|---|
| 1 | `/wp-json/` | 14:14:58 | **200** | `application/json; charset=UTF-8` | 775,203 | n/a (root) | n/a | `root.body.json`, `root.headers.json` |
| 2 | `/wp-json/wp/v2/pages?per_page=1` | 14:15:04 | **429** | `text/html` | 1,168 | absent | absent | `pages.body.json`*, `pages.headers.json` |
| 3 | `/wp-json/wp/v2/posts?per_page=1` | 14:15:08 | **429** | `text/html` | 1,168 | absent | absent | `posts.body.json`*, `posts.headers.json` |

\* Named `.body.json` by the script before the status was known; the content is an **HTML** error page (`<title>429 Too Many Requests</title>`), identical bytes for both (sha256 `21200fdc…e121c0`). Not renamed — evidence as written.

No redirects on any request (`history: []`).

**429 response headers (both):** `Server: nginx` · `Content-Type: text/html` · `X-ac: 24.sin _atomic_bur MISS` · `Server-Timing: a8c-cdn, dc;desc=sin, cache;desc=MISS` · **no `Retry-After`** · no `X-RateLimit-*`. INFERENCE: `_atomic_bur` reads as the WP Cloud/Atomic edge *burst* limiter (Automattic CDN, Singapore PoP); the refusal is issued at the edge before WordPress runs (no `Host-Header: wpcloud`, no WP headers on the 429s, whereas the 200 has them).

### What the prompt asked me to report

| Item | Answer |
|---|---|
| Status codes | 200, 429, 429 |
| Namespaces list | 36: `oembed/1.0, akismet/v1, jetpack/v4, indexnow/v_1.0.4, jetpack-boost-ds, jetpack-boost/v1, my-jetpack/v1, jetpack/v4/explat, redirection/v1, simple-page-ordering/v1, tvo/v1, thrive-product-manager/v1, tcb/v1, yoast/v1, wpcom/v2, jetpack/v4/stats-app, cyberize/v1, ttb/v1, jetpack/v4/blaze-app, jetpack/v4/blaze, td/v1, tss/v1, trd/v1, td-metrics/v1, thrivethemes/v1, tve-dash/v1, theme/v1, jetpack/v4/import, videopress/v1, jetpack/v4/videopress, wpcom/v3, mcp, wp/v2, wp-site-health/v1, wp-block-editor/v1, wp-abilities/v1` |
| `X-WP-Total` / `X-WP-TotalPages` | **Not obtained** (429s carry neither). Root's `Access-Control-Expose-Headers` names both, so WordPress will send them on a served collection. |
| `yoast_head_json` present? | **UNKNOWN** — no object fetched. `yoast/v1` namespace is registered (Yoast is active), which is consistent with, but does not prove, the field. |
| `yoast_head` present? | **UNKNOWN** |
| Top-level keys of one page object | **UNKNOWN** |
| `content.rendered` empty on sampled objects? | **UNKNOWN** |
| Keys `id,type,link,slug,status,date,modified,title,excerpt,content,author,featured_media,categories,tags` exist? | **UNKNOWN** for all 14 |

### What the root document does establish (EVIDENCE, `root.body.json`)

- Root top-level keys: `name, description, url, home, gmt_offset, timezone_string, page_for_posts, page_on_front, show_on_front, namespaces, authentication, routes, site_logo, site_icon, site_icon_url, _links`.
- `name: "Cyberize Group"`, `url`/`home`: `https://cyberizegroup.com` (apex, no `www`) — agrees with `hosts_allowed` binding.
- 924 routes registered. All six bound collection routes exist: `/wp/v2/pages, posts, media, categories, tags, users`.
- `per_page`: default 10, min 1, **max 100** on pages/posts/media/users → §2.4 `per_page: 100` is valid.
- Default `status` filter: `publish` (pages, posts), `inherit` (media) → unauthenticated reads get published content only.
- `show_on_front: page`, `page_on_front: 8245`, `page_for_posts: 79` → the homepage is REST page id 8245 and `/blog/` is page 79 (useful for C4 mapping tests later).
- `site_icon_url: …/wp-content/uploads/2022/12/cyberize-group-favicon.png`; `site_logo: 0`.
- Thrive namespaces present (`tcb/v1`, `tvo/v1`, `ttb/v1`, `thrivethemes/v1`, …) plus Thrive post types under `wp/v2` (`tcb_symbol`, `thrive_template`, `tve_saved_lp`, …) → supports the AC-014 Thrive Architect premise.
- Other `wp/v2` collections exist that the ABM does not bind: `comments, menus, menu-items, navigation, jetpack-forms, feedback, templates, types, taxonomies, search`, etc. Observation only.
- Response headers: `X-Robots-Tag: noindex`, `Allow: GET`, `Host-Header: wpcloud`, gzip.
- Authentication block advertises application-passwords only; nothing was sent.

## E. Compare D against `ABM_CONTRACTS.md` §2.5 (and what D touches elsewhere)

Labels: **MISMATCH** = evidence contradicts the contract · **UNCONFIRMED** = contract may be right, evidence missing · **GAP** = contract silent on something the evidence shows · **OK** = confirmed.

| # | Contract point | Evidence | Label |
|---|---|---|---|
| E-1 | §2.5 fields relied on: `id, type, link, slug, status, date, modified, title.rendered, excerpt.rendered, content.rendered, author, featured_media, categories, tags` | No object fetched | **UNCONFIRMED** (all 14). Note from WP core, not from this probe: `categories`/`tags` exist on posts only, not pages; `excerpt` and `author` on pages depend on post-type supports. Needs a real page object to settle. |
| E-2 | §2.5 `yoast_head_json` (object) and `yoast_head` (string); Yoast sub-keys `title, description, robots, canonical, og_*, twitter_*, schema, article_*` | No object fetched; `yoast/v1` namespace registered | **UNCONFIRMED** |
| E-3 | Contracts header: "REST open, unauthenticated … confirmed by the P0 Part B probe" | Root open (200). Collections refused at the edge (429), not by WordPress auth | **UNCONFIRMED** — "open" is true of WordPress, not yet of the path to it |
| E-4 | §1.4 pause `uniform(2.0, 5.0)` s "between every network request in every stream", REST included | Request 2 arrived **6 s** after request 1 started (2.8 s download + 3 s sleep) and was refused; request 3, 4 s later, refused; a request to a different path **12 min** later, refused | **MISMATCH (pacing assumption).** A 3 s gap sits inside the bound 2–5 s range and was not enough for a plain-`requests` client on this host today. bim000/bim001 proved 2–5 s works for the *browser* stream (10/10 twice); nothing has proved it for `requests`. Either the REST stream needs its own pause range, or the limiter treats a non-browser client differently (TLS/HTTP fingerprint vs a Chrome UA string) — this probe cannot tell which. |
| E-5 | §1.4 stop rule: "3 consecutive `blocked` on any stream stops the run, exit 2" | 2 consecutive 429s on the first two collection requests | **RISK, not mismatch.** As bound, a REST stream that behaves like today trips the stop rule on its third request and ends the whole pipeline with exit 2 — after a fully successful HTML crawl if REST runs second. P1 should ask whether a stream-level stop (REST → `streams.rest: failed`, run continues) is intended. |
| E-6 | §1.4 "never retry 4xx"; no mention of `Retry-After` | 429 carried no `Retry-After` | **OK / GAP.** Nothing to honour today; contract is silent on honouring it if it appears. |
| E-7 | §2.2.1 `block_file` saves a blocked body as evidence — defined for the html stream only | REST 429 body is an HTML page, 1,168 B | **GAP.** No slot for a blocked REST response body. Also: the REST client must not assume a JSON body on non-200 (it is `text/html`). |
| E-8 | §2.4 `root_file: objects/root.json`, `namespaces`, `per_page: 100` | root 200, 775 KB, namespaces list present, max 100 | **OK** |
| E-9 | §2.4 collections `pages, posts, media, categories, tags`; `users` attempted once | all six routes registered | **OK** (existence only; public-ness of `users` unknown) |
| E-10 | §1.4 `hosts_allowed: [cyberizegroup.com, www.cyberizegroup.com]` | `url`/`home` = apex https | **OK** |
| E-11 | §2.3 sitemap fallback: "First that returns XML wins; the rest are not fetched" | `/sitemap.xml` → 429 today | **GAP / ambiguity.** Read literally, a 429 on candidate 1 falls through to `/sitemap_index.xml` then `/wp-sitemap.xml` — three more requests at a host that is refusing us. Proposed reading for P1: 403/429 on any discovery request is `blocked`, ends the fallback chain, counts toward the stop rule. |
| E-12 | §2.6 media sources list | Root exposes `site_icon_url` | **GAP (minor).** Site icon from REST root is not a listed source; `<link rel=icon>` in HTML probably covers the same URL. Observation only. |

**No §2.5 field name was shown wrong. None was shown right either.** Per the build instructions (C4 "Before coding…") and Contracts header, this stays open until a collection object is on disk.

---

## Decisions needed from the Director

1. **Re-probe.** Approve a second attempt at the two collection GETs (and with it the smoke) after a cool-down — suggest next session or ≥ 1 h, requests ≥ 10 s apart, stop at the first 429. I will not touch the host again without your word.
2. **Order next time:** smoke first (browser stream, proven posture), REST GETs last — so a REST refusal cannot poison the smoke.
3. **E-4 / E-5 / E-11 to the Architect** as erratum candidates before C4 (REST pacing, stream-level vs run-level stop, 429 during sitemap fallback). I have proposed readings above; none is applied.
4. **A-1 to the Architect:** AC-001's freeze == lock check is only satisfiable by installing from `requirements-lock.txt`.
5. **P1 readback:** can proceed now with §2.5 carried as an open item, or wait for the re-probe. Your call.

## State left on disk

- Created (untracked, inside the already-untracked module folder): `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/p0/` — this report, `env/` (3 files), `rest_probe/` (8 files), `smoke/` (2 files).
- Created, gitignored: `venv/`, `.env`. Outside the repo: `~/.pyenv/versions/3.12.3`, `~/.cache/ms-playwright/{chromium-1169, chromium_headless_shell-1169}`.
- Modified: `agent_docs/SESSIONS/session_2026-09-18.md`, `RECOVERY.md`.
- `outputs/`: unchanged (`.gitkeep` only). Product code, tests, `requirements*.txt`, contract files: untouched.
- Live requests made in P0, total **4**: three REST GETs + one sitemap GET. Live-run budget used: none (no crawl ran).
