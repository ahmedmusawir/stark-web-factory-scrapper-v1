"""Additional native size/cap checks through the unchanged product supervisor.

Uses existing fixture server, measurement worker, raw reader and recorder. No
replacement transport/controller. All request destinations are loopback guarded.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
r=Path.cwd();sys.path.insert(0,str(r));sys.path.insert(0,str(r/'tests'))
from fixture_server import fixture_server
from handoff_probe import rest_payload
from prepare.reader import RawRun

e=Path(__file__).resolve().parent
for size in (1_500_000,8_000_000,10*1024*1024+4096):
    case=e/'supervisor-size-controls'/str(size);case.mkdir(parents=True,exist_ok=False)
    expected=rest_payload(size);cap=10*1024*1024
    with fixture_server(mode='pipeline',body_responses={
        '/wp-json/wp/v2/posts?per_page=100&page=1':expected}) as (origin,timeline):
        cmd=['venv/bin/python','tests/handoff_worker.py','--project','Fix','--url',origin,
            '--limit','1','--skip-prepare','--no-media-head','--fixture-only',
            '--max-seconds','180','--max-operations','30','--max-bytes','30000000',
            '--output-root',str(case/'output')]
        start=time.monotonic();p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=210)
        (case/'command.log').write_text(p.stdout[:100000])
        raw=RawRun(next((case/'output/Fix/runs').iterdir()))
        body=raw.bytes('rest/responses/posts-1.body')
        response=next(x for x in raw.rest_index['responses'] if x['collection']=='posts')
        col=next(x for x in raw.rest_index['collections'] if x['type']=='posts')
        hashes=raw.inventory();data={'command':cmd,'elapsed_s':time.monotonic()-start,'exit_code':p.returncode,
            'expected_bytes':size,'returned_bytes':len(body),'returned_sha256':hashlib.sha256(body).hexdigest(),
            'expected_returned_sha256':hashlib.sha256(expected[:cap]).hexdigest(),'exact_bytes':body==expected[:cap],
            'body_complete':response['body_complete'],'stop_reason':raw.manifest['access']['stop_reason'],
            'collection_status':col['status'],'objects':col['fetched_objects'],'raw':str(raw.root.relative_to(r)),
            'raw_hashes':hashes,'reader':'valid structurally; raw hashes retained','server_events':timeline}
        (case/'result.json').write_text(json.dumps(data,indent=2)+'\n')
        assert len(p.stdout)<100000
        assert data['exact_bytes']
        if size>cap:
            assert p.returncode==2 and data['stop_reason']=='response_limit'
            assert not response['body_complete'] and col['fetched_objects']==0
            assert not any(x['path'].startswith('/wp-json/wp/v2/media') for x in timeline)
        else:
            assert p.returncode==0 and data['stop_reason'] is None
            assert response['body_complete'] and col['fetched_objects']==100
        assert hashes==raw.inventory()
        print(json.dumps({k:data[k] for k in ('expected_bytes','returned_bytes','exact_bytes','exit_code','stop_reason','elapsed_s')}),flush=True)
