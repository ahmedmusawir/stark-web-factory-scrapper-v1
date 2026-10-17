"""LEAD-02 retest packaging instrument: stage, check, zip and copy the QA review ZIP.

Executor: Claudy (Claude Code, Claude Fable 5). Inclusion: this retest lane
(minus exports/ and caches), plus the run's records (RECOVERY, CHANGELOG, session
log, the committed engineering-era RESPONSES records). Historical QA/engineering
ZIPs are referenced by identity only — never nested or rebuilt; the existing
historical package-check receipts ride along under companions/ (supplied by the
engineering package; not recreated). Writes INDEX.md + INCLUSION_EXCLUSION.json
into staging, then MANIFEST.sha256.json over every other member. Checker
(lane copy of the T-23-validated q2_export_checker): dir mode pre-zip, zip mode
on the lane ZIP and the Downloads copy, exact-location adjudications only. The
final RESPONSES report carries the ZIP hash and stays OUTSIDE the ZIP.
Usage: retest_package.py STAMP ADJUDICATIONS_JSON RESULT_JSON
"""
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1')
LANE = Path(__file__).resolve().parents[1]
STAGE_ROOT = Path('/tmp/claudy-lead02-retest-20261016/package-stage')
DOWNLOADS = Path('/home/moose/Downloads')
VENV = str(REPO/'venv/bin/python')
CHECKER = LANE/'helpers/q2_export_checker.py'
EXCLUDED_PARTS = {'__pycache__'}
RECORDS = ['RECOVERY.md', 'CHANGELOG.md', 'agent_docs/SESSIONS/session_2026-10-16.md',
           'agent_docs/RESPONSES/response_2026-10-16_165613_cody-engineer-recovery.md',
           'agent_docs/RESPONSES/response_2026-10-16_172610_lead02-repair-plan.md',
           'agent_docs/RESPONSES/response_2026-10-16_173731_lead02-engineering-rework.md']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checker(target, manifest, adjudications, report):
    proc = subprocess.run([VENV, str(CHECKER), str(target), str(manifest), '--adjudications',
                           str(adjudications), '--json', str(report)],
                          capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1'})
    rep = json.loads(Path(report).read_text())
    return {'exit': proc.returncode, 'stdout': proc.stdout[-500:], 'stderr': proc.stderr[-500:],
            'verdict': rep['verdict'], 'failures': rep['failures'],
            'adjudicated_hits': rep['adjudicated_hits'], 'report': str(report)}


def main():
    stamp, adjudications, result_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    name = f'WebFactory_LEAD02_QA_Retest_{stamp}'
    stage = STAGE_ROOT/name
    stage.mkdir(parents=True, exist_ok=False)
    lane_name = LANE.name
    included, excluded = {}, []
    for p in sorted(LANE.rglob('*')):
        rel = p.relative_to(LANE)
        if not p.is_file():
            continue
        if EXCLUDED_PARTS & set(rel.parts) or rel.parts[0] == 'exports' or p.suffix == '.zip':
            excluded.append({'path': f'{lane_name}/'+rel.as_posix(),
                             'reason': 'cache / output dir / archive (no nesting)'})
            continue
        included[f'{lane_name}/'+rel.as_posix()] = p
    for rel in RECORDS:
        included['records/'+rel] = REPO/rel
    for dest, src in included.items():
        (stage/dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, stage/dest)
    inclusion = {
        'included_count': len(included),
        'included': {d: str(s) for d, s in included.items()},
        'excluded_from_lane': excluded,
        'referenced_by_identity_never_nested': [
            'WebFactory_QA_Q2_Package_2026-10-16_155121.zip sha256 06f73841cc678badd30d56bfb4c41614c376b16abe7254ea1e374a96c1d974df (499,912 B) - historical QA package, unchanged',
            'WebFactory_LEAD02_Engineering_Rework_2026-10-16_173633.zip sha256 151c15e61ee2d723f4b62fab96e12be3b7706af87641d9bb7eee9931f2b04666 (116,748 B) - engineering package, unchanged',
            'raw fixture archives per plan §0 (hashes re-verified in g0-identity/)',
            'QA retest scratch /tmp/claudy-lead02-retest-20261016/ (snapshot of repaired commit, synthetic collections, pytest basetemps) - disposable, reproducible from lane instruments',
            'retained Q2 scratch /tmp/opencode/q2-scratch-20261016/ and engineering scratch /tmp/cody-lead02-2026-10-16_172752/ (retain/delete: Tony)',
            'collection .runtime profiles (never exported; measured by name/size only in c2/)'],
        'companions_note': ('companions/historical-q2-package-check-receipts/ are the EXISTING historical '
                            'receipts supplied inside the engineering package, included as required; '
                            'nothing historical was recreated.'),
        'disclosure': ('historical receipts adjudicate the public Google Maps embed parameter at exact '
                       'checker locations; the value appears in no authored text of this retest lane')}
    (stage/'INCLUSION_EXCLUSION.json').write_text(json.dumps(inclusion, indent=2)+'\n')
    (stage/'INDEX.md').write_text(
        f'# {name}\n\nLEAD-02 independent QA retest package. Not a certificate: JARVIS adjudicates, Tony decides.\n\n'
        f'- `{lane_name}/EXECUTION_REPORT.md` — start here (ZIP hash receipt is in the sibling RESPONSES report, outside this ZIP)\n'
        f'- `{lane_name}/matrix/AC_EVIDENCE_MATRIX_RETEST.md` — 48-row supplemental matrix\n'
        f'- `{lane_name}/g0-identity/` — DIRECTOR GO (verbatim), identity/diff/source52/fixture verification, snapshot scoping\n'
        f'- `{lane_name}/r1/ r2/ c1/ c2/ c3/ regression/` — per-item instruments, results, runs, JUnit\n'
        f'- `{lane_name}/companions/` — LEAD-02 decision, Architect handoff, historical package-check receipts\n'
        '- `records/` — RECOVERY, CHANGELOG, session log, engineering-era RESPONSES records\n'
        '- `INCLUSION_EXCLUSION.json` / `MANIFEST.sha256.json` — membership and hashes\n')
    manifest = {'members': {p.relative_to(stage).as_posix(): {'sha256': sha(p.read_bytes()),
                                                              'bytes': p.stat().st_size}
                            for p in sorted(stage.rglob('*')) if p.is_file()}}
    (stage/'MANIFEST.sha256.json').write_text(json.dumps(manifest, indent=2)+'\n')
    full = json.loads(json.dumps(manifest))
    full['members']['MANIFEST.sha256.json'] = {
        'sha256': sha((stage/'MANIFEST.sha256.json').read_bytes()),
        'bytes': (stage/'MANIFEST.sha256.json').stat().st_size}
    check_manifest = STAGE_ROOT/f'{name}.checker-manifest.json'
    check_manifest.write_text(json.dumps(full, indent=2)+'\n')
    t = LANE/'exports'
    result = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
              'instrument_sha256': sha(Path(__file__).read_bytes()),
              'package_name': name, 'member_count': len(full['members'])}
    result['pre_zip_dir_check'] = checker(stage, check_manifest, adjudications,
                                          LANE/'exports/package_check_dir.json')
    if result['pre_zip_dir_check']['verdict'] != 'PASS':
        result['stopped'] = 'pre-zip checker FAIL - no ZIP written'
        result_path.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result['pre_zip_dir_check'], indent=1))
        return 1
    zpath = t/f'{name}.zip'
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
    result['post_zip_check_lane'] = checker(zpath, check_manifest, adjudications,
                                            LANE/'exports/package_check_zip_lane.json')
    result['post_zip_check_downloads'] = checker(dl, check_manifest, adjudications,
                                                 LANE/'exports/package_check_zip_downloads.json')
    with zipfile.ZipFile(zpath) as z:
        result['zip_entry_count'] = len(z.infolist())
        result['crc_ok'] = z.testzip() is None
        names = z.namelist()
        result['paths_confined_unique'] = (all(not n.startswith('/') and '..' not in n.split('/')
                                               for n in names) and len(set(names)) == len(names))
    result_path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('package_name', 'member_count', 'zip',
                                             'downloads_copy', 'zip_entry_count', 'crc_ok',
                                             'paths_confined_unique')}, indent=1))
    print(json.dumps({k: result[k]['verdict'] for k in
                      ('pre_zip_dir_check', 'post_zip_check_lane', 'post_zip_check_downloads')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
