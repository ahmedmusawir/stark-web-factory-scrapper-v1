"""DECIDE engineering verification; only native fixture uses sockets, on loopback."""
import asyncio
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
from urllib.parse import urlsplit,parse_qs

import pytest
from recon_pipeline import decide as d
from recon_pipeline import collector as c
from test_selected_collector import Fake,response,ARTICLE,rest,execute

BASE='http://127.0.0.1:9888'
TYPES={'page':{'name':'Pages','rest_base':'pages','rest_namespace':'wp/v2'},
       'post':{'name':'Posts','rest_base':'posts','rest_namespace':'wp/v2'},
       'book':{'name':'Books','rest_base':'books','rest_namespace':'wp/v2'},
       'attachment':{'name':'Media','rest_base':'media','rest_namespace':'wp/v2'}}


def json_response(value,total=None,pages=1):
    headers={'content-type':'application/json'}
    if total is not None:headers.update({'x-wp-total':str(total),'x-wp-totalpages':str(pages)})
    return response(json.dumps(value,ensure_ascii=False).encode(),**headers)


def obj(n,base=BASE):return {'id':n,'link':base+'/article-'+str(n),'title':{'rendered':'Article '+str(n)},'type':'post','date':'2026-10-07T00:00:00'}


def sitemap(base=BASE):
    return response(('<urlset><url><loc>'+base+'/a</loc><lastmod>2026-10-01</lastmod></url><url><loc>'+base+'/a#duplicate</loc></url><url><loc>'+base+'/b</loc></url><url><loc>https://outside.invalid/no</loc></url></urlset>').encode(),**{'content-type':'application/xml'})


def run(tmp_path,answers,**kw):
    fake=Fake(answers);root=tmp_path/'review'
    engine=d.Recon(root,BASE,transport=fake,gap=kw.pop('gap',0),**kw)
    inv=asyncio.run(engine.run());return inv,fake,root


def test_mode_is_explicit_and_incompatible_flag_rejected(tmp_path):
    with pytest.raises(SystemExit) as exc:d.main(['recon','--url',BASE,'--out',str(tmp_path/'x')])
    assert exc.value.code==2 and not (tmp_path/'x').exists()
    with pytest.raises(ValueError):d.Recon(tmp_path/'x',BASE,'default',sitemap=BASE+'/s.xml')


def test_sitemap_dedup_metadata_counts_and_custom_type(tmp_path):
    inv,fake,root=run(tmp_path,[sitemap(),json_response(TYPES),json_response([obj(1)],9,3),json_response([obj(2)],4,2),json_response([obj(3)],1)],mode='sitemap',sitemap=BASE+'/s.xml')
    assert inv['stop_reason'] is None and len(fake.calls)==5
    docs=[x for x in inv['items'] if x['kind']=='document']
    assert len([x for x in docs if x['url']==BASE+'/a'])==1
    assert not any('outside' in x['url'] for x in docs)
    cols={x['type']:x for x in inv['wordpress']['collections']}
    assert cols['page']['advertised_total']==9 and cols['page']['enumerated_unique']==1
    assert cols['page']['gaps']==['metadata_page_limit'] and cols['book']['status']=='enumerated_metadata'
    assert inv['wordpress']['excluded_types']==[{'type':'attachment','reason':'media_not_enumerated_for_review'}]
    assert all('/media' not in url for url,_ in fake.calls)
    assert all('_fields=' in url and 'content' not in parse_qs(urlsplit(url).query).get('_fields',[''])[0] for url,_ in fake.calls[1:])
    assert not (root/'checklist.json').exists() and d.read_review(root/'inventory.json')[0]==inv
    for event in inv['requests']:
        assert c.sha((root/event['body_file']).read_bytes())==event['sha256']


def test_default_page_depth_limit_no_sitemap_switch(tmp_path):
    body=b'<title>Start</title><a href="/one">One</a><a href="/one#x">Again</a><a href="https://outside.invalid/">Other</a><a href="/image.jpg">Image</a>'
    inv,fake,root=run(tmp_path,[response(body),json_response({})],mode='default',max_depth=0)
    assert len(fake.calls)==2 and not any('sitemap' in u for u,_ in fake.calls)
    assert 'discovery_depth_limit' in inv['gaps']
    assert len([x for x in inv['items'] if x['url']==BASE+'/one'])==1
    assert not any(x['url'].endswith('.jpg') for x in inv['items'])


def test_supplied_sitemap_failure_never_switches_to_default(tmp_path):
    inv,fake,_=run(tmp_path,[response(status=404),json_response({})],mode='sitemap',sitemap=BASE+'/missing.xml')
    assert inv['items']==[] and [u for u,_ in fake.calls][0].endswith('missing.xml')
    assert not any(u==BASE+'/' for u,_ in fake.calls)
    assert any('http_404' in x for x in inv['gaps'])


def test_robots_sitemap_discovery(tmp_path):
    inv,fake,_=run(tmp_path,[response(('Sitemap: '+BASE+'/s.xml').encode()),sitemap(),json_response({})],mode='sitemap')
    assert fake.calls[0][0].endswith('/robots.txt') and fake.calls[1][0].endswith('/s.xml')
    assert len([x for x in inv['items'] if x['kind']=='document'])==2


@pytest.mark.parametrize('blocked',[response(status=429),response(status=403),response(b'<title>Just a moment...</title>Verify you are human')])
def test_refusal_stops_and_preserves_partial(tmp_path,blocked):
    inv,fake,root=run(tmp_path,[sitemap(),blocked],mode='sitemap',sitemap=BASE+'/s.xml')
    assert len(fake.calls)==2 and inv['stop_reason']
    assert len(inv['items'])==2 and (root/'evidence/0002.body').exists()
    assert inv['wordpress']['status']=='skipped_or_blocked'


def test_shared_limit_and_pacing(tmp_path):
    inv,fake,_=run(tmp_path,[sitemap(),json_response(TYPES)],mode='sitemap',sitemap=BASE+'/s.xml',max_requests=2,gap=.03)
    assert len(fake.calls)==2 and inv['stop_reason']=='request_limit'
    a,b=inv['requests'];assert b['started']-a['completed']>=.03
    assert all(x['status']=='skipped' for x in inv['wordpress']['collections'])


def test_short_metadata_page_continues_to_advertised_end(tmp_path):
    inv,fake,_=run(tmp_path,[sitemap(),json_response({'post':TYPES['post']}),json_response([obj(1)],3,2),json_response([obj(2),obj(3)],3,2)],mode='sitemap',sitemap=BASE+'/s.xml',max_rest_pages=2,per_page=2)
    col=inv['wordpress']['collections'][0]
    assert col['short_pages']==[1] and col['fetched_pages']==[1,2] and col['enumerated_unique']==3
    assert col['status']=='enumerated_metadata' and len(fake.calls)==4


@pytest.mark.parametrize('records,total,gap',[([obj(1),obj(1)],2,'duplicate_ids'),([obj(1)],2,'advertised_count_mismatch')])
def test_rest_discrepancies_remain_partial(tmp_path,records,total,gap):
    inv,_,_=run(tmp_path,[sitemap(),json_response({'post':TYPES['post']}),json_response(records,total)],mode='sitemap',sitemap=BASE+'/s.xml')
    col=inv['wordpress']['collections'][0]
    assert col['status']=='partial' and gap in col['gaps']


def test_projection_ignored_stops_enumeration(tmp_path):
    value=obj(1);value['content']={'rendered':'Unexpected full content'}
    inv,fake,_=run(tmp_path,[sitemap(),json_response({'post':TYPES['post']}),json_response([value],200,2)],mode='sitemap',sitemap=BASE+'/s.xml',max_rest_pages=2)
    assert len(fake.calls)==3
    assert 'projection_not_honored_no_further_enumeration' in inv['wordpress']['collections'][0]['gaps']


def test_number_selection_export_is_single_item_and_exact_version(tmp_path):
    inv,_,root=run(tmp_path,[sitemap(),json_response({'post':TYPES['post']}),json_response([obj(11945)],1)],mode='sitemap',sitemap=BASE+'/s.xml')
    row=next(x for x in inv['items'] if x['rest_items']);ip=root/'inventory.json';dp=root/'example-decision.json';out=root/'plan.json'
    chosen=d.save_selection(ip,dp,html=[str(row['row'])],rest=[row['id']],actor='EXAMPLE_ONLY',example=True)
    assert chosen['include_html']==[row['id']] and chosen['include_rest']==[row['id']]
    plan=d.export_plan(ip,dp,out)
    assert plan=={'pages':[row['url']],'rest':[{'url':BASE+'/wp-json/wp/v2/posts/11945','paginate':False}]}
    assert c.plan_items(plan) and not (root/'checklist.json').exists()
    full=c.create(root/'fresh-full-capture',plan)
    assert all(x['status']=='pending' and x['result'] is None for x in full['items'])
    assert json.loads((root/'plan.review.json').read_text())['example_only']
    # Whitespace changes the exact saved-file binding, despite unchanged stable IDs.
    ip.write_text(ip.read_text()+'\n')
    with pytest.raises(ValueError,match='different inventory'):d.export_plan(ip,dp,root/'bad.json')
    assert not (root/'bad.json').exists()


def test_reordering_changes_version_not_stable_ids(tmp_path):
    inv,_,root=run(tmp_path,[sitemap(),json_response({})],mode='sitemap',sitemap=BASE+'/s.xml')
    before={x['url']:x['id'] for x in inv['items']}
    inv['items'].reverse()
    for i,row in enumerate(inv['items'],1):row['row']=i
    inv.pop('inventory_id');inv['inventory_id']=d.digest(inv)
    p=root/'reordered.json';d.fresh_json(p,inv)
    assert {x['url']:x['id'] for x in d.read_review(p)[0]['items']}==before
    row=inv['items'][0]
    decision=d.save_selection(p,root/'selection.json',html=['1'],actor='EXAMPLE_ONLY',example=True)
    assert decision['include_html']==[row['id']]


def test_unknown_conflict_and_broad_collection_need_explicit_scope(tmp_path):
    inv,_,root=run(tmp_path,[sitemap(),json_response({'post':TYPES['post']}),json_response([obj(1)],1)],mode='sitemap',sitemap=BASE+'/s.xml')
    ip=root/'inventory.json';row=next(x for x in inv['items'] if x['kind']=='rest_collection')
    for args in [{'html':['999']},{'html':['not-a-real-id']},{'html':['1'],'exclude':['1']},{'rest':[row['id']]}]:
        with pytest.raises(ValueError):d.save_selection(ip,root/'bad.json',actor='Tony',**args)
    decision=d.save_selection(ip,root/'collection-choice.json',rest=[row['id']],actor='EXAMPLE_ONLY',example=True,collection_max_pages=2)
    plan=d.export_plan(ip,root/'collection-choice.json',root/'collection-plan.json')
    assert not plan['pages'] and plan['rest']==[{'url':row['url'],'paginate':True,'max_pages':2}]
    assert d.read_review(ip)[0]['items']==inv['items']


def test_saved_collection_import_empty_content_and_no_network(tmp_path,monkeypatch):
    import socket
    def denied(*args,**kwargs):pytest.fail('offline import used a socket')
    monkeypatch.setattr(socket.socket,'connect',denied)
    root=tmp_path/'saved';state=c.create(root,{'rest':[BASE+'/wp-json/wp/v2/posts/11945']})
    value={'id':11945,'type':'post','link':BASE+'/article','title':{'rendered':'Known post'},'content':{'rendered':''}}
    execute(root,state,[json_response(value)])
    before={str(p):c.sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
    inv=d.import_saved(tmp_path/'imported',collection=root)
    assert inv['origin']=='IMPORTED_CAPTURE_INVENTORY' and not inv['context']['fresh_recon']
    assert 'needs_HTML_review_if_selected' in inv['items'][0]['gaps']
    assert inv['items'][0]['wordpress_type']=='post' and 'WordPress type: post' in d.listing(inv)
    assert inv['items'][0]['rest_items'][0]['url'].endswith('/11945')
    assert before=={str(p):c.sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}


def test_raw_import_reuses_reader_and_preserves_media_gap(tmp_path):
    from raw_fixture_factory import build_raw
    raw=build_raw(tmp_path/'raw','partial')
    inv=d.import_saved(tmp_path/'imported',raw=raw)
    assert inv['origin']=='IMPORTED_CAPTURE_INVENTORY'
    assert inv['context']['historical_capture']['capture_stopped_early']
    assert inv['wordpress']['collections']
    assert all(x['enumerated_unique']==x['unique_ids'] and x['enumerated_records']==x['saved_records'] for x in inv['wordpress']['collections'])
    assert all(Path(ref['file']).exists() for row in inv['items'] for ref in row['sources'])


@contextmanager
def native_server():
    events=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            events.append(self.path);base=f'http://127.0.0.1:{self.server.server_port}'
            path=urlsplit(self.path).path
            if path=='/s.xml':value=sitemap(base)
            elif path=='/wp-json/wp/v2/types':value=json_response({'post':TYPES['post'],'book':TYPES['book']})
            elif path=='/wp-json/wp/v2/posts':value=json_response([obj(11945,base)],166,9)
            elif path=='/wp-json/wp/v2/books':value=json_response([],0,0)
            else:value=response(status=404)
            self.send_response(value['status'])
            for k,v in value['headers'].items():self.send_header(k,v)
            self.send_header('Content-Length',str(len(value['body'])));self.end_headers();self.wfile.write(value['body'])
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}',events
    finally:server.shutdown();server.server_close();thread.join()


def test_native_sitemap_types_and_projected_metadata(tmp_path,monkeypatch):
    with native_server() as (base,events):
        monkeypatch.setattr(d,'BrowserTransport',lambda root:c.BrowserTransport(root,fixture_only=True))
        root=tmp_path/'native';engine=d.Recon(root,base,'sitemap',sitemap=base+'/s.xml',gap=.05,max_requests=4)
        inv=asyncio.run(engine.run())
        destination=os.environ.get('DECIDE_EVIDENCE')
        if destination:d.fresh_json(Path(destination)/'native-result.json',{'inventory':inv,'server_requests':events})
        assert inv['stop_reason'] is None and inv['cleanup_error'] is None
        assert len(inv['requests'])==4 and not any(p=='/wp-json/' for p in events)
        post=next(x for x in inv['wordpress']['collections'] if x['type']=='post')
        assert post['advertised_total']==166 and post['enumerated_unique']==1 and post['status']=='partial'
        assert all(b['started']-a['completed']>=.05 for a,b in zip(inv['requests'],inv['requests'][1:]))
        assert not (root/'checklist.json').exists()


def test_known_empty_content_flag_survives_projected_recon(tmp_path):
    saved=tmp_path/'saved';state=c.create(saved,{'rest':[BASE+'/wp-json/wp/v2/posts/11945']})
    value=obj(11945);value['content']={'rendered':''}
    execute(saved,state,[json_response(value)])
    inv,_,_=run(tmp_path,[sitemap(),json_response({'post':TYPES['post']}),json_response([obj(11945)],1)],mode='sitemap',sitemap=BASE+'/s.xml',known_collection=saved)
    row=next(x for x in inv['items'] if x['rest_items'])
    assert 'historical_rest_content_rendered_empty' in row['gaps'] and 'needs_HTML_review_if_selected' in row['gaps']
    assert any(x.get('saved_at') for x in row['sources'])


def test_scope_does_not_expand_to_external_endpoint_or_redirect(tmp_path):
    with pytest.raises(ValueError):d.Recon(tmp_path/'bad',BASE,'sitemap',sitemap='https://outside.invalid/s.xml')
    r=sitemap();r['final_url']='https://outside.invalid/s.xml'
    inv,fake,_=run(tmp_path,[r],mode='sitemap',sitemap=BASE+'/s.xml')
    assert len(fake.calls)==1 and inv['stop_reason']=='redirect_out_of_origin'
    assert not inv['items']


def test_discovery_page_and_candidate_bounds(tmp_path):
    body=b'<title>Start</title><a href="/one">One</a><a href="/two">Two</a>'
    inv,fake,_=run(tmp_path,[response(body),json_response({})],mode='default',max_pages=1,max_candidates=2)
    assert len(fake.calls)==2 and len(inv['items'])==2
    assert 'candidate_limit' in inv['gaps'] and 'discovery_page_limit' in inv['gaps']


def test_malformed_wp_metadata_is_not_claimed_enumerated(tmp_path):
    inv,_,_=run(tmp_path,[sitemap(),json_response({'post':TYPES['post']}),json_response([{'id':0}],1)],mode='sitemap',sitemap=BASE+'/s.xml')
    col=inv['wordpress']['collections'][0]
    assert 'malformed_metadata' in col['gaps'] and col['enumerated_unique']==0 and col['status']=='partial'


def test_html_published_date_available_and_cleanup_separate(tmp_path):
    html=b'<title>Read page</title><meta property="article:published_time" content="2026-09-01">'
    fake=Fake([response(html),json_response({})],RuntimeError('synthetic cleanup problem'))
    inv=asyncio.run(d.Recon(tmp_path/'review',BASE,'default',gap=0,transport=fake).run())
    assert inv['items'][0]['dates']['article:published_time']=='2026-09-01'
    assert inv['stop_reason'] is None and 'synthetic cleanup problem' in inv['cleanup_error']


def test_budget_exhausted_by_robots_does_not_count_unread_sitemap(tmp_path):
    inv,fake,_=run(tmp_path,[response(('Sitemap: '+BASE+'/s.xml').encode())],mode='sitemap',max_requests=1)
    assert len(fake.calls)==1 and inv['stop_reason']=='request_limit'
    assert inv['context']['discovery_pages_read']==0
