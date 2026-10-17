"""LEAD-02 retest G0 instrument: identity, diff, source52, fixtures, environment, snapshot.

Executor: Claudy (Claude Code, Claude Fable 5).
Expected identities are DERIVED from recorded files, never typed here:
- candidate SHA + repaired source52 + input ZIP hashes: lane g0-identity/DIRECTOR_GO_RETEST.txt
- four repaired file after-hashes: engineering lane changes/target-files-after.sha256
- plan-held hashes (original source52, requirements, fixture ZIPs, plan SHA):
  the installed approved plan 01_QAM_TEST_PLAN_FINAL.md (§0 table)
Checks: HEAD == released candidate; candidate diff vs its parent touches exactly
the four repaired paths + engineering lane records; four worktree file hashes ==
engineering after-hashes == candidate blob hashes; recomputed source52 (original
Q1 method: sha256 of sorted path:hash lines over the recorded 52-path inventory)
== GO expectation; fixtures 34/34; requirements/fixture-ZIP hashes still match
plan; working-tree drift classification; fresh snapshot of the REPAIRED candidate
via git archive into scratch, then source52 recomputed on the snapshot.
Writes argv[1] (JSON).
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1')
LANE = Path(__file__).resolve().parents[1]
ENG = REPO/'agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_2026-10-16_172752'
PLAN = REPO/'agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/WebFactory_Q1_Lead_Review_2026-10-15/01_QAM_TEST_PLAN_FINAL.md'
SCRATCH = Path('/tmp/claudy-lead02-retest-20261016')
SNAP = SCRATCH/'snapshot-repaired'
HEX64 = re.compile(r'`?([0-9a-f]{64})`?')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, capture_output=True, text=True)


def source52(root):
    """Original Q1 method (recorded in engineering baseline/source52-baseline.json):
    sha256(json.dumps(path->sha256, sort_keys=True, separators=(",",":"))) over the
    paths of the ORIGINAL_Q1 governing source-inventory.json."""
    base = json.loads((ENG/'baseline/source52-baseline.json').read_text())
    paths = sorted(base['worktree_map'])
    mapping, missing = {}, []
    for rel in paths:
        f = root/rel
        if not f.is_file():
            missing.append(rel)
            continue
        mapping[rel] = sha(f.read_bytes())
    digest = sha(json.dumps(mapping, sort_keys=True, separators=(',', ':')).encode())
    return digest, len(paths), missing


def main():
    go = (LANE/'g0-identity/DIRECTOR_GO_RETEST.txt').read_text()
    expect = {
        'candidate': re.search(r'RELEASED REPAIRED CANDIDATE\n([0-9a-f]{40})', go).group(1),
        'source52_repaired': re.search(r'Expected repaired source52:\n([0-9a-f]{64})', go).group(1),
        'eng_zip_sha': re.search(r'Engineering ZIP SHA-256:\n([0-9a-f]{64})', go).group(1),
        'hist_zip_sha': re.search(r'Historical QA ZIP SHA-256:\n([0-9a-f]{64})', go).group(1),
        'plan_sha': re.search(r'Approved plan SHA-256:\n([0-9a-f]{64})', go).group(1),
    }
    plan = PLAN.read_text(encoding='utf-8')
    def plan_row(label):
        return next(ln for ln in plan.splitlines() if ln.startswith(f'| {label}'))
    expect['requirements.txt'] = HEX64.search(plan_row('requirements.txt')).group(1)
    expect['requirements-lock.txt'] = HEX64.search(plan_row('requirements-lock.txt')).group(1)
    expect['prepare_zip'] = HEX64.search(plan_row('Prepare fixture ZIP')).group(1)
    expect['growth_zip'] = HEX64.search(plan_row('Growth Call fixture ZIP')).group(1)
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'expected_derived_from': ['g0-identity/DIRECTOR_GO_RETEST.txt',
                                     'engineering lane changes/target-files-after.sha256 + baseline/source52-baseline.json',
                                     str(PLAN) + f' (sha256 {sha(PLAN.read_bytes())})'],
           'plan_sha_matches_go': sha(PLAN.read_bytes()) == expect['plan_sha'],
           'expected': expect}
    head = git('rev-parse', 'HEAD').stdout.strip()
    out['head'] = {'actual': head, 'is_released_candidate': head == expect['candidate'],
                   'branch': git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip()}
    # committed repair diff: candidate vs parent
    ns = git('diff', '--name-status', f'{expect["candidate"]}~1..{expect["candidate"]}').stdout.splitlines()
    repaired = ['recon_pipeline/decide.py', 'tests/test_decide.py',
                'agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py',
                'agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py']
    non_lane = [l for l in ns if 'QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_' not in l]
    out['repair_commit_diff'] = {
        'total_paths': len(ns),
        'non_engineering_lane_paths': non_lane,
        'exactly_four_repaired_product_paths': sorted(l.split('\t')[1] for l in non_lane) == sorted(repaired)}
    # four repaired file hashes: worktree == engineering after == candidate blob
    after = {}
    for ln in (ENG/'changes/target-files-after.sha256').read_text().splitlines():
        h, _, p = ln.partition('  ')
        after[p.strip()] = h
    four = {}
    for rel in repaired:
        wt = sha((REPO/rel).read_bytes())
        blob = git('show', f'{expect["candidate"]}:{rel}').stdout.encode()
        four[rel] = {'worktree': wt, 'eng_after': after.get(rel),
                     'candidate_blob': sha(blob),
                     'all_equal': wt == after.get(rel) == sha(blob)}
    out['repaired_files'] = four
    # source52 on worktree
    dig, n, missing = source52(REPO)
    out['source52_worktree'] = {'digest': dig, 'paths': n, 'missing': missing,
                                'matches_go': dig == expect['source52_repaired']}
    # input ZIPs
    for key, path in {'eng_zip_sha': '/home/moose/Downloads/WebFactory_LEAD02_Engineering_Rework_2026-10-16_173633.zip',
                      'hist_zip_sha': '/home/moose/Downloads/WebFactory_QA_Q2_Package_2026-10-16_155121.zip'}.items():
        a = sha(Path(path).read_bytes())
        out[key] = {'actual': a, 'matches_go': a == expect[key]}
    # requirements + fixture ZIP hashes still match plan
    files = {}
    for rel, key in {'requirements.txt': 'requirements.txt', 'requirements-lock.txt': 'requirements-lock.txt',
                     'agent_docs/RESPONSES/response_2026-10-11_210309_prepare-v01.zip': 'prepare_zip',
                     'agent_docs/RESPONSES/response_2026-10-13_223736_growth-call-follow-up.zip': 'growth_zip'}.items():
        a = sha((REPO/rel).read_bytes())
        files[rel] = {'matches_plan': a == expect[key]}
    out['dependency_and_fixture_zips'] = files
    # fixture manifest 34/34 via existing Q2 helper (read-only against repo)
    q2h = REPO/'agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/Q2_2026-10-16_142632/helpers/verify_fixture_manifest.py'
    rep_path = LANE/'g0-identity/recheck_fixtures_worktree.json'
    proc = subprocess.run([str(REPO/'venv/bin/python'), str(q2h), str(REPO), str(rep_path)],
                          capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
    out['fixtures_worktree'] = {'exit': proc.returncode, 'stdout_tail': proc.stdout[-300:], 'report': str(rep_path)}
    # drift classification
    status = git('status', '--porcelain=v1', '-uall').stdout.splitlines()
    expected_drift = {'CHANGELOG.md', 'RECOVERY.md', 'agent_docs/SESSIONS/session_2026-10-16.md',
                      'agent_docs/RESPONSES/response_2026-10-16_165613_cody-engineer-recovery.md',
                      'agent_docs/RESPONSES/response_2026-10-16_172610_lead02-repair-plan.md'}
    unexpected = [s for s in status
                  if s[3:] not in expected_drift
                  and 'QAM/HANDOFFS/RETEST_LEAD02_2026-10-16_180559' not in s]
    out['working_tree'] = {'entries': len(status), 'unexpected_non_lane_drift': unexpected,
                           'product_paths_changed': [s for s in status if re.search(
                               r' (recon_pipeline|smart_crawler|discover_site|prepare|tests|agent_docs/SKILLS)/|requirements', s)]}
    # fresh snapshot of the repaired committed candidate
    SNAP.mkdir(parents=True, exist_ok=False)
    tar = SCRATCH/'candidate.tar'
    with open(tar, 'wb') as fh:
        subprocess.run(['git', 'archive', expect['candidate']], cwd=REPO, stdout=fh, check=True)
    subprocess.run(['tar', '-xf', str(tar), '-C', str(SNAP)], check=True)
    tar.unlink()
    sdig, sn, smissing = source52(SNAP)
    out['snapshot'] = {'path': str(SNAP), 'source52': sdig, 'paths': sn, 'missing': smissing,
                       'matches_go': sdig == expect['source52_repaired'],
                       'note': 'fresh git-archive of the repaired committed candidate; old pre-repair Q2 snapshot untouched'}
    # environment
    pyv = subprocess.run([str(REPO/'venv/bin/python'), '-V'], capture_output=True, text=True).stdout.strip()
    out['environment'] = {'interpreter': str(REPO/'venv/bin/python'), 'python': pyv}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    keys = ['plan_sha_matches_go']
    summary = {'head_ok': out['head']['is_released_candidate'],
               'diff_four_paths': out['repair_commit_diff']['exactly_four_repaired_product_paths'],
               'four_files_equal': all(v['all_equal'] for v in four.values()),
               'source52_worktree_ok': out['source52_worktree']['matches_go'],
               'source52_snapshot_ok': out['snapshot']['matches_go'],
               'zips_ok': out['eng_zip_sha']['matches_go'] and out['hist_zip_sha']['matches_go'],
               'plan_ok': out['plan_sha_matches_go'],
               'deps_fixture_zips_ok': all(v['matches_plan'] for v in files.values()),
               'fixtures_exit': out['fixtures_worktree']['exit'],
               'unexpected_drift': out['working_tree']['unexpected_non_lane_drift'],
               'product_paths_changed': out['working_tree']['product_paths_changed']}
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
