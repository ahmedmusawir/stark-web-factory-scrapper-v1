"""Actual supervised Chromium worker: caps, SIGINT, hard deadline, partial retention."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import pytest
from fixture_server import fixture_server
from prepare.reader import RawRun


def retain(name, result, timeline, raw):
    dest=os.environ.get('ABM_CONTROL_EVIDENCE')
    if dest:
        folder=Path(dest)/name;folder.mkdir(parents=True,exist_ok=False)
        (folder/'command.log').write_text(result.stdout+result.stderr)
        (folder/'server.json').write_text(json.dumps(timeline,indent=2))
        (folder/'result.json').write_text(json.dumps({'exit_code':result.returncode,'raw':str(raw.root),
            'raw_hashes':raw.inventory(),'stop_reason':raw.manifest['access']['stop_reason']},indent=2))
        import shutil
        shutil.copytree(raw.root,folder/'raw')


@pytest.mark.parametrize('kind',['operation_cap','global_watchdog','interrupt','persistence_cap','bootstrap_challenge'])
def test_actual_worker_preserves_partial_on_stop(tmp_path,kind):
    with fixture_server(mode='pipeline') as (origin,timeline):
        seconds='36' if kind=='global_watchdog' else '120'
        route={'global_watchdog':'/hang/','persistence_cap':'/persistence-cap/','bootstrap_challenge':'/soft-challenge/'}.get(kind,'')
        url=origin+route
        cmd=[sys.executable,'-m','recon_pipeline','--project','Fix','--url',url,'--skip-prepare','--fixture-only',
             '--max-seconds',seconds,'--max-operations','1' if kind=='operation_cap' else '40',
             '--max-bytes','6000000' if kind=='persistence_cap' else '20000000','--output-root',str(tmp_path/'output')]
        start=time.monotonic()
        if kind=='interrupt':
            proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            deadline=time.monotonic()+20
            while not any(e['event']=='request_received' and e['path']=='/robots.txt' for e in timeline):
                assert proc.poll() is None
                assert time.monotonic()<deadline
                time.sleep(.05)
            proc.send_signal(signal.SIGINT)
            out,err=proc.communicate(timeout=12)
            result=subprocess.CompletedProcess(cmd,proc.returncode,out,err)
        else:result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        raw=RawRun(next((tmp_path/'output/Fix/runs').iterdir()))
        retain(kind,result,timeline,raw)
        assert result.returncode==(130 if kind=='interrupt' else 2),result.stdout+result.stderr
        assert raw.manifest['stopped_early']
        if kind in ('global_watchdog','interrupt'):
            assert 'supervisor stop '+('interrupted' if kind=='interrupt' else kind) in raw.bytes('stage_log.txt').decode()
        assert time.monotonic()-start<25
        requests=[e for e in timeline if e['event']=='request_received']
        if kind in ('operation_cap','global_watchdog'):
            assert len(requests)==(2 if kind=='operation_cap' else 1) # bootstrap's image is incidental
        if kind=='operation_cap':
            assert raw.manifest['access']['intentional_dispatches']==1
            assert raw.manifest['access']['stop_reason']=='operation_limit'
            assert raw.routes['sources'][0]['file']=='bootstrap.html'
            assert raw.bytes('discovery/bootstrap.html')
        if kind=='interrupt':assert raw.bytes('discovery/bootstrap.html')
        if kind=='persistence_cap':
            assert len(requests)==1
            assert raw.manifest['access']['stop_reason']=='capture_failure:BufferError'
            assert 'persisted_byte_limit' in raw.bytes('stage_log.txt').decode()
            assert sum(p.stat().st_size for p in raw.root.rglob('*') if p.is_file())<6000000
            assert any(a['stream']=='discovery' and a['outcome']=='failed' for a in raw.absences)
        if kind=='bootstrap_challenge':
            assert len(requests)==1 and raw.manifest['access']['stop_reason']=='explicit_block_document'
            assert raw.manifest['counts']['captured']==0
            assert b'Access Denied' in raw.bytes('discovery/bootstrap-failed.html')
        assert not (tmp_path/'output/Fix/packs').exists()
