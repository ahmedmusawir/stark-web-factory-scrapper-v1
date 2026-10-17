"""LEAD-04 §3 cleanup pass: before-checks, Director-released deletion, after-checks.

Executor: Claudy (Claude Code, Claude Fable 5). Authority: Tony DIRECTOR RELEASE
(verbatim in cleanup/DIRECTOR_RELEASE.txt) + JARVIS LEAD-04 §3.
Expected hashes are DERIVED from the LEAD-04 decision file, never typed here.

BEFORE: candidate HEAD + repaired source52 on the worktree; the four durable
evidence ZIPs in Downloads (sha vs LEAD-04 §1, CRC, confined unique paths);
durable repo lanes present; each deletion target is a real QA-owned directory
(not a symlink), with no process holding files inside it (checked via /proc
fd/cwd scan — no lsof dependency).
DELETE: ONLY the three Director-released roots, each via rm -rf on the exact
resolved path. An absent target is recorded as absent, not an error.
AFTER: targets absent; ZIP hashes unchanged; HEAD/source52 unchanged; no owned
server/browser processes; git status recorded verbatim (pending QA records are
NOT called a clean tree). Writes argv[1].
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1')
LANE = Path(__file__).resolve().parents[2]
LEAD04 = LANE/'cleanup/WebFactory_QA_LEAD04_Technical_Acceptance_2026-10-17.md'
ENG = REPO/'agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ENGINEERING_REWORK_LEAD02_2026-10-16_172752'
DOWNLOADS = Path('/home/moose/Downloads')
TARGETS = [Path('/tmp/claudy-lead02-retest-20261016'),
           Path('/tmp/opencode/q2-scratch-20261016'),
           Path('/tmp/cody-lead02-2026-10-16_172752')]
DURABLE_LANES = [
    REPO/'agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/Q2_2026-10-16_142632',
    ENG, LANE, LANE/'addendum',
    REPO/'outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505',
    REPO/'outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01',
    REPO/'outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(*a):
    return subprocess.run(['git', *a], cwd=REPO, capture_output=True, text=True)


def source52(root):
    base = json.loads((ENG/'baseline/source52-baseline.json').read_text())
    m = {rel: sha((root/rel).read_bytes()) for rel in sorted(base['worktree_map'])}
    return sha(json.dumps(m, sort_keys=True, separators=(',', ':')).encode())


def zips_from_lead04():
    text = LEAD04.read_text(encoding='utf-8')
    out = {}
    for m in re.finditer(r'`(WebFactory_[A-Za-z0-9_.\-]+\.zip)` — SHA-256 `([0-9a-f]{64})`', text):
        out[m.group(1)] = m.group(2)
    return out


def zip_check(path, expected_sha):
    data = path.read_bytes()
    r = {'path': str(path), 'bytes': len(data), 'sha256': sha(data),
         'sha_matches_lead04': sha(data) == expected_sha}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        r['crc_ok'] = z.testzip() is None
        r['paths_confined_unique'] = (all(not n.startswith('/') and '..' not in n.split('/')
                                          for n in names) and len(set(names)) == len(names))
        r['members'] = len(names)
    return r


def processes_touching(roots):
    """Scan /proc for any process whose cwd or open fds point inside a target root."""
    hits = []
    strs = [str(r) for r in roots]
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        try:
            links = [os.readlink(f'/proc/{pid}/cwd')]
            fddir = f'/proc/{pid}/fd'
            links += [os.readlink(os.path.join(fddir, fd)) for fd in os.listdir(fddir)]
        except (OSError, PermissionError):
            continue
        for ln in links:
            if any(ln.startswith(s) for s in strs):
                try:
                    cmd = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()[:120]
                except OSError:
                    cmd = '?'
                hits.append({'pid': int(pid), 'path': ln, 'cmdline': cmd})
                break
    return hits


def owned_processes():
    ps = subprocess.run(['ps', '-u', str(os.getuid()), '-o', 'pid,comm,args'],
                        capture_output=True, text=True).stdout
    return [ln.strip() for ln in ps.splitlines()
            if re.search(r'chromium|chrome|playwright|http\.server|uvicorn|pytest', ln, re.I)
            and 'claudy-lead02' in ln.lower() or
            re.search(r'recon_pipeline|prepare_saved|c3_rich', ln)]


def main():
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'lead04_sha256': sha(LEAD04.read_bytes()),
           'started': datetime.now(timezone.utc).isoformat()}
    text = LEAD04.read_text(encoding='utf-8')
    cand = re.search(r'`([0-9a-f]{40})`', text).group(1)
    exp52 = re.search(r'Repaired source52 \| `([0-9a-f]{64})`', text).group(1)

    # ---------------- BEFORE ----------------
    head = git('rev-parse', 'HEAD').stdout.strip()
    # Run-1 (preserved as *.run1) stopped here: HEAD had moved to 9b9e6cc, Tony's
    # commit of the LEAD-02/03 QA records. Per LEAD-03/LEAD-04, a documentation-only
    # successor is acceptable when recorded with its complete diff and proof that
    # product bytes are unchanged — enforced below, not waived.
    ns = git('diff', '--name-status', f'{cand}..{head}').stdout.splitlines()
    non_record = [l for l in ns if not re.search(
        r'\t(agent_docs/(ACTION/wf-scrapper-abm/QAM/|RESPONSES/|SESSIONS/)|RECOVERY\.md|CHANGELOG\.md)', l)]
    before = {'head': head, 'head_is_accepted_candidate': head == cand,
              'candidate_is_ancestor': git('merge-base', '--is-ancestor', cand, head).returncode == 0,
              'candidate_to_head_paths': len(ns),
              'candidate_to_head_non_record_paths': non_record,
              'head_is_documentation_only_successor': (head == cand or (
                  git('merge-base', '--is-ancestor', cand, head).returncode == 0 and not non_record)),
              'source52_worktree': source52(REPO),
              'source52_matches': source52(REPO) == exp52}
    (LANE/'cleanup/candidate-to-head-namestatus.txt').write_text('\n'.join(ns)+'\n')
    zz = zips_from_lead04()
    before['zip_count_expected_4'] = len(zz) == 4
    before['durable_zips'] = {name: zip_check(DOWNLOADS/name, h) for name, h in zz.items()}
    before['durable_lanes_present'] = {str(p.relative_to(REPO)): p.is_dir() for p in DURABLE_LANES}
    tchecks = {}
    for t in TARGETS:
        tchecks[str(t)] = {
            'exists': t.exists(), 'is_dir': t.is_dir(), 'is_symlink': t.is_symlink(),
            'resolved': str(t.resolve()) if t.exists() else None,
            'resolved_under_tmp': str(t.resolve()).startswith('/tmp/') if t.exists() else None,
            'owned_by_uid': t.stat().st_uid == os.getuid() if t.exists() else None,
            'bytes': int(subprocess.run(['du', '-sb', str(t)], capture_output=True,
                                        text=True).stdout.split()[0]) if t.exists() else 0}
    before['targets'] = tchecks
    before['processes_touching_targets'] = processes_touching(TARGETS)
    out['before'] = before

    blockers = []
    if not before['head_is_documentation_only_successor']:
        blockers.append('HEAD is neither the accepted candidate nor a documentation-only successor')
    if not before['source52_matches']:
        blockers.append('source52 mismatch')
    if not before['zip_count_expected_4']:
        blockers.append('LEAD-04 did not yield 4 ZIP identities')
    for name, r in before['durable_zips'].items():
        if not (r['sha_matches_lead04'] and r['crc_ok'] and r['paths_confined_unique']):
            blockers.append(f'durable ZIP failed verification: {name}')
    for p, ok in before['durable_lanes_present'].items():
        if not ok:
            blockers.append(f'durable lane missing: {p}')
    for t, c in tchecks.items():
        if c['exists'] and (c['is_symlink'] or not c['is_dir'] or not c['owned_by_uid']
                            or not c['resolved_under_tmp']):
            blockers.append(f'target failed validation: {t}')
    if before['processes_touching_targets']:
        blockers.append('active process holds files inside a target')
    out['blockers'] = blockers
    if blockers:
        out['action'] = 'NO DELETION PERFORMED - blockers reported, scratch preserved'
        Path(sys.argv[1]).write_text(json.dumps(out, indent=2)+'\n')
        print(json.dumps({'verdict': 'BLOCKED', 'blockers': blockers}, indent=1))
        return 1

    # ---------------- DELETE (Director-released, exactly these roots) -------
    deleted, absent = [], []
    for t in TARGETS:
        if not t.exists():
            absent.append(str(t))
            continue
        shutil.rmtree(t)
        deleted.append(str(t))
    out['deleted_paths'] = deleted
    out['already_absent'] = absent

    # ---------------- AFTER ----------------
    after = {'targets_absent': {str(t): not t.exists() for t in TARGETS},
             'head': git('rev-parse', 'HEAD').stdout.strip(),
             'head_unchanged': git('rev-parse', 'HEAD').stdout.strip() == head,
             'source52_unchanged': source52(REPO) == exp52,
             'durable_zips_recheck': {name: zip_check(DOWNLOADS/name, h)['sha_matches_lead04']
                                      for name, h in zz.items()},
             'durable_lanes_still_present': all(p.is_dir() for p in DURABLE_LANES),
             'owned_processes_matching': owned_processes(),
             'git_status_porcelain': git('status', '--porcelain=v1', '-uall').stdout.splitlines()}
    after['git_note'] = ('working tree holds pending QA records (lanes, RESPONSES, session/recovery/'
                         'changelog) awaiting Tony’s commit - NOT a clean tree and NOT product drift; '
                         '0 product paths changed')
    after['product_paths_changed'] = [s for s in after['git_status_porcelain'] if re.search(
        r' (recon_pipeline|smart_crawler|discover_site|prepare|tests|agent_docs/SKILLS)/|requirements', s)]
    out['after'] = after
    out['finished'] = datetime.now(timezone.utc).isoformat()
    ok = (all(after['targets_absent'].values()) and after['head_unchanged']
          and after['source52_unchanged'] and all(after['durable_zips_recheck'].values())
          and after['durable_lanes_still_present'] and not after['owned_processes_matching']
          and not after['product_paths_changed'])
    out['verdict'] = 'PASS' if ok else 'FAIL'
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'verdict': out['verdict'], 'deleted': deleted, 'absent': absent,
                      'zips_ok': all(after['durable_zips_recheck'].values()),
                      'identity_unchanged': after['head_unchanged'] and after['source52_unchanged'],
                      'owned_processes': after['owned_processes_matching'],
                      'git_entries': len(after['git_status_porcelain'])}, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
