"""Native planned-shutdown proofs; doubles are explicitly defensive checks."""
import asyncio
import json
import time
from types import SimpleNamespace

import pytest
from fixture_server import fixture_server, ENTITY
from smart_crawler.browser_session import BrowserSession, Bounds, CollectionStopped
from test_browser_controls import retain
from test_resolution_stop import setup_resolution


class ShutdownProof(BrowserSession):
    async def created(self, page, context, **kwargs):
        if self.page is page:
            return await super().created(page, context, **kwargs)
        close = page.close
        async def observed_close(*args, **kw):
            self.event('fixture_close_invoked', closing=self.closing, stop_reason=self.stop_reason)
            result = await close(*args, **kw)
            self.event('fixture_close_returned', closed=page.is_closed())
            return result
        page.close = observed_close
        result = await super().created(page, context, **kwargs)
        send = self.cdp.send
        async def observed_send(command, params=None):
            relevant = command in ('Fetch.continueRequest','Fetch.failRequest')
            if relevant:
                self.event('fixture_python_cdp_attempt', command=command,
                           request_id=params['requestId'], owner_guid=self.cdp._impl_obj._guid)
            gate = (command == 'Fetch.failRequest' and params['requestId'] ==
                    getattr(self, 'fixture_params', {}).get('requestId'))
            if gate and getattr(self, 'fixture_before_reply', False):
                self.fixture_send_held.set()
                await self.fixture_send_release.wait()
            try:
                answer = await send(command, params)
            except Exception as exc:
                if relevant: self.event('fixture_python_cdp_error', command=command,
                                        request_id=params['requestId'], error=type(exc).__name__)
                raise
            if relevant:
                self.event('fixture_python_cdp_reply', command=command,
                           request_id=params['requestId'], owner_guid=self.cdp._impl_obj._guid)
            if gate and getattr(self, 'fixture_after_reply', False):
                self.fixture_send_held.set()
                await self.fixture_send_release.wait()
            return answer
        self.cdp.send = observed_send
        return result

    def paused_event(self, owner, params):
        self.event('fixture_native_pause', request_id=params['requestId'],
                   network_id=params.get('networkId'), frame_id=params.get('frameId'),
                   resource_type=params['resourceType'], predecessor=params.get('redirectedRequestId'),
                   url=params['request']['url'], owner_guid=owner._impl_obj._guid)
        super().paused_event(owner, params)
        self.event('fixture_registered', request_id=params['requestId'],
                   state=self.interceptions[params['requestId']].state)
        if params['request']['url'].endswith('/shutdown-late'):
            self.fixture_late.set()

    async def paused(self, params):
        if params['request']['url'].endswith('/cleanup-held'):
            self.fixture_params = params
            if getattr(self, 'fixture_barrier', False):
                self.event('fixture_preclassification_hold', request_id=params['requestId'])
                self.fixture_held.set()
                await self.fixture_release.wait()
        await super().paused(params)

    def event(self, name, **values):
        super().event(name, **values)
        if name == 'pause' and self.op and self.op.url.endswith('/cleanup-held'):
            self.event('fixture_product_pacing_hold', operation_id=self.op.operation_id)
            self.fixture_held.set()


def proof_session(origin, tmp_path):
    s = ShutdownProof(origin, bounds=Bounds(operations=3, seconds=60),
                      runtime_dir=tmp_path/'runtime', loopback_only=True)
    (s.fixture_held,s.fixture_release,s.fixture_send_held,
     s.fixture_send_release,s.fixture_late) = (asyncio.Event() for _ in range(5))
    return s


def assert_confirmed_before_close(s, timeline, rid):
    replies = [e for e in s.events if e['event']=='fixture_python_cdp_reply' and e['request_id']==rid]
    assert len(replies)==1 and replies[0]['command']=='Fetch.failRequest'
    close = next(e for e in s.events if e['event']=='fixture_close_invoked')
    assert replies[0]['monotonic'] < close['monotonic']
    attempts = [e['command'] for e in s.events if e['event']=='fixture_python_cdp_attempt' and e['request_id']==rid]
    assert attempts==['Fetch.failRequest']
    entry=s.interceptions[rid]
    assert entry.state=='resolved' and entry.abort_confirmed is True
    assert not any(e['event']=='request_received' and e['path']=='/cleanup-held' for e in timeline)
    assert not s.shutdown_result['unconfirmed']
    assert s.shutdown_result['finished']<=s.shutdown_result['deadline']


@pytest.mark.parametrize('case',['normal-barrier','stop-barrier','normal-pacing','stop-pacing','write-failure-pacing'])
def test_native_planned_shutdown_aborts_held_intentional_before_close(tmp_path, case):
    with fixture_server() as (origin, timeline):
        async def exercise():
            s=proof_session(origin,tmp_path);s.fixture_barrier=case.endswith('barrier')
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    task=asyncio.create_task(s.read(origin+'/cleanup-held'))
                    await asyncio.wait_for(s.fixture_held.wait(),5)
                    assert not any(e['path']=='/cleanup-held' for e in timeline)
                    if case.startswith('stop'):s.stop('fixture_original_refusal')
                    if case=='write-failure-pacing':
                        def fail_once(row):
                            if row['event']=='fixture_evidence_write_failure':raise OSError('fixture sink unavailable')
                        s.log=fail_once;s.event('fixture_evidence_write_failure')
                        assert s.closing and s.stop_reason=='evidence_write_limit'
                    cleanup=await s.shutdown()
                    result=await asyncio.wait_for(task,5)
                    assert result['incomplete'] and result['error']
                    assert s.stop_reason==('fixture_original_refusal' if case.startswith('stop') else
                                           'evidence_write_limit' if case=='write-failure-pacing' else 'collector_shutdown')
                    assert cleanup['confirmed_aborts']>=1
                    assert s.dispatches==1
                    rid=s.fixture_params['requestId'];assert_confirmed_before_close(s,timeline,rid)
                    old=s.shutdown_task
                    assert await s.shutdown()==s.shutdown_result and s.shutdown_task is old
                    with pytest.raises(CollectionStopped):await s.read(origin+'/never')
                await asyncio.sleep(.1)
                assert not any(e['path'] in ('/cleanup-held','/never') for e in timeline)
            finally:
                s.fixture_release.set();retain(tmp_path,'planned-'+case,s,timeline)
        asyncio.run(exercise())


def test_native_shutdown_handles_new_pause_during_abort(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=proof_session(origin,tmp_path);s.fixture_barrier=s.fixture_before_reply=True
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    task=asyncio.create_task(s.read(origin+'/cleanup-held'))
                    await asyncio.wait_for(s.fixture_held.wait(),5)
                    cleanup=asyncio.create_task(s.shutdown())
                    await asyncio.wait_for(s.fixture_send_held.wait(),5)
                    await s.page.evaluate("() => {fetch('/shutdown-late').catch(()=>null);}")
                    await asyncio.wait_for(s.fixture_late.wait(),5)
                    s.fixture_send_release.set()
                    drained=await asyncio.wait_for(cleanup,5)
                    assert (await task)['incomplete']
                    assert drained['confirmed_aborts']==2 and not drained['unconfirmed']
                    assert_confirmed_before_close(s,timeline,s.fixture_params['requestId'])
                    late=next(e for e in s.interceptions.values() if e.classification=='shutdown_unclassified')
                    assert late.abort_confirmed
                    assert_confirmed_before_close(s,timeline,late.details['request_id'])
                    assert not any(e['path']=='/shutdown-late' for e in timeline)
                    assert s.dispatches==1
            finally:
                s.fixture_send_release.set();s.fixture_release.set();retain(tmp_path,'planned-new-pause',s,timeline)
        asyncio.run(exercise())


def test_native_shutdown_awaits_already_resolving_abort_once(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=proof_session(origin,tmp_path);s.fixture_barrier=s.fixture_after_reply=True
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    task=asyncio.create_task(s.read(origin+'/cleanup-held'))
                    await asyncio.wait_for(s.fixture_held.wait(),5)
                    entry=s.interceptions[s.fixture_params['requestId']]
                    resolver=s.spawn(s.resolve_interception(entry,'Fetch.failRequest'))
                    await asyncio.wait_for(s.fixture_send_held.wait(),5)
                    assert entry.state=='resolving'
                    cleanup=asyncio.create_task(s.shutdown())
                    await asyncio.sleep(.05)
                    assert not s.page.is_closed() and not cleanup.done()
                    s.fixture_send_release.set()
                    assert await resolver
                    await cleanup
                    assert (await task)['incomplete']
                    assert_confirmed_before_close(s,timeline,entry.details['request_id'])
            finally:
                s.fixture_send_release.set();s.fixture_release.set();retain(tmp_path,'planned-resolving-abort',s,timeline)
        asyncio.run(exercise())


def test_native_successful_read_and_pacing_remain_intact(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=proof_session(origin,tmp_path)
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    result=await s.read(origin+'/data')
                    assert result['body']==ENTITY and not result['incomplete']
                    dispatch=[e for e in s.events if e['event']=='intentional_dispatch']
                    assert len(dispatch)==2 and dispatch[1]['monotonic']-dispatch[1]['preceding_completion']>=5
                assert s.stop_reason is None and not s.shutdown_result['unconfirmed']
            finally:retain(tmp_path,'planned-normal-success',s,timeline)
        asyncio.run(exercise())


def test_native_external_close_still_fails_without_cancellation_claim(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=proof_session(origin,tmp_path);s.fixture_barrier=True
            try:
                async with s:
                    assert (await s.capture(origin+'/background'))['ok']
                    task=asyncio.create_task(s.read(origin+'/cleanup-held'))
                    await asyncio.wait_for(s.fixture_held.wait(),5)
                    await s.page.close() # External to the repaired shutdown, deliberate negative control.
                    s.fixture_release.set()
                    result=await asyncio.wait_for(task,5)
                    assert result['incomplete'] and result['error']=='browser_page_closed'
                assert s.stop_reason=='browser_page_closed'
                entry=s.interceptions[s.fixture_params['requestId']]
                assert not entry.abort_confirmed
                assert s.shutdown_result['unconfirmed']
                assert not any(e['event']=='fixture_python_cdp_reply' and e['request_id']==entry.details['request_id'] for e in s.events)
            finally:s.fixture_release.set();retain(tmp_path,'planned-external-close-negative',s,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('fault',['abort-error','hung-abort','already-continuing'])
def test_shutdown_doubles_preserve_unconfirmed_and_bound_cleanup(tmp_path,fault):
    async def exercise():
        s,cdp,entry=setup_resolution();s.bounds=Bounds(seconds=2,finalization_reserve=.2)
        s.stop('fixture_original_stop');order=[]
        class Crawler:
            async def __aexit__(self,*exc):order.append('planned-close')
        s.crawler=Crawler()
        if fault=='abort-error':cdp.error=RuntimeError('fixture abort reply unavailable')
        if fault=='hung-abort':
            original=cdp.send
            async def hung(command,args):
                await original(command,args);order.append('abort-attempt');await asyncio.Event().wait()
            cdp.send=hung
        if fault=='already-continuing':
            entry.state='resolving';entry.command='Fetch.continueRequest'
            async def settle():
                await asyncio.sleep(.025);entry.state='resolved';s.shutdown_changed.set()
            s.spawn(settle())
        t=time.monotonic();result=await s.shutdown()
        assert time.monotonic()-t<.5 and result['unconfirmed']
        assert entry.abort_confirmed is False and s.stop_reason=='fixture_original_stop'
        assert order[-1]=='planned-close'
        assert len(cdp.calls)==(0 if fault=='already-continuing' else 1)
        assert await s.shutdown()==result
        retain(tmp_path,'planned-double-'+fault,s,[])
    asyncio.run(exercise())


@pytest.mark.parametrize('shift',[0,10000])
def test_complete_fixture_shutdown_clock_shift_is_checked(shift):
    from snapshot_compare import validate_complete_shutdown
    rows=shutdown_snapshot_rows(shift)
    validate_complete_shutdown(rows,{'finalization_reserve':30})


def shutdown_snapshot_rows(shift=0):
    return [
        {'event':'shutdown_start','monotonic':100+shift,'deadline':130+shift,'drain_deadline':129+shift},
        {'event':'shutdown_drain','monotonic':101+shift,'confirmed_aborts':0,'unconfirmed_count':0,'unconfirmed_sample':[]},
        {'event':'shutdown_planned_close','monotonic':101.1+shift,'deadline':130+shift},
        {'event':'shutdown_complete','monotonic':101.2+shift,'deadline':130+shift,'finished':101.19+shift,
         'confirmed_aborts':0,'unconfirmed_count':0,'unconfirmed_sample':[],'stop_reason':None}]


@pytest.mark.parametrize('fault',['reserve','drain-deadline','late-finish','finish-observation',
                                  'unconfirmed','abort-count','early-close','duplicate-start'])
def test_shutdown_timing_projection_cannot_hide_invalid_facts(fault):
    from snapshot_compare import validate_complete_shutdown
    rows=shutdown_snapshot_rows()
    if fault=='reserve':rows[0]['deadline']=131
    elif fault=='drain-deadline':rows[0]['drain_deadline']=131
    elif fault=='late-finish':rows[3]['finished']=131
    elif fault=='finish-observation':rows[3]['finished']=102
    elif fault=='unconfirmed':rows[3]['unconfirmed_count']=1
    elif fault=='abort-count':rows[3]['confirmed_aborts']=1
    elif fault=='early-close':rows[2]['monotonic']=100.5
    elif fault=='duplicate-start':rows.append(dict(rows[0]))
    with pytest.raises(AssertionError):validate_complete_shutdown(rows,{'finalization_reserve':30})
