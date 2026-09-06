# RUN_NOTES

## Phase C1 functional baseline (2026-09-02)

Exact commands used on branch `phase-c1-cleanup`, machine: Linux, pyenv Python 3.12.3. All commands from the repo root.

### 1. Environment

```bash
python --version                              # Python 3.12.3 (pyenv via .python-version)
python -m venv venv
venv/bin/pip install -r requirements.txt      # exit 0
venv/bin/pip freeze > requirements-lock.txt   # 94 lines
venv/bin/playwright install chromium          # Chromium Headless Shell 136.0.7103.25 (playwright build v1169)
```

Pins in `requirements.txt` are the exact versions carried over from the retired `poetry.lock`: crawl4ai 0.6.3, playwright 1.52.0, python-dotenv 1.1.0, beautifulsoup4 4.13.4, requests 2.32.3, pytest 8.3.5, plus chardet 5.2.0 (transitive; pinned to the lock version because an unpinned resolve pulled 7.6.0 and tripped a requests compatibility warning). No versions were upgraded. `crawl4ai-setup` was not needed.

### 2. Tests

```bash
venv/bin/pytest -q
# ......                                                                   [100%]
# 6 passed in 0.23s
```

### 3. Discovery — https://cyberizegroup.com/

```bash
printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com/
```

Result: sitemap index at `/sitemap.xml` with 3 child sitemaps (post, page, category). Exit 0. Wrote `outputs/discovered_pages.json` with 194 URLs.

### 4. Crawl — 5-page subset

```bash
# (C1 used a one-liner here to copy the first 5 URLs into a separate "final" file; retired in bim000 — the crawler now reads discovered_pages.json directly, see §7)
printf 'y\n' | venv/bin/python -m smart_crawler.crawler
```

Result: exit 0, 5/5 successful, ~6.5 s per page. Files in `outputs/pages/` (gitignored):

| File | Bytes |
|---|---|
| cyberizegroup-com-blog.md | 12,283 |
| cyberizegroup-com-web-design-process.md | 14,284 |
| cyberizegroup-com-what-to-look-for-in-ppc-agency.md | 26,532 |
| cyberizegroup-com-our-covid-19-plan.md | 7,537 |
| cyberizegroup-com-5-foundational-principles-for-online-success.md | 18,897 |

Note: `fit_markdown` came back empty on all 5 pages, so the crawler used `raw_markdown` (nav-heavy). The run config sets no content filter, which crawl4ai 0.6.x requires for `fit_markdown`. Left for a later phase.

### 5. Donor-identity purge proof

Every surviving file outside `agent_docs/` (protocol audit trail) and `CLAUDE.md` (factory doctrine) must be free of the donor project's identity. The bracketed characters in the pattern below are the standard `grep [p]attern` idiom so this file does not match itself.

```bash
grep -rniE "g[h]l|gohigh[l]evel|gen[a]i|file[s]earch|file [s]earch|chat[b]ot|\br[a]g\b" \
  --include=*.py --include=*.md --include=*.toml --include=*.txt --include=*.cfg --include=*.ini . \
  --exclude-dir=agent_docs --exclude-dir=venv --exclude-dir=.git --exclude=CLAUDE.md
# (no output — zero hits)
```

### 6. Branch state

```
2dfad72 cp3 done
123e115 cp2 packaging done
35e65e0 cp1 done
```
CP4 (this file, README rewrite, session state) is committed by the Operator after review.

## bim000 — Stage prep + controlled upgrade (2026-09-05)

Branch `web-factory-p1-bim000`. Module docs: `agent_docs/ACTION/web-factory-p1-bim000/`. Reports: `agent_docs/RESPONSES/response_2026-09-05_123610_bim000-stage1-upgrade.md` (Stage 1), `response_2026-09-05_131346_bim000-stage2-complete.md` (Stage 2), `response_2026-09-05_160321_bim000-ac21-rework.md` (AC-21 fix), `QA_PREQ_web-factory-p1-bim000_2026-09-05.md` + `response_2026-09-05_161757_bim000-ac21-cody-retest.md` (QA).

### Stage 1 — crawl4ai 0.6.3 → 0.9.3 (committed 600d181)

```bash
# fresh venv on the new pin (old venv kept as venv.bak/ until accepted)
mv venv venv.bak && python -m venv venv
venv/bin/pip install -r requirements.txt        # exit 0, 61 s
venv/bin/pip freeze > requirements-lock.txt     # 98 lines, == pip freeze
venv/bin/pip check                              # No broken requirements found.
venv/bin/playwright install --dry-run chromium  # chromium-1169 already present → no install
venv/bin/pytest -q                              # 6 passed
```
Smoke on 0.9.3 with the unchanged C1 crawler: 194 URLs discovered, 10/10 crawled, all HTTP 200, 67.5 s.

### Stage 2 — two-command flow

```bash
printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com
venv/bin/python -m smart_crawler.crawler --limit 10
venv/bin/pytest -q                              # 13 passed
```
The manual "copy the first N URLs into a separate final JSON" step is gone: the crawler reads `outputs/discovered_pages.json` directly; `--limit N` replaces the trim; `--input PATH` overrides the file. Per-page status is printed and written to `outputs/run_summary.json`; 403/429 are `blocked`; three consecutive blocked pages stop the run. Random 2–5 s pause between pages. UA: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36` → crawl4ai `sec-ch-ua` = `"Chromium";v="140", "Not_A Brand";v="8", "Google Chrome";v="140"`. The unused Playwright sidebar discoverer module was deleted (nothing imported it; see CHANGELOG).

Final smoke, 2026-09-05 13:09 (+06), from the repo root:

```
$ printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com
[SUCCESS] Saved 194 links to .../outputs/discovered_pages.json        # 0.7 s, 4 GETs
$ venv/bin/python -m smart_crawler.crawler --limit 10                 # 81.0 s
Batch crawler — crawl4ai 0.9.3
Ready to crawl 10 URL(s) ... Pause between pages: 2-5 s (random) ... Estimated time: ~1.8 min
[1/10] 200 ok 6.2s https://cyberizegroup.com/blog/ -> cyberizegroup-com-blog.md (15,381 chars)
⏸ pause 3.7s
[2/10] 200 ok 5.5s https://cyberizegroup.com/web-design-process/ -> cyberizegroup-com-web-design-process.md (14,255 chars)
⏸ pause 2.8s
[3/10] 200 ok 5.3s https://cyberizegroup.com/what-to-look-for-in-ppc-agency/ -> cyberizegroup-com-what-to-look-for-in-ppc-agency.md (26,565 chars)
⏸ pause 3.2s
[4/10] 200 ok 5.1s https://cyberizegroup.com/our-covid-19-plan/ -> cyberizegroup-com-our-covid-19-plan.md (7,557 chars)
⏸ pause 3.9s
[5/10] 200 ok 5.3s https://cyberizegroup.com/5-foundational-principles-for-online-success/ -> cyberizegroup-com-5-foundational-principles-for-online-success.md (18,832 chars)
⏸ pause 2.3s
[6/10] 200 ok 5.5s https://cyberizegroup.com/5-mistakes-real-estate-agents-make/ -> cyberizegroup-com-5-mistakes-real-estate-agents-make.md (24,607 chars)
⏸ pause 2.5s
[7/10] 200 ok 4.3s https://cyberizegroup.com/covid-19-safety-tips-for-the-2020-pandemic/ -> cyberizegroup-com-covid-19-safety-tips-for-the-2020-pandemic.md (6,213 chars)
⏸ pause 2.5s
[8/10] 200 ok 5.3s https://cyberizegroup.com/on-page-seo-audit/ -> cyberizegroup-com-on-page-seo-audit.md (26,694 chars)
⏸ pause 2.6s
[9/10] 200 ok 5.3s https://cyberizegroup.com/what-to-expect-from-a-ppc-agency/ -> cyberizegroup-com-what-to-expect-from-a-ppc-agency.md (24,754 chars)
⏸ pause 2.6s
[10/10] 200 ok 5.3s https://cyberizegroup.com/ppc-agency-checklist/ -> cyberizegroup-com-ppc-agency-checklist.md (29,642 chars)
```
`outputs/run_summary.json`: 10 pages, all `status: 200`, `ok: true`, `error: null`; `crawl4ai_version: "0.9.3"`, `pause_range_s: [2, 5]`. Nine pause lines, all within 2–5 s. Running discovery from `/tmp` (with the repo on `PYTHONPATH` so the module resolves) still writes to the repo's `outputs/` and nothing under `/tmp`.

### Final certified result — SOL Gate Q PASS (2026-09-05)

Certified: branch `qa/web-factory-p1-bim000`, SHA `81099eedb0b7072ceaa8ee20ebaf336466a369bb`.

| Item | Result |
|---|---|
| Crawl4AI pin | `crawl4ai==0.9.3` (from 0.6.3); playwright 1.52.0 unchanged; lock 98 lines == `pip freeze`; `pip check` clean |
| Discovery | `python -m discover_site.discover https://cyberizegroup.com` → 194 URLs, 4 GETs, <1 s |
| 10-page smoke | `python -m smart_crawler.crawler --limit 10` → 10/10 HTTP 200, 9 pauses in 2–5 s, `run_summary.json` all 200 (Claudy 13:09; Cody independently 08:59 UTC) |
| Regression | `venv/bin/pytest -q` → **14 passed** (6 C1 + 7 Stage 2 + 1 AC-21) |
| AC-21 empty input | `--input <file containing []>` → zero crawls, exit 0, `run_summary.json` rewritten with `pages: []` and full metadata (regression test `test_empty_input_writes_truthful_summary_without_crawling`) |
| QA | Cody PRE-Q found AC-21 → fixed dcfb1ea → Cody retest PASS → SOL Gate Q PASS; AC-10/41/45 PASS WITH NOTE, AC-52 PASS WITH SPEC/DOCTRINE NOTE |
