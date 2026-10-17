"""LEAD-03 addendum packaging: stage, check, zip and copy the evidence addendum.

Executor: Claudy (Claude Code, Claude Fable 5). Contents: the addendum tree
(A1/A2/A3 artifacts + results, helpers, identity recheck, matrix note, LEAD-03
copy, retain/delete inventory, report copy), INDEX.md, INCLUSION_EXCLUSION.json
and MANIFEST.sha256.json. The lane export checker runs in dir mode pre-zip and
zip mode on the lane and Downloads copies. ZIP/hash receipts stay outside the
ZIP. No historical ZIPs nested; .runtime never exported.
Usage: addendum_package.py STAMP ADJUDICATIONS RESULT_JSON
"""
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1')
LANE = Path(__file__).resolve().parents[2]
ADD = LANE/'addendum'
STAGE_ROOT = Path('/tmp/claudy-lead02-retest-20261016/addendum-stage')
DOWNLOADS = Path('/home/moose/Downloads')
VENV = str(REPO/'venv/bin/python')
CHECKER = LANE/'helpers/q2_export_checker.py'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def checker(target, manifest, adjudications, report):
    proc = subprocess.run([VENV, str(CHECKER), str(target), str(manifest), '--adjudications',
                           str(adjudications), '--json', str(report)],
                          capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1'})
    rep = json.loads(Path(report).read_text())
    return {'exit': proc.returncode, 'verdict': rep['verdict'], 'failures': rep['failures'],
            'adjudicated_hits': rep['adjudicated_hits'], 'report': str(report)}


def main():
    stamp, adjudications, result_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    name = f'WebFactory_LEAD03_Evidence_Addendum_{stamp}'
    stage = STAGE_ROOT/name
    stage.mkdir(parents=True, exist_ok=False)
    included, excluded = {}, []
    for p in sorted(ADD.rglob('*')):
        rel = p.relative_to(ADD)
        if not p.is_file():
            continue
        if rel.parts[0] == 'exports' or p.suffix == '.zip' or '__pycache__' in rel.parts:
            excluded.append({'path': 'addendum/'+rel.as_posix(), 'reason': 'receipt/output dir or archive'})
            continue
        if '.runtime' in rel.parts:
            excluded.append({'path': 'addendum/'+rel.as_posix(), 'reason': 'runtime never exported'})
            continue
        included['addendum/'+rel.as_posix()] = p
    for dest, src in included.items():
        (stage/dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, stage/dest)
    inclusion = {
        'included_count': len(included), 'included': {d: str(s) for d, s in included.items()},
        'excluded': excluded,
        'referenced_by_identity_never_nested': [
            'WebFactory_LEAD02_QA_Retest_2026-10-16_183150.zip sha256 b734010a…fab9d0 (209,786 B) - preserved, re-verified in addendum/identity_recheck.json',
            'WebFactory_LEAD02_Engineering_Rework_2026-10-16_173633.zip sha256 151c15e6…b04666',
            'WebFactory_QA_Q2_Package_2026-10-16_155121.zip sha256 06f73841…d974df'],
        'runtime_statement': '.runtime trees measured by name/size only (a3/) and never exported'}
    (stage/'INCLUSION_EXCLUSION.json').write_text(json.dumps(inclusion, indent=2)+'\n')
    (stage/'INDEX.md').write_text(
        f'# {name}\n\nLEAD-03 §3 bounded evidence addendum. Not a certificate: JARVIS reviews, Tony decides.\n\n'
        '- `addendum/REPORT.md` — start here\n'
        '- `addendum/a1/` — C1 original raw/initial/reviewed artifacts, hash chain, reviewed-v2 with consistent final index\n'
        '- `addendum/a2/` — C3 original checklist/result/body chain + labeled 1,104-byte reconstruction\n'
        '- `addendum/a3/` — runtime-byte sizing demonstration + du-note correction\n'
        '- `addendum/identity_recheck.json`, `addendum/MATRIX_NOTE.md`, `addendum/RETAIN_DELETE_INVENTORY.md`\n'
        '- `addendum/WebFactory_QA_LEAD03_Retest_Decision_2026-10-16.md` — governing decision (unchanged copy)\n'
        '- `MANIFEST.sha256.json` — sha256 + bytes of every other member\n')
    manifest = {'members': {p.relative_to(stage).as_posix(): {'sha256': sha(p.read_bytes()),
                                                              'bytes': p.stat().st_size}
                            for p in sorted(stage.rglob('*')) if p.is_file()}}
    (stage/'MANIFEST.sha256.json').write_text(json.dumps(manifest, indent=2)+'\n')
    full = json.loads(json.dumps(manifest))
    full['members']['MANIFEST.sha256.json'] = {
        'sha256': sha((stage/'MANIFEST.sha256.json').read_bytes()),
        'bytes': (stage/'MANIFEST.sha256.json').stat().st_size}
    cm = STAGE_ROOT/f'{name}.checker-manifest.json'
    cm.write_text(json.dumps(full, indent=2)+'\n')
    result = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
              'instrument_sha256': sha(Path(__file__).read_bytes()),
              'package_name': name, 'member_count': len(full['members'])}
    result['pre_zip_dir_check'] = checker(stage, cm, adjudications, ADD/'exports/addendum_check_dir.json')
    if result['pre_zip_dir_check']['verdict'] != 'PASS':
        result['stopped'] = 'pre-zip checker FAIL - no ZIP written'
        result_path.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result['pre_zip_dir_check'], indent=1))
        return 1
    zpath = ADD/'exports'/f'{name}.zip'
    with zipfile.ZipFile(zpath, 'x', zipfile.ZIP_DEFLATED) as z:
        for member in sorted(full['members']):
            z.write(stage/member, member)
    dl = DOWNLOADS/zpath.name
    if dl.exists():
        raise SystemExit(f'refusing to overwrite {dl}')
    shutil.copyfile(zpath, dl)
    zb, db = zpath.read_bytes(), dl.read_bytes()
    result['zip'] = {'path': str(zpath), 'sha256': sha(zb), 'bytes': len(zb)}
    result['downloads_copy'] = {'path': str(dl), 'sha256': sha(db), 'bytes': len(db),
                                'byte_identical': zb == db}
    result['post_zip_check_lane'] = checker(zpath, cm, adjudications, ADD/'exports/addendum_check_zip_lane.json')
    result['post_zip_check_downloads'] = checker(dl, cm, adjudications, ADD/'exports/addendum_check_zip_downloads.json')
    with zipfile.ZipFile(zpath) as z:
        names = z.namelist()
        result['zip_entry_count'] = len(names)
        result['crc_ok'] = z.testzip() is None
        result['paths_confined_unique'] = (all(not n.startswith('/') and '..' not in n.split('/')
                                               for n in names) and len(set(names)) == len(names))
    result_path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('package_name', 'member_count', 'zip', 'downloads_copy',
                                             'zip_entry_count', 'crc_ok', 'paths_confined_unique')}, indent=1))
    print(json.dumps({k: result[k]['verdict'] for k in
                      ('pre_zip_dir_check', 'post_zip_check_lane', 'post_zip_check_downloads')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
