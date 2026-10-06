"""Narrow custom CDP boundary; native loopback browser/server evidence only."""
import asyncio
import hashlib

import pytest

from smart_crawler.browser_session import BrowserSession, Bounds
from fixture_server import fixture_server, ENTITY
from test_browser_controls import retain


CONTROLLED = {'Document', 'Fetch', 'XHR'}


def assert_no_excluded_pauses(session):
    # Entries are registered only by our owned Fetch.requestPaused listener.
    assert session.interceptions
    assert {e.details['resource_type'] for e in session.interceptions.values()} <= CONTROLLED
    assert all(e['resource_type'] in CONTROLLED for e in session.events
               if e['event'] in ('request_classified', 'interception_command',
                                  'interception_command_error'))


def test_excluded_resources_load_without_custom_pauses(tmp_path):
    with fixture_server() as (origin, timeline):
        async def exercise():
            s=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),
                             runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with s:
                    result=await s.capture(origin+'/boundary')
                    assert result['ok'] and not s.stop_reason
                    # Assert actual script execution, stylesheet application and image decode.
                    assert await s.page.evaluate("""() => [window.boundaryScript,
                        getComputedStyle(document.body).color,
                        document.querySelector('#boundary-image').naturalWidth]""")==[True,'rgb(12, 34, 56)',20]
                    for path,kind in [('/boundary.css','Stylesheet'),('/boundary.js','Script'),('/boundary.png','Image')]:
                        assert any(e['event']=='body_sent' and e['path']==path for e in timeline)
                        assert any(e['event']=='browser_response' and e['url']==origin+path and e['status']==200 for e in s.events)
                        assert any(e['event']=='cdp_request_will_be_sent' and e['url']==origin+path and e['resource_type']==kind for e in s.events)
                    assert_no_excluded_pauses(s)
                    response=await s.read(origin+'/data')
                    assert response['body']==ENTITY and hashlib.sha256(response['body']).digest()==hashlib.sha256(ENTITY).digest()
                    assert not response['incomplete'] and s.dispatches==2 and not s.stop_reason
                    row,=[e for e in s.events if e['event']=='request_classified' and e['url']==origin+'/data']
                    # Installed Chromium's two native domains disagree in this precise way.
                    assert row['classification']=='intentional'
                    assert (row['resource_type'],row['network_resource_type'])==('XHR','Fetch')
                    assert_no_excluded_pauses(s)
            finally:retain(tmp_path,'narrow-boundary-loads',s,timeline)
        asyncio.run(exercise())


def test_image_navigation_cancellation_stays_outside_custom_resolution(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=BrowserSession(origin,bounds=Bounds(seconds=75,finalization_reserve=5),
                             runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with s:
                    assert (await s.capture(origin+'/boundary'))['ok']
                    await s.page.evaluate("""() => {
                        for(let i=0;i<2;i++) {let image=new Image();
                            image.src='/boundary-cancel.png?i='+i;document.body.append(image);}
                    }""")
                    async def both_started():
                        while len([e for e in timeline if e['event']=='body_prefix_sent' and
                                   e['path'].startswith('/boundary-cancel.png')])<2:
                            await asyncio.sleep(.01)
                    await asyncio.wait_for(both_started(),5)
                    assert (await s.capture(origin+'/article/'))['ok']
                    ids={e['network_id'] for e in s.events if e['event']=='cdp_request_will_be_sent' and
                         '/boundary-cancel.png' in e['url']}
                    assert len(ids)==2
                    canceled={e['request_id'] for e in s.events if e['event']=='cdp_loading_failed' and e['canceled']}
                    assert ids <= canceled
                    assert not any(e.details['network_id'] in ids for e in s.interceptions.values())
                    assert not any(e['event']=='interception_command_error' for e in s.events)
                    assert_no_excluded_pauses(s)
                    read=await s.read(origin+'/data')
                    assert read['body']==ENTITY and not read['incomplete']
                    assert not s.stop_reason and s.dispatches==3
                    for d in [e for e in s.events if e['event']=='intentional_dispatch'][1:]:
                        assert d['monotonic']-d['preceding_completion']>=5
            finally:retain(tmp_path,'narrow-image-navigation-churn',s,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('method',['GET','HEAD'])
def test_narrow_read_redirect_scope_prevents_target_dispatch(tmp_path,method):
    with fixture_server() as (origin,timeline):
        async def exercise():
            s=BrowserSession(origin,bounds=Bounds(seconds=45,finalization_reserve=5),
                             runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with s:
                    assert (await s.capture(origin+'/boundary'))['ok']
                    result=await s.read(origin+'/boundary-denied',method)
                    assert result['incomplete'] and result['error']=='redirect_out_of_scope'
                    denied=[e for e in s.events if e['event']=='intentional_prevented' and e['reason']=='redirect_out_of_scope']
                    assert len(denied)==1 and denied[0]['resource_type'] in ('Fetch','XHR')
                    assert denied[0]['resolved_predecessor'] is not None
                    assert denied[0]['predecessor'] is None  # Native omission remains untouched.
                    assert denied[0]['correlation_source']=='owned_network_transition_missing_fetch_parent'
                    assert not any(e['event'] in ('incidental_prevented','external_test_request_prevented')
                                   and '/never-boundary' in e.get('url','') for e in s.events)
                    assert s.dispatches==2 and not any(e['path']=='/never-boundary' for e in timeline)
                    assert_no_excluded_pauses(s)
            finally:retain(tmp_path,'narrow-scope-'+method,s,timeline)
        asyncio.run(exercise())
