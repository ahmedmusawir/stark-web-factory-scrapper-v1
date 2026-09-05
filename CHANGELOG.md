# CHANGELOG

Doc/playbook change log for this repo. `[CC]` = Claude Code, `[TS]` = Tony Stark manual edit. Newest first.

## 2026-09-05 — [CC] Claude Code — bim000 Stage prep + controlled upgrade

- **Updated:** `requirements.txt`, `requirements-lock.txt` — crawl4ai 0.6.3 → 0.9.3 (exact pin; lock regenerated, 98 lines). Stage 1, committed 600d181.
- **Updated:** `smart_crawler/crawler.py` — `--input PATH` / `--limit N` (reads `outputs/discovered_pages.json` by default, no prompt); status validation (≥400 or `success=False` = failed, no file; 403/429 = `blocked`; 3 consecutive → stop, exit 2); per-page status lines; `outputs/run_summary.json`; random 2–5 s pause between pages; complete Chrome UA; paths anchored to repo root, no import-time mkdir; truthful banner (version from package metadata, count from `len(urls)`).
- **Updated:** `discover_site/sitemap_utils.py` — `USER_AGENT` constant + shared `requests.Session` used for every discovery call.
- **Updated:** `discover_site/discover.py` — uses the shared session; unused `import sys` removed.
- **Removed:** `discover_site/smart_discover.py` — retired (Docusaurus-only, unused, nothing imported it).
- **Updated:** `tests/test_discover.py`, `tests/test_sitemap_utils.py` — fixtures use `example.com`; sitemap stub targets `SESSION.get`.
- **Added:** `tests/test_crawler.py` — 7 offline tests (status handling, blocked-stop, pacing, flags, session UA, import side effects). Suite: 13 passed.
- **Updated:** `README.md` — two-command run section; references to the retired sidebar discoverer and the separate "final" input file removed; layout updated.
- **Updated:** `RUN_NOTES.md` — bim000 section (Stage 1 + Stage 2 commands).
- **Updated:** `CLAUDE.md` — Protocol Directory Layout: `agent_docs/RESPONSES/OLD/` row (archived responses, Director-managed).
- **Updated:** `agent_docs/SESSIONS/session_2026-09-02.md`, `session_2026-09-03.md` — stale `RESPONSES/` paths repointed to `RESPONSES/OLD/`.
- **Added:** `CHANGELOG.md` — this file.
- **Reason:** web-factory-p1-bim000 brief §3 (F3 handoff fix, status validation, pacing, identity, F4 truth, R-B retire, paths, hygiene, docs).
