"""Local proof: observe bytes already consumed by the JS reader before handoff.

Runs preserved pre-fix and current read methods against the same native fixture.
The test-only counter records chunk length, never source body/header contents.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path.cwd()
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from fixture_server import fixture_server
from smart_crawler.browser_session import BrowserSession, Bounds

HERE=Path(__file__).resolve().parent
prior=HERE/'before/smart_crawler/browser_session.py'
spec=importlib.util.spec_from_file_location('preserved_browser_session',prior)
before=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=before
spec.loader.exec_module(before)


async def exercise(base,label,origin,server):
    class ObservedChunks(base):
        async def correlated_read(self,expression):
            marker='count+=Math.min(value.length,room);'
            assert marker in expression
            expression=expression.replace(marker,marker+' globalThis.fixtureByteCount=count;')
            self.event('fixture_setup_delay',seconds=0.6)
            await asyncio.sleep(.6)
            return await super().correlated_read(expression)
        async def run_read_script(self,op):
            self.fixture_context=op.context_id
            return await super().run_read_script(op)
    events=[]
    s=ObservedChunks(origin,bounds=Bounds(seconds=60,read_seconds=8,finalization_reserve=5),
                     log=events.append,runtime_dir=HERE/('chunk-proof-runtime-'+label),loopback_only=True)
    async with s:
        assert (await s.capture(origin+'/background'))['ok']
        response=await s.read(origin+'/deadline-stream')
        observed=await s.cdp.send('Runtime.evaluate',{'expression':'globalThis.fixtureByteCount',
            'contextId':s.fixture_context,'returnByValue':True})
        native_count=observed['result'].get('value')
        data={'label':label,'browser_js_consumed_bytes':native_count,
              'returned_bytes':len(response['body']),'incomplete':response['incomplete'],
              'error':response.get('error'),'events':events,'server':server,
              'method':'Actual old/current read method; test-only JS byte counter and0.6s setup latency; real Chromium/loopback; no HTTP substitution'}
    (HERE/('chunk-proof-'+label+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    assert native_count==2048
    assert response['incomplete'] and response['error']=='read_deadline'
    assert len(response['body'])==(0 if label=='before' else 2048)
    print(json.dumps({k:v for k,v in data.items() if k not in ('events','server')}))


for cls,label in [(before.BrowserSession,'before'),(BrowserSession,'after')]:
    with fixture_server() as (origin,timeline):
        asyncio.run(exercise(cls,label,origin,timeline))
print('PASS: browser-owned partial bytes lost before repair, preserved after; old controller SHA256 '+hashlib.sha256(prior.read_bytes()).hexdigest())
