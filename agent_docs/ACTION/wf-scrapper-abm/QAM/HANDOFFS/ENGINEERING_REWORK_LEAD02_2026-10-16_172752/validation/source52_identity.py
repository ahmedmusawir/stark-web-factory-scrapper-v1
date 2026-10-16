"""Recompute the source52 identity over the WORKTREE with the LEAD-01 §0 method
(SHA-256 of compact sorted JSON path->sha256 map), plus any added product/test
paths given after the output path so additions cannot hide behind the 52 list."""
import hashlib, json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[7]
INV = REPO/'agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/WebFactory_Q1_Lead_Review_2026-10-15/ORIGINAL_Q1/governing/source-inventory.json'
def digest(m): return hashlib.sha256(json.dumps(m, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
inv = json.loads(INV.read_bytes()); recorded = inv['files']
worktree = {p: hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in recorded}
extra = {p: hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in sys.argv[2:]}
out = {'method': 'sha256(json.dumps(path->sha256, sort_keys=True, separators=(",",":")))', 'inventory_file': str(INV.relative_to(REPO)),
       'recorded_source52': inv['sha256'], 'worktree_source52': digest(worktree), 'file_count': len(worktree),
       'changed_vs_inventory': {p: {'inventory': recorded[p], 'worktree': h} for p, h in worktree.items() if recorded[p] != h},
       'added_paths_outside_52': extra, 'source52_plus_additions': digest({**worktree, **extra}) if extra else None, 'worktree_map': worktree}
Path(sys.argv[1]).write_text(json.dumps(out, indent=1)+'\n'); print(json.dumps({k: out[k] for k in ('recorded_source52','worktree_source52','file_count')}, indent=1)); print('changed:', list(out['changed_vs_inventory']))
