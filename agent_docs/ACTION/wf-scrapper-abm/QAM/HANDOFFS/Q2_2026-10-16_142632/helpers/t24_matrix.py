"""Q2 T-24 instrument: generate matrix/AC_EVIDENCE_MATRIX.md (48 AC IDs).

Executor: Claudy (Claude Code, Claude Opus 5.5).
Applicability + current obligation are taken verbatim from the reviewed
GOVERNING/CURRENT_TOOL_SCOPE.md crosswalk; original historical status from the
canonical ABM_LEDGER.md rows (read-only; ledger unchanged). Per-test Q2 results
and evidence citations are the Executor's record (TESTS below); every cited
lane path is checked to exist before the matrix is written. Writes the matrix
and prints a JSON summary.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1')
LANE = Path(__file__).resolve().parents[1]
SCOPE = LANE.parent/'WebFactory_Q1_Lead_Review_2026-10-15/GOVERNING/CURRENT_TOOL_SCOPE.md'
LEDGER = REPO/'agent_docs/ACTION/wf-scrapper-abm/ABM_LEDGER.md'

T20 = json.loads((LANE/'t20/t20_result.json').read_text())

# test -> (Q2 measurement, executor, evidence (lane-relative), notes)
TESTS = {
    'T-01': ('PASS (operator path); AC-001 clean-install NOT RUN', 'Opy', ['attempts/t01/t01_record.txt', 'g2-fixtures/restoration_run.txt'],
             '--help x3 exit 0; missing-fixture negative fails on the missing saved input. Snapshot operation only; fresh clone/clean venv untested.'),
    'T-02': ('PASS', 'Opy', ['offline/t02_result.json', 'offline/t02_t03_run.txt'], '13/13 bad-plan classes exit 2, no directory; destination/scope/refresh refusals byte-preserving.'),
    'T-03': ('PASS', 'Opy', ['offline/t03_result.json', 'offline/t03_correction_run.txt'], 'import/list/select/export, binding refusals, offline add zero transport; REST single-item scope closed in T-21. G3 correction recorded.'),
    'T-04': ('PASS', 'Opy', ['native/t04_t07_result.json', 'native/t04_t07_result.run1.json', 'native/selected-collector-evidence/native-denial/timeline.json'],
             'native default gap min 5.0046 s; unlinked route never requested; 429/challenge stop via regression native-denial evidence.'),
    'T-05': ('PASS (suite-mapped)', 'Opy', ['attempts/t22/junit_current.xml', 'attempts/t22/t22_current_suite.txt'], 'exit semantics 0/2/3/130 asserted in the once-only regression; native crash/teardown cancellation unproved (plan §6).'),
    'T-06': ('PASS + FINDING O6', 'Opy', ['offline/t06_t14_result.json', 'offline/t06_t14_labels_run.txt'],
             "O6: candidate() accepts 'Read more →' (U+2192) as a title - supply and replace demonstrated; finding against current behavior, no waiver."),
    'T-07': ('PASS', 'Opy', ['native/t04_t07_result.json', 'native/t04_t07_result.run1.json'], 'rendered != original, Unicode preserved, independent Chromium capture byte-identical; sparse-page refusal preserved honestly (run1).'),
    'T-08': ('PASS (suite-mapped + native)', 'Opy', ['attempts/t22/junit_current.xml', 'native/t21_result.json'], 'REST body byte-identical to served entity (T-21); pagination/identity variants in regression.'),
    'T-09': ('PASS', 'Opy', ['offline/t09_t15_t10_t11_result.json', 'offline/t09_t15_t10_t11_run.txt'], 'Andromeda 6h/7p/15li exact from raw; present-empty REST gap visible; Oct 7/10/11 kept separate; authored claims adjudicated.'),
    'T-10': ('PASS (limited current check); media gap OPEN', 'Opy', ['offline/t09_t15_t10_t11_result.json'], 'image_completeness UNVERIFIED in both packages; historical media discrepancy OPEN outside scope.'),
    'T-11': ('PASS', 'Opy', ['offline/t09_t15_t10_t11_result.json', 'native/t21_result.json'], 'native records coherent; raw/prepared/authored provenance distinguishable.'),
    'T-12': ('PASS', 'Opy', ['offline/t12_result.json', 'offline/t12_t16_t18_run.txt'], 'zero source changes; 4 tamper negatives refused before output.'),
    'T-13': ('PASS + HELPER LIMITATION (O5)', 'Opy', ['offline/t13_result.json', 'offline/t13_t19_run.txt'], '20+9 references resolve + hash-match; synthetic article>header>h1 title routed to BOILERPLATE - helper limitation, not counted as content preservation.'),
    'T-14': ('PASS', 'Opy', ['offline/t06_t14_result.json', 'offline/t09_t15_t10_t11_result.json'], 'twin 36/36 after html.unescape; Agency Services kept category/listing; no site-wide extrapolation.'),
    'T-15': ('PASS', 'Opy', ['offline/t09_t15_t10_t11_result.json', 'native/t21_result.json'], 'post11945 content.rendered present-empty; FIELDS projection excludes content; native full-field fidelity in T-21.'),
    'T-16': ('PASS (key disclosure)', 'Opy', ['offline/t16_result.json'], "initial/reviewed/raw-parent agree; child content UNKNOWN. Evidence quotes the public page's own Google Maps embed parameter (recorded in lane evidence, redacted from authored text)."),
    'T-17': ('PASS (suite-mapped + offline)', 'Opy', ['attempts/t22/junit_current.xml', 'offline/t02_result.json'], 'paginated refresh refused; prior attempt bytes preserved; only .writer.lock new.'),
    'T-18': ('PASS', 'Opy', ['offline/t18_result.json'], 'twins byte-identical; index diffs confined to declared allowlist.'),
    'T-19': ('PASS', 'Opy', ['offline/t19_result.json', 'offline/t19_external_refusal_result.json', 'offline/t19_correction_run.txt'], '35-file delivery tree; external-root refusals visible; O4 boundary recorded.'),
    'T-20': (T20['measurement'], 'Claudy + fresh reader', ['t20/t20_result.json', 't20/reader_response.md', 't20/reader_task.txt', 't20/packet.manifest.json', 't20/packet_check_adjudicated.json'], T20['matrix_note']),
    'T-21': ('PASS', 'Opy', ['native/t21_result.json', 'native/t21_agent_stage.json', 'native/t21_flow_run.txt'], 'loopback recon->select->export->collect->prepare->agent authoring; 12/12 references.'),
    'T-22': ('PASS (97 + 27); limit-trigger sub-obligation NOT RUN', 'Opy', ['attempts/t22/junit_current.xml', 'attempts/t22/junit_retained.xml', 'attempts/t22/t22_current_suite.txt', 'attempts/t22/t22_retained_suite.txt'],
             'baselines matched exactly. Limit semantics are suite-asserted only (test_cap_preserves_partial_not_complete, test_limit_resume_and_cleanup_separate, test_shared_limit_and_pacing); independent Q2 max_requests=1 / tiny deadline / small byte allowance fixtures and the O2 directory-byte record were NOT RUN - gap surfaced by the incoming Executor at T-24.'),
    'T-23': ('PASS + ADJUDICATE B1-B3', 'Claudy', ['offline/t23_untrusted_privacy_result.json', 'offline/t23_adjudication.json', 'offline/t23_untrusted_privacy_run.txt'],
             'active destinations/script-class markup stripped, refusals pre-output, raw unchanged, checker validated 9x2. Boundaries: B1 escaped <script> text decoded to literal markup in md; B2 markdown-link-shaped javascript: text unescaped; B3 index image source_src keeps javascript:.'),
    'T-24': ('RECORDED (this matrix, rechecks, package)', 'Claudy', ['t24/t24_readiness_result.json', 't24/t24_readiness_run.txt'], 'identities stable, 0 product path changes, QA disk within ceiling, no non-loopback host in native evidence; ZIP receipt in t24/.'),
}
RETIRED = {'AC-015', 'AC-018', 'AC-028', 'AC-040'}
AC_NOTES = {
    'AC-001': 'PARTIALLY TESTED - clean-install reproducibility NOT RUN (plan §0.2).',
    'AC-015': 'NOT APPLICABLE TO CURRENT SCOPE, HISTORICAL STATUS PRESERVED; limited current image-reference check only.',
    'AC-018': 'Retired screenshot stream NOT APPLICABLE TO CURRENT SCOPE, HISTORICAL STATUS PRESERVED; current authored/captured distinction PASS (T-11).',
    'AC-028': 'NOT APPLICABLE TO CURRENT SCOPE, HISTORICAL STATUS PRESERVED.',
    'AC-035': 'QA-owner applicability decision: current cold-read executed in T-20; historical twelve-B7 certificate binding not revived.',
    'AC-040': 'NOT APPLICABLE TO CURRENT SCOPE, HISTORICAL STATUS PRESERVED; no E2/live run.',
    'AC-042': 'O2 directory-byte measurement NOT RUN by Q2 (see T-22).',
    'AC-043': 'B1-B3 sanitization boundaries for Lead adjudication.',
    'AC-044': 'Checker is QA-authored (no product checker exists); real exports gated at T-24.',
    'AC-046': 'Canonical ABM_LEDGER.md 48 rows read-only, unchanged; this matrix supplements it.',
}


def cell(text):
    return text.replace('|', '\\|').replace('\n', ' ')


def main():
    scope = {}
    for line in SCOPE.read_text(encoding='utf-8').splitlines():
        m = re.match(r'\| (AC-\d{3}) — ([^|]+)\| ([^|]+)\| (.+?) \| (T-\d{2}) \|$', line)
        if m:
            scope[m.group(1)] = {'title': m.group(2).strip(), 'applicability': m.group(3).strip(),
                                 'obligation': m.group(4).strip(), 'test': m.group(5)}
    ledger = {}
    for line in LEDGER.read_text(encoding='utf-8').splitlines():
        m = re.match(r'\| (AC-\d{3}) \| ([^|]+)\|', line)
        if m:
            cols = [c.strip() for c in line.strip('|').split('|')]
            ledger[m.group(1)] = f'eng {cols[1]}; QA {cols[5]}; {cols[7]}'
    missing = [p for t in TESTS.values() for p in t[2] if not (LANE/p).exists()]
    assert len(scope) == 48 and len(ledger) == 48, (len(scope), len(ledger))
    assert not missing, missing
    rows = []
    for ac in sorted(scope):
        s = scope[ac]
        meas, who, ev, note = TESTS[s['test']]
        if ac in RETIRED:
            meas = 'NOT APPLICABLE TO CURRENT SCOPE, HISTORICAL STATUS PRESERVED' + (f' (current sub-check: {meas})' if ac in ('AC-015', 'AC-018') else '')
        rows.append(f"| {ac} | {cell(s['title'])} | {cell(s['applicability'])} | {cell(s['obligation'])} | {cell(ledger[ac])} | "
                    f"{s['test']} | {cell(meas)} | {who} | {'<br>'.join('`'+p+'`' for p in ev)} | {cell(AC_NOTES.get(ac, note))} |")
    head = f"""# AC_EVIDENCE_MATRIX — Q2 independent QA (LEAD-01)

Lane: `agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/Q2_2026-10-16_142632/` (evidence paths below are lane-relative).
Product candidate `8fbcff289fde5149be0c0631b08e8a5fbcb3faa4`; execution HEAD and all identity rechecks: `t24/t24_readiness_result.json`.
Executors: Opy (OpenCode, GLM 5.3) G0 → content group; Claudy (Claude Code, Claude Opus 5.5) T-23 → T-24 (transition at the T-23 seam; both outside the engineering seat).
Columns 3–5 are taken from the reviewed crosswalk `GOVERNING/CURRENT_TOOL_SCOPE.md` and the canonical `ABM_LEDGER.md` (read-only, unchanged).
Vocabulary per plan §0.2: PASS / FAIL / BLOCKED / NOT RUN / ADJUDICATE; applicability is separate from measurement.
**Not a certificate.** Independent QA executed and recorded; JARVIS (QA Lead) reviews and adjudicates; Tony decides.

## Standing findings, limitations and open items

| ID | Type | Statement | Evidence |
|---|---|---|---|
| O6 | FINDING | `candidate()` accepts `'Read more →'` (U+2192 not in the rstrip set) as a candidate title; supply and replace both demonstrated. Recorded against current behavior, no waiver. | `offline/t06_t14_result.json` |
| T23-B1 | ADJUDICATE | Entity-escaped `&lt;script&gt;` source text becomes literal `<script>` markup in derived page Markdown (active only under a raw-HTML-passing renderer). | `offline/t23_adjudication.json` |
| T23-B2 | ADJUDICATE | Markdown-link-shaped plain text with a `javascript:` target passes through unescaped into derived Markdown. | `offline/t23_adjudication.json` |
| T23-B3 | ADJUDICATE | SOURCE_INDEX image `source_src` keeps raw `javascript:` src values (data field). | `offline/t23_adjudication.json` |
| T-13 | HELPER LIMITATION (O5) | Synthetic `article > header > h1` title routed to BOILERPLATE by the helper. | `offline/t13_result.json` |
| T-10 | OPEN (outside scope) | Image/hidden/deferred completeness UNVERIFIED; historical media discrepancy stays OPEN. | `offline/t09_t15_t10_t11_result.json` |
| T-16 | DISCLOSURE | Lane evidence quotes the public page's own Google Maps embed parameter from verified fixture bytes; shipped faithfully, adjudicated at exact checker locations, redacted from all authored text. | `offline/t16_result.json`, `t24/` checker reports |
| T-22 | NOT RUN (sub-obligation) | Independent limit-trigger fixtures and O2 directory-byte record not executed; suite assertions only. | `attempts/t22/` |
| AC-001 | NOT RUN (sub-obligation) | Clean-clone / clean-venv install reproducibility. | `attempts/t01/` |
| T-20 | {cell(T20['measurement'])} | {cell(T20['matrix_note'])} | `t20/` |

## Matrix (48 IDs)

| AC | Title | Applicability | Current obligation (crosswalk) | Historical ledger status | Test | Q2 measurement | Executor | Evidence | Notes / remaining gaps |
|---|---|---|---|---|---|---|---|---|---|
"""
    out = LANE/'matrix/AC_EVIDENCE_MATRIX.md'
    out.write_text(head+'\n'.join(rows)+'\n', encoding='utf-8')
    print(json.dumps({'rows': len(rows), 'written': str(out)}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
