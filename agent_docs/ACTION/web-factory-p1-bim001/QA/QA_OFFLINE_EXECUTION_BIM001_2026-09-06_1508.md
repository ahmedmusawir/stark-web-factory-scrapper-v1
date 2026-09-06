# BIM001 QA Stage 2 — Independent offline execution

## 1. Candidate identity / no-drift check

**EVIDENCE:** The first actions were the requested read-only branch, HEAD and status checks. They returned:

```text
qa/web-factory-p1-bim001
657e25e9191e5d91a822a49301c0260bde8f1bd4
?? agent_docs/ACTION/web-factory-p1-bim001/QA/
```

Pinned QA candidate: **`657e25e9191e5d91a822a49301c0260bde8f1bd4`**. Main comparison baseline: **`57a0f597b0ae6c15cfc9a43d5bebf367a6ebb2f0`**. Prior intake: [QA_RECON_BIM001_2026-09-06_1438.md](QA_RECON_BIM001_2026-09-06_1438.md).

Only authorized QA artifacts were untracked. No tracked source/test/contract/dependency changes existed, and no candidate drift occurred. Reconfirmed after execution: [final_integrity.json](evidence/final_integrity.json), [final_status.stdout.txt](evidence/final_status.stdout.txt), [final_head.stdout.txt](evidence/final_head.stdout.txt). Actual repository `outputs/` names, file bytes/hashes, sizes and mtimes were identical before and after this stage.

**EVIDENCE — execution boundaries:** All authored scripts, fixtures, logs, JSON snapshots, persisted stub artifacts, pytest temporary trees, and JUnit files are under this QA lane. Existing venv only; no installs, pin edits, implementation fixes, existing-test edits, frozen-contract edits, git mutations, or live crawls. Browser calls in QA artifact probes are replaced by an explicit offline fake; a Python audit hook rejects socket connect/DNS attempts. All those probes recorded zero network attempts. The existing test suite uses its inspected offline stubs. CLI negative/help probes execute the real unmodified module with the existing venv.

**EVIDENCE — harness:** [offline_driver.py](offline_driver.py) captures command argv, cwd, selected environment, elapsed time, exact stdout/stderr and exit codes. [offline_probe.py](offline_probe.py) exercises actual `main → run → crawl_all → crawl_page → record_capture → close_run` with only browser results, output constants, pacing sleeps, and the requested HTML writer error substituted. [artifact_probes.py](artifact_probes.py) reads persisted artifacts independently; [verify_offline_evidence.py](verify_offline_evidence.py) cross-checks outcomes, JUnit records, baseline assertions, docs, summary source keys and final integrity.

Output constants are relocated to each case's `QA/evidence/artifact_cases/<case>/outputs/`; manifest strings retain their required logical `outputs/...` values. This relocation is explicit test isolation, not a production path change. Original output constants are proven in `smart_crawler/crawler.py:43–49`; real CLI negative probes also inspect the actual repository output tree. No existing engineering smoke artifact was graded as QA evidence.

All AC statuses below are execution findings for SOL, not Gate Q. **No certification or Gate Q verdict is issued.**

## 2. Static contract results

Exact commands and outputs are stored as `<name>.command.json`, `<name>.stdout.txt`, `<name>.stderr.txt` in `evidence/`. Source snapshots carry original line numbers. Static observations:

| AC | Literal/static evidence | Result / limitation |
|---|---|---|
| AC-12 | `grep -n mkdir smart_crawler/crawler.py`; AST parent walk | Calls at lines 190 (write_summary), 231 (create), 490 (main), all inside functions; none at module level. Foreign-CWD import test passed later in both regressions. |
| AC-22 | `grep -c 'def slugify' smart_crawler/crawler.py` | stdout `1`, exit 0. |
| AC-60 | `frozen_summary_source_keys.json`; source lines 116 and 182–191; unchanged test assertions | Exact five summary and five page keys, plus runtime proof in §12. |
| AC-61 | `git diff main -- smart_crawler/crawler.py`; full function source comparison with main | `save_markdown` source exactly equal, no changed lines inside its body; current lines 170–179. |
| AC-62 | Separate `grep -nF` for all four config literals and pause source | `wait_for_images=True`:112; `delay_before_return_html=3.0`:111; `page_timeout=90000`:110; `CacheMode.BYPASS`:109; exactly one each. `PAUSE_RANGE_S = (2, 5)`:58 and `random.uniform(*PAUSE_RANGE_S)`:407 remain. |
| AC-80 | `grep -ncF` canonical command README/RUN_NOTES | stdout `1` for each; exact missing-project output also verified. |
| AC-81 | RUN_NOTES.md:160 | Explicit sentence says manifest.json is BIM001+ run record and run_summary.json is frozen BIM000 compatibility contract. |
| AC-82 | CHANGELOG.md:21–34, `docs_verified.json` | All required topics, named amendments, and `no pin changes` found. Permission to make an amendment is separately graded under AC-71. |
| AC-90 | `git diff --name-status main HEAD`; `git diff --stat main` | RECOVERY.md is outside the closed list. No exception granted; context separately below and in §14. |
| AC-91 | freeze, exact byte comparison, pip check | freeze byte-identical to lock; `diff -u` empty/exit 0; pip check clean/exit 0. |
| AC-92 | Exact recursive grep, AST import list, I-1 provenance | Literal nonzero match result; metadata lookup, not import. Three separate facts below. |
| AC-93 | author/history and available BIM001 report audit | Same author string as main baseline, no report records an agent executing mutating git. Scope is repository-record evidence, not authenticated actor identity. |

Primary evidence: [static_facts.json](evidence/static_facts.json), [frozen_summary_source_keys.json](evidence/frozen_summary_source_keys.json), [docs_verified.json](evidence/docs_verified.json), [implementation_diff.stdout.txt](evidence/implementation_diff.stdout.txt), [literal_ac61_diff.stdout.txt](evidence/literal_ac61_diff.stdout.txt), [tests_diff.stdout.txt](evidence/tests_diff.stdout.txt). Each grep has its own command/stdout/stderr file.

### AC-90 — literal surface first

**EVIDENCE — frozen text, `BIM001_ACCEPTANCE_SPEC.md:190`:**

**AC-90 — Surface.**
Check: `git diff --stat main` lists only: `smart_crawler/crawler.py`, files under `tests/`, `README.md`, `RUN_NOTES.md`, `CHANGELOG.md`, and files under `agent_docs/`. Nothing under `discover_site/`. `requirements*.txt` unchanged.

**EVIDENCE:** Full surface: [surface.stdout.txt](evidence/surface.stdout.txt), [surface_stat.stdout.txt](evidence/surface_stat.stdout.txt). Stat: **38 files changed, 1979 insertions(+), 50 deletions(-)**. Every changed non-agent_docs file is:

```text
CHANGELOG.md
README.md
RECOVERY.md
RUN_NOTES.md
smart_crawler/crawler.py
tests/test_crawler.py
```

Only `smart_crawler/crawler.py` is implementation; only `tests/test_crawler.py` is a test change. Nothing under `discover_site/`; requirements and lock are unchanged ([pin_diff.stdout.txt](evidence/pin_diff.stdout.txt), empty). **RED FLAG:** RECOVERY.md is not in AC-90's allowed list. The full agent_docs surface, including archive renames, is preserved in the linked evidence.

**Separate process context, not an exception:** Root `CLAUDE.md:326` onward requires recovery updates; completion report `BIM001_complete_2026-09-06.md:126` asks the Director to commit RECOVERY.md. That documentation/process purpose does not satisfy or amend AC-90. Per this stage's instruction to preserve the discrepancy without deciding its final PASS/FAIL, the aggregate status is **PASS-PENDING-ADJUDICATION**; the implementation/test/pin surface is within scope, while this documentation exception remains for SOL.

### AC-91 — environment evidence

**EVIDENCE:** `venv/bin/pip freeze`, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit 0; full unchanged freeze at [pip_freeze.stdout.txt](evidence/pip_freeze.stdout.txt), stderr [pip_freeze.stderr.txt](evidence/pip_freeze.stderr.txt). `freeze_diff` compared this exact byte output against `requirements-lock.txt`; baseline pin diff is empty. No install was performed.

**EVIDENCE — `diff -u requirements-lock.txt /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/pip_freeze.stdout.txt`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **0**, elapsed 0.0021 s. Exact execution context: [freeze_diff.command.json](evidence/freeze_diff.command.json).

stdout: [freeze_diff.stdout.txt](evidence/freeze_diff.stdout.txt)

```text
(empty)
```

stderr: [freeze_diff.stderr.txt](evidence/freeze_diff.stderr.txt)

```text
(empty)
```

**EVIDENCE — `venv/bin/pip check`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **0**, elapsed 1.1701 s. Exact execution context: [pip_check.command.json](evidence/pip_check.command.json).

stdout: [pip_check.stdout.txt](evidence/pip_check.stdout.txt)

```text
No broken requirements found.
```

stderr: [pip_check.stderr.txt](evidence/pip_check.stderr.txt)

```text
WARNING: The directory '/home/moose/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
```

### AC-92 — three separate facts

**EVIDENCE — frozen text, `BIM001_ACCEPTANCE_SPEC.md:196`:**

**AC-92 — No forbidden imports.**
Check: `grep -rn "litellm\|playwright\|google.generativeai\|genai" smart_crawler/ discover_site/` → 0 hits in our code.

**1. EVIDENCE — literal command/result; no reinterpretation:**

**EVIDENCE — `grep -rn 'litellm\|playwright\|google.generativeai\|genai' smart_crawler/ discover_site/`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **0**, elapsed 0.0024 s. Exact execution context: [forbidden_literal.command.json](evidence/forbidden_literal.command.json).

stdout: [forbidden_literal.stdout.txt](evidence/forbidden_literal.stdout.txt)

```text
smart_crawler/crawler.py:285:            "playwright_version": importlib.metadata.version("playwright"),  # metadata lookup only (I-1 ruling)
```

stderr: [forbidden_literal.stderr.txt](evidence/forbidden_literal.stderr.txt)

```text
grep: smart_crawler/__pycache__/crawler.cpython-312.pyc: binary file matches
grep: discover_site/__pycache__/smart_discover.cpython-312.pyc: binary file matches
```

The single source hit alone disproves a zero-hit source result. Stderr also reports existing `.pyc` matches, including the retired `smart_discover` cache. These caches were not deleted or repaired. Bytecode writes were disabled in this QA stage; the source/metadata question does not depend on excluding the binary lines.

**2. EVIDENCE — implementation fact:** `smart_crawler/crawler.py:285` contains both the `playwright_version` schema key and `importlib.metadata.version("playwright")`. AST import inventory ([static_facts.json](evidence/static_facts.json)) shows `import importlib.metadata` at line 23 and no Playwright import. This establishes a metadata lookup rather than a Playwright API import; it does not make the grep return zero.

**3. Separate CLAIM / EVIDENCE — approval provenance:** `BIM001_plan_2026-09-06.md:134` requests the metadata-hit allowance; `agent_docs/SESSIONS/session_2026-09-06.md:40` records:

> **Status:** APPROVED (12:30). Rulings: I-1 accept metadata hit (erratum at QA); I-2 record file actually written; I-3 run_id wait confirmed; I-4 accept. P2 chunk 1 started.

This is an on-disk engineering record of approval, not an executed zero-hit check or a signed QA erratum. The frozen acceptance erratum table remains blank. **PASS-PENDING-ADJUDICATION** preserves the no-Playwright-import implementation fact and the literal discrepancy for SOL; it grants no exception.

### AC-93 — available repository audit

**EVIDENCE:** [authors.stdout.txt](evidence/authors.stdout.txt) has six `Ahmed Musawir` lines. [history.stdout.txt](evidence/history.stdout.txt) preserves hashes, author fields and subjects; [baseline_author.stdout.txt](evidence/baseline_author.stdout.txt) records the same author name/email at certified-main close `57a0f59`. All six BIM001 commit author fields match that baseline identity.

**EVIDENCE:** Audited the available `agent_docs/RESPONSES/BIM001_*.md` records, with full text in [claudy_reports_full.txt](evidence/claudy_reports_full.txt) and command/context hits in [claudy_git_mentions.txt](evidence/claudy_git_mentions.txt). Recorded executed git commands are read-only status/log/diff/rev-parse/merge-base inspections. Mentions of commit/stage requests address the Director; plan chunks and future to-dos are not reported agent executions. No available report records Claudy executing add/commit/merge/rebase/push/reset/stash/checkout/switch.

**CLAIM / GAP:** Engineering attributes commits to the Director. Matching author strings and report statements do not authenticate the human or process that executed git. AC-93 is marked PASS for the prescribed **repository author/report check**, with this explicit evidentiary limit; no claim is made that git authors prove operator identity. QA itself executed no mutating git command.

## 3. CLI subprocess results

**EVIDENCE:** Fixture [one_url.json](evidence/one_url.json) is a valid one-entry JSON containing only `https://example.invalid/offline-only`. These real-module invocations never reached a browser/network path. Every invocation has before/after actual repository output snapshots, including content hashes and mtimes; all are equal ([cli_results.json](evidence/cli_results.json)). No production output was created or modified.

### CLI help

**EVIDENCE — `venv/bin/python -m smart_crawler.crawler --help`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **0**, elapsed 1.0874 s. Exact execution context: [cli_help.command.json](evidence/cli_help.command.json).

stdout: [cli_help.stdout.txt](evidence/cli_help.stdout.txt)

```text
usage: crawler.py [-h] [--project PROJECT] [--input INPUT] [--limit LIMIT]

Crawl discovered pages to markdown + raw HTML

options:
  -h, --help         show this help message and exit
  --project PROJECT  project name this run belongs to (required; validated at
                     runtime)
  --input INPUT      discovery JSON to read (default:
                     /home/moose/python/stark-web-factory-
                     scrapper-v1/outputs/discovered_pages.json)
  --limit LIMIT      crawl only the first N URLs (default: all)
```

stderr: [cli_help.stderr.txt](evidence/cli_help.stderr.txt)

```text
(empty)
```

### CLI missing project

**EVIDENCE — `venv/bin/python -m smart_crawler.crawler --input /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/one_url.json`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **2**, elapsed 1.0908 s. Exact execution context: [cli_missing_project.command.json](evidence/cli_missing_project.command.json).

stdout: [cli_missing_project.stdout.txt](evidence/cli_missing_project.stdout.txt)

```text
(empty)
```

stderr: [cli_missing_project.stderr.txt](evidence/cli_missing_project.stderr.txt)

```text
❌ --project is required. Name the project this run belongs to.
   Example: python -m smart_crawler.crawler --project CyberizeGroup --limit 10
   Help:    python -m smart_crawler.crawler --help
```

### CLI invalid space

**EVIDENCE — `venv/bin/python -m smart_crawler.crawler --project 'Cyberize Group' --input /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/one_url.json`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **2**, elapsed 1.0779 s. Exact execution context: [cli_invalid_space.command.json](evidence/cli_invalid_space.command.json).

stdout: [cli_invalid_space.stdout.txt](evidence/cli_invalid_space.stdout.txt)

```text
(empty)
```

stderr: [cli_invalid_space.stderr.txt](evidence/cli_invalid_space.stderr.txt)

```text
❌ --project is invalid: 'Cyberize Group'. Allowed: letters, digits, '-' and '_'; 1-64 characters; must start with a letter or digit.
   Example: python -m smart_crawler.crawler --project CyberizeGroup --limit 10
   Help:    python -m smart_crawler.crawler --help
```

### CLI invalid dotdot

**EVIDENCE — `venv/bin/python -m smart_crawler.crawler --project ../x --input /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/one_url.json`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **2**, elapsed 1.0809 s. Exact execution context: [cli_invalid_dotdot.command.json](evidence/cli_invalid_dotdot.command.json).

stdout: [cli_invalid_dotdot.stdout.txt](evidence/cli_invalid_dotdot.stdout.txt)

```text
(empty)
```

stderr: [cli_invalid_dotdot.stderr.txt](evidence/cli_invalid_dotdot.stderr.txt)

```text
❌ --project is invalid: '../x'. Allowed: letters, digits, '-' and '_'; 1-64 characters; must start with a letter or digit.
   Example: python -m smart_crawler.crawler --project CyberizeGroup --limit 10
   Help:    python -m smart_crawler.crawler --help
```

### CLI limit zero

**EVIDENCE — `venv/bin/python -m smart_crawler.crawler --project CyberizeGroup --limit 0 --input /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/one_url.json`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **2**, elapsed 1.0947 s. Exact execution context: [cli_limit_zero.command.json](evidence/cli_limit_zero.command.json).

stdout: [cli_limit_zero.stdout.txt](evidence/cli_limit_zero.stdout.txt)

```text
(empty)
```

stderr: [cli_limit_zero.stderr.txt](evidence/cli_limit_zero.stderr.txt)

```text
usage: crawler.py [-h] [--project PROJECT] [--input INPUT] [--limit LIMIT]
crawler.py: error: --limit must be >= 1
```

### CLI missing input

**EVIDENCE — `venv/bin/python -m smart_crawler.crawler --project CyberizeGroup --input /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/intentionally_missing.json`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **1**, elapsed 1.1014 s. Exact execution context: [cli_missing_input.command.json](evidence/cli_missing_input.command.json).

stdout: [cli_missing_input.stdout.txt](evidence/cli_missing_input.stdout.txt)

```text
❌ File not found: /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/intentionally_missing.json
   Run discovery first: python -m discover_site.discover <url>
```

stderr: [cli_missing_input.stderr.txt](evidence/cli_missing_input.stderr.txt)

```text
(empty)
```

**EVIDENCE — exact checks:** Help contains `--project`, `--input`, `--limit`; missing project has `--project is required`; both invalid names have `--project is invalid`; all three include the exact canonical example and help pointer. Limit zero preserves `--limit must be >= 1` and argparse exit 2. Missing input with valid project exits 1.

**EVIDENCE — independent constructor seam:** [missing_project_seam/invocation.json](evidence/artifact_cases/missing_project_seam/invocation.json) records exit 2, **0 browser constructions, 0 arun calls**, no output directory, zero network attempts. This executes real `main()` with the browser constructor counted, separately from the real unmodified `python -m` subprocess. Existing `test_ac02_missing_project_refuses_before_crawl` also passed with its browser/input-read trap.

## 4. Targeted BIM001 test results

**EVIDENCE:** Explicit selection: `tests/test_crawler.py -k test_ac`. [targeted_collect.stdout.txt](evidence/targeted_collect.stdout.txt) lists the exact 40 item IDs. Collection: **40/48 tests collected (8 deselected) in 1.11s**, exit 0. There are 39 BIM001 functions; AC-06 parametrization produces two items.

**EVIDENCE — `venv/bin/pytest -q tests/test_crawler.py -k test_ac`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **0**, elapsed 7.0566 s. Exact execution context: [targeted.command.json](evidence/targeted.command.json).

stdout: [targeted.stdout.txt](evidence/targeted.stdout.txt)

```text
........................................                                 [100%]
- generated xml file: /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/targeted.xml -
40 passed, 8 deselected in 6.56s
```

stderr: [targeted.stderr.txt](evidence/targeted.stderr.txt)

```text
(empty)
```

Targeted outcome: **40 passed, 8 deselected, 0 failed, 0 errors**, 6.56 s pytest duration (7.0566 s subprocess elapsed). No warnings were printed; stderr is empty. [targeted.xml](evidence/targeted.xml) and [pytest_verified.json](evidence/pytest_verified.json) independently enumerate passing cases. The targeted-green prerequisite was satisfied before full regression started. No failures were repaired.

## 5. Combined collision probe

**EVIDENCE — frozen text, `BIM001_ACCEPTANCE_SPEC.md:115`:**

**AC-35 — Per-page values.**
Check: `url`, `status`, `ok`, `elapsed_s`, `error` are **identical** to the same page's entry in `outputs/run_summary.json` · `slug` is the filename stem actually used, suffix included · `outcome` ∈ `{"captured", "blocked", "failed", "unsupported"}` · when `outcome == "captured"`: `html_file == "html/<slug>.html"`, `html_bytes` is an int equal to the file size, `reason is None` · otherwise `html_file is None`, `html_bytes is None`, `reason` is a non-empty string · `md_file` is `"pages/<slug>.md"` relative to `outputs/` when bim000 wrote the markdown file, else `None`.

**EVIDENCE — actual persisted path first:** [collision run](evidence/artifact_cases/collision/outputs/CyberizeGroup/runs/2026-09-06T09-00-46Z); [fixture.json](evidence/artifact_cases/collision/fixture.json); [invocation.json](evidence/artifact_cases/collision/invocation.json); [probe command](evidence/probe_collision.command.json). Real main/capture/close path; process exit **0**; three browser-result calls; three HTML write attempts, three distinct preserved files.

| URL | Manifest slug | html_file | Actual md_file |
|---|---|---|---|
| `https://example.invalid/x/` | `example-invalid-x` | `html/example-invalid-x.html` | `pages/example-invalid-x.md` |
| `https://example.invalid/x` | `example-invalid-x-2` | `html/example-invalid-x-2.html` | `pages/example-invalid-x.md` |
| `http://example.invalid/x` | `example-invalid-x-3` | `html/example-invalid-x-3.html` | `pages/example-invalid-x.md` |

The HTML bodies are `<p>first É</p>`, `<p>second\r\n</p>` and `<p>third</p>` (the middle body contains actual CRLF bytes). All three files equal their exact fixture UTF-8 bytes, without newline normalization. The serialized and reloaded manifest maps all three URLs correctly. Its write count/file count is 3/3. There is exactly one legacy markdown file, containing `third markdown`, confirming BIM000 overwrite behavior.

**Literal AC-35 comparison:** Second collision's actual `md_file` is `pages/example-invalid-x.md`; the literal `pages/<slug>.md` equation requires `pages/example-invalid-x-2.md`. The third similarly differs. This is a persisted, independently reproduced discrepancy, not a hypothetical source inference. All other checked page fields match the frozen summary and HTML artifact rules.

**Separate prior-ruling context:** `BIM001_plan_2026-09-06.md:135` proposes recording the markdown file actually written; `session_2026-09-06.md:40` records **“I-2 record file actually written.”** Frozen front-door R1 keeps markdown behavior, while R4 requires HTML suffixes. No QA erratum has been applied to the frozen spec. AC-23 is independently proven; AC-35 is **PASS-PENDING-ADJUDICATION**, with the literal equation mismatch explicitly preserved for SOL.

Source behavior: `smart_crawler/crawler.py:170–179` (markdown), `:238–251` (HTML suffix/write), `:367–385` (base md_file independently supplied alongside suffixed HTML slug). No implementation was changed.

## 6. Write-failure probe

**EVIDENCE:** [write_failure run](evidence/artifact_cases/write_failure/outputs/CyberizeGroup/runs/2026-09-06T09-00-47Z); [fixture](evidence/artifact_cases/write_failure/fixture.json); [invocation](evidence/artifact_cases/write_failure/invocation.json); [command/exit](evidence/probe_write_failure.command.json); [stdout](evidence/probe_write_failure.stdout.txt).

The QA-only wrapper raises `OSError("QA injected HTML write failure")` for the first `RunFolder.save_html` call and delegates the next call to the original writer. It leaves the rest of the actual run/close path unchanged. First page: `outcome="failed"`, `reason="write failed: QA injected HTML write failure"`, HTML fields null, no file. Second page: `captured` with exact fixture bytes. Both input URLs are attempted. Both legacy markdown results remain `ok: true`. The process exits **0**, matching the normal two-page subprocess's exit 0; it does not crash or change normal exit semantics. Absences record exactly the first failed page/reason; run end is written. AC-28 **PASS**.

## 7. AC-32 hostname/netloc probe

**EVIDENCE:** [port run](evidence/artifact_cases/port/outputs/CyberizeGroup/runs/2026-09-06T09-00-49Z); [fixture](evidence/artifact_cases/port/fixture.json); [command](evidence/probe_port.command.json). Input URLs:

```text
https://example.invalid:8443/port
https://example.invalid/plain
```

Actual persisted `input_hosts`:

```json
["example.invalid", "example.invalid:8443"]
```

Literal sorted unique hostnames:

```json
["example.invalid"]
```

**FAIL — literal requirement independently disproven.** AC-32 (`BIM001_ACCEPTANCE_SPEC.md:102`) says “`input_hosts` is the sorted list of unique hostnames across all input URLs.” Source `smart_crawler/crawler.py:316` uses `urlparse(u).netloc`, retaining the explicit port. This probe uses controlled stubs only; no endpoint was contacted. Other identity fields—including exact reconstructed argv string, input_path, project, run_dir, summary_path and run_id—passed. No hostname-specific erratum was found. Existing I-4 concerns command reconstruction, not netloc/hostname equivalence.

## 8. Empty-HTML edge probe

**EVIDENCE:** [empty_html run](evidence/artifact_cases/empty_html/outputs/CyberizeGroup/runs/2026-09-06T09-00-50Z); [fixture](evidence/artifact_cases/empty_html/fixture.json); [invocation](evidence/artifact_cases/empty_html/invocation.json). Stub explicitly has `status_code=200`, `success=True`, and an existing `html` attribute equal to `""`. Result:

```json
{"outcome":"unsupported","reason":"no html in result","html_file":null,"html_bytes":null}
```

Process exits 0, markdown is written, HTML directory is empty, and absences contains the attempted unsupported page. Source `crawler.py:150` converts the empty string to None; `:375–376` chooses unsupported.

**Literal observation:** AC-20 (`spec:57–58`) says a file exists “where `result.html` is present.” The attribute is present in this fixture, yet no file exists. Ordinary nonempty successful captures passed independently. **QUESTION:** SOL must interpret “present” for an existing empty attribute. AC-20 is **PASS-PENDING-ADJUDICATION** to preserve that unresolved wording question; this is not a final interpretation or an exception grant.

## 9. Full regression root

**EVIDENCE — `venv/bin/pytest -q`**, cwd `/home/moose/python/stark-web-factory-scrapper-v1`, exit **0**, elapsed 8.583 s. Exact execution context: [regression_root.command.json](evidence/regression_root.command.json).

stdout: [regression_root.stdout.txt](evidence/regression_root.stdout.txt)

```text
......................................................                   [100%]
- generated xml file: /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/regression_root.xml -
54 passed in 8.12s
```

stderr: [regression_root.stderr.txt](evidence/regression_root.stderr.txt)

```text
(empty)
```

**EVIDENCE — context:** Existing repo `venv/bin/pytest`, cwd repository root. `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=<QA>/evidence/tmp`, `PYTHONPATH=<repo>`. `PYTEST_ADDOPTS` contains only `-p no:cacheprovider`, QA-lane `--basetemp`, and QA-lane `--junitxml`; the exact values are in the command JSON. These isolate QA files without changing test assertions or selecting out tests. **54 passed in 8.12s**, 0 failures/errors/skips; stderr empty and no warnings printed. JUnit: [regression_root.xml](evidence/regression_root.xml).

## 10. Full regression /tmp

**EVIDENCE — `/home/moose/python/stark-web-factory-scrapper-v1/venv/bin/pytest -q /home/moose/python/stark-web-factory-scrapper-v1/tests`**, cwd `/tmp`, exit **0**, elapsed 8.1285 s. Exact execution context: [regression_tmp.command.json](evidence/regression_tmp.command.json).

stdout: [regression_tmp.stdout.txt](evidence/regression_tmp.stdout.txt)

```text
......................................................                   [100%]
- generated xml file: /home/moose/python/stark-web-factory-scrapper-v1/agent_docs/ACTION/web-factory-p1-bim001/QA/evidence/regression_tmp.xml -
54 passed in 7.63s
```

stderr: [regression_tmp.stderr.txt](evidence/regression_tmp.stderr.txt)

```text
(empty)
```

**EVIDENCE — context:** Cwd is exactly `/tmp`; absolute `<repo>/venv/bin/pytest -q <repo>/tests`, `PYTHONPATH=<repo>`, existing venv. Same bytecode/cache controls; distinct QA-lane basetemp and JUnit destinations. **54 passed in 7.63s**, 0 failures/errors/skips; stderr empty and no warnings printed. JUnit: [regression_tmp.xml](evidence/regression_tmp.xml). No QA temporary tree or test log was placed in `/tmp`; `/tmp` was only the execution cwd.

## 11. BIM000 14-test regression proof

**EVIDENCE:** All 14 exact baseline function names are present as passing cases in both full JUnit records. This is case-level proof, not an inference from total counts. [bim000_passing_proof.json](evidence/bim000_passing_proof.json) cross-matches every baseline function and its exact unchanged Assert text. **47 Assert statements are source-identical to main**. `tests/test_discover.py` and `tests/test_sitemap_utils.py` remain unchanged.

| Exact BIM000 test | Current source | Root | /tmp | Unchanged assertions |
|---|---|---|---|---:|

| `test_403_and_500_write_no_file_and_are_recorded` | `tests/test_crawler.py:65` | PASS | PASS | 10 |

| `test_three_consecutive_429_stop_the_run` | `tests/test_crawler.py:87` | PASS | PASS | 5 |

| `test_blocked_counter_resets_on_success` | `tests/test_crawler.py:97` | PASS | PASS | 1 |

| `test_pause_between_pages_not_before_first` | `tests/test_crawler.py:108` | PASS | PASS | 2 |

| `test_limit_and_input_flags` | `tests/test_crawler.py:115` | PASS | PASS | 4 |

| `test_session_user_agent_on_sitemap_calls` | `tests/test_crawler.py:127` | PASS | PASS | 5 |

| `test_import_from_foreign_cwd_creates_no_directory` | `tests/test_crawler.py:146` | PASS | PASS | 1 |

| `test_empty_input_writes_truthful_summary_without_crawling` | `tests/test_crawler.py:152` | PASS | PASS | 6 |

| `test_is_valid_link_rejects_empty_mailto_tel_and_fragments` | `tests/test_discover.py:7` | PASS | PASS | 5 |

| `test_is_valid_link_accepts_relative_and_same_domain_only` | `tests/test_discover.py:15` | PASS | PASS | 3 |

| `test_normalize_link_strips_fragment_and_query_and_resolves_relative` | `tests/test_discover.py:21` | PASS | PASS | 2 |

| `test_flat_sitemap_returns_all_locs` | `tests/test_sitemap_utils.py:25` | PASS | PASS | 1 |

| `test_sitemap_index_follows_child_sitemaps` | `tests/test_sitemap_utils.py:33` | PASS | PASS | 1 |

| `test_unparseable_sitemap_returns_empty` | `tests/test_sitemap_utils.py:41` | PASS | PASS | 1 |

### AC-71 — literal amendment evidence first

**EVIDENCE — frozen text, `BIM001_ACCEPTANCE_SPEC.md:165`:**

**AC-71 — Permitted amendments only.**
Check: the only permitted edits to bim000 test files are: (a) the `sandbox` fixture additionally redirects the run-root constant to `tmp_path`; (b) any bim000 test that invokes `main()` with argv gains `--project <name>` in that argv; (c) the stub gains an **optional** `html` field defaulting to absent. Each amendment is listed by test name in `CHANGELOG.md`. Anything else is a FAIL.

**EVIDENCE:** [tests_diff.stdout.txt](evidence/tests_diff.stdout.txt) shows these existing infrastructure/function amendments:

- `sandbox` at `tests/test_crawler.py:49`: redirect RUN_ROOT to tmp_path — category (a).
- `test_empty_input_writes_truthful_summary_without_crawling` at `:162`: argv gains `--project TestProj` — category (b), assertions unchanged.
- `_result` at `:17–28`: optional `html=None`, attribute absent by default — category (c).
- **Additional edit:** `FakeCrawler.arun` at `:36–41` replaces direct return of the next result with assignment, `isinstance(result, Exception)`, raise that instance, else return. This is outside the three explicit categories.

**FAIL — literal requirement independently disproven.** The closed edit list says “Anything else is a FAIL.” No existing assertion was weakened, but preservation of assertions does not authorize an additional helper edit.

**Separate engineering/process context:** `CHANGELOG.md:26` records the exception helper under (c); completion report `BIM001_complete_2026-09-06.md:106` calls it helper-only and notes it for SOL. The approved plan's §G (`BIM001_plan_2026-09-06.md:111–120`) lists exactly three permitted amendments and says “No other bim000 test changes.” No explicit AC-71 exception approval was located. SOL can adjudicate this permission discrepancy; QA has neither reverted the helper nor granted an exception.

## 12. Offline artifact/schema proof

**EVIDENCE:** [artifact_results.json](evidence/artifact_results.json) records every independent check and discrepancy; [artifact_supplement.json](evidence/artifact_supplement.json) verifies expected outcome sequences and absence of unmapped HTML files. Each case has fixture.json, input.json, invocation.json, persisted `outputs/` artifacts, and `verification_<run_id>.json`. [artifact_file_listing.txt](evidence/artifact_file_listing.txt) enumerates them. Console/exit evidence is in `probe_<case>.*`; raw outputs are not collapsed or replaced.

| Offline case | Process exit | Attempted outcome sequence | Evidence |
|---|---:|---|---|

| normal | 0 | captured, captured | [normal run](evidence/artifact_cases/normal/outputs/CyberizeGroup/runs/2026-09-06T09-00-39Z) |

| empty | 0 | none (empty input) | [empty run](evidence/artifact_cases/empty/outputs/CyberizeGroup/runs/2026-09-06T09-00-41Z) |

| limit | 0 | captured, captured | [limit run](evidence/artifact_cases/limit/outputs/CyberizeGroup/runs/2026-09-06T09-00-42Z) |

| stop | 2 | blocked, blocked, blocked | [stop run](evidence/artifact_cases/stop/outputs/CyberizeGroup/runs/2026-09-06T09-00-43Z) |

| mixed | 0 | captured, blocked, failed, failed, unsupported, captured, failed | [mixed run](evidence/artifact_cases/mixed/outputs/CyberizeGroup/runs/2026-09-06T09-00-45Z) |

| collision | 0 | captured, captured, captured | [collision run](evidence/artifact_cases/collision/outputs/CyberizeGroup/runs/2026-09-06T09-00-46Z) |

| write_failure | 0 | failed, captured | [write_failure run](evidence/artifact_cases/write_failure/outputs/CyberizeGroup/runs/2026-09-06T09-00-47Z) |

| port | 0 | captured, captured | [port run](evidence/artifact_cases/port/outputs/CyberizeGroup/runs/2026-09-06T09-00-49Z) |

| empty_html | 0 | unsupported | [empty_html run](evidence/artifact_cases/empty_html/outputs/CyberizeGroup/runs/2026-09-06T09-00-50Z) |

| two_runs | 0 | captured | [two_runs run](evidence/artifact_cases/two_runs/outputs/CyberizeGroup/runs/2026-09-06T09-00-52Z) |

**EVIDENCE — independently verified for the generated artifacts as applicable:**

- Exact direct RUN_DIR children are `html/`, `manifest.json`, `stage_log.txt`, `absences.json`; nothing else. Verification files and invocation records are outside RUN_DIR.
- Exact 23 manifest top-level keys and 11 per-page keys; fixed schema/access rung/fallbacks, true wait_for_images, delay 3.0, timeout 90000, pause [2,5], crawl4ai 0.9.3, playwright 1.52.0, Python 3.12 prefix.
- Case-preserved project, UTC run ID regex and equal started instant, exact logical run_dir/summary_path, exact invoked argument reconstruction, resolved input_path, count before limit, nullable limit, actual attempt counts, stopped_early, timestamp equality with summary. **Exception:** the explicit-port case disproves literal input_hosts hostnames, documented in §7.
- Exact frozen five-key summary and five-key page records, and identical values for URL/status/ok/elapsed/error between summary and manifest.
- Captured HTML path/slug relation, integer html_bytes equal to on-disk bytes, null reason; noncaptured null HTML fields and nonempty reason. **Exception:** collision md_file stems differ from the literal AC-35 equation, documented in §5.
- Absences list type, exact three keys, allowed outcomes, complete disjoint captured/absent coverage for the unique fixture URLs, attempted-absent entries first then unattempted in input order. Mixed noncaptures have reasons identical to the manifest. Stop fixture combines **3 attempted blocked + 2 stop_rule skipped + 2 limit skipped**. Limit fixture has exactly 2 limit-skipped absences. No deduplication assumptions were needed for these fixtures.
- Stage logs decode UTF-8; all lines have timestamp prefixes, correct start/project/run_id, one matching outcome event per attempt, stop line only when applicable, and run end. Exact line counts checked.
- Nonempty successful HTML—including `É`, literal `&amp;`, CRLF, spaces and final newline—equals the stub's exact UTF-8 byte sequence. Per-file size, SHA-256 and hexadecimal bytes are preserved in verification files. Failed/blocked/exception/missing-HTML/write-error pages have no HTML file; there are no unmapped extras.
- Markdown-independent capture succeeds with empty fit/raw markdown while legacy ok remains false/error `empty markdown`. Markdown remains at the BIM000 path with its unchanged strip/overwrite behavior.

**EVIDENCE — two runs:** [two_run_proof.json](evidence/artifact_cases/two_runs/two_run_proof.json) records distinct IDs `2026-09-06T09-00-52Z` and `2026-09-06T09-00-54Z`; the first manifest's before/after SHA-256 is `fc4633932cd49f3cc76fb75b3f3722e8b4cbd0552e4814d80989f3d50aa7087b` in both snapshots. The first summary was copied outside RUN_DIR before the second overwrote the legacy summary. The targeted two-run test also passed. No clock or run-ID implementation was changed.

**GAP:** These are controlled offline specimens, not live Crawl4AI browser-response evidence. AC-21's required live size check and all AC-74 live conditions remain unexecuted. The empty-but-present HTML interpretation is explicitly pending, not included as a proven AC-20 success.

## 13. AC-by-AC status update

Statuses apply to all **52** frozen ACs, using the requested vocabulary. PASS means independent evidence for the prescribed check within its stated evidentiary scope. PASS-PENDING-ADJUDICATION never means the literal discrepancy disappeared. UNTESTED can retain partial offline evidence when a required live clause has not run. Source AC titles/wording remain frozen; the prior recon preserves them verbatim.

| AC | Status | Independent evidence / remaining issue |
|---|---|---|

| AC-01 | PASS | Real help subprocess and passing optional-parser test; cli_help + targeted XML. |

| AC-02 | PASS | Real missing-project exit 2, unchanged actual outputs; constructor seam 0 calls plus targeted trap. |

| AC-03 | PASS | cli_missing_project.stderr.txt contains exact --project is required. |

| AC-04 | PASS | Same stderr contains exact canonical example. |

| AC-05 | PASS | Same stderr contains exact help pointer. |

| AC-06 | PASS | Both actual invalid-name subprocesses, exact messages/exits/no outputs; regex and length tests pass. |

| AC-07 | PASS | Fresh CyberizeGroup case preserved in physical sandbox project folder and manifest; targeted test. |

| AC-08 | PASS | Real help keeps input/limit; real limit-zero argparse error/exit 2. |

| AC-10 | PASS | Every fresh RUN_DIR exact four children; layout tests pass. |

| AC-11 | PASS | Every fixture run ID matches regex, folder and UTC started instant. |

| AC-12 | PASS | Literal mkdir grep/AST scopes; unchanged foreign-CWD import test passes root and /tmp. |

| AC-13 | PASS | Fresh empty-input main subprocess exits 0, empty artifacts/full summary/nonempty log, zero browser constructions. |

| AC-14 | PASS | Two fresh consecutive runs distinct; first manifest before/after bytes identical. |

| AC-20 | PASS-PENDING-ADJUDICATION | Nonempty success captures pass; present html="" is unsupported/no file. Meaning of present deferred to SOL (§8). |

| AC-21 | UNTESTED | Offline Unicode/CRLF exact-byte checks pass; required live captured-page size comparison not run. |

| AC-22 | PASS | One slugify definition; noncolliding HTML/markdown stem test passes. |

| AC-23 | PASS | Three colliding URLs, three writes/files/distinct byte contents and persisted manifest mapping (§5). |

| AC-24 | PASS | 403 stub blocked and no HTML; mixed artifacts and targeted test. |

| AC-25 | PASS | 500 and arun exception failed/no HTML; exception-prefixed reason preserved. |

| AC-26 | PASS | Missing html attribute unsupported/no file/reason contains html; no AttributeError. |

| AC-27 | PASS | Fresh HTML with empty markdown captured while summary ok false/empty markdown. |

| AC-28 | PASS | Injected writer failure records failed/write reason; next URL captured; process exit unchanged at 0. |

| AC-30 | PASS | Exact 23-key manifests independently deserialized for all run cases. |

| AC-31 | PASS | All fixed values and types match; existing environment freeze/check also clean. |

| AC-32 | FAIL | Explicit port remains in input_hosts netloc; literal unique hostnames disproven (§7). |

| AC-33 | PASS | Counts match full input/limit/attempted slices, including combined stop/limit fixture. |

| AC-34 | PASS | Every persisted page has exact 11 keys. |

| AC-35 | PASS-PENDING-ADJUDICATION | All tested fields pass except literal collision md_file equation; actual file recorded per I-2, SOL ruling pending (§5). |

| AC-36 | PASS | Exact started_at/finished_at strings equal fresh legacy summaries. |

| AC-37 | PASS | Normal/empty/three-blocked all persist manifest; early stop true and exit 2. |

| AC-40 | PASS | Fresh absences list/exact keys/allowed outcomes. |

| AC-41 | PASS | Fresh absence completeness, disjointness and exact order against fixture input. |

| AC-42 | PASS | Combined stop fixture distinguishes 2 stop_rule and 2 limit skips; dedicated unit test passes. |

| AC-43 | PASS | Every attempted absence reason equals corresponding persisted manifest reason. |

| AC-50 | PASS | Logs exist, UTF-8 decode, timestamp prefix every line. |

| AC-51 | PASS | Logs have exact start/end, per-attempt outcomes, and stop marker when applicable. |

| AC-60 | PASS | Source constants/key sets, 47 unchanged baseline asserts, fresh summaries and both regression runs. |

| AC-61 | PASS | Full save_markdown source equal to main; fresh normal and collision legacy markdown artifacts. |

| AC-62 | PASS | Exact four source literal hit counts and unchanged 2,5 pacing pair; passing config regression. |

| AC-63 | PASS | Actual negative CLI exits 1/2, offline normal exit 0 and early-stop exit 2. |

| AC-70 | PASS | 14 exact baseline names passed in both JUnit records; 47 assertion statements source-identical. |

| AC-71 | FAIL | FakeCrawler.arun exception-raising edit exceeds the three literal permitted categories (§11). |

| AC-72 | PASS | 39 new AC-named functions / 40 selected items; all prescribed named coverage exists and passes. |

| AC-73 | PASS | Root 54 passed in 8.12s; /tmp absolute venv + repo PYTHONPATH 54 passed in 7.63s. |

| AC-74 | UNTESTED | No live crawl authorized or executed; entirely untested. |

| AC-80 | PASS | Canonical command count 1 in each doc and exact missing-project stderr example. |

| AC-81 | PASS | RUN_NOTES.md:160 explicit two-file compatibility/run-record sentence. |

| AC-82 | PASS | BIM001 changelog lists every prescribed topic/no pin changes/named amendments; AC-71 permission remains separate. |

| AC-90 | PASS-PENDING-ADJUDICATION | Full surface known; RECOVERY.md outside literal list. Per instruction, final surface disposition held for SOL (§2). |

| AC-91 | PASS | Freeze byte-equal to unchanged lock; pip check exit 0, No broken requirements found. |

| AC-92 | PASS-PENDING-ADJUDICATION | Literal grep nonzero: source metadata key/lookup plus two binary-cache matches. No Playwright import; I-1 context separate (§2). |

| AC-93 | PASS | Repository check: six matching baseline author identities, no report records agent mutating git execution. Does not authenticate actors (§2). |

**Counts:** **PASS: 44**, **FAIL: 2**, **UNTESTED: 2**, **BLOCKED: 0**, **PASS-PENDING-ADJUDICATION: 4**. Total **52 ACs**.

## 14. Discrepancies requiring SOL adjudication

1. **RED FLAG — AC-32 literal FAIL:** explicit-port URL produces netloc with port instead of hostname. This is a demonstrated persisted data mismatch. No applicable hostname exception found. Do not use the normal live site's lack of ports to erase this result.
2. **RED FLAG — AC-71 literal FAIL:** additional existing FakeCrawler.arun exception-simulation edit exceeds closed categories. Its usefulness and passing regressions do not grant permission. Engineering acknowledgement and approved-plan context are separate in §11.
3. **QUESTION — AC-35 / I-2:** persisted collision md_file fails the literal suffixed equation but follows recorded I-2 and unchanged markdown behavior. SOL must adjudicate; frozen spec and erratum lane untouched.
4. **QUESTION — AC-92 / I-1:** exact grep is nonzero; no direct Playwright import. I-1 approval is recorded by Engineering; source result, implementation fact, and approval provenance remain separate. Binary cache stderr is preserved without cleanup.
5. **QUESTION — AC-90:** RECOVERY.md is outside the frozen list; process documentation calls for its update. No automatic process exemption or final surface PASS/FAIL issued in this stage.
6. **QUESTION — AC-20:** existing empty html attribute results in no file. Resolve “present” wording before an unqualified grade; no final interpretation issued here.
7. **GAP — AC-21/74 live evidence:** no live capped smoke or live byte-size proof. Historical engineering 10/10 smoke remains CLAIM, not this QA session's evidence.
8. **GAP — recon source context:** the phase map and Web Factory doctrine journal were unavailable in the prior recon; no new authoritative versions or signed exception text were supplied in this stage. The on-disk session approval record remains the available I-1/I-2 provenance.
9. **GAP — actor provenance:** git author strings match baseline; available reports record no agent mutation. That check cannot establish who physically ran git. No unsupported identity claim is made.

**EVIDENCE:** Targeted and full automated suites are green, but they did not expose the independent hostname edge mismatch or resolve literal edit/surface/import/collision wording issues. No repairs or contract changes were made to reconcile them.

## 15. Readiness recommendation for live AC-74 smoke

**Recommendation: do not proceed to live smoke yet.** Offline execution is complete and reviewable; send this evidence to SOL for the two literal failures and four pending-adjudication criteria. SOL/Director should decide disposition and whether to authorize AC-74 on this specimen or require a new candidate. If a new candidate is supplied, re-pin and scope repeat QA to its changes. This is a readiness recommendation, not Gate Q.

Only after explicit SOL authorization: reverify discovery input identity/count, then run a fresh capped CyberizeGroup smoke and capture the remaining AC-21 live size check plus every AC-74 artifact/count/prefix condition. No live crawl was executed in Stage 2.
