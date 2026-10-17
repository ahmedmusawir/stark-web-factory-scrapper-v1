"""Q2 QA-authored export/privacy checker (T-23 validated, gates T-24 packaging).

Not a product feature: the product has no export/privacy checker. This tool
checks a candidate export TREE (directory mode) or ZIP (zip mode) against an
explicit inclusion manifest {"members": {relpath: sha256 | {"sha256", "bytes"}}}:

  (a) membership exact (missing / unexpected members listed)
  (b) per-member sha256 (and bytes when given) - exact mismatch locations
  (c) prohibited members (runtime profiles, cookies/auth storage, credential/env
      files, dependencies, caches, Git internals, symlinks, unsafe zip names)
  (d) nested archives rejected explicitly (no-nesting rule)
  (e) content scan of EVERY member for credential-shaped values

Hits are reported by member + line + pattern id only; matched values are never
printed. Word mentions in prose ('cookie', '.env', 'Set-Cookie') are not banned:
only value-bearing shapes match. A false positive can be adjudicated only at an
exact (member, line, pattern) location via --adjudications; adjudicated hits stay
listed, unmatched adjudications are reported stale and fail the run.

Usage: q2_export_checker.py TREE_OR_ZIP MANIFEST [--json OUT] [--adjudications FILE]
Exit: 0 PASS, 1 FAIL, 2 usage/input error.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

PATTERNS = {
    'authorization_header': re.compile(r'(?im)^\s*Authorization\s*:\s*\S+'),
    'set_cookie_value': re.compile(r'(?im)^\s*Set-Cookie\s*:\s*[^\s=;]+='),
    'credential_assignment': re.compile(
        r'(?im)\b(api[_-]?key|apikey|password|passwd|secret|access[_-]?token|auth[_-]?token|client[_-]?secret)\b'
        r'\s*[:=]\s*["\']?[A-Za-z0-9+/_.\-]{8,}["\']?'),
    'aws_access_key_id': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    'google_api_key': re.compile(r'\bAIza[0-9A-Za-z_\-]{35}\b'),
}
NESTED_SUFFIXES = ('.zip', '.tar', '.tgz', '.tar.gz', '.gz', '.7z', '.rar')
PROHIBITED_DIRS = {'.runtime': 'runtime profile', '.git': 'Git internals', '__pycache__': 'cache',
                   '.pytest_cache': 'cache', 'node_modules': 'dependency tree', 'venv': 'dependency tree',
                   '.venv': 'dependency tree', 'site-packages': 'dependency tree', '.crawl4ai': 'runtime profile'}
PROHIBITED_NAMES = {'cookies.json': 'cookie storage', 'auth_storage.json': 'auth storage',
                    'storage_state.json': 'auth storage', 'Cookies': 'browser cookie store',
                    'credentials.json': 'credential file', 'id_rsa': 'private key', 'id_ed25519': 'private key',
                    '.writer.lock': 'runtime lock'}
PROHIBITED_SUFFIXES = {'.pyc': 'cache', '.pem': 'key material', '.key': 'key material'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prohibited_reason(rel):
    parts = PurePosixPath(rel).parts
    for part in parts[:-1]:
        if part in PROHIBITED_DIRS:
            return PROHIBITED_DIRS[part]+f' ({part}/)'
    name = parts[-1]
    if name in PROHIBITED_NAMES:
        return PROHIBITED_NAMES[name]
    if name == '.env' or name.startswith('.env.'):
        return 'credential/env file'
    for suffix, reason in PROHIBITED_SUFFIXES.items():
        if name.endswith(suffix):
            return reason
    return None


def read_members(target):
    """Return ({relpath: bytes}, [structural problems])."""
    members, problems = {}, []
    if target.is_dir():
        for p in sorted(target.rglob('*')):
            rel = p.relative_to(target).as_posix()
            if p.is_symlink():
                problems.append({'path': rel, 'reason': 'symlink member'})
            elif p.is_file():
                members[rel] = p.read_bytes()
        return members, problems
    with zipfile.ZipFile(target) as archive:
        bad = archive.testzip()
        if bad is not None:
            problems.append({'path': bad, 'reason': 'zip CRC failure'})
        for info in archive.infolist():
            name = info.filename
            pure = PurePosixPath(name)
            if name.startswith('/') or '..' in pure.parts or '\\' in name:
                problems.append({'path': name, 'reason': 'unsafe zip member name'})
                continue
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                problems.append({'path': name, 'reason': 'symlink member'})
                continue
            if info.is_dir():
                continue
            if name in members:
                problems.append({'path': name, 'reason': 'duplicate zip member'})
            members[name] = archive.read(info)
    return members, problems


def scan(rel, data):
    text = data.decode('utf-8', errors='replace')
    hits = []
    for pattern_id, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            hits.append({'path': rel, 'line': text.count('\n', 0, match.start())+1, 'pattern': pattern_id})
    return hits


def check(target, manifest, adjudications=()):
    expected = {k: (v if isinstance(v, dict) else {'sha256': v}) for k, v in manifest['members'].items()}
    members, problems = read_members(target)
    report = {'target': str(target), 'mode': 'dir' if target.is_dir() else 'zip',
              'members_found': len(members), 'members_expected': len(expected),
              'missing': sorted(set(expected)-set(members)), 'unexpected': sorted(set(members)-set(expected)),
              'hash_mismatch': [], 'size_mismatch': [], 'structural': problems, 'prohibited': [],
              'nested_archives': [], 'content_hits': [], 'adjudicated_hits': [], 'stale_adjudications': []}
    for rel, data in sorted(members.items()):
        want = expected.get(rel)
        if want is not None:
            if sha(data) != want['sha256']:
                report['hash_mismatch'].append({'path': rel, 'expected': want['sha256'], 'actual': sha(data)})
            if 'bytes' in want and len(data) != want['bytes']:
                report['size_mismatch'].append({'path': rel, 'expected': want['bytes'], 'actual': len(data)})
        reason = prohibited_reason(rel)
        if reason:
            report['prohibited'].append({'path': rel, 'reason': reason})
        if rel.lower().endswith(NESTED_SUFFIXES):
            report['nested_archives'].append(rel)
        report['content_hits'].extend(scan(rel, data))
    allowed = {(a['path'], a['line'], a['pattern']) for a in adjudications}
    used = set()
    for hit in list(report['content_hits']):
        loc = (hit['path'], hit['line'], hit['pattern'])
        if loc in allowed:
            used.add(loc)
            report['content_hits'].remove(hit)
            report['adjudicated_hits'].append(hit)
    report['stale_adjudications'] = [dict(zip(('path', 'line', 'pattern'), loc)) for loc in sorted(allowed-used)]
    failing = ('missing', 'unexpected', 'hash_mismatch', 'size_mismatch', 'structural', 'prohibited',
               'nested_archives', 'content_hits', 'stale_adjudications')
    report['failures'] = {k: len(report[k]) for k in failing if report[k]}
    report['verdict'] = 'FAIL' if report['failures'] else 'PASS'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('target', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--json', type=Path)
    parser.add_argument('--adjudications', type=Path)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_bytes())
        adjudications = json.loads(args.adjudications.read_bytes()) if args.adjudications else []
        if not args.target.exists():
            raise FileNotFoundError(args.target)
        report = check(args.target, manifest, adjudications)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(f'checker error: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict': report['verdict'], 'mode': report['mode'], 'members_found': report['members_found'],
                      'failures': report['failures'], 'adjudicated_hits': len(report['adjudicated_hits'])}))
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
