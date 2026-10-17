"""Q2 T-24 instrument: stage, check, zip and copy the indexed review package.

Executor: Claudy (Claude Code, Claude Opus 5.5).
Explicit inclusion: the Q2 lane (minus caches and the exports/ output dir),
the installed LEAD-01 review folder (plan, approval, amendments, governing
snapshots, original Q1 records), and the run's session/recovery/handoff/report
records. Writes INDEX.md + INCLUSION_EXCLUSION.json inside the staging tree, then
MANIFEST.sha256.json over every other member. Checker: dir mode on staging
(pre-zip), zip mode on the lane ZIP and on the Downloads copy (post-zip), with
exact-location adjudications for the public embed parameter only. No nesting:
the lane's own exports/ and any *.zip are excluded and the checker rejects
nested archives. The final RESPONSES report carries this ZIP's hash, so it stays outside;
the ZIP carries t24/EXECUTION_REPORT.md (same content minus the hash receipt).
Usage: t24_package.py STAMP ADJUDICATIONS_JSON RESULT_JSON
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
REVIEW = LANE.parent/'WebFactory_Q1_Lead_Review_2026-10-15'
STAGE_ROOT = Path('/tmp/opencode/q2-scratch-20261016/t24-stage')
DOWNLOADS = Path('/home/moose/Downloads')
VENV = str(REPO/'venv/bin/python')
CHECKER = LANE/'helpers/q2_export_checker.py'
EXCLUDED_PARTS = {'__pycache__'}
RECORDS = ['RECOVERY.md', 'CHANGELOG.md', 'agent_docs/SESSIONS/session_2026-10-16.md',
           'agent_docs/RESPONSES/response_2026-10-16_152740_q2-executor-handoff.md']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checker(target, manifest, adjudications, report):
    proc = subprocess.run([VENV, str(CHECKER), str(target), str(manifest), '--adjudications', str(adjudications),
                           '--json', str(report)], capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1'})
    rep = json.loads(Path(report).read_text())
    return {'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr, 'verdict': rep['verdict'],
            'failures': rep['failures'], 'adjudicated_hits': rep['adjudicated_hits'], 'report': str(report)}


def main():
    stamp, adjudications, result_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    name = f'WebFactory_QA_Q2_Package_{stamp}'
    stage = STAGE_ROOT/name
    stage.mkdir(parents=True, exist_ok=False)
    included, excluded = {}, []
    for p in sorted(LANE.rglob('*')):
        rel = p.relative_to(LANE)
        if not p.is_file():
            continue
        if EXCLUDED_PARTS & set(rel.parts) or rel.parts[0] == 'exports' or p.suffix == '.zip':
            excluded.append({'path': 'Q2_2026-10-16_142632/'+rel.as_posix(), 'reason': 'cache / output dir / archive (no nesting)'})
            continue
        included['Q2_2026-10-16_142632/'+rel.as_posix()] = p
    for p in sorted(REVIEW.rglob('*')):
        if p.is_file():
            included['governing/WebFactory_Q1_Lead_Review_2026-10-15/'+p.relative_to(REVIEW).as_posix()] = p
    for rel in RECORDS:
        included['records/'+rel] = REPO/rel
    for dest, src in included.items():
        (stage/dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, stage/dest)
    inclusion = {'included_count': len(included), 'included': {d: str(s) for d, s in included.items()},
                 'excluded_from_lane': excluded,
                 'referenced_but_omitted': [
                     'raw fixture archives agent_docs/RESPONSES/response_2026-10-11_210309_prepare-v01.zip and '
                     'response_2026-10-13_223736_growth-call-follow-up.zip (hashes in plan §0; verified in t24 readiness)',
                     'restored fixture collections/prepared packages under the snapshot (34-file manifest; verified)',
                     'QA scratch /tmp/opencode/q2-scratch-20261016/ (snapshot, synthetic collections, T-20 packet copy, '
                     'checker control trees) - disposable; manifests/reports for each are in the lane',
                     'collection .runtime profiles (never exported)', 'earlier Q1 exports (not nested)'],
                 'disclosure': "lane evidence offline/t16_result.json quotes the public page's own Google Maps embed "
                               'parameter from verified fixture bytes; shipped faithfully, adjudicated at exact checker '
                               'locations, redacted from all authored text'}
    (stage/'INCLUSION_EXCLUSION.json').write_text(json.dumps(inclusion, indent=2)+'\n')
    (stage/'INDEX.md').write_text(
        f'# {name}\n\nIndependent QA Q2 (LEAD-01) review package. Not a certificate: JARVIS reviews, Tony decides.\n\n'
        '- `Q2_2026-10-16_142632/t24/EXECUTION_REPORT.md` — execution report (start here; ZIP hash receipt is in the sibling RESPONSES report)\n'
        '- `Q2_2026-10-16_142632/matrix/AC_EVIDENCE_MATRIX.md` — 48-ID evidence matrix\n'
        '- `Q2_2026-10-16_142632/` — full evidence lane (g0/g1/g2 readiness, attempts, offline, native, t20, t24, helpers)\n'
        '- `governing/WebFactory_Q1_Lead_Review_2026-10-15/` — exact approved plan, approval, amendments, governing snapshots\n'
        '- `records/` — session log, RECOVERY, CHANGELOG, executor handoff\n'
        '- `INCLUSION_EXCLUSION.json` — explicit inclusion list, exclusions, referenced-but-omitted inputs\n'
        '- `MANIFEST.sha256.json` — sha256 + bytes of every other member\n')
    manifest = {'members': {p.relative_to(stage).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
                            for p in sorted(stage.rglob('*')) if p.is_file()}}
    (stage/'MANIFEST.sha256.json').write_text(json.dumps(manifest, indent=2)+'\n')
    full = json.loads(json.dumps(manifest))
    full['members']['MANIFEST.sha256.json'] = {'sha256': sha((stage/'MANIFEST.sha256.json').read_bytes()),
                                               'bytes': (stage/'MANIFEST.sha256.json').stat().st_size}
    check_manifest = STAGE_ROOT/f'{name}.checker-manifest.json'
    check_manifest.write_text(json.dumps(full, indent=2)+'\n')
    t24 = LANE/'t24'
    result = {'executor': 'Claudy (Claude Code, Claude Opus 5.5)', 'instrument_sha256': sha(Path(__file__).read_bytes()),
              'package_name': name, 'member_count': len(full['members'])}
    result['pre_zip_dir_check'] = checker(stage, check_manifest, adjudications, t24/'package_check_dir.json')
    if result['pre_zip_dir_check']['verdict'] != 'PASS':
        result['stopped'] = 'pre-zip checker FAIL - no ZIP written'
        result_path.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result['pre_zip_dir_check'], indent=1)); return 1
    zpath = LANE/'exports'/f'{name}.zip'
    with zipfile.ZipFile(zpath, 'x', zipfile.ZIP_DEFLATED) as z:
        for member in sorted(full['members']):
            z.write(stage/member, member)
    dl = DOWNLOADS/zpath.name
    if dl.exists():
        raise SystemExit(f'refusing to overwrite {dl}')
    shutil.copyfile(zpath, dl)
    zbytes, dbytes = zpath.read_bytes(), dl.read_bytes()
    result['zip'] = {'path': str(zpath), 'sha256': sha(zbytes), 'bytes': len(zbytes)}
    result['downloads_copy'] = {'path': str(dl), 'sha256': sha(dbytes), 'bytes': len(dbytes),
                                'byte_identical': zbytes == dbytes}
    result['post_zip_check_lane'] = checker(zpath, check_manifest, adjudications, t24/'package_check_zip_lane.json')
    result['post_zip_check_downloads'] = checker(dl, check_manifest, adjudications, t24/'package_check_zip_downloads.json')
    with zipfile.ZipFile(zpath) as z:
        result['zip_entry_count'] = len(z.infolist())
    result_path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('package_name', 'member_count', 'zip', 'downloads_copy')}, indent=1))
    print(json.dumps({k: result[k]['verdict'] for k in ('pre_zip_dir_check', 'post_zip_check_lane', 'post_zip_check_downloads')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
