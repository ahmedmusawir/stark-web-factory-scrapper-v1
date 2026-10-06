"""CHK scoped repair: actual Chromium request identity, no live targets."""
import asyncio
import pytest
from smart_crawler.browser_session import BrowserSession, Bounds
from fixture_server import fixture_server
from test_browser_controls import retain


@pytest.mark.parametrize('kind',['stylesheet','image','fetch','xhr'])
def test_same_url_document_background_is_incidental(tmp_path,kind):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                                   runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    result=await session.capture(origin+'/identity/'+kind)
                    assert result['ok'] and session.stop_reason is None, session.stop_reason
                    assert session.dispatches==1
                    requests=[e for e in session.events if e['event']=='browser_request']
                    assert any(e['resource_type']==kind for e in requests)
                    assert len([e for e in timeline if e['event']=='request_received'])==2
            finally:retain(tmp_path,'same-url-'+kind,session,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('method',['GET','HEAD'])
@pytest.mark.parametrize('background',['fetch','xhr'])
def test_read_cannot_be_impersonated(tmp_path,method,background):
    class RacingPage(BrowserSession):
        async def run_read_script(self,op):
            # Same URL/method/main-frame; spoofed sourceURL is NOT a scriptId.
            js='''async ([url,method,kind]) => {
              if(kind==='fetch') return (await fetch(url,{method})).status;
              return await new Promise(resolve=>{let x=new XMLHttpRequest();
                x.open(method,url); x.onload=()=>resolve(x.status);x.send();});
            }\n//# sourceURL=abm-coordinator-read'''
            assert await self.page.evaluate(js,[op.url,op.method,background])==403
            assert self.stop_reason is None
            return await super().run_read_script(op)
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=RacingPage(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                                runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    response=await session.read(origin+'/read-identity',method)
                    assert response['status']==200 and not response['incomplete'],response.get('error')
                    assert response['body']==(b'' if method=='HEAD' else b'coordinator response')
                    assert not session.stop_reason and session.dispatches==2
                    rows=[e for e in session.events if e['event']=='request_classified' and e['url']==origin+'/read-identity']
                    assert [e['classification'] for e in rows]==['incidental','intentional']
                    assert rows[0]['initiator_script_id']!=rows[1]['initiator_script_id']
                    assert rows[0]['frame_id']==rows[1]['frame_id']==session.main_frame
                    if background=='fetch':
                        assert rows[0]['resource_type']==rows[1]['resource_type']
                        assert rows[0]['network_resource_type']==rows[1]['network_resource_type']=='Fetch'
                    assert len([e for e in timeline if e['event']=='request_received'])==3
            finally:retain(tmp_path,f'read-race-{background}-{method}',session,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('fault',['duplicate','missing-initiator'])
def test_read_duplicate_and_ambiguity_stop_before_dispatch(tmp_path,fault):
    class FaultSession(BrowserSession):
        def network_request(self,p):
            super().network_request(p)
            if fault=='missing-initiator' and self.op and self.op.kind=='read':
                # Native event preserved; explicitly injected observation loss.
                self.network_requests[(p['requestId'],p['request']['url'])]['initiator_script_id']=None
                self.event('fixture_identity_fault',fault=fault,network_id=p['requestId'])
        async def correlated_read(self,expression):
            if fault=='duplicate':
                # Both actual fetches originate in the SAME compiled script.
                expression=expression.replace('const r=await window.fetch',
                    "const extra=window.fetch(url,{method,signal:ctl.signal}).catch(()=>null); const r=await window.fetch")
            return await super().correlated_read(expression)
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=FaultSession(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                                  runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    response=await session.read(origin+'/data')
                    expected='ambiguous_intentional_request' if fault=='duplicate' else 'ambiguous_request_identity'
                    assert response['incomplete'] and session.stop_reason==expected,response.get('error')
                    assert session.dispatches==1 # Only bootstrap; reads held at five-second gap.
                    assert not any(e['path']=='/data' for e in timeline)
                    assert any(e['event']==('intentional_prevented' if fault=='duplicate' else 'unresolved_prevented') for e in session.events)
            finally:retain(tmp_path,'read-fault-'+fault,session,timeline)
        asyncio.run(exercise())


def test_genuine_second_document_is_prevented(tmp_path):
    class DuplicateDocument(BrowserSession):
        async def after_goto(self,page,response=None,**kwargs):
            await super().after_goto(page,response,**kwargs)
            try:
                await page.goto(self.op.url,timeout=10000)
            except Exception:
                pass
            return page
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=DuplicateDocument(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                                       runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    result=await session.capture(origin+'/article/')
                    assert not result['ok'] and session.stop_reason=='ambiguous_intentional_request'
                    assert session.dispatches==1
                    assert len([e for e in timeline if e['event']=='request_received'])==1
                    denied=[e for e in session.events if e['event']=='intentional_prevented']
                    assert denied and denied[0]['resource_type']=='Document'
            finally:retain(tmp_path,'document-duplicate',session,timeline)
        asyncio.run(exercise())


def test_sticky_stop_names_incidental_prevention(tmp_path):
    class StopBeforeStyle(BrowserSession):
        async def paused(self,params):
            if params['resourceType']=='Stylesheet':
                self.stop('fixture_forced_stop')
            await super().paused(params)
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=StopBeforeStyle(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                                    runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    result=await session.capture(origin+'/identity/stylesheet')
                    assert not result['ok'] and session.stop_reason=='fixture_forced_stop'
                    assert session.dispatches==1
                    assert len([e for e in timeline if e['event']=='request_received'])==1
                    assert any(e['event']=='incidental_prevented' and e['resource_type']=='Stylesheet' for e in session.events)
                    assert not any(e['event']=='intentional_prevented' for e in session.events)
            finally:retain(tmp_path,'incidental-sticky-prevention',session,timeline)
        asyncio.run(exercise())
