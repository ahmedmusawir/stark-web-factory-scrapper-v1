"""LEAD-02 supplemental 48-row acceptance matrix generator.

Executor: Claudy (Claude Code, Claude Fable 5). Reads the historical Q2 matrix
rows UNCHANGED (first seven columns reproduced verbatim as the preserved
baseline) and appends two retest columns: the LEAD-02 baseline adjudication and
this retest's measurement with evidence and reuse justification. Reuse of
unaffected evidence is justified by the repaired-candidate diff: exactly four
paths changed (recon_pipeline/decide.py, tests/test_decide.py,
prepare_saved.py, test_prepare_saved.py; g0-identity/g0_retest_identity.json),
so collector/transport/REST/reader/inventory behavior is byte-identical to the
Q2-measured candidate. Writes argv[1].
"""
import re
import sys
from pathlib import Path

LANE = Path(__file__).resolve().parents[1]
Q2 = LANE.parent/'Q2_2026-10-16_142632/matrix/AC_EVIDENCE_MATRIX.md'

REUSE = ('REUSED (unchanged evidence): candidate diff touches only decide/prepare '
         'and their tests; this AC’s measured surface is byte-identical '
         '(`g0-identity/g0_retest_identity.json`). Six-module rerun also passed (144/144).')

RETEST = {
    'AC-007': ('T-06/O6 title guard: **FAIL** (CTA supplied/replaced titles)',
               '**PASS** - arrow/decoration variants all declined for supply and replacement in both orders; '
               'informative Unicode titles byte-exact; stable IDs; UNDECIDED; provenance retained '
               '(`r1/r1_title_guard_result.json`); full Q2 T-06 recheck incl. 36/36 raw-anchor titles '
               'repeats clean with arrow finding gone (`r1/t06_t14_retest_result.json`).'),
    'AC-008': ('T-06/O6 title guard: **FAIL**',
               '**PASS** - same evidence as AC-007; T-14 twin agreement re-verified on repaired snapshot.'),
    'AC-021': ('C1 final-heading obligation: **FAIL as delivered** (reviewed rendition missing)',
               '**PASS** - initial helper output reproduces the O5 limitation and is preserved; NEW reviewed '
               'rendition restores the heading to main content with paragraphs/CTA kept, nav/footer separated, '
               'index/hash/provenance updated, raw bytes unchanged (`c1/c1_article_review_result.json`). '
               'O5 helper limitation itself remains OPEN (no helper code change, per LEAD-02).'),
    'AC-022': ('C1 final-heading obligation: **FAIL as delivered**',
               '**PASS** - reference resolution re-verified in the reviewed rendition (same evidence as AC-021).'),
    'AC-041': ('C2 limit triggers + O2: **NOT RUN**',
               '**PASS** - max_requests=1 (request_limit, 1 attempt persisted, second pending), tiny deadline '
               '(in-flight: request_error/TimeoutError cancellation at deadline - OBSERVATION on stop labeling; '
               'pre-dispatch: time_limit), small byte allowance (persisted_byte_limit post-receipt with +65536 '
               'overhead estimate; crossing body not persisted). O2 actual directory bytes incl. .writer.lock '
               'and .runtime-by-name recorded (`c2/c2_limit_fixtures_result.json`).'),
    'AC-042': ('C2 limit triggers + O2: **NOT RUN**',
               '**PASS** - same evidence as AC-041; estimate/post-receipt semantics documented, no wire-byte or '
               'instantaneous-cancellation guarantee claimed.'),
    'AC-043': ('T-23 B1/B2 inert presentation: **FAIL** (B3 accepted as data)',
               '**PASS** - B1/B2 emitted as backslash-escaped literals at the converter boundary in page AND '
               'boilerplate; markdown-it-py 4.2.0 commonmark/default, html on/off: 0 script elements, 0 active-scheme '
               'destinations, B1/B2 readable; controls (headings/lists/emphasis/links/Unicode) intact; B3 retained '
               'as untrusted JSON data (`r2/r2_inert_boundary_result.json`); full T-23 instrument rerun clean '
               '(`regression/t23_retest_result.json`).'),
    'AC-044': ('Accepted (export hygiene separate from AC-043)',
               '**PASS (re-verified)** - 9/9 checker controls meet expectations in dir and zip modes; no matched '
               'values echoed (`regression/t23_retest_result.json`).'),
    'AC-011': ('C3 rich-native sub-obligation: **NOT DEMONSTRATED**',
               '**PASS** - one controlled loopback native capture: rich formatted UTF-8 JSON (Unicode, tabs/blank '
               'lines, content, yoast SEO, nested unknown keys) saved byte-identical to served entity; no _fields '
               'on the selected URL or any observed query; synthetic Set-Cookie excluded from metadata '
               '(`c3/c3_rich_native_rest_result.json`). Suite-mapped + Q2 native evidence otherwise reused.'),
    'AC-012': ('C3 rich-native sub-obligation: **NOT DEMONSTRATED**',
               '**PASS** - same capture as AC-011 (byte fidelity of the complete saved entity).'),
    'AC-013': ('C3 rich-native sub-obligation: **NOT DEMONSTRATED**',
               '**PASS** - same capture as AC-011 (header allowlist honored; set-cookie absent).'),
    'AC-025': ('C3 rich-native sub-obligation: **NOT DEMONSTRATED**',
               '**PASS** - rich-payload REST fidelity demonstrated natively (`c3/`); T-15 suite checks reused.'),
    'AC-034': ('T-20 accepted as bounded consumer check',
               'REUSED with justification: consumer packet content is the HISTORICAL prepared packages, which are '
               'byte-unchanged on disk (fixtures 34/34, `g0-identity/`); the repair alters only NEWLY prepared '
               'Markdown (added escapes). No consumer content/structure/navigation change invalidates T-20; no new '
               'cold-read round per LEAD-02 §5.'),
    'AC-035': ('T-20 accepted', 'REUSED - same justification as AC-034.'),
    'AC-038': ('T-20 accepted', 'REUSED - same justification as AC-034.'),
    'AC-045': ('T-24 recorded', 'RE-RECORDED for this retest: identity/diff/source52/fixture rechecks in '
               '`g0-identity/`; this matrix; packaging receipts in `exports/` + RESPONSES report.'),
    'AC-046': ('T-24 recorded', 'RE-RECORDED - same as AC-045.'),
    'AC-048': ('T-24 recorded', 'RE-RECORDED - same as AC-045.'),
}


def main():
    lines = Q2.read_text(encoding='utf-8').splitlines()
    out = ['# AC_EVIDENCE_MATRIX_RETEST — LEAD-02 supplemental (48 IDs)', '',
           'Lane: `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/RETEST_LEAD02_2026-10-16_180559/` '
           '(retest evidence paths lane-relative).',
           'Repaired candidate `0f98bcf095781a3ac7a231c276199224dc531f11` (= execution HEAD); repaired source52 '
           '`6f35cf8d…e986f4`; identity/diff rechecks: `g0-identity/g0_retest_identity.json`.',
           'Executor: Claudy (Claude Code, **Claude Fable 5**; Q2 baseline ran on Opus 5.5 - model switched by '
           'the Director before this retest, same QA seat).',
           'Historical Q2 columns are reproduced VERBATIM from the Q2 matrix and remain the preserved baseline; '
           'LEAD-02 adjudications are restated, not rewritten. **Not a certificate** - JARVIS adjudicates, Tony decides.',
           '',
           '| AC | Title | Test | Q2 measurement (historical, preserved) | LEAD-02 baseline adjudication | Retest measurement / reuse justification |',
           '|---|---|---|---|---|---|']
    count = 0
    for ln in lines:
        m = re.match(r'^\| (AC-\d+) \|', ln)
        if not m:
            continue
        cols = [c.strip() for c in ln.strip().strip('|').split('|')]
        if len(cols) < 10:
            continue  # the standing-findings table also has an AC-001 row
        ac, title, test, q2meas = cols[0], cols[1], cols[5], cols[6]
        base, retest = RETEST.get(ac, ('accepted / unchanged', REUSE))
        out.append(f'| {ac} | {title} | {test} | {q2meas} | {base} | {retest} |')
        count += 1
    out += ['', f'Rows: {count}. Six-module regression on the repaired candidate: **144 passed, 0 failed, '
            '0 errors, 0 skipped** (`regression/six-modules-junit.xml`), new regression tests included in actual totals.',
            '', '## Standing items after retest', '',
            '- O5 helper limitation: OPEN (final-output obligation closed by the reviewed rendition; helper unchanged by design).',
            '- T-10 media completeness, AC-001 clean install, crash/cancellation breadth, hostile-viewer breadth, '
            'external-site access, four historical controller findings: unchanged, explicitly untested (LEAD-02 §5).',
            '- C2 OBSERVATION for the Lead: in-flight deadline cancellation is recorded as stop_reason '
            '`request_error` with item error `TimeoutError`, while pre-dispatch deadline yields `time_limit`; '
            'the run stops at the deadline either way (`c2/c2_limit_fixtures_result.json`).',
            '- T-16 disclosure unchanged: the public Maps embed parameter ships in historical evidence only, '
            'adjudicated at exact locations, never reproduced in authored text.']
    Path(sys.argv[1]).write_text('\n'.join(out)+'\n', encoding='utf-8')
    print(f'rows={count}')
    return 0 if count == 48 else 1


if __name__ == '__main__':
    sys.exit(main())
