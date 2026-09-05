# web-factory-p1-bim000 — BRIEF
## Stage Prep + Controlled Upgrade

> **Module:** `web-factory-p1-bim000` · **Type:** BIM (brownfield Python) · **Version:** 1.0 · **Date:** 2026-09-05
> **Status:** AUTHORED → SOL review → Director approval → Claudy Plan Mode
> **Parent:** `WEB_FACTORY_P1_PHASE_MAP_v0_2.md` · 9-Phase Plan §5
> **Repo:** `~/python/stark-web-factory-scrapper-v1` · branch: Director names it (suggest `bim000-stage-prep`)
> **Evidence base:** recon 2026-09-04 · run-002 analysis 2026-09-05 · Director rulings 2026-09-05
> **Seats:** Director Tony (git, cloud, approvals) · Architect Fable · Engineer Claudy (Plan Mode, git-zero) · QA SOL (verdict)
> **Environment:** Zorin VM. Unit tests plus one capped 10-page smoke on cyberizegroup.com. No Ubuntu box needed for this module.

---

## 1. Goal

Make the scraper a clean, current, honest base that bim001 can build on. Nothing new is captured in this module. The tool does the same job it did in run-002, but on an upgraded Crawl4AI, without the manual copy step, without lying, and without letting a block page pass as success.

## 2. Why this module exists

Run-002 proved the tool runs on Cyberize (10/10, all 200). It also proved the tool is not ready to be built on: two halves glued by a shell one-liner, a headless robot identity, no status check, no pause, stale text, a dead Playwright file, and a Crawl4AI pin the Director ruled too old to build the acquisition layer on.

## 3. Scope — two stages, in order

**Stage 1 — Controlled Crawl4AI upgrade (isolated).**
Establish installed version (0.6.3). Identify current stable target. Read the changelog / breaking-change surface for the APIs we touch (`AsyncWebCrawler`, `BrowserConfig`, `CrawlerRunConfig`, `arun`, `CacheMode`, result fields `status_code`, `html`, `markdown`). Pin the chosen version exactly in `requirements.txt`, refresh `requirements-lock.txt`, install into the venv, refresh Playwright browsers only if the upgrade requires it. Rerun the full existing baseline (6 tests + one capped 10-page smoke). **Stop rule:** baseline breaks or migration turns into a rabbit hole → stop, write the finding, bring it back for a ruling. Stage 2 does not start until Stage 1 is green.

**Stage 2 — Stage prep (the cleanup and the run-002 additions).**
- **F3 handoff fix.** Discovery writes `outputs/discovered_pages.json`. Crawler reads it by default. `--input PATH` overrides. `--limit N` replaces the manual trim. The `_final` filename and the manual copy step are gone from code and docs.
- **Status validation.** Crawler reads `result.status_code`. Any code ≥ 400, or `success=False`, is a failed page. Failed pages are never saved as content. Per-URL status is written to `outputs/run_summary.json` (url, status, ok, elapsed_s, error). 403 and 429 are named as `blocked` in the summary; the run continues on a single blocked page but stops after three consecutive blocked pages.
- **Pacing.** Randomized pause between pages, uniform 2–5 s, logged. `delay_before_return_html` stays. `wait_for_images` stays (change deferred; note for bim001).
- **Identity.** Complete, current Chrome-shaped user agent (full token set, so `sec-ch-ua` is non-empty). Discovery `requests` calls send the same UA via a `Session`. No stealth, no navigator patching.
- **F4 truth.** Banner, docstring, and progress strings: version read from the installed package, URL count from `len(urls)`, no "AI-cleaned" claims.
- **R-B retire.** Delete `discover_site/smart_discover.py` after confirming no import or doc dependency. Remove its README mention.
- **Paths.** `crawler.py` anchors `outputs/` to repo root like `discover.py`. No `mkdir` at import time.
- **Hygiene.** Drop unused `import sys` in `discover.py`. Neutralize `cyberizegroup.com` in test fixtures to `example.com`.
- **Docs.** README run instructions rewritten to the new two-command flow. RUN_NOTES gets a bim000 section. `CHANGELOG.md` created (first entry: this module). The four stale `RESPONSES/` path references (`RECOVERY.md:5`, `session_2026-09-03.md:30`, `session_2026-09-02.md:41,47`) repointed to `RESPONSES/OLD/`. `CLAUDE.md` Protocol Directory Layout table gains one row for `agent_docs/RESPONSES/OLD/` (archived responses, Director-managed).
- **Tests.** New offline tests: crawler treats 403/429/500 as failed and does not write a file; `--limit` and `--input` behave; discovery `Session` carries the UA. Existing 6 stay green.

## 4. Explicitly out of scope

Raw HTML saving (bim001) · WP REST (bim002) · media inventory (bim003) · `fit_markdown` / content filter (F1 deferred) · stealth · `wait_for_images` changes · `KIP_REGISTRY.md` / `SKILLS/README.md` / `ACTION/` (separate hygiene pass) · Gemini / LLM extraction (proto001) · any `.env.example` change (R-D keep) · any LiteLLM removal (R-A tolerate) · any git command.

## 5. Exit gate

See `BIM000_ACCEPTANCE_SPEC.md`. Short form: upgraded pin, 6+ tests green, `discover` then `crawler` with no manual step, a capped 10-page Cyberize smoke with `run_summary.json` showing 10 × 200, no `_final`, no `smart_discover.py`, no lying strings, CHANGELOG present, SOL PASS.

## 6. Delivery

Feature branch. Claudy commits nothing. Director reviews the diff, merges rebase-and-merge. Module folder freezes when Claudy receives CP1.

## 7. Risks

- Crawl4AI target version may change `arun` result fields or `BrowserConfig` args. Stop rule covers it.
- Upgrade may pull a newer Playwright and require a browser download. Allowed, logged.
- A new Crawl4AI may change default headers; identity AC must be checked against the installed version, not assumed.
- Ten-page smoke could hit a 429 if Pressable tightened since run-002. Then the status check has done its job; report it.
