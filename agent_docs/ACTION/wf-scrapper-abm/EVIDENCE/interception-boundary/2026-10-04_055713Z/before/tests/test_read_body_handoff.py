"""Native size/fidelity proof, including the actual Capture worker/supervisor."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit

import pytest
from fixture_server import fixture_server
from handoff_probe import MeasuredSession,rest_payload,SIZES,retain_measurement
from smart_crawler.browser_session import Bounds,CollectionStopped
from prepare.reader import RawRun
from test_pipeline_shutdown import retain as retain_pipeline


@pytest.mark.parametrize('size,history',[(size,1) for size in SIZES]+[(4_000_000,3)])
def test_native_rest_size_byte_fidelity(tmp_path,size,history):
    expected=rest_payload(size)
    with fixture_server(body_responses={'/handoff-rest':expected}) as (origin,timeline):
        async def exercise():
            s=MeasuredSession(origin,bounds=Bounds(seconds=180,document_slots=4),
                runtime_dir=tmp_path/'runtime',loopback_only=True)
            result=None;started=time.monotonic()
            try:
                async with s:
                    for _ in range(history):assert (await s.capture(origin+'/handoff-activity'))['ok']
                    result=await s.read(origin+'/handoff-rest')
                    assert result['body']==expected[:s.bounds.response_bytes]
                    assert result['sha256']==hashlib.sha256(expected[:s.bounds.response_bytes]).hexdigest()
                    if size>s.bounds.response_bytes:
                        assert result['incomplete'] and result['error']==s.stop_reason=='response_limit'
                        with pytest.raises(CollectionStopped):await s.read(origin+'/never')
                    else:
                        assert not result['incomplete'] and result['error'] is None and s.stop_reason is None
                        decoded=json.loads(result['body']);assert len(decoded)==100
                        assert decoded[0]['title']['rendered']=='বাংলা café 😀 0'
                        assert decoded[0]['unknown']['large']==900719925474099312345
                        assert 'yoast_head_json' in decoded[0]
                    dispatch=[v for v in s.events if v['event']=='intentional_dispatch']
                    assert len(dispatch)==history+1
                    assert all(v['monotonic']-v['preceding_completion']>=5 for v in dispatch[1:])
                    assert not any(v['event']=='external_test_request_prevented' or
                                   v.get('reason')=='fixture_egress' for v in s.events)
                    assert all(urlsplit(v['url']).hostname=='127.0.0.1' for v in s.events
                               if v['event'] in ('intentional_dispatch','browser_request'))
            finally:
                retain_measurement(os.environ.get('ABM_CONTROL_EVIDENCE',tmp_path),
                    f'body-{size}-history-{history}',s,timeline,result,expected,time.monotonic()-started)
        asyncio.run(exercise())


def test_actual_supervisor_rest_body_handoff(tmp_path):
    expected=rest_payload(4_000_000)
    with fixture_server(mode='pipeline',body_responses={
            '/wp-json/wp/v2/posts?per_page=100&page=1':expected}) as (origin,timeline):
        cmd=[sys.executable,str(Path(__file__).with_name('handoff_worker.py')),
            '--project','Fix','--url',origin,'--limit','1','--skip-prepare','--no-media-head',
            '--fixture-only','--max-seconds','180','--max-operations','30',
            '--max-bytes','30000000','--output-root',str(tmp_path/'output')]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
        raw=RawRun(next((tmp_path/'output/Fix/runs').iterdir()))
        retain_pipeline('supervised-rest-handoff',result,timeline,raw)
        assert result.returncode==0,result.stdout+result.stderr
        assert raw.bytes('rest/responses/posts-1.body')==expected
        response=next(x for x in raw.rest_index['responses'] if x['collection']=='posts')
        assert response['body_complete'] and response['sha256']==hashlib.sha256(expected).hexdigest()
        collection=next(x for x in raw.rest_index['collections'] if x['type']=='posts')
        assert collection['status']=='complete' and collection['fetched_objects']==100
        assert not (tmp_path/'output/Fix/packs').exists()
