"""Package the engineering lane: value-aware hygiene scan, MANIFEST.sha256.json,
ZIP to Downloads, verification (CRC, confined unique names, exact membership,
sizes/hashes) and a receipt written OUTSIDE the ZIP. Usage: package_lane.py <lane> <zip-path>"""
import hashlib, json, os, re, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
lane, zpath = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
EXCLUDE_DIRS = {'__pycache__'}; EXCLUDE_NAMES = {'MANIFEST.sha256.json', 'ZIP_RECEIPT.json', 'hygiene_scan.json'}
PROHIBITED = re.compile(r'(^|/)(\.runtime|\.env|\.git|node_modules)(/|$)|\.(zip|pem|key|p12|sqlite)$')
# Value-aware patterns: secrets by shape, not by vocabulary (words like "cookie"/"token" in tests/docs are not failures).
PATTERNS = {'google_api_key': re.compile(r'AIza[0-9A-Za-z_\-]{35}'), 'aws_access_key': re.compile(r'AKIA[0-9A-Z]{16}'), 'private_key_block': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
            'bearer_token': re.compile(r'(?i)bearer\s+[A-Za-z0-9\-_\.=]{20,}'), 'set_cookie_header_value': re.compile(r'(?i)^set-cookie:\s*\S+', re.M), 'github_token': re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),
            'password_assignment': re.compile(r'(?i)(password|passwd|secret)\s*[:=]\s*["\'][^"\']{6,}["\']')}
ADJUDICATED = {}  # exact-location adjudications {relpath: [pattern names accepted]} — none expected for this lane
files = sorted(p for p in lane.rglob('*') if p.is_file() and not (set(p.relative_to(lane).parts) & EXCLUDE_DIRS) and p.name not in EXCLUDE_NAMES)
hits, prohibited = [], []
for p in files:
    rel = p.relative_to(lane).as_posix()
    if PROHIBITED.search(rel): prohibited.append(rel)
    try: text = p.read_text(encoding='utf-8')
    except UnicodeDecodeError: continue
    for name, rx in PATTERNS.items():
        for m in rx.finditer(text):
            if name in ADJUDICATED.get(rel, []): continue
            hits.append({'file': rel, 'pattern': name, 'line': text.count('\n', 0, m.start())+1})  # location only; value never echoed
scan = {'files_scanned': len(files), 'prohibited_members': prohibited, 'unadjudicated_hits': hits, 'adjudicated': ADJUDICATED, 'result': 'PASS' if not hits and not prohibited else 'FAIL'}
(lane/'hygiene_scan.json').write_text(json.dumps(scan, indent=1)+'\n')
if scan['result'] != 'PASS': print(json.dumps(scan, indent=1)); sys.exit(2)
manifest = {'lane': lane.name, 'created_utc': datetime.now(timezone.utc).isoformat(), 'historical_q2_zip': {'name': 'WebFactory_QA_Q2_Package_2026-10-16_155121.zip', 'sha256': '06f73841cc678badd30d56bfb4c41614c376b16abe7254ea1e374a96c1d974df', 'bytes': 499912, 'nested': False},
            'members': {p.relative_to(lane).as_posix(): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in files + [lane/'hygiene_scan.json']}}
(lane/'MANIFEST.sha256.json').write_text(json.dumps(manifest, indent=1)+'\n')
members = files + [lane/'hygiene_scan.json', lane/'MANIFEST.sha256.json']
if zpath.exists(): sys.exit('refusing to overwrite '+str(zpath))
with zipfile.ZipFile(zpath, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in members: z.write(p, (lane.name+'/'+p.relative_to(lane).as_posix()))
# Verify: CRC, confined unique names, exact membership against manifest, sizes/hashes
with zipfile.ZipFile(zpath) as z:
    bad = z.testzip(); names = z.namelist()
    assert bad is None, bad; assert len(names) == len(set(names)); assert all(not n.startswith('/') and '..' not in n.split('/') for n in names)
    expected = {lane.name+'/'+k for k in manifest['members']} | {lane.name+'/MANIFEST.sha256.json'}; assert set(names) == expected, (set(names) ^ expected)
    for n in names:
        data = z.read(n); key = n[len(lane.name)+1:]
        if key != 'MANIFEST.sha256.json': assert hashlib.sha256(data).hexdigest() == manifest['members'][key]['sha256'] and len(data) == manifest['members'][key]['bytes'], key
receipt = {'zip': str(zpath), 'bytes': zpath.stat().st_size, 'sha256': hashlib.sha256(zpath.read_bytes()).hexdigest(), 'members': len(names), 'verified': ['crc', 'unique_confined_names', 'exact_manifest_membership', 'sizes_hashes', 'hygiene_scan PASS'], 'created_utc': manifest['created_utc']}
(lane/'ZIP_RECEIPT.json').write_text(json.dumps(receipt, indent=1)+'\n'); print(json.dumps(receipt, indent=1))
