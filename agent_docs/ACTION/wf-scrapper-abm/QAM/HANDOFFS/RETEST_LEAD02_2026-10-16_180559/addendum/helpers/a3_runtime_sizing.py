"""LEAD-03 A3 instrument: demonstrate runtime-byte inclusion in the product sizing routine.

Executor: Claudy (Claude Code, Claude Fable 5). Per LEAD-03 §3 A3:
1. Inspect the RETAINED C3 native collection's .runtime tree BY NAMES/SIZES ONLY
   (no contents read beyond stat): file/dir counts, per-entry sizes, runtime-file
   subtotal, writer-lock size, other-file subtotal, total. Observation recorded
   as-is: an empty runtime tree is a valid observation, not nonzero overhead.
2. The retained native runtime holds no regular files, so a SEPARATE disposable
   QA clone of the synthetic qa-c2-maxreq1 collection (run-3 scratch) is used:
   a known-size non-secret sentinel (1,337 bytes of 'S', sha recorded) is placed
   at .runtime/qa-sentinel/sentinel.bin and the ACTUAL product sizing routine is
   measured before/after. The routine is the persistence check inside
   run_collection (recon_pipeline/collector.py line 435):
       size = sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
   It is executed here verbatim against the clone root, with the module path and
   sha256 of the candidate collector recorded. The demonstration: the routine's
   total increases by exactly the sentinel's bytes; an independent os.walk
   per-file sum agrees; the real zero-byte .writer.lock stays in the accounting.
3. du/interpretation correction for the earlier o2_note (recorded in the result).
The maintained collector, tests and original collections are untouched; only the
clone (inside QA scratch) is modified, and .runtime itself is NOT exported.
Writes argv[1].
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SNAP = Path('/tmp/claudy-lead02-retest-20261016/snapshot-repaired')
NATIVE = SNAP/'outputs/collections/qa-c3-rich-rest'
SRC_CLONE = Path('/tmp/claudy-lead02-retest-20261016/c2-run3/qa-c2-maxreq1')
CLONE = Path('/tmp/claudy-lead02-retest-20261016/a3-clone/qa-c2-maxreq1-sentinel')
COLLECTOR = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1/recon_pipeline/decide.py').parent/'collector.py'
SENTINEL = b'S' * 1337


def sha(b):
    return hashlib.sha256(b).hexdigest()


def product_sizing_routine(root: Path) -> int:
    """Verbatim expression from run_collection's persistence check (collector.py:435)."""
    return sum(p.stat().st_size for p in root.rglob('*') if p.is_file())


def independent_sum(root: Path):
    total, files = 0, {}
    for dirpath, _dirs, names in os.walk(root):
        for n in names:
            p = Path(dirpath)/n
            if p.is_file():
                s = p.stat().st_size
                files[p.relative_to(root).as_posix()] = s
                total += s
    return total, files


def runtime_report(root: Path):
    rt = root/'.runtime'
    entries = []
    files = dirs = 0
    subtotal = 0
    if rt.exists():
        for p in sorted(rt.rglob('*')):
            if p.is_dir():
                dirs += 1
                entries.append({'name': p.relative_to(root).as_posix()+'/', 'kind': 'dir'})
            elif p.is_file():
                files += 1
                s = p.stat().st_size
                subtotal += s
                entries.append({'name': p.relative_to(root).as_posix(), 'kind': 'file', 'bytes': s})
    return {'exists': rt.exists(), 'entries_by_name_and_size_only': entries,
            'file_count': files, 'dir_count': dirs, 'runtime_file_subtotal': subtotal}


def main():
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'sizing_routine': {'module': str(COLLECTOR), 'module_sha256': sha(COLLECTOR.read_bytes()),
                              'location': 'run_collection persistence check, line 435',
                              'expression': "sum(p.stat().st_size for p in root.rglob('*') if p.is_file())",
                              'note': ("pathlib's rglob('*') matches dot-prefixed names, so .runtime "
                                       'files and .writer.lock are inside the routine’s domain; '
                                       'demonstrated below with a sentinel')}}

    # --- 1. retained native runtime inspection (names/sizes only) ------------
    nat = runtime_report(NATIVE)
    lock = NATIVE/'.writer.lock'
    total_native = product_sizing_routine(NATIVE)
    ind_native, files_native = independent_sum(NATIVE)
    other = {k: v for k, v in files_native.items()
             if not k.startswith('.runtime') and k != '.writer.lock'}
    out['retained_native_collection'] = {
        'path': str(NATIVE), 'runtime': nat,
        'writer_lock_bytes': lock.stat().st_size if lock.exists() else 'absent',
        'other_file_subtotal': sum(other.values()), 'other_file_count': len(other),
        'routine_total': total_native, 'independent_total': ind_native,
        'totals_agree': total_native == ind_native,
        'observation': ('retained native .runtime holds 0 regular files across 3 directories '
                        '(crawl4ai cache tree created empty); a zero-byte .writer.lock exists. '
                        'Valid observation of this run; NOT evidence of nonzero runtime overhead, '
                        'so the sentinel-clone demonstration below is used per LEAD-03.')}

    # --- 2. sentinel demonstration in a disposable clone ----------------------
    if CLONE.exists():
        raise SystemExit(f'refusing to reuse {CLONE}')
    shutil.copytree(SRC_CLONE, CLONE)
    before_routine = product_sizing_routine(CLONE)
    before_ind, _ = independent_sum(CLONE)
    sdir = CLONE/'.runtime/qa-sentinel'
    sdir.mkdir(parents=True)
    (sdir/'sentinel.bin').write_bytes(SENTINEL)
    after_routine = product_sizing_routine(CLONE)
    after_ind, after_files = independent_sum(CLONE)
    du = int(subprocess.run(['du', '-sb', str(CLONE)], capture_output=True, text=True).stdout.split()[0])
    dub = int(subprocess.run(['du', '-s', '--block-size=1', '--apparent-size', str(CLONE)],
                             capture_output=True, text=True).stdout.split()[0])
    out['sentinel_demonstration'] = {
        'clone_of': str(SRC_CLONE), 'clone': str(CLONE),
        'sentinel': {'path': '.runtime/qa-sentinel/sentinel.bin', 'bytes': len(SENTINEL),
                     'sha256': sha(SENTINEL), 'content': 'non-secret: 1337 bytes of ASCII "S"'},
        'routine_before': before_routine, 'routine_after': after_routine,
        'routine_delta': after_routine - before_routine,
        'delta_equals_sentinel_bytes': after_routine - before_routine == len(SENTINEL),
        'independent_before': before_ind, 'independent_after': after_ind,
        'independent_agrees': after_ind == after_routine and before_ind == before_routine,
        'writer_lock_in_accounting': '.writer.lock' in after_files,
        'writer_lock_bytes': after_files.get('.writer.lock'),
        'runtime_file_counted': '.runtime/qa-sentinel/sentinel.bin' in after_files}

    # --- 3. du / interpretation correction ------------------------------------
    out['du_note_correction'] = {
        'earlier_o2_note': ('c2 o2_note claimed "du -sb exceeds the per-file sum", while the recorded '
                            'numbers were equal'),
        'correction': ('du -sb implies --apparent-size, so it reports per-file apparent bytes PLUS '
                       'directory-entry apparent sizes; on this filesystem the directory entries '
                       'reported 0/negligible apparent size for these small trees, so du -sb equaled '
                       'the per-file sum. The product routine sums regular-file apparent sizes only '
                       '(no directories), which is what the byte allowance bounds. Filesystem BLOCK '
                       'usage (du without --apparent-size) is larger and is NOT what the product '
                       'measures. No exact persisted-byte ceiling is claimed.'),
        'clone_measurements': {'routine_per_file_sum': after_routine, 'du_sb_apparent': du,
                               'du_apparent_explicit': dub,
                               'du_matches_routine_plus_dir_entries': du - after_routine}}

    checks = [out['retained_native_collection']['totals_agree'],
              out['sentinel_demonstration']['delta_equals_sentinel_bytes'],
              out['sentinel_demonstration']['independent_agrees'],
              out['sentinel_demonstration']['writer_lock_in_accounting'],
              out['sentinel_demonstration']['runtime_file_counted']]
    out['verdict_a3'] = 'PASS' if all(checks) else 'FAIL'
    out['export_note'] = ('only this measurement report is exported; .runtime trees and the clone '
                          'are not exported')
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_a3': out['verdict_a3'],
                      'native_runtime_files': nat['file_count'],
                      'routine_delta': out['sentinel_demonstration']['routine_delta'],
                      'sentinel_bytes': len(SENTINEL)}, indent=1))
    return 0 if out['verdict_a3'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
