# LEAD-03 evidence addendum — report

**Executor:** Claudy, Independent QA (Claude Code, Claude Fable 5). **Not a certificate** — JARVIS reviews; Tony decides. Authority: Tony GO (in-session) + LEAD-03 §3 (unchanged copy in this directory, sha `357a7eb3…d4c1f7`).
**Identity recheck:** HEAD = candidate `0f98bcf…` (no successor commit); repaired source52 `6f35cf8d…e986f4` matches on worktree AND retained snapshot; 0 product paths changed; retest ZIP unchanged (`identity_recheck.json`).

## A1 — C1 artifacts + final index — PASS
- Original collection (checklist → result → raw body) exported with the full hash chain verified; raw body sha equals the LEAD-02-recorded fixture sha (unchanged).
- Initial and reviewed-v1 renditions exported byte-for-byte, untouched; their index references all verify.
- The Lead's finding is CONFIRMED: reviewed-v1 `content.headings=[]` and `boilerplate_locations=[header,header,footer]` still described the initial extraction.
- **`qa-c1-article-reviewed-v2/`** authored (QA derived-material correction, v1 preserved): final `content.headings=['Meaningful Page Title']`, final `boilerplate_locations=[header,footer]`, initial values preserved as labeled initial-extraction metadata, authored reference hashed and labeled. All v2 checks PASS, including the CTA's actual destination (`/book` → `https://example.test/book`, present in the Markdown). (`a1/a1_result.json`)

## A2 — C3 saved chain — PASS
- `checklist.json`, result metadata (path resolved FROM the checklist: `attempts/888f03b3…/a60f27da…/result.json`) and the original saved body exported.
- Chain verified: checklist→result digest, result→body sha/bytes, `body_complete`, completed REST item, URL `http://127.0.0.1:37785/wp-json/wp/v2/posts/1101` with no `_fields`, headers within the allowlist, synthetic cookie value absent.
- Independent reconstruction (labeled, kept apart from the capture) is exactly **1,104 bytes, sha `74310307…f83525`** — matching LEAD-03 §1 — and the ORIGINAL saved body is byte-identical to it. No recapture. (`a2/a2_result.json`)

## A3 — runtime-byte sizing — PASS
- Retained native `.runtime`: 0 regular files across 3 directories (names/sizes only; valid observation, not overhead); zero-byte `.writer.lock`; routine and independent totals agree.
- Sentinel demonstration in a disposable clone of `qa-c2-maxreq1`: a 1,337-byte non-secret sentinel under `.runtime/qa-sentinel/` raises the ACTUAL product sizing routine (`recon_pipeline/collector.py:435`, module sha recorded) by exactly 1,337 bytes; independent `os.walk` sums agree; the writer lock stays in the accounting. `.runtime` itself is not exported.
- The earlier `du -sb` interpretation note is corrected: `du -sb` is apparent-size and equaled the per-file sum here; the product bounds regular-file apparent bytes, not filesystem block usage; no exact ceiling claimed. (`a3/a3_result.json`)

## Qualifications and closeout
- `MATRIX_NOTE.md` qualifies the earlier C1/C2-O2/C3 matrix claims per LEAD-03.
- Nothing rerun: no recon, suite, cold reader, Prepare or capture. No product edits, installs, network or Git mutations. Both historical packages and the retest ZIP preserved and re-verified.
- Writer seat reacquired 19:22 and released at closeout. Owned processes: none started beyond local file work.
- Retain/delete proposals: `RETAIN_DELETE_INVENTORY.md`.
