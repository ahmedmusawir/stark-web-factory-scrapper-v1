"""Q2 T-24 instrument: closing readiness rechecks (read-only).

Executor: Claudy (Claude Code, Claude Opus 5.5).
Expected identities are DERIVED from recorded files, never typed here:
plan §0 table (candidate SHA, source52, requirements + fixture-ZIP hashes) and
the G0 successor record (execution HEAD). Rechecks: HEAD + candidate ancestry
(read-only git), source52 on worktree and snapshot (existing G1 helper),
fixture manifest 34/34 on real repo and snapshot (existing G2 helper),
requirements/fixture-ZIP hashes, complete `git status --porcelain=v1 -uall`
classification, QA disk (scratch + lane), result JSON parseability, preserved
prior runs, and a loopback-only audit of every request URL recorded in native
timelines/results. Writes argv[1].
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1')
LANE = Path(__file__).resolve().parents[1]
PLAN = LANE.parent/'WebFactory_Q1_Lead_Review_2026-10-15/01_QAM_TEST_PLAN_FINAL.md'
SCRATCH = Path('/tmp/opencode/q2-scratch-20261016')
SNAP = SCRATCH/'snapshot-scoped'
VENV = str(REPO/'venv/bin/python')
HEX64 = re.compile(r'`([0-9a-f]{64})`')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, capture_output=True, text=True)


def plan_row(text, label):
    line = next(ln for ln in text.splitlines() if ln.startswith(f'| {label}'))
    return line


def du(path):
    return int(subprocess.run(['du', '-sb', str(path)], capture_output=True, text=True).stdout.split()[0])


def main():
    plan = PLAN.read_text(encoding='utf-8')
    expect = {
        'candidate': re.search(r'`([0-9a-f]{40})`', plan_row(plan, 'Product candidate')).group(1),
        'source52': HEX64.search(plan_row(plan, 'Source52 |')).group(1),
        'requirements.txt': HEX64.search(plan_row(plan, 'requirements.txt')).group(1),
        'requirements-lock.txt': HEX64.search(plan_row(plan, 'requirements-lock.txt')).group(1),
        'agent_docs/RESPONSES/response_2026-10-11_210309_prepare-v01.zip': HEX64.search(plan_row(plan, 'Prepare fixture ZIP')).group(1),
        'agent_docs/RESPONSES/response_2026-10-13_223736_growth-call-follow-up.zip': HEX64.search(plan_row(plan, 'Growth Call fixture ZIP')).group(1),
        'execution_head': re.search(r'^([0-9a-f]{40}) \|', (LANE/'g0-identity/successor_verification.txt').read_text(), re.M).group(1),
    }
    out = {'executor': 'Claudy (Claude Code, Claude Opus 5.5)', 'instrument_sha256': sha(Path(__file__).read_bytes()),
           'expected_derived_from': {'plan': str(PLAN), 'plan_sha256': sha(PLAN.read_bytes()),
                                     'execution_head': 'g0-identity/successor_verification.txt'},
           'expected': expect}
    head = git('rev-parse', 'HEAD').stdout.strip()
    out['head'] = {'actual': head, 'matches_execution_head': head == expect['execution_head'],
                   'branch': git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip(),
                   'candidate_is_ancestor': git('merge-base', '--is-ancestor', expect['candidate'], head).returncode == 0}
    files = {}
    for rel in ('requirements.txt', 'requirements-lock.txt',
                'agent_docs/RESPONSES/response_2026-10-11_210309_prepare-v01.zip',
                'agent_docs/RESPONSES/response_2026-10-13_223736_growth-call-follow-up.zip'):
        actual = sha((REPO/rel).read_bytes())
        files[rel] = {'actual': actual, 'matches_plan': actual == expect[rel]}
    out['dependency_and_fixture_zip_hashes'] = files
    t24 = LANE/'t24'
    for name, argv in {
            'source52_worktree': [VENV, str(LANE/'helpers/verify_sources52.py'), str(REPO), str(t24/'recheck_source52_worktree.json')],
            'source52_snapshot': [VENV, str(LANE/'helpers/verify_sources52.py'), str(SNAP), str(t24/'recheck_source52_snapshot.json')],
            'fixtures_real_repo': [VENV, str(LANE/'helpers/verify_fixture_manifest.py'), str(REPO), str(t24/'recheck_fixtures_real_repo.json')],
            'fixtures_snapshot': [VENV, str(LANE/'helpers/verify_fixture_manifest.py'), str(SNAP), str(t24/'recheck_fixtures_snapshot.json')]}.items():
        proc = subprocess.run(argv, capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
        rep = json.loads(Path(argv[-1]).read_text())
        out[name] = {'exit': proc.returncode, 'stdout_tail': proc.stdout[-400:], 'report': argv[-1],
                     'summary': {k: v for k, v in rep.items() if not isinstance(v, (dict, list))}}
        if name.startswith('source52'):
            out[name]['matches_plan'] = expect['source52'] in json.dumps(rep)
    status = git('status', '--porcelain=v1', '-uall').stdout.splitlines()
    out['git_status'] = {'entry_count': len(status), 'entries': status,
                         'product_paths_changed': [s for s in status if re.search(
                             r' (recon_pipeline|smart_crawler|discover_site|prepare|tests|agent_docs/SKILLS)/|requirements', s)]}
    out['qa_disk'] = {'scratch_bytes': du(SCRATCH), 'lane_bytes': du(LANE)}
    out['qa_disk']['total_bytes'] = out['qa_disk']['scratch_bytes']+out['qa_disk']['lane_bytes']
    out['qa_disk']['within_500000000'] = out['qa_disk']['total_bytes'] <= 500_000_000
    parse = {}
    for p in sorted(LANE.rglob('*.json')):
        try:
            json.loads(p.read_bytes()); parse[p.relative_to(LANE).as_posix()] = 'ok'
        except ValueError as exc:
            parse[p.relative_to(LANE).as_posix()] = f'PARSE ERROR {exc}'
    out['result_json_parse'] = {'count': len(parse), 'errors': {k: v for k, v in parse.items() if v != 'ok'}}
    out['preserved_prior_runs'] = sorted(p.relative_to(LANE).as_posix() for p in LANE.rglob('*')
                                         if re.search(r'\.(run\d+|attempt\d+)\.', p.name))
    urls = set()
    for p in list((LANE/'native').rglob('*.json'))+list((LANE/'native').rglob('*.txt')):
        urls |= set(re.findall(r'https?://[^\s"\'<>\\]+', p.read_text(errors='replace')))
    def host(u):
        return re.match(r'https?://([^/:]+)', u).group(1)
    hosts = sorted({host(u) for u in urls})
    out['native_url_hosts'] = {'distinct_hosts': hosts,
                               'non_loopback_hosts': [h for h in hosts if h not in ('127.0.0.1', 'localhost')],
                               'note': 'hosts appearing anywhere in native evidence text; a non-loopback host here is '
                                       'data (e.g. a saved/declared URL), not proof of a request - classified below'}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'head_ok': out['head']['matches_execution_head'], 'ancestor': out['head']['candidate_is_ancestor'],
                      'hashes_ok': all(v['matches_plan'] for v in files.values()),
                      'source52': [out['source52_worktree']['matches_plan'], out['source52_snapshot']['matches_plan']],
                      'fixtures_exit': [out['fixtures_real_repo']['exit'], out['fixtures_snapshot']['exit']],
                      'git_entries': len(status), 'product_paths_changed': out['git_status']['product_paths_changed'],
                      'disk': out['qa_disk'], 'json_errors': out['result_json_parse']['errors'],
                      'non_loopback_hosts': out['native_url_hosts']['non_loopback_hosts']}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
