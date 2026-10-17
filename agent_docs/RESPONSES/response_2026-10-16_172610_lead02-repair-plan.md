# LEAD-02 bounded repair — engineering plan (Cody, Engineer seat)

Written 17:26 +06 / 11:26 UTC, 2026-10-16. Authority: Tony's DIRECTOR GO (this session) + JARVIS handoff `WEB_FACTORY_LEAD02_CODY_REPAIR_HANDOFF_2026-10-16.txt` + LEAD-02 decision. Inputs verified: QA ZIP SHA-256 `06f73841…d974df`, 499,912 B.

## Baseline (read-only Git)
Branch `qa/wf-scrapper-abm`; HEAD `51abe5437a3f10883a946495bf02dabc3e232495`; candidate `8fbcff28…` → HEAD diff touches **0** product/test/config paths. Working tree: only this session's two records (session log edit + recovery response). Interpreter `venv/bin/python` → Python 3.12.3 (pyenv); Crawl4AI 0.9.3, bs4 4.13.4, markdown-it-py 4.2.0, pytest 8.3.5. No owned pytest/prepare/chromium processes running. QA scratch `/tmp/opencode/q2-scratch-20261016/` present (50 MB) — retained.

## Reproduced mechanisms
- **R1** `recon_pipeline/decide.py:74`: `label.casefold().rstrip(' .…›»>')` — fixed suffix set; U+2192 (and any other trailing symbol/emoji, leading arrows, doubled inner spaces) bypasses the `GENERIC_LINK_LABELS` membership test, so `'Read more →'` supplies/replaces a title. Sources are appended before the title check (provenance already retained).
- **R2** `prepare_saved.py:42 markdown()`: crawl4ai's vendored html2text (`escape_snob` etc. all False) unescapes entities and emits text verbatim → `&lt;script&gt;` → raw `<script>` (B1); `[click me](javascript:…)` text → valid link syntax (B2). Probed: `escape_snob=True` backslash-escapes `[ ] ( ) * _ # ! \` { }` in text nodes only (converter-generated links/emphasis/headings untouched; real 3-page fixture renders to identical text), but leaves `<`/`>` alone. A backslash inserted before `<`/`>` in text nodes passes the converter unchanged and renders as literal `&lt;`/`&gt;` in markdown-it commonmark/default, html on/off, including headings, link labels, blockquotes; autolinks unaffected.

## Plan
1. Create lane `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_<ts>/` + scratch `/tmp/cody-lead02-<ts>/`; record writer-seat acquisition, Git baseline, environment, source52 baseline (original method), pre-change hashes of the 4 files.
2. **Tests first** (unchanged product): add R1 cases to `tests/test_decide.py` (arrow supply → None; arrow replace → exact 'Informative Title Kept'; label_guard_cases controls + leading-arrow/emoji/double-space variants + informative longer-label controls; default-discovery transport double with arrow in both orders asserting title, stable ID, locators, UNDECIDED, 2 calls, raw label bytes + sha in hashed evidence). Add R2 test to `test_prepare_saved.py` (fresh synthetic collection with exact B1/B2 fragments in main AND header boilerplate + positive controls; asserts on derived MD text, markdown-it tokens and DOM under three declared configs, readable marker text, raw/metadata/checklist hashes unchanged, SOURCE_INDEX hashes). Run both modules → capture expected failures (junit+log).
3. **R1 fix** (`decide.py`): `generic_label()` — casefold, collapse whitespace, strip leading/trailing Unicode punctuation/symbol/separator categories, exact set membership. No substring rule; displayed title text untouched.
4. **R2 fix** (`prepare_saved.py markdown()`): work on a copy; backslash-escape `<`/`>` in text nodes outside code/pre; pass `escape_snob: True`. Both page and boilerplate callers share the seam. B3 untouched.
5. Run affected modules with the handoff's argument template (resolved paths, new basetemp, junit in lane, PYTHONDONTWRITEBYTECODE=1); run renderer-boundary script writing inputs/MD/tokens/HTML/settings to lane.
6. Records: patch, before/after hashes, repaired source52 (new identity; additions listed), ENGINEERING_HANDOFF.md, MANIFEST, ZIP to Downloads (companions: handoff + LEAD-02 + existing t24 package-check receipts), receipt outside ZIP, RESPONSES report, session/RECOVERY/CHANGELOG, writer-seat release, Git reminder.

## Files
Modify: `recon_pipeline/decide.py`, `tests/test_decide.py`, `agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py`, `agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py`. Create: lane records, ZIP, response, session/RECOVERY/CHANGELOG entries. Not touched: collector/transport/limits, QA lane Q2_*, historical packages, raw collections, B3 data, archived QA helpers, dependencies, Git.

## Assumptions / risks
- Historical derived hashes change for any re-run (escaping adds backslashes); recorded as legitimate, not an expectation.
- `escape_snob` makes MD noisier (`Now\!`) while rendering identically; smallest converter-native literal treatment available without replacing the converter.
- C1/C2/C3 stay with QA; Gate Q withheld; no self-certification.
