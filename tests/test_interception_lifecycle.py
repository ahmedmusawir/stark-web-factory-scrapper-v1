"""Native loopback cancellation and scoped interception lifecycle controls."""
import asyncio

from smart_crawler.browser_session import BrowserSession, Bounds
from fixture_server import fixture_server, ENTITY
from test_browser_controls import retain


class NativeCancellation(BrowserSession):
    """Hold a real paused request until Chromium reports AbortController cancellation.

    Only scheduling is controlled: no injected CDP error or fabricated native event.
    """
    async def paused(self, params):
        if params['request']['url'].endswith('/cancel-fixture'):
            self.fixture_paused = params
            self.fixture_held.set()
            await self.fixture_release.wait()
        await super().paused(params)

    def network_failed(self, params):
        super().network_failed(params)
        if params['requestId'] == getattr(self, 'fixture_paused', {}).get('networkId'):
            self.fixture_failure = params
            self.event('fixture_native_cancellation', request_id=self.fixture_paused['requestId'],
                       network_id=params['requestId'], frame_id=self.fixture_paused.get('frameId'),
                       canceled=params.get('canceled'), error_text=params.get('errorText'))
            self.fixture_canceled.set()


def test_native_canceled_incidental_preserves_document_and_read(tmp_path):
    with fixture_server() as (origin, timeline):
        async def exercise():
            session = NativeCancellation(origin, bounds=Bounds(seconds=60, finalization_reserve=5),
                                         runtime_dir=tmp_path/'runtime', loopback_only=True)
            session.fixture_held = asyncio.Event()
            session.fixture_release = asyncio.Event()
            session.fixture_canceled = asyncio.Event()
            try:
                async with session:
                    document = await session.capture(origin+'/background')
                    assert document['ok'] and not session.stop_reason
                    response = await session.read(origin+'/data')
                    assert response['body'] == ENTITY and not response['incomplete']
                    await session.page.evaluate("""() => {
                        window.fixtureAbort = new AbortController();
                        window.fixturePromise = fetch('/cancel-fixture', {signal:fixtureAbort.signal})
                            .catch(e => e.name);
                    }""")
                    await asyncio.wait_for(session.fixture_held.wait(), 5)
                    await session.page.evaluate('fixtureAbort.abort()')
                    await asyncio.wait_for(session.fixture_canceled.wait(), 5)
                    assert session.fixture_failure['canceled'] is True
                    session.fixture_release.set()
                    await asyncio.gather(*list(session.tasks))
                    assert session.stop_reason is None, session.stop_reason
                    result = await session.read(origin+'/data?after-cancel')
                    assert result['body'] == ENTITY and not result['incomplete']
                    assert session.dispatches == 3
                    assert not any(e['path']=='/cancel-fixture' for e in timeline)
            finally:
                session.fixture_release.set()
                retain(tmp_path, 'native-incidental-cancellation', session, timeline)
        asyncio.run(exercise())


def test_native_frame_teardown_cancellation_is_correlated(tmp_path):
    with fixture_server() as (origin, timeline):
        async def exercise():
            s = NativeCancellation(origin, bounds=Bounds(seconds=60, finalization_reserve=5),
                                   runtime_dir=tmp_path/'runtime', loopback_only=True)
            s.fixture_held, s.fixture_release, s.fixture_canceled = (asyncio.Event() for _ in range(3))
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    await s.page.evaluate("""() => {
                        window.fixtureFrame=document.createElement('iframe');
                        fixtureFrame.src='/cancel-fixture';document.body.append(fixtureFrame);
                    }""")
                    await asyncio.wait_for(s.fixture_held.wait(), 5)
                    await s.page.evaluate('fixtureFrame.remove()')
                    await asyncio.wait_for(s.fixture_canceled.wait(), 5)
                    s.fixture_release.set()
                    await asyncio.gather(*list(s.tasks))
                    assert s.stop_reason is None, s.stop_reason
                    response=await s.read(origin+'/data')
                    assert response['body']==ENTITY and not response['incomplete']
                    assert s.dispatches==2
                    assert any(e['event']=='interception_frame_detached' and
                               e['frame_id']==s.fixture_paused['frameId'] for e in s.events)
                    assert any(e['event']=='interception_incidental_canceled' for e in s.events)
            finally:
                s.fixture_release.set()
                retain(tmp_path,'native-frame-cancellation',s,timeline)
        asyncio.run(exercise())


import pytest
from dataclasses import replace


@pytest.mark.parametrize('kind',['document','GET','HEAD'])
def test_native_intentional_cancellation_never_succeeds(tmp_path,kind):
    class CanceledIntentional(NativeCancellation):
        async def correlated_read(self, expression):
            # Native AbortController; change only the fixture abort timing.
            return await super().correlated_read(expression.replace('ctl.abort(),timeout','ctl.abort(),300'))
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=CanceledIntentional(origin,bounds=Bounds(seconds=60,finalization_reserve=5),
                                  runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.fixture_held,s.fixture_release,s.fixture_canceled=(asyncio.Event() for _ in range(3))
            try:
                async with s:
                    if kind!='document':assert (await s.capture(origin+'/background'))['ok']
                    task=asyncio.create_task(s.capture(origin+'/cancel-fixture') if kind=='document'
                                             else s.read(origin+'/cancel-fixture',kind))
                    await asyncio.wait_for(s.fixture_held.wait(),5)
                    if kind=='document':await s.cdp.send('Page.stopLoading')
                    await asyncio.wait_for(s.fixture_canceled.wait(),5)
                    s.fixture_release.set()
                    result=await asyncio.wait_for(task,15)
                    await asyncio.gather(*list(s.tasks))
                    assert not result['ok'] if kind=='document' else result['incomplete']
                    assert s.stop_reason is not None
                    assert not any(e['event']=='interception_incidental_canceled' for e in s.events)
                    assert not any(e['path']=='/cancel-fixture' for e in timeline)
                    attempted=[e for e in s.events if e['event']=='interception_command' and
                               e['request_id']==s.fixture_paused['requestId']]
                    assert len(attempted)<=1 # No abort/retry after stale resolution.
            finally:
                s.fixture_release.set()
                retain(tmp_path,'native-intentional-cancel-'+kind,s,timeline)
        asyncio.run(exercise())


def test_duplicate_listener_and_late_resolution_do_not_touch_next_read(tmp_path):
    class DuplicateDelivery(BrowserSession):
        async def paused(self,params):
            # Explicit duplicate event injection, not a native Chromium duplicate.
            self.paused_event(self.cdp,params)
            await super().paused(params)
        async def run_read_script(self,op):
            old=next(e for e in self.interceptions.values() if e.classification=='intentional')
            assert old.operation is not op and old.state=='resolved'
            assert not await self.resolve_interception(old,'Fetch.failRequest')
            assert op.error is None and self.stop_reason is None
            return await super().run_read_script(op)
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=DuplicateDelivery(origin,bounds=Bounds(seconds=60,finalization_reserve=5),
                                runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    result=await s.read(origin+'/data')
                    assert result['body']==ENTITY and not result['incomplete']
                    assert s.dispatches==2 and not s.stop_reason
                    commands=[e['request_id'] for e in s.events if e['event']=='interception_command']
                    assert len(commands)==len(set(commands))
                    assert sum(e['event']=='controls_installed' for e in s.events)==1
                    assert any(e['event']=='interception_resolution_skipped' for e in s.events)
            finally:retain(tmp_path,'duplicate-event-late-resolution',s,timeline)
        asyncio.run(exercise())


def test_wrong_session_cannot_resolve_another_interception(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=BrowserSession(origin,bounds=Bounds(seconds=30,finalization_reserve=5),
                             runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with s:
                    assert (await s.capture(origin+'/article/'))['ok']
                    old=next(iter(s.interceptions.values()))
                    foreign=replace(old,owner=object(),state='pending')
                    assert not await s.resolve_interception(foreign,'Fetch.continueRequest')
                    assert s.stop_reason=='interception_session_mismatch'
                    assert old.state=='resolved' and s.dispatches==1
            finally:retain(tmp_path,'foreign-session-rejected',s,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('fault',['unexplained-invalid-id','canceled-other-error','canceled-unresolved','cleanup-primary'])
def test_injected_defensive_protocol_failures_remain_fatal(tmp_path,fault):
    class DefensiveSession(NativeCancellation):
        async def admission_kind(self,params,op):
            if fault=='canceled-unresolved' and params['request']['url'].endswith('/cancel-fixture'):
                return 'unresolved',None # Explicit observation-loss injection.
            return await super().admission_kind(params,op)
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=DefensiveSession(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                               runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.fixture_held,s.fixture_release,s.fixture_canceled=(asyncio.Event() for _ in range(3))
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    await s.page.evaluate("""() => {
                        window.fixtureAbort=new AbortController();
                        fetch('/cancel-fixture',{signal:fixtureAbort.signal}).catch(()=>null);
                    }""")
                    await asyncio.wait_for(s.fixture_held.wait(),5)
                    if fault!='unexplained-invalid-id':
                        await s.page.evaluate('fixtureAbort.abort()')
                        await asyncio.wait_for(s.fixture_canceled.wait(),5)
                    original=s.cdp.send
                    async def injected(command,args=None):
                        if command in ('Fetch.continueRequest','Fetch.failRequest') and args['requestId']==s.fixture_paused['requestId']:
                            suffix='Unexpected protocol fault.' if fault=='canceled-other-error' else 'Invalid InterceptionId.'
                            raise RuntimeError(f'CDPSession.send: Protocol error ({command}): '+suffix)
                        return await original(command,args)
                    s.cdp.send=injected
                    if fault=='cleanup-primary':s.stop('fixture_original_stop')
                    s.event('fixture_injected_protocol_error',fault=fault)
                    s.fixture_release.set()
                    await asyncio.gather(*list(s.tasks))
                    assert s.stop_reason==('fixture_original_stop' if fault=='cleanup-primary' else 'interception_error:RuntimeError')
                    assert not any(e['event']=='interception_incidental_canceled' for e in s.events)
                    errors=[e for e in s.events if e['event']=='interception_command_error']
                    assert len(errors)==1 and errors[0]['request_id']==s.fixture_paused['requestId']
                    assert errors[0]['supported_incidental'] is False
                    assert sum(e['event']=='interception_command' and e['request_id']==s.fixture_paused['requestId'] for e in s.events)==1
            finally:
                s.fixture_release.set()
                retain(tmp_path,'defensive-'+fault,s,timeline)
        asyncio.run(exercise())


def test_native_cancellation_during_capture_does_not_poison_document(tmp_path):
    class DuringCapture(NativeCancellation):
        async def after_goto(self,page,response=None,**kwargs):
            await super().after_goto(page,response,**kwargs)
            await page.evaluate("""() => {
                window.fixtureAbort=new AbortController();
                fetch('/cancel-fixture',{signal:fixtureAbort.signal}).catch(()=>null);
            }""")
            await asyncio.wait_for(self.fixture_held.wait(),5)
            await page.evaluate('fixtureAbort.abort()')
            await asyncio.wait_for(self.fixture_canceled.wait(),5)
            self.fixture_release.set()
            await asyncio.gather(*list(self.tasks))
            return page
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=DuringCapture(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                            runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.fixture_held,s.fixture_release,s.fixture_canceled=(asyncio.Event() for _ in range(3))
            try:
                async with s:
                    result=await s.capture(origin+'/background')
                    assert result['ok'] and result['status']==200
                    assert 'substantive local article' in result['html']
                    read=await s.read(origin+'/data')
                    assert read['body']==ENTITY and not read['incomplete']
                    assert s.dispatches==2 and not s.stop_reason
                    row,=[e for e in s.events if e['event']=='interception_incidental_canceled']
                    assert row['operation_id']=='op-1' and row['classification']=='incidental'
            finally:
                s.fixture_release.set()
                retain(tmp_path,'native-cancel-during-capture',s,timeline)
        asyncio.run(exercise())


def test_protocol_diagnostics_redact_and_bound_error_text():
    from smart_crawler.browser_session import protocol_detail
    raw='Protocol error https://user:private@host.invalid/path?secret=value#private '+('x'*5000)
    text=protocol_detail(raw)
    assert len(text)==2048 and 'https://host.invalid/path' in text
    assert all(token not in text for token in ('user','private','secret','value'))
    exact='CDPSession.send: Protocol error (Fetch.continueRequest): Invalid InterceptionId.'
    assert protocol_detail(exact)==exact


def test_diagnostic_limit_is_explicit_and_sticky():
    s=BrowserSession('http://127.0.0.1')
    s.diagnostic_events=20_000
    s.diagnostic('not_retained')
    assert s.stop_reason=='interception_evidence_limit'
    assert [e['event'] for e in s.events]==['stop']
    s.diagnostic('not_retained_either')
    assert len(s.events)==1


@pytest.mark.parametrize('cause',['response-cap','intentional-abort'])
def test_native_read_cancellation_before_result_handoff_preserves_failure(tmp_path,cause):
    class NativeHandoffRace(BrowserSession):
        def network_failed(self,params):
            super().network_failed(params)
            if self.op and params['requestId'] in getattr(self.op,'network_ids',{}):
                self.fixture_failure=params
                self.fixture_canceled.set()
        async def correlated_read(self,expression):
            if cause=='intentional-abort':
                expression=expression.replace('if(r.body) { const reader',
                    'setTimeout(()=>ctl.abort(),300); if(r.body) { const reader')
            return await super().correlated_read(expression)
        async def run_read_script(self,op):
            result=await super().run_read_script(op)
            # Native event only: enforce the demonstrated event-before-result
            # ordering without injecting a protocol failure/cancellation flag.
            await asyncio.wait_for(self.fixture_canceled.wait(),5)
            self.event('fixture_native_failure_before_result',network_id=self.fixture_failure['requestId'])
            return result
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=NativeHandoffRace(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                                runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.fixture_canceled=asyncio.Event()
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    if cause=='response-cap':s.bounds.response_bytes=1024
                    result=await s.read(origin+'/cancel-stream')
                    assert s.fixture_failure['canceled'] is True
                    assert result['incomplete'] is True
                    assert result['body']==(b'a'*1024 if cause=='response-cap' else b'a'*2048)
                    assert result['error']==s.stop_reason==('response_limit' if cause=='response-cap' else 'AbortError')
                    from smart_crawler.browser_session import CollectionStopped
                    with pytest.raises(CollectionStopped):await s.read(origin+'/never')
                    assert s.dispatches==2 and not any(e['path']=='/never' for e in timeline)
            finally:retain(tmp_path,'native-read-handoff-'+cause,s,timeline)
        asyncio.run(exercise())
