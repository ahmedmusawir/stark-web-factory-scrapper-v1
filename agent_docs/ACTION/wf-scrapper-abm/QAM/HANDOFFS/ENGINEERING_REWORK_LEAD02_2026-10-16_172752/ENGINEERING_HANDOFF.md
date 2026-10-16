# LEAD-02 bounded engineering repair — ENGINEERING HANDOFF

**Engineer:** Cody (Engineer seat; Claude Code, Claude Fable 5.1). **Written:** 2026-10-16 17:36:32 +06 (+0600).
**Authority:** Tony DIRECTOR GO (pasted into this session) · JARVIS `WEB_FACTORY_LEAD02_CODY_REPAIR_HANDOFF_2026-10-16.txt` · QA Lead decision LEAD-02 (both copied unchanged under `companions/`).
**Status:** R1 and R2 implemented with regression tests; affected modules pass. **Gate Q remains withheld. This is engineering handback, not QA, not a certificate.** Repaired commit and candidate release are PENDING Tony. No Git mutation was performed by Cody.

## 0. Identity and baseline

| Item | Value |
|---|---|
| Repository / branch | `/home/moose/PYTHON/stark-web-factory-scrapper-v1` · `qa/wf-scrapper-abm` |
| Starting HEAD (full) | `51abe5437a3f10883a946495bf02dabc3e232495` — "QAM Q2 independent QA run: evidence lane, matrix, package, reports" |
| Original product candidate | `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4` (ancestor of HEAD: yes) |
| Candidate → HEAD diff on product/test/config paths | **0 entries** (`baseline/diff-candidate-to-head-product-paths.txt`); successor commits are documentation/QA records only (`baseline/diff-candidate-to-head-namestatus.txt`) |
| Working tree before edits | only this session's engineering records (session-log edit, recovery response); no QA writer active (`baseline/git-status-before.txt`, `WRITER_SEAT.md`) |
| Historical QA ZIP (referenced, not nested) | `WebFactory_QA_Q2_Package_2026-10-16_155121.zip` · 499,912 B · SHA-256 `06f73841cc678badd30d56bfb4c41614c376b16abe7254ea1e374a96c1d974df` — re-verified at start |
| source52 before (worktree, LEAD-01 §0 method) | `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` = recorded `39b9728ac72cd2699410b6fda05c68c38b842b23eff7bd6490d9fb4f6d3d8314` (0 per-file mismatches) |
| **source52 after — NEW identity** | `6f35cf8dacf3aeecc17a89b1c96e3558ea52e3c03edf63c2e402a766a1e986f4` · changed paths: `agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py`, `agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py`, `recon_pipeline/decide.py`, `tests/test_decide.py` · **added product/test paths: none** (all four repaired files are inside the 52-path inventory) |
| Interpreter | `/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python` → `/home/moose/.pyenv/versions/3.12.3/bin/python3.12`, Python 3.12.3 |
| Dependencies | Crawl4AI 0.9.3, playwright 1.52.0, beautifulsoup4 4.13.4, pytest 8.3.5, markdown-it-py 4.2.0, mdurl 0.1.2, requests 2.32.3, python-dotenv 1.1.0, MarkupSafe 3.0.3; `pip check`: No broken requirements found.; PYTHONPATH empty |
| Engineering lane | `/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_2026-10-16_172752` |
| Engineering scratch | `/tmp/cody-lead02-2026-10-16_172752` |

## 1. Changed paths, hashes and patch

| Path | Candidate blob | Before (worktree) | After (worktree, full SHA-256) | Bytes |
|---|---|---|---|---|
| `recon_pipeline/decide.py` | `9158a6d576eab337…` | `9158a6d576eab337…` (= candidate: True) | `2a0a91c5262c350e21013efe850b79b8cd57fb67dba6e547d6f03108b1b458e6` | 36417 |
| `tests/test_decide.py` | `8a7bd67f8b6c226c…` | `8a7bd67f8b6c226c…` (= candidate: True) | `de514b062e7f197efb644c47643dbc1e14775b9c255221c534b9c41c3b22538e` | 26101 |
| `agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py` | `047121f1357cfe86…` | `047121f1357cfe86…` (= candidate: True) | `962add46f1172018963808a31af5d4fb08276b2bd6c5b4c91a2d952513c69c06` | 9986 |
| `agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py` | `0d2db73b57c0cef1…` | `0d2db73b57c0cef1…` (= candidate: True) | `b44a6af7e4234f90972d1a79b35660554dfbc3c0b71451930a7728b9b4289047` | 11730 |

Patch: `changes/working-tree.patch` — 12210 bytes, SHA-256 `85ff6b1bf1e123933236c14e94d0325aeee64227e4cf4003284e4dfb231464a0` (`git diff` of exactly these four paths; +122/−4 lines). No other product, test, dependency, fixture or configuration path changed. Unrelated pre-existing modifications preserved (session log, RESPONSES records). Full map: `changes/baseline-and-path-hashes.json`, `changes/source52-repaired.json`.

## 2. R1 — generic CTA titles (`recon_pipeline/decide.py`)

**Mechanism (baseline).** `candidate()` tested `label.casefold().rstrip(' .…›»>') not in GENERIC_LINK_LABELS`. The fixed suffix set did not contain U+2192 (nor other trailing symbols/emoji, leading arrows or doubled inner spaces), so `'Read more →'` passed as informative and was assigned to `row['title']`, both supplying an unknown title and replacing an informative one.

**Change.** New `generic_label(label)` (decide.py, after `ASSET`): casefold → collapse whitespace → strip leading/trailing characters whose Unicode category is Punctuation, Symbol or Separator → **exact** membership in the unchanged `GENERIC_LINK_LABELS`. `candidate()` now reads `if any(char.isalnum() for char in label) and not generic_label(label)`. Not a substring rule; the displayed title text is never normalized (informative strings are stored exactly, arrows included). Sources are still appended before the title test, so every locator and the raw label remain provenance. No slug-derived titles; stable IDs, selection (`UNDECIDED`) and version binding untouched.

**Reproduction (`validation/r1_reproduction.json`, candidate blob vs repaired module):**
- supply `'Read more →'` on unknown row: before `'Read more →'` → after `None`
- informative then `'Read more →'`: before `'Read more →'` → after `'Informative Title Kept'`; CTA-first then informative → `'Informative Title Kept'`
- controls after: `Read more ›`, `READ MORE…`, `?!...`, whitespace, `→→`, `→ Read more`, `Read  more 👉`, `Continue reading »`, `» Learn More !` → None; Andromeda heading, `Read more about the Andromeda recovery process`, `Learn More: 5 Tactics`, `Café SEO 🚀`, `বাংলা শিরোনাম →` → exact text kept.

**Regression tests added (`tests/test_decide.py`):** `test_arrow_cta_cannot_supply_unknown_title`, `test_arrow_cta_cannot_replace_informative_title`, `test_label_guard_cases_keep_exact_informative_text` (15 params), `test_arrow_cta_discovery_double_both_orders` (2 params: default-discovery transport double, anchors both orders; asserts title, stable ID, locators `a[href][0..1]`, UNDECIDED, exactly 2 transport calls = destination never fetched, raw `Read more →` bytes recoverable in the hashed evidence file at the recorded locator with matching SHA). Existing Read Post / Read more... / Continue reading / Learn More / View post, Unicode heading, punctuation-order, weak-label and provenance tests retained and passing.

**Limitations.** Membership is still the five-entry set; new CTA vocabulary (e.g. "Details") is not generic. Decoration stripping covers Unicode P/S/Z categories only.

## 3. R2 — inert source text at the Markdown boundary (`prepare_saved.py`)

**Mechanism (baseline).** `markdown()` fed `str(node)` to crawl4ai 0.9.3's vendored html2text (`CustomHTML2Text`, all `escape_*` options False). The converter decodes entities and emits text data verbatim, so `&lt;script&gt;…` became a raw `<script>` element (B1) and `[click me](javascript:…)` text became syntactically valid link syntax (B2). `clean()`'s `a[href]` scheme filter cannot see a text-node link. Confirmed in the bounded reproducer (`validation/renderer-boundary/pre-fix/`).

**Change (smallest correction at the seam, both page and boilerplate callers share it).**
1. `html2text_options` gains `'escape_snob': True` — the converter's own literal-text treatment: backslash-escapes `` ` * _ { } [ ] ( ) # ! `` **in text data only**; converter-generated headings, lists, emphasis and `[label](url)` links are untouched (verified on controls and the real fixture).
2. Angle brackets are outside that set, so `markdown()` now works on a copy (`BeautifulSoup(str(node))`) and backslash-escapes `<`/`>` in plain `NavigableString` nodes outside `code`/`pre` (`ANGLE = re.compile(r'([<>])')`). The copy keeps `main` unmodified for the SOURCE_INDEX heading/link/paragraph statistics (asserted). B3 `images[].source_src` is untouched JSON provenance (shown in `post-fix/SOURCE_INDEX.json` still carrying the raw `javascript:` value as data).

**Derived output after:** `Escaped markup text: \<script\>alert\('t23-escaped-text'\)\</script\> shown as characters.` and `Markdown-shaped text: \[click me\]\(javascript:alert\('t23-md-inject'\)\) should remain plain text.` (`validation/renderer-boundary/post-fix/derived_page.md`, `derived_BOILERPLATE.md`).

**Renderer/parser boundary (markdown-it-py 4.2.0, HTML parser for assertions: bs4 html.parser (beautifulsoup4 4.13.4), custom link validator: none, linkify: off).** html tokens / DOM `<script>` elements / B1 literal in rendered text — pre-fix → post-fix; plus post-fix javascript hrefs / B2 literal:

| Config | File | pre-fix | post-fix | post-fix js hrefs / B2 literal |
|---|---|---|---|---|
| commonmark html=True | page | 3 / 1 / False | 1 / 0 / True | [] / True |
| commonmark html=True | boilerplate | 2 / 1 / False | 0 / 0 / True | [] / True |
| default html=True | page | 3 / 1 / False | 1 / 0 / True | [] / True |
| default html=True | boilerplate | 2 / 1 / False | 0 / 0 / True | [] / True |
| default html=False | page | 0 / 0 / True | 0 / 0 / True | [] / True |
| default html=False | boilerplate | 0 / 0 / True | 0 / 0 / True | [] / True |

The single post-fix `html_block` token on the page file is the helper's own fixed `<!-- MAIN CONTENT -->` header comment, not source text (token content recorded in `tokens_page_*.json`). Pre-fix `js_hrefs: []` already held only because markdown-it's `validateLink` rejects `javascript:`; the Lead's requirement is met at the **converter output** (no `<script>` substring, no `](javascript:` substring in either file) and verified again under `html=True`, so B1 is not hidden by disabling raw HTML. Declared settings:

```json
{
 "commonmark html=True": {
  "preset": "commonmark",
  "options": {
   "maxNesting": 20,
   "html": true,
   "linkify": false,
   "typographer": false,
   "quotes": "“”‘’",
   "xhtmlOut": true,
   "breaks": false,
   "langPrefix": "language-",
   "highlight": null
  },
  "validateLink(\"javascript:alert(1)\")": false,
  "linkify": false,
  "custom_link_validator": null
 },
 "default html=True": {
  "preset": "default",
  "options": {
   "maxNesting": 100,
   "html": true,
   "linkify": false,
   "typographer": false,
   "quotes": "“”‘’",
   "xhtmlOut": false,
   "breaks": false,
   "langPrefix": "language-",
   "highlight": null
  },
  "validateLink(\"javascript:alert(1)\")": false,
  "linkify": false,
  "custom_link_validator": null
 },
 "default html=False": {
  "preset": "default",
  "options": {
   "maxNesting": 100,
   "html": false,
   "linkify": false,
   "typographer": false,
   "quotes": "“”‘’",
   "xhtmlOut": false,
   "breaks": false,
   "langPrefix": "language-",
   "highlight": null
  },
  "validateLink(\"javascript:alert(1)\")": false,
  "linkify": false,
  "custom_link_validator": null
 }
}
```

**Actual safety boundary.** Derived Markdown now contains only literal text for these constructs under CommonMark backslash-escape semantics; this is verified for markdown-it-py (commonmark/default, html on/off). It is not a claim about every viewer (a renderer that does not honour backslash escapes, or that renders `.md` as raw HTML, is outside this check), and no browser exploit was demonstrated or claimed.

**Regression test added (`agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py::test_source_text_stays_inert_in_page_and_boilerplate`):** fresh synthetic saved collection via the module's existing `saved()` fixture builder with the exact B1/B2 fragments in `<main>` **and** in `<header id="thrive-header">` (shared boilerplate path) plus positive controls; asserts raw body/metadata/checklist hashes unchanged, SOURCE_INDEX hashes match the written files, converter-boundary substrings absent, marker strings present, token/DOM inspection under the three declared configs, readable B1/B2 sentences in rendered text, controls (h1/h2, strong/em, `1 < 2`, ul/ol items, relative + absolute links with resolved destinations) intact, boilerplate `Home` link kept, `content.headings` unaffected. Existing non-content removal, unsafe-anchor label, traversal/hash refusal, new-output-directory, saved three-page content and provenance tests retained and passing.

**Historical fixture (`validation/historical-fixture/`).** Raw collection `outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505` byte-unchanged across a fresh prepare (8 files; checklist/result/body hashes consistent). All four historical prepared packages still self-consistent with their SOURCE_INDEX hashes (untouched). Fresh repaired run (into engineering scratch) vs accepted v01 package:

| Page | accepted sha | fresh sha | rendered text identical | headings / links identical | backslashes |
|---|---|---|---|---|---|
| 3a1a77925e47639b5f9fd201 (landing page) | `c96d3e8f435be9e6…` | `2eda1437d99b4016…` | True | True / True | 0 → 1 |
| ae3d8256cdd00e50ca26c1f2 (category/article listing) | `e15c63d2707e2ff7…` | `840173e81beeb742…` | True | True / True | 0 → 2 |
| 76f31511d3acb8433bdb9d50 (article) | `8ea04171ebbb3583…` | `1af647753e638d46…` | True | True / True | 0 → 2 |
| BOILERPLATE.md | `35b6fb78c148e903…` | `b7bd3bd3c8d1784e…` | True | — | 0 → 14 |

Derived bytes legitimately change (added escapes); historical derived hashes stay historical and are not expectations for new runs.

## 4. Validation records

| Phase | Command record | Result | Exit |
|---|---|---|---|
| Pre-fix (new tests on unchanged product) | `validation/prefix/command.json` → `affected-run-prefix.log`, `affected-junit-prefix.xml` | **85 collected, 8 failed, 77 passed** — exactly the expected set: arrow supply, arrow replace, 4 arrow/decoration params, discovery heading-then-arrow order, R2 inert test | 1 |
| Post-fix run 1 | `validation/affected-command.run1.json` → `affected-run.run1.log`, `affected-junit.run1.xml` | 84 passed, 1 failed — the new R2 test's own over-broad scan (whole page file incl. the `<!-- MAIN CONTENT -->` header marker); test scoped to converted main content, product unchanged | 1 |
| **Post-fix run 2 (final)** | `validation/affected-command.json` → `affected-run.log`, `affected-junit.xml` | **85 passed, 0 failed** (test_decide 74; test_prepare_saved 11) | 0 |

Executable `/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python` (→ `/home/moose/.pyenv/versions/3.12.3/bin/python3.12`), cwd `/home/moose/PYTHON/stark-web-factory-scrapper-v1`, env `PYTHONDONTWRITEBYTECODE=1`, `DECIDE_EVIDENCE` unset, argv exactly: `/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python -m pytest tests/test_decide.py agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py -p no:cacheprovider -q --basetemp=/tmp/cody-lead02-2026-10-16_172752/pytest --junitxml=/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_2026-10-16_172752/validation/affected-junit.xml`. Start 2026-10-16T17:32:34+06:00 → end 2026-10-16T17:32:43+06:00. Fresh basetemp under engineering scratch; no run touched the retained QA snapshot trees or any historical Q2 lane; the archived QA helpers were not executed. Renderer-boundary runs: `validation/renderer-boundary/*-command.json` (+ logs). JUnit per-module summary: `validation/junit-summary.json`. New node IDs: 20 (2 + 15 + 2 + 1); totals are not forced to the old 97/124.

Engineering instrument corrections (recorded, product unaffected): renderer instrument token-JSON serialization fixed before its first successful pre-fix run; `source52_identity.py` repo-path depth fixed before its first run; R2 test scan scoped to main content (run 1 → run 2).

## 5. QA-owned completion items — NOT implemented or claimed here

- **C1 / T-13:** final reviewed `article>header>h1` heading preservation in a NEW reviewed rendition — independent QA.
- **C2 / T-22, AC-041/042, O2:** `max_requests=1`, tiny deadline, small byte allowance fixtures and actual directory-byte measurement — independent QA.
- **C3 / T-08/T-15:** rich native REST byte-fidelity capture — independent QA.
No unrelated product change was made toward these. Engineering validation does not replace the independent retest; QA binds its snapshot to Tony's REPAIRED commit (handoff §10) and runs the six required modules once, including the new tests in actual totals.

## 6. Controls

- **Zero external requests**: all tests use loopback doubles / saved fixtures; the Prepare tests' autouse `no_network` fixture forbids sockets; renderer-boundary and historical-fixture instruments touch only local files.
- **No Git mutations**, no dependency install/upgrade, no `.env` use. Read-only `git status/log/diff/show/rev-parse/merge-base` only.
- **Preserved**: raw collections, historical prepared packages, QA lane `Q2_2026-10-16_142632/`, QA scratch `/tmp/opencode/q2-scratch-20261016/` (29.7 MB), historical ZIPs, Director archives.
- **Owned processes**: none left running (`baseline/processes.txt`, re-checked at closeout).

## 7. Writer seat, scratch and proposed retain/delete (Tony decides; nothing deleted)

Writer seat **released to Tony** at closeout (see `WRITER_SEAT.md`). No further writes to product/test paths after this handoff.

| Item | Class | Proposal |
|---|---|---|
| `/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_2026-10-16_172752` | durable engineering record (this lane) | RETAIN; Tony commits with the four repaired files |
| `/home/moose/Downloads/WebFactory_LEAD02_Engineering_Rework_<ts>.zip` | durable review package | RETAIN |
| `/tmp/cody-lead02-2026-10-16_172752` (3.2 MB: pytest basetemps, renderer pre/post synthetic inputs+outputs, candidate blob copy, fresh historical run) | engineering scratch, fully reproducible from lane instruments | DELETE after Tony's commit and QA retest start, at Tony's discretion |
| `/tmp/opencode/q2-scratch-20261016/` | QA scratch | RETAIN until QA completes C1–C3 (LEAD-02 §6) |
| `/tmp/cody-lead02-probe` (empty probe dir created early) | engineering scratch | already removed (empty, own) |

## 8. Suggested exact-path commit (Tony only; Cody does not stage or commit)

```bash
git add recon_pipeline/decide.py tests/test_decide.py \
        agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py \
        agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py \
        agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_2026-10-16_172752/ \
        agent_docs/RESPONSES/response_2026-10-16_165613_cody-engineer-recovery.md \
        agent_docs/RESPONSES/response_2026-10-16_172610_lead02-repair-plan.md \
        agent_docs/RESPONSES/response_2026-10-16_<closeout>_lead02-engineering-rework.md \
        agent_docs/SESSIONS/session_2026-10-16.md RECOVERY.md CHANGELOG.md
git commit -m "LEAD-02 bounded repair: generic CTA title guard (R1) and inert Markdown source text (R2) with regression tests; engineering lane"
```
