"""Real installed Chromium boundary proofs. Only loopback HTTP is permitted."""
import asyncio
import json
import os
from pathlib import Path

import pytest

from smart_crawler.browser_session import BrowserSession, Bounds, CollectionStopped, challenge_reason
from fixture_server import fixture_server, ENTITY


def retain(tmp_path, name, session, server):
    result={'browser_events':session.events,'server_events':server,'runtime':session.runtime,
            'dispatches':session.dispatches,'stop_reason':session.stop_reason}
    (tmp_path / (name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    # Optional engineering evidence destination; no secrets/environment dump.
    evidence=os.environ.get('ABM_CONTROL_EVIDENCE')
    if evidence:
        folder=Path(evidence);folder.mkdir(parents=True,exist_ok=True)
        with (folder/(name+'.json')).open('x') as f: json.dump(result,f,indent=2)


def test_real_redirect_completion_and_fetch_fidelity(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin, bounds=Bounds(seconds=120,operations=8,finalization_reserve=5),
                                   runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    result=await session.capture(origin+'/redirect')
                    assert result['ok'], (result,session.stop_reason)
                    assert result['status']==200 and result['final_url']==origin+'/article/'
                    response=await session.read(origin+'/data')
                    assert response['body']==ENTITY and not response['incomplete']
                    assert response['status']==200 and response['transport'].startswith('Chromium same-page')
                    # Correlate actual dispatches with browser completion and independent server timeline.
                    dispatch=[e for e in session.events if e['event']=='intentional_dispatch']
                    assert len(dispatch)==3
                    for d in dispatch[1:]: assert d['monotonic']-d['preceding_completion']>=5
                    completion=next(e for e in session.events if e['event']=='intentional_browser_completion' and e['url']==origin+'/redirect')
                    received=next(e for e in timeline if e['event']=='request_received' and e['path']=='/article/')
                    assert received['monotonic']-completion.get('completed',completion['monotonic'])>=5
                    from discover_site.sitemap_utils import USER_AGENT
                    assert all(e['user_agent'] == USER_AGENT for e in timeline if e['event'] == 'request_received')
                    assert not session.stop_reason
            finally: retain(tmp_path,'redirect-and-fidelity',session,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('status,headers,html,expected',[
    (200,{'cf-mitigated':'challenge'},'<p>wait</p>',True),
    (200,{},'<title>Access Denied</title><p>Access to this page has been denied</p>',True),
    (200,{},'<title>Access Denied</title><article>This article explains error messages, not a blocked session.</article>',False),
    (200,{},'<p></p>',False),(503,{},'<p>ordinary outage</p>',False),
    (429,{'retry-after':'42'},'',True),
])
def test_challenge_positive_and_false_positive(status,headers,html,expected):
    assert bool(challenge_reason(status,headers,html)) is expected


def test_real_background_post_incidental_failure_and_refusal(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=120,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    record=await session.capture(origin+'/background')
                    assert record['ok'] and session.stop_reason is None
                    assert any(e['path']=='/beacon' and e['method']=='POST' for e in timeline)
                    assert any(e['event']=='browser_response' and e['status']==403 for e in session.events)
                    response=await session.read(origin+'/refusal')
                    assert session.stop_reason=='http_429'
                    assert response['status']==429 and response['headers']['retry-after']=='42'
                    with pytest.raises(CollectionStopped): await session.read(origin+'/never')
                    assert not any(e['path']=='/never' for e in timeline)
                    assert session.dispatches==2
            finally: retain(tmp_path,'background-and-refusal',session,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('path,expected',[('/denied-redirect','redirect_out_of_scope'),('/loop','redirect_loop')])
def test_real_redirect_denial_before_dispatch(tmp_path,path,expected):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    record=await session.capture(origin+path)
                    assert not record['ok'] and record['error']==expected
                    assert session.dispatches==1
                    assert len([e for e in timeline if e['event']=='request_received'])==1
                    assert any(e['event']=='intentional_prevented' and e['reason']==expected for e in session.events)
            finally: retain(tmp_path,path.strip('/')+'-denial',session,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('path,reason',[('/forbidden','http_403'),('/challenge','cf_mitigated_challenge'),('/soft-challenge','explicit_block_document')])
def test_real_document_refusals_are_sticky(tmp_path,path,reason):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    record=await session.capture(origin+path)
                    assert not record['ok'] and record['error']=='blocked'
                    assert session.stop_reason==reason
                    with pytest.raises(CollectionStopped): await session.capture(origin+'/never')
                    assert session.dispatches==1
                    assert not any(e['path']=='/never' for e in timeline)
            finally: retain(tmp_path,path.strip('/')+'-sticky',session,timeline)
        asyncio.run(exercise())


def test_real_decoded_cap_preserves_partial_and_stops(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    session.bounds.response_bytes=1024
                    response=await session.read(origin+'/large')
                    assert response['incomplete'] and response['body']==b'a'*1024
                    assert session.stop_reason=='response_limit'
                    with pytest.raises(CollectionStopped): await session.read(origin+'/never')
                    assert session.dispatches==2
            finally: retain(tmp_path,'response-cap',session,timeline)
        asyncio.run(exercise())


def test_real_budget_stops_before_second_dispatch(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,operations=1,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    with pytest.raises(CollectionStopped,match='operation_limit'): await session.read(origin+'/never')
                    assert session.dispatches==1 and not any(e['path']=='/never' for e in timeline)
            finally: retain(tmp_path,'operation-cap',session,timeline)
        asyncio.run(exercise())


def test_real_fetch_redirect_and_head_share_completion_gap(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=120,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    response=await session.read(origin+'/redirect')
                    assert response['status']==200 and not response['incomplete']
                    head=await session.read(origin+'/image.png',method='HEAD')
                    assert head['status']==200 and head['body']==b'' and head['headers']['content-length']=='4096'
                    dispatch=[e for e in session.events if e['event']=='intentional_dispatch']
                    assert len(dispatch)==4
                    for d in dispatch[1:]: assert d['monotonic']-d['preceding_completion']>=5
            finally: retain(tmp_path,'fetch-redirect-head',session,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('hops,success',[(4,True),(5,False)])
def test_real_five_hop_bound(tmp_path,hops,success):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=120,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    record=await session.capture(origin+f'/chain/{hops}')
                    assert record['ok'] is success
                    assert len(record['redirect_chain'])==5 and session.dispatches==6
                    if not success: assert record['error']=='redirect_loop'
            finally: retain(tmp_path,'hop-bound-'+str(hops),session,timeline)
        asyncio.run(exercise())


def test_real_deadline_prevents_wait_and_dispatch(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=120,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    import time
                    session.bounds.seconds=time.monotonic()-session.started+6
                    response=await session.read(origin+'/never')
                    assert response['incomplete'] and session.dispatches==1
                    assert session.stop_reason=='wall_clock_limit_before_gap'
                    assert not any(e['path']=='/never' for e in timeline)
            finally: retain(tmp_path,'deadline-gap',session,timeline)
        asyncio.run(exercise())


def test_real_head_redirect_then_refusal(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=120,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    head=await session.read(origin+'/redirect',method='HEAD')
                    assert head['status']==200 and head['redirect_chain']==[origin+'/image.png']
                    response=await session.read(origin+'/refusal',method='HEAD')
                    assert response['status']==429 and session.stop_reason=='http_429'
                    with pytest.raises(CollectionStopped): await session.read(origin+'/never',method='HEAD')
                    assert session.dispatches==4
            finally: retain(tmp_path,'head-redirect-refusal',session,timeline)
        asyncio.run(exercise())


@pytest.mark.parametrize('path,expected',[('/popup-source','unexpected_top_level_page'),('/worker-source','uncontrolled_service_worker')])
def test_real_uncontrolled_context_stops_admission(tmp_path,path,expected):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    record=await session.capture(origin+path)
                    assert not record['ok'] and session.stop_reason==expected
                    with pytest.raises(CollectionStopped): await session.read(origin+'/never')
                    assert not any(e['path'] in ('/never','/popup') for e in timeline if e['event']=='request_received')
            finally: retain(tmp_path,path.strip('/')+'-control',session,timeline)
        asyncio.run(exercise())


def test_real_cors_failure_is_explicit_without_fallback(tmp_path):
    with fixture_server() as (origin,timeline), fixture_server() as (other,other_timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    response=await session.read(other+'/data')
                    assert response['incomplete'] and response['error']
                    assert session.stop_reason and session.dispatches==2
                    assert len([e for e in other_timeline if e['event']=='request_received'])==1
            finally: retain(tmp_path,'cors-failure',session,timeline+other_timeline)
        asyncio.run(exercise())


def test_real_document_deadline_stops_and_keeps_timeline(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    assert (await session.capture(origin+'/article/'))['ok']
                    # Five-second shared gap, then interrupt the delayed body.
                    # Browser startup/binary hashing must not consume this proof.
                    session.bounds.document_seconds=6
                    with pytest.raises(CollectionStopped,match='document_deadline'): await session.capture(origin+'/slow')
                    with pytest.raises(CollectionStopped): await session.read(origin+'/never')
                    assert session.dispatches==2
                    assert any(e['event']=='headers_sent' and e['path']=='/slow' for e in timeline)
                    assert not any(e['event']=='request_received' and e['path']=='/never' for e in timeline)
            finally: retain(tmp_path,'document-deadline',session,timeline)
        asyncio.run(exercise())


def test_fixture_egress_guard_separates_incidental_resources(tmp_path):
    with fixture_server() as (origin,timeline):
        async def exercise():
            session=BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=tmp_path/'runtime',loopback_only=True)
            try:
                async with session:
                    record=await session.capture(origin+'/offscope-resource')
                    assert record['ok'] and session.stop_reason is None and session.dispatches==1
                    assert any((e['event']=='incidental_prevented' and e['reason']=='fixture_egress') or e['event']=='external_test_request_prevented' for e in session.events)
            finally:retain(tmp_path,'fixture-egress',session,timeline)
        asyncio.run(exercise())
