# wf-scrapper-abm — RECOVERY REPORT

**Result: BLOCKED / UNRESOLVED.** REST/SEO acquisition is **not** complete. No acceptance criterion changed. Branch `wf-scrapper-abm` @ `9c20bc4`, read-only git only.

## 1. Attempted and changed

- **Product code, tests, requirements, contract files: no change.** (The pacing override in Step 3.4 was conditional on Steps 3.1–3.3 succeeding; they did not, so it was not made.)
- Created, all under `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recovery/`:
  - `RECOVERY_LOG.md` — start time, every live request (UTC, URL, status, key headers, bytes).
  - `paced_get.py` — `requests.Session` + project `USER_AGENT`, timeout 30, one request in flight, ≥15 s after the previous response **completes**, `Retry-After` (seconds or HTTP-date), first-429 → pause all → one retry of the same URL, second 429 → sticky hard stop, later 429 → stop with no second cooldown, wait beyond deadline → stop. Saves `<name>.body` / `.headers.json` / `.meta.json` for every response. `allow_redirects=False` so no request leaves unpaced.
  - `test_paced_get_local.py` — offline proof against `127.0.0.1` `http.server`: **T1** gap enforced + bytes saved · **T2** `Retry-After: 2` honored (2.00 s), one retry → 200, later 429 → stop, stop is sticky (no request leaves) · **T3** 429 without `Retry-After` → cooldown → one retry → BLOCKED · **T4** `Retry-After` beyond budget → immediate stop. **ALL PASS** before any live request.
  - `live_step3.py` — the Step 3 driver (sitemap → `page-sitemap.xml` only → pages → posts).
  - `live/` — 6 files, the two responses below.

## 2. Live requests (2 total — nothing passed)

| # | UTC | URL | Status | Bytes | Key headers |
|---|---|---|---|---:|---|
| 1 | 2026-09-19T07:03:58Z | `https://cyberizegroup.com/sitemap.xml` | **429** | 1,168 | `Content-Type: text/html` · `X-ac: 24.sin _atomic_bur MISS` · `Server: nginx` · **no `Retry-After`** |
| — | 07:03:58 → 07:08:58 | all requests paused 300 s (policy default, no `Retry-After`) | | | |
| 2 | 2026-09-19T07:08:58Z | same URL, the one allowed retry | **429** | 1,168 | identical |

Policy outcome: retry also 429 → **stop live work, BLOCKED.** No fallback sitemap URLs, no REST requests, no browser, no bypass. Request #1 was this machine's first contact with the host in **≈16 h 36 min** (previous: 2026-09-18T14:27Z).

Body is byte-identical to yesterday's three 429s (sha256 `21200fdc…`): *"You have been rate-limited for making too many requests in a short time frame. Website owner? … please contact support."*

## 3. Obtained or not

| Item | Obtained |
|---|---|
| Sitemap index / `page-sitemap.xml` | **No** |
| Page object | **No** |
| Post object | **No** |
| Browser smoke | **Not run** (precondition failed; also barred after a 429) |

## 4. Contracts §2.5 comparison

**Still unconfirmed.** All 14 relied-on keys, `yoast_head_json`, `yoast_head`, `content.rendered` emptiness, `X-WP-Total` / `X-WP-TotalPages`: no evidence either way. C4's precondition remains unmet.

## 5. Step 1 research (≤10 min, no live traffic)

**a. Pressable KB "Understanding 429 errors".** EVIDENCE from the page: two causes — (1) request rate limiting when a source sends "more than two requests per second", source identified by "several signals", not IP alone; (2) resource exhaustion (PHP-worker saturation beyond plan + burst), which appears as **599** in server logs while the browser sees 429. Remedy stated: ≤2 req/s (≥0.5 s apart). Block duration, `Retry-After`, and edge headers: **not stated**.

Reading our clues against it — all **INFERENCE**:

| Clue | Points toward |
|---|---|
| Body text says "rate-limited for making too many requests in a short time frame"; refusal issued at the edge (`X-ac … _atomic_bur`, no `Host-Header: wpcloud`, no WP headers) | cause 1 (rate limiting), as the edge *labels* it |
| We have never exceeded 2 req/s: yesterday 3 requests over 10 s; today 1 request after 16.6 h of silence | **against** cause 1 as the KB describes it — our own rate cannot have tripped a >2 req/s rule today |
| Penalty on a different path 12 min later yesterday, and on first contact today | a persisting state keyed to the source identity or to the site, not to a path or a momentary burst |
| Yesterday's only 200 was a 775 KB uncached (`MISS`, 1.8 s origin time) root listing 924 routes; the refusals began on the next request | compatible with cause 2 (expensive uncached PHP work) — weakly; one data point |
| "Several signals": Chrome UA string sent by python-`requests` (non-browser TLS/HTTP fingerprint) | possible identity mismatch flag — cannot be tested without traffic; **not** tested, and no alternative client was tried |
| Same PoP/limiter tag both days (`24.sin _atomic_bur`) | same edge rule both days |

**What cannot be told from here:** whether the block is on this source only or the site is 429ing for everyone (resource exhaustion / 599 in the logs). Only the site owner's Pressable logs, or a request from another network, can separate those — the second is outside this mission's policy. **I do not claim 3 s spacing caused yesterday's 429, and today shows 15 s pacing was never even exercised** — the first request was refused.

**b. crawl4ai 0.9.3 in the venv** (`venv/lib/python3.12/site-packages/crawl4ai/`):
- `RateLimiter` exists — `async_dispatcher.py:28-39`: `base_delay=(1.0, 3.0)`, `max_delay=60.0`, `max_retries=3`, `rate_limit_codes` default `[429, 503]`. Per-domain state; `wait_if_needed` `:45-63`; `update_delay` `:65-85` doubles the delay ×(0.75–1.25) on a limit code up to `max_delay`, decays ×0.75 on success, returns `False` once `fail_count > max_retries`.
- Dispatchers: `MemoryAdaptiveDispatcher` `:148`, `SemaphoreDispatcher` `:639`; both `max_session_permit=20` by default (`:155`, `:643`).
- `arun_many` `async_webcrawler.py:974`; with no dispatcher it builds `MemoryAdaptiveDispatcher(max_session_permit=semaphore_count or 10, RateLimiter(base_delay=(0.1, 0.4), max_delay=60, max_retries=3))` `:1055-1066` — i.e. **up to 10 concurrent sessions at 0.1–0.4 s** by default.
- Would `max_session_permit=1` + `RateLimiter` give sequential paced fetches with backoff? **Partly.** Sequential and delayed: yes. But the "retry" is not a retry: on 429 the dispatcher only lengthens the delay for *later* URLs and, past `max_retries`, marks the task failed (`async_dispatcher.py:326-331`); the refused URL is **not** re-fetched, `Retry-After` is never read, and the delay counts from request *start* (`last_request_time` set before the fetch, `:63`), not from response completion. It cannot express the Director's policy.
- **Decision:** plain `requests` + `paced_get.py` for sitemap and REST; the existing sequential crawler for any browser smoke. I am **not** proposing crawl4ai for REST, so the 127.0.0.1 byte-fidelity check was not needed and was not run (verdict: not evaluated).

## 6. What remains unconfirmed

- The cause of the 429s, and whether it is specific to this machine/network.
- How long the refusal lasts (≥16.6 h observed on this source, or re-triggered by something unknown).
- Whether 15 s pacing is sufficient — untested.
- Whether the browser stream is refused too — untested since 2026-09-07 (last 10/10 on record).
- Contracts §2.5 field names; totals; Thrive empty-`content.rendered` sample.

## 7. Exact next action

1. **Director, off-tool:** open `https://cyberizegroup.com/sitemap.xml` in a normal browser from the same network as Zorin, then (if possible) from a phone on mobile data. 429 on both → site-wide (resource exhaustion; check Pressable logs for 599). 200 on mobile only → this network's source identity is blocked. 200 on both → the refusal is aimed at the non-browser client.
2. **Site-owner route (cleanest):** Cyberize is ours to ask — check the Pressable dashboard/logs for 429 vs 599 at 2026-09-18T14:15Z and 2026-09-19T07:03Z, and ask Pressable support whether this source is rate-limit listed and for how long. An allowlist or a documented limit would turn the pacing binding from a guess into a fact.
3. **Only on new Director word:** rerun `live_step3.py` as-is (helper and policy unchanged). No code is waiting on anything else.
4. **Unblocked work that needs no network:** "Run P1." — the readback can be written now with §2.5, REST pacing (P0 E-4), stop-rule scope (E-5), sitemap-fallback-on-429 (E-11) and AC-001 (A-1) carried as open erratum candidates; C1–C3, C5–C6 and all of Prepare are fixture-driven and do not depend on the live host. CHK and E2 do.

Evidence: `EVIDENCE/recovery/RECOVERY_LOG.md`, `EVIDENCE/recovery/live/*`, yesterday's `EVIDENCE/p0/`.

## 8. Clock

Start **2026-09-19T07:01:56Z** · live work ended 07:08:59Z · report written **07:12Z** · **≈10 min used of 60.** Stopped early because policy ended live work; the remaining budget was not spent on anything the mission did not authorize.

## Uncommitted paths

```
agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/recovery/     (new: RECOVERY_LOG.md, RECOVERY_REPORT.md, paced_get.py, test_paced_get_local.py, live_step3.py, live/ ×6)
agent_docs/SESSIONS/session_2026-09-19.md                (new)
RECOVERY.md                                              (modified)
```
