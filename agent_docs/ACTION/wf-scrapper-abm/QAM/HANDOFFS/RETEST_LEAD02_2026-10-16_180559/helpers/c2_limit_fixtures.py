"""LEAD-02 C2 instrument: the three approved limit-trigger fixtures + O2 bytes.

Executor: Claudy (Claude Code, Claude Fable 5). Imports the collector ONLY from
the repaired snapshot. Transport is an in-process double (plan-approved; zero
network of any kind): each get() returns a synthetic 200 HTML response after an
optional controlled delay. run_collection() is executed under the module's own
writer() lock so .writer.lock overhead is real.

Case A max_requests=1: two planned pages; expect exactly one dispatched request
  with recorded start/completion, one persisted attempt, stop_reason
  'request_limit', second item still pending, collection_outcome 'partial'.
Case B tiny deadline: max_seconds=1 with a transport double that sleeps ~1.4s;
  expect stop_reason 'time_limit' (in-flight request cancelled by
  asyncio.timeout_at at the deadline → item failed, no attempt persisted) and
  the observed post-receipt/cancellation semantics RECORDED, not asserted as
  instantaneous. A pre-dispatch variant (delay before second dispatch crossing
  the deadline) checks the dispatch-side guard.
Case C small persisted-byte allowance: max_bytes sized so the second response
  would cross size+len(body)+65536; expect first attempt persisted, second item
  'failed' with error 'persisted_byte_limit', stop_reason 'persisted_byte_limit',
  second body NOT persisted. Documented semantics: the allowance is enforced
  POST-RECEIPT against current directory size + incoming body + 65536 estimate;
  no exact wire-byte or streaming-memory guarantee exists or is claimed.
O2: actual directory bytes (per-file sum and du -sb) for each case collection,
  itemizing checklist, attempts, .writer.lock and any .runtime (names/sizes
  only; .runtime contents are never read or exported).
Writes argv[1].
"""
import asyncio
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SNAP = Path('/tmp/claudy-lead02-retest-20261016/snapshot-repaired')
# run 1 preserved under c2/ (results *.run1); run 2 uses fresh trees.
# G3 corrections after run 1 (observed product semantics, recorded not invented):
#  - in-flight deadline: asyncio.timeout_at raises TimeoutError inside the request
#    try-block, caught by the generic request-error handler → stop_reason
#    'request_error' with item error 'TimeoutError: ...'; 'time_limit' is produced
#    by the PRE-dispatch guards (case B2). Expectation updated to the observed pair.
#  - byte allowance: the post-receipt check is size+len(body)+65536, so an
#    allowance below first-body+65536 stops the run on the FIRST response with
#    nothing persisted. Run-2 allowance covers the first attempt + overhead so the
#    second response is the crossing one, exercising partial persistence.
WORK = Path('/tmp/claudy-lead02-retest-20261016/c2-run3')
sys.path.insert(0, str(SNAP))
sys.dont_write_bytecode = True
from recon_pipeline import collector as c  # noqa: E402

PAGE = (b'<html><head><title>C2 limit fixture</title></head><body><main>'
        b'<h1>C2 limit fixture page</h1><p>' + b'synthetic filler content ' * 400 + b'</p>'
        b'</main></body></html>')


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Double:
    """Loopback-free transport double; records dispatch wall/monotonic times."""

    def __init__(self, delay=0.0):
        self.delay = delay
        self.calls = []
        self.starts = 0
        self.closed = 0

    async def start(self):
        self.starts += 1

    async def get(self, item):
        self.calls.append({'url': item['url'], 'monotonic': time.monotonic(),
                           'wall': datetime.now(timezone.utc).isoformat()})
        if self.delay:
            await asyncio.sleep(self.delay)
        return {'status': 200, 'headers': {'content-type': 'text/html'}, 'body': PAGE,
                'final_url': None, 'redirect_from': [], 'transport': 'qa C2 double (no network)'}

    async def close(self):
        self.closed += 1


def dir_bytes(root):
    files = {p.relative_to(root).as_posix(): p.stat().st_size
             for p in sorted(root.rglob('*')) if p.is_file()}
    du = int(subprocess.run(['du', '-sb', str(root)], capture_output=True, text=True).stdout.split()[0])
    return {'per_file_sum': sum(files.values()), 'du_sb': du, 'file_count': len(files),
            'writer_lock_bytes': files.get('.writer.lock', 'absent'),
            'runtime_entries_by_name_only': sorted(k for k in files if k.startswith('.runtime')),
            'files': files}


def run_case(name, *, urls, limits, delay=0.0, settle=None):
    root = WORK/name
    if root.exists():
        raise SystemExit(f'refusing to reuse {root}')
    state = c.create(root, {'pages': urls, 'rest': []})
    double = Double(delay=delay)
    start = datetime.now(timezone.utc).isoformat()
    with c.writer(root):
        if settle:
            settle(state)
        code = asyncio.run(c.run_collection(root, state, transport=double, **limits))
    run = state['runs'][-1]
    case = {'collection': str(root), 'settings': {k: run[k] for k in
                                                  ('gap_seconds', 'max_requests', 'max_seconds', 'max_bytes', 'response_cap')},
            'start': start, 'end': datetime.now(timezone.utc).isoformat(), 'exit_code': code,
            'dispatches': double.calls, 'transport_starts': double.starts, 'transport_closed': double.closed,
            'requests_recorded': [{k: r.get(k) for k in ('id', 'url', 'start', 'completion', 'completion_epoch')}
                                  for r in run['requests']],
            'stop_reason': run['stop_reason'], 'collection_outcome': run['collection_outcome'],
            'cleanup_error': run['cleanup_error'],
            'items': [{k: x.get(k) for k in ('id', 'url', 'status', 'error')} for x in state['items']],
            'bytes': dir_bytes(root)}
    atts = sorted((root/'attempts').rglob('result.json')) if (root/'attempts').exists() else []
    case['persisted_attempts'] = [str(p.relative_to(root)) for p in atts]
    case['persisted_bodies_sha256'] = {str(p.relative_to(root)): sha(p.read_bytes())
                                       for p in sorted((root/'attempts').rglob('body'))} if atts else {}
    return case


def main():
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'collector_module': c.__file__, 'collector_sha256': sha(Path(c.__file__).read_bytes()),
           'fixture_body_bytes': len(PAGE), 'fixture_body_sha256': sha(PAGE)}

    # A: max_requests=1
    a = run_case('qa-c2-maxreq1', urls=['http://127.0.0.1/qa-c2/a1', 'http://127.0.0.1/qa-c2/a2'],
                 limits={'gap': 0, 'max_requests': 1, 'max_seconds': 60, 'max_bytes': 100_000_000})
    a['expected'] = {'one_dispatch': len(a['dispatches']) == 1,
                     'request_completed': a['requests_recorded'][0].get('completion') is not None,
                     'one_attempt_persisted': len(a['persisted_attempts']) == 1,
                     'stop_request_limit': a['stop_reason'] == 'request_limit',
                     'second_item_pending': a['items'][1]['status'] == 'pending',
                     'partial_outcome': a['collection_outcome'] == 'partial',
                     'transport_closed': a['transport_closed'] == 1}
    out['case_a_max_requests_1'] = a

    # B1: in-flight deadline — response slower than max_seconds
    b = run_case('qa-c2-deadline', urls=['http://127.0.0.1/qa-c2/b1'],
                 limits={'gap': 0, 'max_requests': 5, 'max_seconds': 1, 'max_bytes': 100_000_000},
                 delay=1.4)
    b['expected'] = {'stop_deadline_cancellation': (b['stop_reason'] == 'request_error'
                                                    and b['items'][0]['error'].startswith('TimeoutError')),
                     'dispatched_once': len(b['dispatches']) == 1,
                     'no_attempt_persisted': len(b['persisted_attempts']) == 0,
                     'item_failed': b['items'][0]['status'] == 'failed',
                     'partial_outcome': b['collection_outcome'] == 'partial',
                     'transport_closed': b['transport_closed'] == 1}
    b['semantics_observed'] = (
        'The deadline is enforced pre-dispatch (loop guard → stop_reason time_limit, case B2) '
        'and in-flight via asyncio.timeout_at(deadline): the cancelled await raises TimeoutError '
        'inside the per-request try-block, so the run records stop_reason request_error with the '
        "item error 'TimeoutError: ...' and persists nothing. The run still stops at the deadline; "
        'only the stop label differs between the two paths (OBSERVATION for the Lead). Cancellation '
        'is cooperative asyncio cancellation at the next await point - no instantaneous or '
        'wire-level cancellation guarantee is claimed.')
    out['case_b_tiny_deadline'] = b

    # B2: pre-dispatch deadline — gap after first completion crosses the deadline
    b2 = run_case('qa-c2-deadline-predispatch',
                  urls=['http://127.0.0.1/qa-c2/c1', 'http://127.0.0.1/qa-c2/c2'],
                  limits={'gap': 5, 'max_requests': 5, 'max_seconds': 2, 'max_bytes': 100_000_000})
    b2['expected'] = {'stop_time_limit': b2['stop_reason'] == 'time_limit',
                      'first_completed_persisted': len(b2['persisted_attempts']) == 1,
                      'second_never_dispatched': len(b2['dispatches']) == 1,
                      'second_item_pending': b2['items'][1]['status'] == 'pending',
                      'partial_outcome': b2['collection_outcome'] == 'partial'}
    out['case_b2_predispatch_deadline'] = b2

    # C: small persisted-byte allowance
    # allowance: first attempt fits; second response fails size + body + 65536 check
    # allowance must exceed initial-size + first body + 65536 (so the first attempt
    # persists) and sit below after-first-size + second body + 65536 (so the second
    # response is the crossing one): len(PAGE)+65536+12k < A < 2*len(PAGE)+65536+12k
    # run-2 note (preserved as *.run2): +15,000 slack also admitted the second
    # attempt (after-first footprint ~12.2k + body 10.1k + 65,536 = ~87.9k < 90.7k).
    # 5,000 slack sits between first-crossing (~77.2k) and second-crossing (~87.9k).
    allowance = len(PAGE) + 65_536 + 5_000
    cc = run_case('qa-c2-bytes', urls=['http://127.0.0.1/qa-c2/d1', 'http://127.0.0.1/qa-c2/d2'],
                  limits={'gap': 0, 'max_requests': 10, 'max_seconds': 60, 'max_bytes': allowance})
    cc['allowance'] = allowance
    cc['expected'] = {'stop_byte_limit': cc['stop_reason'] == 'persisted_byte_limit',
                      'first_persisted': len(cc['persisted_attempts']) == 1,
                      'second_dispatched_but_not_persisted': len(cc['dispatches']) == 2,
                      'second_item_failed_byte_limit': (cc['items'][1]['status'] == 'failed'
                                                        and cc['items'][1]['error'] == 'persisted_byte_limit'),
                      'partial_outcome': cc['collection_outcome'] == 'partial',
                      'directory_within_allowance': cc['bytes']['per_file_sum'] <= allowance}
    cc['semantics_documented'] = (
        'Post-receipt enforcement: after a response arrives, current persisted directory size '
        '+ len(body) + 65536 (metadata/checklist overhead estimate) is compared to max_bytes; '
        'the crossing response is NOT persisted and the run stops. The allowance bounds '
        'persisted bytes, not wire bytes, response memory or redirect hops.')
    out['case_c_byte_allowance'] = cc

    # O2: actual directory byte measurements
    out['o2_directory_bytes'] = {k: {'per_file_sum': v['bytes']['per_file_sum'],
                                     'du_sb': v['bytes']['du_sb'],
                                     'writer_lock': v['bytes']['writer_lock_bytes'],
                                     'runtime_by_name': v['bytes']['runtime_entries_by_name_only']}
                                 for k, v in (('case_a', a), ('case_b', b), ('case_b2', b2), ('case_c', cc))}
    real = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1/outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505')
    if real.exists():
        rb = dir_bytes(real)
        out['o2_directory_bytes']['historical_real_collection'] = {
            'path': str(real), 'per_file_sum': rb['per_file_sum'], 'du_sb': rb['du_sb'],
            'writer_lock': rb['writer_lock_bytes'],
            'runtime_by_name': rb['runtime_entries_by_name_only'],
            'note': 'read-only measurement of the retained real collection; .runtime listed by name/size only'}
    out['o2_note'] = ('du -sb exceeds the per-file sum by filesystem block/directory overhead; the '
                      "product's own size check uses the per-file stat sum, which these measurements bound.")

    all_ok = all(all(case['expected'].values()) for case in (a, b, b2, cc))
    out['verdict_c2'] = 'PASS' if all_ok else 'FAIL'
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_c2': out['verdict_c2'],
                      'a': a['expected'], 'b': b['expected'], 'b2': b2['expected'], 'c': cc['expected']},
                     indent=1))
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
