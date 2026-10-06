"""Regenerate into a NEW retained directory and check independently authored facts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fixture_server import fixture_server
from snapshot_compare import compare_capture, compare_two_captures
from smart_crawler.rest_client import source_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',required=True,action='store_true')
    p.add_argument('--variant',choices=['complete'],required=True)
    p.add_argument('--stage',choices=['capture','pipeline'],required=True)
    p.add_argument('--compare-to',type=Path,help='prior independent capture with the identical source inventory')
    args=p.parse_args()
    if args.stage!='capture':p.error('pipeline snapshot remains pending Stage P/E1; no false success')
    parent=Path(os.environ.get('ABM_CONTROL_EVIDENCE',tempfile.gettempdir()));parent.mkdir(parents=True,exist_ok=True)
    evidence=Path(tempfile.mkdtemp(prefix='F09-complete-',dir=parent))
    with fixture_server(mode='pipeline',port=8765) as (origin,timeline):
        cmd=[sys.executable,'-m','recon_pipeline','--project','Fix','--url',origin,'--skip-prepare','--fixture-only',
             '--max-operations','40','--max-seconds','600','--max-bytes','20000000','--output-root',str(evidence/'output')]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
        (evidence/'command.log').write_text(result.stdout+result.stderr)
        (evidence/'command.json').write_text(json.dumps({'argv':cmd,'exit_code':result.returncode},indent=2))
        (evidence/'server.json').write_text(json.dumps(timeline,indent=2))
        print('FIXTURE EVIDENCE: '+str(evidence))
        assert result.returncode==0,'Capture fixture failed; inspect preserved command.log'
        root=next((evidence/'output/Fix/runs').iterdir())
        compared=compare_capture(root,timeline)
        (evidence/'comparison.json').write_text(source_json(compared)+'\n')
        if args.compare_to:
            (evidence/'full-comparison.json').write_text(json.dumps(compare_two_captures(args.compare_to,root),indent=2))
    print('PASS F-09 complete Capture facts, source bytes, references, inventory and actual pacing')


if __name__=='__main__':main()
