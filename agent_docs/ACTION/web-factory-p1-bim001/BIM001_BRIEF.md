# BIM001 BRIEF — Raw HTML Capture

> **Module:** `web-factory-p1-bim001` · **Version:** 1.0 · **Date:** 2026-09-06 · **Status:** FROZEN AT HANDOFF
> **Author:** Fable (Architect) · **Approved by:** Tony Stark (Director) · **Reviewed by:** SOL (QA Lead)
> **Evidence base:** `agent_docs/RECON/READ_pre-bim001_2026-09-06.md` · `BIM000_RETROSPECTIVE.md` · Director rulings 2026-09-06 (R1–R5, R3-A, CLI usability addition)

---

## Goal

Every page the crawler successfully fetches has its rendered HTML saved **untouched** into a run folder, with a machine-readable manifest that says what was captured, what was not, and why.

## Why

bim000 made the crawler honest and current. It still saves markdown only. Phase 1's product is the Raw Recon Package: evidence that survives interpretation. Rendered HTML is the first evidence stream. bim002 (REST + SEO) and bim003 (media) add streams into the folder this module creates.

## What changes

One implementation surface: `smart_crawler/crawler.py`, its tests, and the three docs (`README.md`, `RUN_NOTES.md`, `CHANGELOG.md`).

1. **Project identity.** New `--project NAME` flag. Explicit, validated at runtime, no default, no inference. Missing or invalid → refuse before crawling, exit 2, print corrective usage.
2. **Run folder.** `outputs/<project>/runs/<run_id>/` created in `main()` only. `run_id` is `started_at` made filesystem-safe (`2026-09-06T14-30-00Z`).
3. **HTML capture.** `result.html` written byte-for-byte to `html/<slug>.html` for every page that fetched successfully. Same `slugify` as bim000. Collision in the same run → `-2`, `-3` suffix.
4. **Manifest.** `manifest.json` in the run folder. Truth for bim001 onward. Exact schema in the acceptance spec.
5. **Absences.** `absences.json` names every input URL that produced no HTML, typed `blocked / failed / unsupported / skipped`, with a reason.
6. **Stage log.** `stage_log.txt` in the run folder: one timestamped line per run event and per page.
7. **CLI failure output.** Missing/invalid `--project` prints what is wrong, the canonical example, and `--help` pointer. argparse `--help` is preserved.

## What does not change

- Markdown side product: `outputs/pages/<slug>.md`, same behavior, same overwrite (R1).
- `outputs/run_summary.json`: same path, same five top-level keys, same five per-page keys, same values (R2).
- Failure ladder, status validation, 3-consecutive-blocked stop rule and exit 2, pacing, identity, `wait_for_images=True`, `delay_before_return_html=3.0`, `page_timeout=90000`, `CacheMode.BYPASS` (R5).
- `discover_site/*`, `discovered_pages.json`, pins, lock file.

## Canonical command

```
python -m discover_site.discover https://cyberizegroup.com
python -m smart_crawler.crawler --project CyberizeGroup --limit 10
```

## Decisions carried as assumptions (labeled, not rulings)

- **A1.** HTML filenames use the existing bim000 slug (`cyberizegroup-com-about-us.html`), not a shortened form. The Director's `about.html` example was shape, not literal. Reuse beats a second slug rule.
- **A2.** HTML is captured only for pages that fetched successfully (`status < 400` and `success` true). A 403 block page's body is **not** saved in bim001. Capturing block-page evidence is a candidate for a later module.
- **A3.** HTML capture does not depend on markdown. A page with empty markdown (today `ok=False`, `error="empty markdown"`) still gets its HTML captured. `run_summary.json`'s `ok` keeps its bim000 meaning.
- **A4.** "Target identity" in the manifest is recorded as `input_hosts`: the sorted unique hostnames of all input URLs. No single "site URL" is inferred.
- **A5.** Temporary two-file state (`run_summary.json` + `manifest.json`) is documented in `RUN_NOTES.md` with a one-line pointer that `run_summary.json` is the frozen bim000 contract, queued for retirement in bim004 or later.

## Exit gate (plain)

Director runs the canonical command on a fresh checkout. A run folder appears under `outputs/CyberizeGroup/runs/`. It contains one `.html` per fetched page, byte-identical to what Crawl4AI returned, a manifest that lists every input URL with its outcome and file, an absences file, and a stage log. `run_summary.json` still looks exactly like bim000's. All 14 bim000 tests green, new bim001 tests green, full regression green. Missing `--project` refuses with a usable message and exit 2.

## Risks

- **Test 8 (empty input) invokes `main()`.** It may need `--project` added to its call and the run root redirected. This is the one bim000 test amendment the spec permits (AC-30). Assertions do not change.
- **`--limit` truncates inside `load_urls`.** Recording limit-skipped URLs as absences needs the total count without changing `load_urls`' tested behavior. Engineer proposes the mechanism in Plan Mode.
- **Stub results lack `html`.** Guarded access is mandatory; `unsupported` is the honest label.
- **Import-time side effects.** Test 7 fails if any new directory is created at import.

## Out of scope

WP REST · Yoast · media · sitemap/discovery changes · `fit_markdown` · stealth · Gemini · timing tuning · project registry · retiring `run_summary.json` · any pin change.
