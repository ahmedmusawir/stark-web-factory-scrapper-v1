# ENGINEERING REPAIR — BIM001 — QA Stage 2 rulings — 2026-09-06_1528

**Branch (read-only):** `qa/web-factory-p1-bim001` · **Candidate before repair:** `657e25e9191e5d91a822a49301c0260bde8f1bd4` (verified) · **Engineer:** Claudy · **Scope:** surgical repair per Architect Fable's adjudication. Not a QA verdict; no Gate Q; no certification.

## Files changed (`git diff --name-only`)
```
CHANGELOG.md
smart_crawler/crawler.py
tests/test_crawler.py
```
`git diff --stat`: CHANGELOG.md +2/−1 · smart_crawler/crawler.py +2/−1 · tests/test_crawler.py +22/−10. Nothing else touched. Session log / RECOVERY.md deliberately **not** updated in this cycle because the repair prompt restricts edits to the three files above; if the Director wants the protocol entries, say so and I will add them as a separate step.

## AC-32 fix (exact)
`smart_crawler/crawler.py`, function `input_hosts`:
```diff
-    return sorted({urlparse(u).netloc for u in urls})
+    """Sorted unique hostnames of the input URLs (hostname, not netloc: no ports; None skipped)."""
+    return sorted({h for h in (urlparse(u).hostname for u in urls) if h})
```
Semantics: `urlparse(u).hostname` (no port, lower-cased by the stdlib), `None` hostnames skipped, output sorted unique. `https://example.invalid:8443/port` + `https://example.invalid/plain` → `["example.invalid"]`. No other product behavior changed.

## AC-71 fix (exact)
1. `tests/test_crawler.py::FakeCrawler` — the whole class restored **byte-for-byte** to `main` (the extra Exception-raising branch removed).
2. New bim001-only subclass, placed under the bim001 chunk-3 section header:
```python
class RaisingFakeCrawler(FakeCrawler):
    """bim001-only test infrastructure: like FakeCrawler, but an Exception instance in the
    results list is raised from arun() instead of returned (simulates a crawl4ai failure)."""

    async def arun(self, url, config=None):
        result = await super().arun(url, config)
        if isinstance(result, Exception):
            raise result
        return result
```
3. `_crawl()` helper gains `crawler_cls=FakeCrawler`; `test_ac25_failed_and_exception_no_html` passes `crawler_cls=RaisingFakeCrawler`. It was the **only** test relying on Exception objects in results (grep for `RuntimeError`/`Exception(`: one site, line 437 pre-repair).
4. bim000 tests: no behavior change beyond a/b/c. All 14 names present; `git diff main -- tests/` shows 0 removed `assert` lines.
5. `CHANGELOG.md` amendment list now reads exactly (a) sandbox `RUN_ROOT` redirection, (b) test 8 argv gains `--project`, (c) optional `html` on the stub. The sentence about `FakeCrawler.arun` raising was removed from (c). `RaisingFakeCrawler` is described in the repair note as bim001-only infrastructure, not an amendment.

## Tests changed
- `test_ac32_manifest_identity_values` — extended: inputs add `https://example.invalid:8443/port` and `https://example.invalid/plain`; asserts `input_hosts == ["a.example.com", "b.example.com", "example.invalid"]`, `"example.invalid:8443" not in input_hosts`, direct `input_hosts([...port..., ...plain...]) == ["example.invalid"]`, and that a non-URL string (hostname `None`) is skipped.
- `test_ac25_failed_and_exception_no_html` — now uses `RaisingFakeCrawler`; assertions unchanged.
- `_crawl` helper — optional `crawler_cls` parameter.
- No test added or removed; item count unchanged.

## FakeCrawler main-equivalence proof (read-only)
```
diff <(git show main:tests/test_crawler.py | awk '/^class FakeCrawler:/{f=1} f&&/^@pytest.fixture/{exit} f') \
     <(awk '/^class FakeCrawler:/{f=1} f&&/^@pytest.fixture/{exit} f' tests/test_crawler.py)
→ (no output) IDENTICAL
```

## Test results
| Run | Command | Result |
|---|---|---|
| Targeted | `venv/bin/pytest -q tests/test_crawler.py -k "ac25 or ac32 or ac41 or ac43 or ac35"` | `5 passed, 43 deselected in 2.03s` |
| Root regression | `venv/bin/pytest -q` | `54 passed in 7.30s` |
| /tmp regression | `cd /tmp && PYTHONPATH=<repo> <repo>/venv/bin/pytest -q <repo>/tests` | `54 passed in 7.48s` |
Count unchanged at 54 (no new parametrization).

## Confirmations
- **No live crawl.** No network command was run. The only run folder under `outputs/CyberizeGroup/runs/` is `2026-09-06T07-30-16Z`, the P3 smoke from 13:30 local today, predating this repair. `outputs/` is gitignored and was not touched.
- **No git mutation.** Only `git branch --show-current`, `git rev-parse`, `git status`, `git diff`, `git show main:…` were run.
- Rulings honoured with **no implementation change**: AC-35 (I-2, `md_file` = file actually written), AC-92 (I-1, metadata lookup kept), AC-90 (RECOVERY.md untouched), AC-20 (empty `html` stays `unsupported / no html in result`; no zero-byte files — already the behavior: `getattr(result, "html", None) or None`).

## Unexpected findings
None. One observation for QA's erratum lane: `urlparse().hostname` lower-cases the host, so a mixed-case input host now appears lower-cased in `input_hosts` (netloc preserved case). This follows from the ruling's "hostname" semantics; flagging so the erratum wording can cover it if a grader compares against raw input text.

**Repair complete — ready for QA re-pin and re-execution. Not a PASS; SOL owns Gate Q.**

```
🔔 GIT REMINDER — uncommitted on qa/web-factory-p1-bim001:
   M CHANGELOG.md
   M smart_crawler/crawler.py
   M tests/test_crawler.py
  ?? agent_docs/ACTION/web-factory-p1-bim001/QA/   (Cody's artifacts + this report)
→ Your call. I will not run it.
```
