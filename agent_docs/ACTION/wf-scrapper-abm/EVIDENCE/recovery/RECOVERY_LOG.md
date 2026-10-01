# RECOVERY LOG — wf-scrapper-abm recovery mission

**Start (UTC):** 2026-09-19T07:01:56Z · **Hard end:** 2026-09-19T08:01:56Z · Budget 60 min, no extension.

## Step 1–2 (no live traffic)

- Pressable KB read; crawl4ai 0.9.3 dispatcher inspected; decision: plain requests + paced_get.py.
- 2026-09-19T07:03:57Z paced_get.py offline test vs 127.0.0.1: T1 gap, T2 Retry-After+one retry+later-429 stop, T3 cooldown→BLOCKED, T4 over-budget stop — ALL PASS.

## Step 3 — live requests (policy: 1 in flight, ≥15 s after completion, shared schedule)

- 2026-09-19T07:03:58+00:00 #1 GET https://cyberizegroup.com/sitemap.xml -> **429** 1168 B 0.55s {"Content-Type": "text/html", "Content-Length": "1168", "X-ac": "24.sin _atomic_bur MISS", "Server": "nginx"} -> `sitemap.*`
- 2026-09-19T07:03:58+00:00 first 429: ALL requests paused 300s (no Retry-After, default cooldown), then ONE retry
- 2026-09-19T07:08:58+00:00 #2 GET https://cyberizegroup.com/sitemap.xml -> **429** 1168 B 0.52s {"Content-Type": "text/html", "Content-Length": "1168", "X-ac": "24.sin _atomic_bur MISS", "Server": "nginx"} -> `sitemap.retry.*`
- 2026-09-19T07:08:59+00:00 **STOP** retry of https://cyberizegroup.com/sitemap.xml also 429 — BLOCKED

## End

- 2026-09-19T07:10:38Z mission closed: BLOCKED after 2 live requests; no further traffic. Report: RECOVERY_REPORT.md.
