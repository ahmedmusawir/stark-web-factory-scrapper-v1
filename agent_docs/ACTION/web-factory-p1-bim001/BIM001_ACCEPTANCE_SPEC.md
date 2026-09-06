# BIM001 ACCEPTANCE SPEC — Raw HTML Capture

> **Module:** `web-factory-p1-bim001` · **Version:** 1.0 · **Date:** 2026-09-06 · **Status:** FROZEN AT HANDOFF
> **Grading rule (J-16):** each AC is graded by its **Check** as written. Intent does not rescue a failed literal check; QA records an erratum instead (J-04).
> **Grader:** Cody executes, SOL adjudicates, Director holds final adjudication.
> **Baseline:** `main` @ bim000 close (`57a0f59`), 14 tests green (`pytest -q` → `14 passed`).

Paths are relative to repo root. `RUN_DIR` means `outputs/<project>/runs/<run_id>/`. "The stub" means the fake `result` object built in `tests/test_crawler.py:17-24` (or its bim001 equivalent). Single stage; no CP numbering.

---

## A. CLI and project identity (R3-A + usability addition)

**AC-01 — `--project` flag exists and is optional to the parser.**
Check: `python -m smart_crawler.crawler --help` exits 0 and its output contains the string `--project`. `parse_args(["--limit", "3"])` returns without raising.

**AC-02 — Missing `--project` refuses before crawling.**
Check: run `python -m smart_crawler.crawler --input <a valid 1-URL json>` with no `--project`. Exit code is `2`. No browser is launched (verifiable: `AsyncWebCrawler` is not constructed — in tests, patch it and assert not called). No file is created under `outputs/` by this invocation (`outputs/` listing before == after).

**AC-03 — Missing `--project` output names the flag.**
Check: the stderr+stdout of the AC-02 invocation contains the exact substring `--project is required`.

**AC-04 — Missing `--project` output shows the canonical example.**
Check: the same output contains the exact substring `python -m smart_crawler.crawler --project CyberizeGroup --limit 10`.

**AC-05 — Missing `--project` output points to help.**
Check: the same output contains the exact substring `python -m smart_crawler.crawler --help`.

**AC-06 — Project name is validated.**
Check: valid names match the regex `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`. Invoking with `--project "Cyberize Group"` (space) and with `--project "../x"` each exits `2`, prints a line containing the exact substring `--project is invalid`, and prints the same example and help lines as AC-04 and AC-05. No file created under `outputs/`.

**AC-07 — Case is preserved.**
Check: `--project CyberizeGroup` produces `outputs/CyberizeGroup/` (not lowercased).

**AC-08 — argparse help is preserved, not replaced.**
Check: `python -m smart_crawler.crawler --help` output still contains `--input` and `--limit`. `--limit 0` still produces the bim000 argparse error and exit `2`.

## B. Run folder

**AC-10 — Layout.**
Check: after a run with `--project CyberizeGroup`, exactly this exists: `outputs/CyberizeGroup/runs/<run_id>/html/`, `.../manifest.json`, `.../stage_log.txt`, `.../absences.json`. No other files or directories directly inside `RUN_DIR`.

**AC-11 — `run_id` format.**
Check: `<run_id>` matches `^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$` and denotes the same instant as `manifest.json["started_at"]`.

**AC-12 — Created at runtime only.**
Check: `test_import_from_foreign_cwd_creates_no_directory` passes unchanged. `grep -n "mkdir" smart_crawler/crawler.py` shows no `mkdir` call at module level (every hit is inside a function body).

**AC-13 — Empty input still produces a run folder.**
Check: `--project CyberizeGroup --input <json containing []>` exits 0 and creates `RUN_DIR` with `html/` (empty), `manifest.json` (`pages == []`, `input_total == 0`), `absences.json` (`[]`), `stage_log.txt` (non-empty). `outputs/run_summary.json` is also written, as in bim000 AC-21.

**AC-14 — Two runs, two folders.**
Check: two consecutive runs with the same project produce two distinct `run_id` folders; the first is not modified by the second (its `manifest.json` bytes are identical before and after the second run).

## C. HTML capture

**AC-20 — Captured for successful fetches.**
Check: for every page record with `status < 400` and `success` truthy where `result.html` is present, a file `RUN_DIR/html/<slug>.html` exists.

**AC-21 — Byte-for-byte.**
Check (unit): stub with `html="<html><body>É &amp; ok</body></html>"` → file bytes equal exactly `html.encode("utf-8")`. No trailing newline added, no whitespace changed, no `\r\n` normalization.
Check (live smoke): for one captured page, `len(file bytes) == manifest["pages"][i]["html_bytes"]`.

**AC-22 — Slug reuse.**
Check: the `.html` filename stem for a non-colliding URL equals the `.md` filename stem bim000 writes for the same URL (`slugify(url minus scheme)`). `grep -c "def slugify" smart_crawler/crawler.py` → `1`.

**AC-23 — Collision suffix (R4).**
Check (unit): three URLs in one run that slugify identically produce exactly `<slug>.html`, `<slug>-2.html`, `<slug>-3.html`, with three distinct byte contents preserved. `manifest.json["pages"]` maps each URL to its own `html_file`. No file is overwritten (write count == 3, files == 3).

**AC-24 — Not captured for blocked.**
Check (unit): stub `status_code=403` → no `.html` file; manifest outcome `blocked`.

**AC-25 — Not captured for failed.**
Check (unit): stub `status_code=500` → no `.html`, outcome `failed`. Stub raising an exception from `arun` → no `.html`, outcome `failed`, reason starts with `exception:`.

**AC-26 — Unsupported when `html` absent.**
Check (unit): stub with `status_code=200`, `success=True`, **no `html` attribute** → no `.html`, outcome `unsupported`, reason contains `html`. No `AttributeError` raised.

**AC-27 — Independent of markdown.**
Check (unit): stub with `status_code=200`, `success=True`, `html="<p>x</p>"`, and `markdown` whose `fit_markdown` and `raw_markdown` are both empty → `.html` file is written and outcome is `captured`, while `run_summary.json` per-page `ok` is `False` with the bim000 empty-markdown error (bim000 behavior preserved).

**AC-28 — Write failure is a failure, not a crash.**
Check (unit): make `RUN_DIR/html/` unwritable (or patch the writer to raise) → outcome `failed`, reason contains `write`, run continues to the next URL, exit code unchanged by this event.

## D. Manifest (R2 — bim001+ truth)

**AC-30 — Exact top-level keys.**
Check: `sorted(json.load(open(RUN_DIR/"manifest.json")))` equals exactly:
```
["access_rung", "command", "crawl4ai_version", "delay_before_return_html_s",
 "fallbacks_fired", "finished_at", "input_hosts", "input_path", "input_total",
 "limit", "page_timeout_ms", "pages", "pause_range_s", "playwright_version",
 "project_name", "python_version", "run_dir", "run_id", "schema",
 "started_at", "stopped_early", "summary_path", "wait_for_images"]
```
(23 keys, count verified at write time.)

**AC-31 — Fixed values.**
Check: `schema == "bim001-manifest-v1"` · `access_rung == "a"` · `fallbacks_fired == []` · `wait_for_images is True` · `delay_before_return_html_s == 3.0` · `page_timeout_ms == 90000` · `pause_range_s == [2, 5]` · `crawl4ai_version == "0.9.3"` · `playwright_version == "1.52.0"` · `python_version` starts with `"3.12"`.

**AC-32 — Identity values.**
Check: `project_name` equals the `--project` argument verbatim · `run_id` equals the folder name · `run_dir` equals `outputs/<project>/runs/<run_id>` (posix, relative to repo root, no trailing slash) · `command` equals the invoked argv joined by single spaces, starting with `python -m smart_crawler.crawler` · `input_path` is the resolved input file path as a string · `input_hosts` is the sorted list of unique hostnames across all input URLs · `summary_path == "outputs/run_summary.json"`.

**AC-33 — Counts.**
Check: `input_total` equals the number of entries in the input JSON before `--limit` · `limit` equals the `--limit` value or `null` when not given · `len(pages)` equals the number of URLs **attempted** (after `--limit`, and truncated by the stop rule).

**AC-34 — Exact per-page keys.**
Check: for every entry in `pages`, `sorted(entry)` equals exactly:
```
["elapsed_s", "error", "html_bytes", "html_file", "md_file", "ok",
 "outcome", "reason", "slug", "status", "url"]
```
(11 keys.)

**AC-35 — Per-page values.**
Check: `url`, `status`, `ok`, `elapsed_s`, `error` are **identical** to the same page's entry in `outputs/run_summary.json` · `slug` is the filename stem actually used, suffix included · `outcome` ∈ `{"captured", "blocked", "failed", "unsupported"}` · when `outcome == "captured"`: `html_file == "html/<slug>.html"`, `html_bytes` is an int equal to the file size, `reason is None` · otherwise `html_file is None`, `html_bytes is None`, `reason` is a non-empty string · `md_file` is `"pages/<slug>.md"` relative to `outputs/` when bim000 wrote the markdown file, else `None`.

**AC-36 — Timestamps.**
Check: `started_at` and `finished_at` are the same strings written to `run_summary.json` for that run.

**AC-37 — Written on every exit path that reaches the crawl.**
Check: normal completion, empty input (AC-13), and 3-consecutive-blocked early stop each leave a valid `manifest.json`. On early stop, `stopped_early is True` and process exit code is `2`.

## E. Absences

**AC-40 — Shape.**
Check: `RUN_DIR/absences.json` is a JSON list. Each entry's `sorted(keys)` equals exactly `["outcome", "reason", "url"]`. `outcome ∈ {"blocked", "failed", "unsupported", "skipped"}`.

**AC-41 — Completeness.**
Check: `{e["url"] for e in absences}` equals `{p["url"] for p in pages if p["outcome"] != "captured"} ∪ {every input URL not attempted}`. In other words: every input URL is either `captured` in the manifest or listed in absences. No URL is in both. Order: attempted-and-absent first in attempt order, then skipped in input order.

**AC-42 — Skipped reasons are distinct.**
Check: a URL cut by `--limit` has `reason == "limit"`. A URL not attempted because of the 3-consecutive-blocked stop has `reason == "stop_rule"`. Unit test covers both.

**AC-43 — Attempted-and-absent reasons match the manifest.**
Check: for every absence with outcome in `{blocked, failed, unsupported}`, `reason` equals the manifest page entry's `reason` for the same URL.

## F. Stage log

**AC-50 — Exists and is plain text.**
Check: `RUN_DIR/stage_log.txt` exists, decodes as UTF-8, every line begins with a timestamp matching `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}`.

**AC-51 — Contents.**
Check: first line contains `run start` and the project name and `run_id`; contains exactly one line per attempted URL containing that URL and its outcome word; contains a line containing `stop rule` when the early stop fires; last line contains `run end`.

## G. Legacy compatibility (R1, R2, R5)

**AC-60 — `run_summary.json` unchanged.**
Check: written to `outputs/run_summary.json` (path unchanged). `sorted(top-level keys) == ["crawl4ai_version", "finished_at", "pages", "pause_range_s", "started_at"]`. `sorted(per-page keys) == ["elapsed_s", "error", "ok", "status", "url"]`. Tests 1 and 8 key-set assertions pass unmodified.

**AC-61 — Markdown side product unchanged.**
Check: `outputs/pages/<slug>.md` written for ok pages exactly as before; `save_markdown` body is unchanged (`git diff main -- smart_crawler/crawler.py` shows no hunk inside `save_markdown`).

**AC-62 — Crawler config unchanged.**
Check: `grep -n "wait_for_images=True" smart_crawler/crawler.py` → 1 hit · `delay_before_return_html=3.0` → 1 hit · `page_timeout=90000` → 1 hit · `CacheMode.BYPASS` → 1 hit · `random.uniform(2, 5)` (or equivalent constant pair `2, 5`) unchanged.

**AC-63 — Exit codes unchanged.**
Check: input file missing → exit 1; `--limit 0` → exit 2; 3-consecutive-blocked → exit 2; normal → exit 0. Missing/invalid `--project` → exit 2 (new, AC-02/AC-06).

## H. Tests and regression

**AC-70 — bim000 tests preserved.**
Check: the 14 test functions named in `READ_pre-bim001_2026-09-06.md` §4 all still exist by the same name and all pass. Their assertion lines are unchanged (`git diff main -- tests/` shows no removed `assert` line in these functions).

**AC-71 — Permitted amendments only.**
Check: the only permitted edits to bim000 test files are: (a) the `sandbox` fixture additionally redirects the run-root constant to `tmp_path`; (b) any bim000 test that invokes `main()` with argv gains `--project <name>` in that argv; (c) the stub gains an **optional** `html` field defaulting to absent. Each amendment is listed by test name in `CHANGELOG.md`. Anything else is a FAIL.

**AC-72 — Targeted bim001 tests exist.**
Check: new tests cover, by name, each of: AC-02/03/04/05 (missing project), AC-06 (invalid project), AC-07 (case), AC-13 (empty input run folder), AC-21 (byte-for-byte), AC-23 (collision), AC-24/25 (blocked/failed no HTML), AC-26 (unsupported), AC-27 (independent of markdown), AC-30/34 (manifest key sets), AC-41/42 (absences incl. `limit` and `stop_rule`), AC-51 (stage log lines). Minimum 14 new tests. Test names contain the AC number (e.g. `test_ac23_collision_suffix`).

**AC-73 — Full regression green.**
Check: `venv/bin/pytest -q` → `N passed`, `0 failed`, `N >= 28`. Run from repo root and from `/tmp` with `PYTHONPATH=<repo>` (bim000 AC-10 erratum convention).

**AC-74 — Live capped smoke.**
Check: `python -m smart_crawler.crawler --project CyberizeGroup --limit 10` on `discovered_pages.json` from `https://cyberizegroup.com` completes exit 0; `manifest.json` has 10 pages, ≥ 9 `captured`; each captured file starts with `<!DOCTYPE` or `<html` (case-insensitive); `absences.json` lists exactly the non-captured ones plus 184 `skipped`/`limit` entries (194 − 10; count from the current `discovered_pages.json`, re-verify at QA time).

## I. Docs

**AC-80 — Canonical command in three places, identical.**
Check: the exact line `python -m smart_crawler.crawler --project CyberizeGroup --limit 10` appears in `README.md`, `RUN_NOTES.md`, and the missing-project error output (AC-04). `grep -c` ≥ 1 in each file.

**AC-81 — Two-file state documented.**
Check: `RUN_NOTES.md` contains a sentence stating that `manifest.json` is the run record from bim001 onward and that `run_summary.json` is the frozen bim000 contract retained for compatibility.

**AC-82 — Changelog.**
Check: `CHANGELOG.md` has a `bim001` section listing: `--project` flag, run folder layout, HTML capture, manifest, absences, stage log, permitted test amendments (AC-71), and the statement "no pin changes".

## J. Boundaries

**AC-90 — Surface.**
Check: `git diff --stat main` lists only: `smart_crawler/crawler.py`, files under `tests/`, `README.md`, `RUN_NOTES.md`, `CHANGELOG.md`, and files under `agent_docs/`. Nothing under `discover_site/`. `requirements*.txt` unchanged.

**AC-91 — No pins, no installs.**
Check: `venv/bin/pip freeze` output equals `requirements-lock.txt` (as at bim000 close). `pip check` clean.

**AC-92 — No forbidden imports.**
Check: `grep -rn "litellm\|playwright\|google.generativeai\|genai" smart_crawler/ discover_site/` → 0 hits in our code.

**AC-93 — No mutating git by agents.**
Check: `git log main..HEAD --format=%an` shows only the Director's author. Claudy's reports contain no mutating git command executed (read-only inspection is allowed per J-08).

---

## Erratum lane (append-only, QA writes here)

| AC | Finding | Adjudication | Date |
|---|---|---|---|
| | | | |
