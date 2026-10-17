"""Short REST pages and closed-target cleanup: offline and native loopback proof."""
import asyncio
import hashlib
import json
from types import SimpleNamespace

import pytest
from fixture_server import fixture_server, wp_inputs, ENTITY
from smart_crawler.crawler import RunFolder, utc_now
from smart_crawler.rest_client import collect_rest
from smart_crawler.browser_session import BrowserSession, Bounds
from test_rest_client import Browser, ORIGIN
from test_resolution_stop import setup_resolution, retain as retain_resolution
from test_browser_controls import retain


def media_case(tmp_path, variant):
    inputs=wp_inputs(ORIGIN); endpoint=ORIGIN+'/wp-json/wp/v2/media?per_page=100&page='
    pages=[[{'id':i} for i in range(1,101)], [{'id':i} for i in range(101,197)], [{'id':i} for i in range(197,201)]]
    total=200
    if variant=='mismatch':total=204
    if variant=='duplicate':pages[2][-1]['id']=1
    if variant=='empty':pages[1]=[]
    for n,values in enumerate(pages,1):
        response={'status':200,'body':json.dumps(values,ensure_ascii=False).encode(),'headers':{'x-wp-total':str(total),'x-wp-totalpages':'3'},'incomplete':False}
        if n==2:
            if variant=='missing_totals':response['headers'].pop('x-wp-totalpages')
            if variant=='changed_totals':response['headers']['x-wp-total']='201'
            if variant=='malformed':response['body']=b'{}'
            if variant=='partial':response.update(body=b'[{',incomplete=True,error='response_limit')
            if variant=='refusal':response.update(status=429,body=b'refused')
        inputs[endpoint+str(n)]=response
    run=RunFolder('Fix',utc_now(),root=tmp_path).create();browser=Browser(inputs)
    if variant=='budget':
        original=browser.read
        async def bounded(url):
            if url==endpoint+'3':
                from smart_crawler.browser_session import CollectionStopped
                browser.stop('operation_limit');raise CollectionStopped('operation_limit')
            return await original(url)
        browser.read=bounded
    objects,absences=asyncio.run(collect_rest(browser,ORIGIN,run))
    return run,browser,objects,absences,endpoint


@pytest.mark.parametrize('variant',['complete','mismatch','duplicate'])
def test_short_intermediate_continues_and_counts_remain_honest(tmp_path,variant):
    run,browser,objects,absences,endpoint=media_case(tmp_path,variant)
    c=next(c for c in run.rest_index['collections'] if c['type']=='media')
    assert [u for u in browser.calls if '/media?' in u]==[endpoint+str(n) for n in (1,2,3)]
    assert c['status']==('complete' if variant=='complete' else 'partial')
    assert c['fetched_objects']==200
    assert c['total']==(204 if variant=='mismatch' else 200)
    row=next(x for x in run.rest_index['responses'] if x['collection']=='media' and x['page']==2)
    assert row['pagination_anomalies']==['short_intermediate_page']
    if variant!='complete':assert any(a['reason']==('duplicate_object_id' if variant=='duplicate' else 'pagination_count_mismatch') for a in absences)
    for row in run.rest_index['responses']:
        body=(run.dir/'rest'/row['file']).read_bytes()
        assert body==browser.inputs[row['url']]['body']
        assert hashlib.sha256(body).hexdigest()==row['sha256']
    if variant=='duplicate':assert 'objects/media-1-2.json' in objects


@pytest.mark.parametrize('variant,reason',[
    ('empty','empty_intermediate_page'),('missing_totals','pagination_totals_unknown'),
    ('changed_totals','pagination_totals_changed'),('malformed','malformed_response'),
    ('partial','response_limit'),('refusal','http_429'),('budget','stop_rule')])
def test_pagination_gaps_and_stops_do_not_become_complete(tmp_path,variant,reason):
    run,browser,_,absences,endpoint=media_case(tmp_path,variant)
    c=next(c for c in run.rest_index['collections'] if c['type']=='media')
    assert c['status']=='partial'
    assert endpoint+'3' not in browser.calls
    assert any(a['reason']==reason for a in absences)
    if variant in ('refusal','budget'):
        assert browser.stop_reason
        assert not any('/categories?' in u for u in browser.calls)


@pytest.mark.parametrize('variant',['eligible','prior-stop','not-closing','active','intentional','unresolved','open-target','other-error','continue'])
def test_cleanup_exception_is_narrow_and_never_resolves_twice(tmp_path,variant):
    async def exercise():
        TargetClosedError=type('TargetClosedError',(Exception,),{}) # Explicit double, not native evidence.
        error=TargetClosedError('Target page, context or browser has been closed') if variant!='other-error' else RuntimeError('different protocol fault')
        s,cdp,entry=setup_resolution(error=error)
        s.closing=variant!='not-closing';s.op=None if variant!='active' else s.op
        entry.operation=None;entry.classification='incidental'
        if variant in ('intentional','unresolved'):entry.classification=variant
        s.page=SimpleNamespace(is_closed=lambda:variant!='open-target')
        if variant=='prior-stop':s.stop('original_refusal')
        # continue branch is tested with no closing guard, so its error cannot qualify.
        if variant=='continue':s.closing=False
        command='Fetch.continueRequest' if variant=='continue' else 'Fetch.failRequest'
        returned=[await s.resolve_interception(entry,command),await s.resolve_interception(entry,'Fetch.failRequest')]
        retain_resolution(tmp_path,'closed-cleanup-'+variant,s,cdp,entry,returned)
        assert len(cdp.calls)==1 and cdp.calls[0]['command']==command
        assert returned==[False,False]
        if variant in ('eligible','prior-stop'):
            assert entry.state=='closed'
            assert s.stop_reason==('original_refusal' if variant=='prior-stop' else None)
            assert any(e['event']=='interception_cleanup_closed' for e in s.events)
        else:
            assert entry.state=='error' and s.stop_reason=='interception_error:'+type(error).__name__
    asyncio.run(exercise())


def test_native_closed_target_incidental_abort_preserves_success(tmp_path):
    class HeldCleanup(BrowserSession):
        async def paused(self,params):
            if params['request']['url'].endswith('/cleanup-held'):
                self.held_params=params;self.held.set();await self.release.wait()
            await super().paused(params)
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=HeldCleanup(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.held,s.release=asyncio.Event(),asyncio.Event()
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    assert (await s.read(origin+'/data'))['body']==ENTITY
                    await s.page.evaluate("() => { fetch('/cleanup-held').catch(()=>null); }")
                    await asyncio.wait_for(s.held.wait(),5)
                    assert s.op is None
                    s.closing=True # Exercise normal-cleanup state with deterministic native closure ordering.
                    await s.page.close()
                    assert s.page.is_closed()
                    s.release.set();await asyncio.gather(*list(s.tasks))
                    assert s.stop_reason is None
                    entry=s.interceptions[s.held_params['requestId']]
                    assert entry.state=='closed'
                    assert not await s.resolve_interception(entry,'Fetch.failRequest')
                    errors=[e for e in s.events if e['event']=='interception_command_error' and e['request_id']==s.held_params['requestId']]
                    assert len(errors)==1 and errors[0]['error']=='TargetClosedError'
                    # CDP detach during page.close may release incidental HTTP
                    # independently; retain the server trace without claiming zero
                    # resource traffic. The controller never continues/reissues it.
                    assert sum(e['event']=='request_received' and e['path']=='/cleanup-held' for e in timeline)<=1
                    commands=[e for e in s.events if e['event']=='interception_command' and e['request_id']==s.held_params['requestId']]
                    assert [e['command'] for e in commands]==['Fetch.continueRequest','Fetch.failRequest']
                    assert any(e['event']=='interception_continuation_prevented' and e['request_id']==s.held_params['requestId'] for e in s.events)
                    assert not any(e['event']=='interception_command_complete' and e['request_id']==s.held_params['requestId'] for e in s.events)
                    assert s.dispatches==2
                assert s.stop_reason is None
            finally:
                s.release.set();retain(tmp_path,'native-closed-cleanup',s,timeline)
        asyncio.run(exercise())


def test_native_unexpected_closure_during_read_remains_failure(tmp_path):
    class HeldRead(BrowserSession):
        async def paused(self,params):
            if params['request']['url'].endswith('/cleanup-held'):
                self.held.set();await self.release.wait()
            await super().paused(params)
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=HeldRead(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.held,s.release=asyncio.Event(),asyncio.Event()
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    task=asyncio.create_task(s.read(origin+'/cleanup-held'))
                    await asyncio.wait_for(s.held.wait(),5)
                    assert s.op is not None and not s.closing
                    await s.page.close()
                    s.release.set()
                    result=await asyncio.wait_for(task,10)
                    await asyncio.gather(*list(s.tasks))
                    assert result['incomplete'] and result['error']
                    assert s.stop_reason=='browser_page_closed'
                    assert not any(e['event']=='interception_cleanup_closed' for e in s.events)
                    stop=next(e for e in s.events if e['event']=='stop')
                    assert not any(e['event']=='intentional_dispatch' and e['monotonic']>=stop['monotonic'] for e in s.events)
                assert s.stop_reason=='browser_page_closed'
            finally:
                s.release.set();retain(tmp_path,'native-unexpected-close-active-read',s,timeline)
        asyncio.run(exercise())
