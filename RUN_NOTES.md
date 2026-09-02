# RUN_NOTES — Phase C1 functional baseline (2026-09-02)

Exact commands used on branch `phase-c1-cleanup`, machine: Linux, pyenv Python 3.12.3. All commands from the repo root.

## 1. Environment

```bash
python --version                              # Python 3.12.3 (pyenv via .python-version)
python -m venv venv
venv/bin/pip install -r requirements.txt      # exit 0
venv/bin/pip freeze > requirements-lock.txt   # 94 lines
venv/bin/playwright install chromium          # Chromium Headless Shell 136.0.7103.25 (playwright build v1169)
```

Pins in `requirements.txt` are the exact versions carried over from the retired `poetry.lock`: crawl4ai 0.6.3, playwright 1.52.0, python-dotenv 1.1.0, beautifulsoup4 4.13.4, requests 2.32.3, pytest 8.3.5, plus chardet 5.2.0 (transitive; pinned to the lock version because an unpinned resolve pulled 7.6.0 and tripped a requests compatibility warning). No versions were upgraded. `crawl4ai-setup` was not needed.

## 2. Tests

```bash
venv/bin/pytest -q
# ......                                                                   [100%]
# 6 passed in 0.23s
```

## 3. Discovery — https://cyberizegroup.com/

```bash
printf '1\n' | venv/bin/python -m discover_site.discover https://cyberizegroup.com/
```

Result: sitemap index at `/sitemap.xml` with 3 child sitemaps (post, page, category). Exit 0. Wrote `outputs/discovered_pages.json` with 194 URLs.

## 4. Crawl — 5-page subset

```bash
venv/bin/python -c "import json;d=json.load(open('outputs/discovered_pages.json'))[:5];json.dump(d,open('outputs/discovered_pages_final.json','w'),indent=2)"
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

## 5. Donor-identity purge proof

Every surviving file outside `agent_docs/` (protocol audit trail) and `CLAUDE.md` (factory doctrine) must be free of the donor project's identity. The bracketed characters in the pattern below are the standard `grep [p]attern` idiom so this file does not match itself.

```bash
grep -rniE "g[h]l|gohigh[l]evel|gen[a]i|file[s]earch|file [s]earch|chat[b]ot|\br[a]g\b" \
  --include=*.py --include=*.md --include=*.toml --include=*.txt --include=*.cfg --include=*.ini . \
  --exclude-dir=agent_docs --exclude-dir=venv --exclude-dir=.git --exclude=CLAUDE.md
# (no output — zero hits)
```

## 6. Branch state

```
2dfad72 cp3 done
123e115 cp2 packaging done
35e65e0 cp1 done
```
CP4 (this file, README rewrite, session state) is committed by the Operator after review.
