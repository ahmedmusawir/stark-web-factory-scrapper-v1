"""Owned missing-parent redirects: native traffic, explicit event-order/fault fixtures."""
import asyncio
import pytest
from smart_crawler.browser_session import BrowserSession, Bounds, CollectionStopped
from fixture_server import fixture_server, ENTITY
from test_browser_controls import retain


class OrderedRedirect(BrowserSession):
    ordering = 'network-later'
    fault = None

    def network_request(self, params):
        if params.get('redirectResponse'):
            self.event('fixture_native_redirect_arrival',network_id=params['requestId'],
                       previous_url=params['redirectResponse']['url'],next_url=params['request']['url'],
                       ordering=self.ordering,fault=self.fault)
            self.native_redirect_seen = True
            async def deliver():
                if self.ordering=='network-later':await asyncio.sleep(.2)
                if self.fault=='missing-transition':return
                # Faults modify observation handling only; original native facts
                # above are retained. No injected HTTP/protocol result.
                copy={**params,'request':dict(params['request']),
                      'redirectResponse':dict(params['redirectResponse'])}
                if self.fault=='wrong-previous':copy['redirectResponse']['url']+='wrong'
                if self.fault=='wrong-frame':copy['frameId']='fixture-wrong-frame'
                if self.fault=='wrong-resource':copy['type']='Image'
                if self.fault=='wrong-method':copy['request']['method']='POST'
                super(OrderedRedirect,self).network_request(copy)
            self.spawn(deliver())
        else:super().network_request(params)

    async def paused(self, params):
        if self.op and params.get('networkId') in getattr(self.op,'network_ids',{}):
            self.event('fixture_native_redirect_pause',network_id=params.get('networkId'),
                       request_id=params['requestId'],predecessor=params.get('redirectedRequestId'),
                       ordering=self.ordering)
            if self.ordering=='network-first':
                async def arrived():
                    while not getattr(self,'native_redirect_seen',False):await asyncio.sleep(.001)
                await asyncio.wait_for(arrived(),3)
                # deliver() is queued by the native event; let it complete first.
                await asyncio.sleep(.05)
        await super().paused(params)


@pytest.mark.parametrize('method',['GET','HEAD'])
@pytest.mark.parametrize('ordering',['network-later','network-first'])
def test_owned_missing_parent_allowed_redirect(tmp_path,method,ordering):
    with fixture_server() as (other,other_timeline), fixture_server(redirect_destination=other+'/boundary-data') as (origin,timeline):
        async def exercise():
            s=OrderedRedirect(origin,bounds=Bounds(seconds=60,finalization_reserve=5),
                              runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.ordering=ordering
            try:
                async with s:
                    assert (await s.capture(origin+'/article/'))['ok']
                    result=await s.read(origin+'/boundary-allowed',method)
                    assert result['status']==200 and not result['incomplete'] and result['error'] is None
                    assert result['body']==(ENTITY if method=='GET' else b'')
                    assert result['redirect_chain']==[other+'/boundary-data']
                    assert not s.stop_reason and s.dispatches==3
                    resolved,=[e for e in s.events if e['event']=='redirect_identity_resolved']
                    assert resolved['predecessor'] is None
                    assert resolved['resolved_predecessor'] and resolved['correlation_source']=='owned_network_transition_missing_fetch_parent'
                    dispatched=[e for e in s.events if e['event']=='intentional_dispatch']
                    assert dispatched[-1]['resolved_predecessor']==dispatched[-2]['request_id']
                    assert dispatched[-1]['predecessor'] is None
                    for row in dispatched[1:]:assert row['monotonic']-row['preceding_completion']>=5
                    received,=[e for e in other_timeline if e['event']=='request_received']
                    assert received['monotonic']-resolved['completed']>=5
                    assert received['method']==method and received['path']=='/boundary-data'
                    wait,=[e for e in s.events if e['event']=='redirect_identity_wait']
                    transition,=[e for e in s.events if e['event']=='cdp_request_will_be_sent' and e['redirect_from']]
                    assert (wait['monotonic']<transition['monotonic'])==(ordering=='network-later')
            finally:retain(tmp_path,'missing-parent-'+ordering+'-'+method,s,timeline+other_timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('fault',['missing-transition','wrong-previous','wrong-frame','wrong-resource','wrong-method'])
def test_owned_redirect_conflict_never_becomes_incidental(tmp_path,fault):
    with fixture_server() as (other,other_timeline), fixture_server(redirect_destination=other+'/boundary-data') as (origin,timeline):
        async def exercise():
            s=OrderedRedirect(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                              runtime_dir=tmp_path/'runtime',loopback_only=True)
            s.fault=fault
            try:
                async with s:
                    assert (await s.capture(origin+'/article/'))['ok']
                    s.bounds.read_seconds=8 # Local shortened limit; product defaults unchanged.
                    result=await s.read(origin+'/boundary-allowed')
                    assert result['incomplete'] and result['error']==s.stop_reason=='ambiguous_redirect_identity'
                    assert s.dispatches==2 and not other_timeline
                    pending,=[e for e in s.events if e['event']=='fixture_native_redirect_pause']
                    rows=[e for e in s.events if e.get('request_id')==pending['request_id']]
                    assert not any(e['event']=='request_classified' and e['classification']=='incidental' for e in rows)
                    commands=[e for e in rows if e['event']=='interception_command']
                    assert len(commands)==1 and commands[0]['command']=='Fetch.failRequest'
                    assert not any(e['event']=='intentional_dispatch' and e['url']==other+'/boundary-data' for e in s.events)
                    with pytest.raises(CollectionStopped):await s.read(origin+'/never')
                    stop=next(e for e in s.events if e['event']=='stop')
                    assert not any(e['event']=='intentional_dispatch' and e['monotonic']>stop['monotonic'] for e in s.events)
            finally:retain(tmp_path,'missing-parent-fault-'+fault,s,timeline+other_timeline)
        asyncio.run(exercise())
