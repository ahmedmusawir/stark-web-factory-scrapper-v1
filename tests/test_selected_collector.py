"""Focused engineering checks for explicit collection; native cases use loopback only."""
import asyncio
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import time

import pytest
from recon_pipeline import collector as c

BASE = 'http://127.0.0.1:9876'
ARTICLE = b'<html><head><title>Selected article</title></head><body><article><h1>Selected article</h1><p>A substantive selected article paragraph preserved by the browser for later architect review.</p><a href="/unselected">Do not crawl this link</a></article></body></html>'


def response(body=ARTICLE, status=200, **headers):
    return dict(status=status, headers={'content-type': 'text/html', **headers}, body=body,
                final_url=None, redirect_from=[], transport='test double')


def rest(ids, total=None, pages=None):
    body = json.dumps([{'id': i, 'title': {'rendered': 'বাংলা café 🦊'},
                       'content': {'rendered': '<p>Whole content</p>'}, 'unknown': {'precise': 'retained'}} for i in ids], ensure_ascii=False).encode()
    headers = {'content-type': 'application/json'}
    if total is not None:
        headers.update({'x-wp-total': str(total), 'x-wp-totalpages': str(pages)})
    return response(body, **headers)


class Fake:
    def __init__(self, results=(), close_error=None):
        self.results = iter(results); self.calls = []; self.starts = 0; self.close_error = close_error
    async def start(self): self.starts += 1
    async def get(self, item):
        self.calls.append((item['url'], time.monotonic()))
        value = next(self.results)
        if isinstance(value, BaseException): raise value
        return dict(value)
    async def close(self):
        if self.close_error: raise self.close_error


def execute(root, state, results, **kwargs):
    fake = results if isinstance(results, Fake) else Fake(results)
    code = asyncio.run(c.run_collection(root, state, transport=fake, gap=kwargs.pop('gap', 0), **kwargs))
    return code, fake


def collection(tmp_path, pages=('/a', '/b'), rest_entries=()):
    root = tmp_path/'collection'
    return root, c.create(root, {'pages': [BASE+p for p in pages], 'rest': list(rest_entries)})


def test_selected_only_and_pacing(tmp_path):
    root, state = collection(tmp_path)
    code, fake = execute(root, state, [response(), response()], gap=.04)
    assert code == 0 and [x[0] for x in fake.calls] == [BASE+'/a', BASE+'/b']
    events = state['runs'][-1]['requests']
    assert events[1]['start'] - events[0]['completion'] >= .04
    assert c.run_collection.__kwdefaults__['gap'] == 5
    assert all(c.valid_result(root, x) for x in state['items'])


@pytest.mark.parametrize('blocked', [response(status=429, **{'retry-after': '60'}), response(status=403), response(status=401), response(b'<title>Just a moment...</title><p>Verify you are human</p>')])
def test_refusal_stops_without_retry(tmp_path, blocked):
    root, state = collection(tmp_path, pages=('/a', '/b', '/c'))
    code, fake = execute(root, state, [response(), blocked])
    assert code == 2 and len(fake.calls) == 2
    assert [x['status'] for x in state['items']] == ['completed', 'failed', 'pending']
    assert state['runs'][-1]['stop_reason']
    saved = json.loads((root/state['items'][1]['result']['file']).read_bytes())
    assert saved['status'] == blocked['status'] and saved['headers'] == blocked['headers']


def test_json_quoted_challenge_is_source_not_denial():
    r = rest([1])
    r['body'] = json.dumps([{'id':1, 'content': {'rendered':'<div id="challenge-running">source</div>'}}]).encode()
    result, stop = c.classify({'kind':'rest'}, r, 10000)
    assert result['ok'] and stop is None


def test_interruption_reopen_skips_completed(tmp_path):
    root, state = collection(tmp_path)
    code, _ = execute(root, state, [response(), asyncio.CancelledError()])
    assert code == 130 and state['items'][0]['status'] == 'completed'
    first = state['items'][0]['result'].copy()
    reopened = c.load(root)
    code, fake = execute(root, reopened, [response()])
    assert code == 0 and [x[0] for x in fake.calls] == [BASE+'/b']
    assert reopened['items'][0]['result'] == first


def test_missing_and_corrupt_results_are_not_skipped(tmp_path):
    root, state = collection(tmp_path)
    execute(root, state, [response(), response()])
    meta = c.valid_result(root, state['items'][0]); body = root/meta['body_file']
    body.rename(body.with_name('retained-missing-test-original'))
    second = root/c.valid_result(root, state['items'][1])['body_file']
    second.write_bytes(b'corrupt test fixture')
    code, fake = execute(root, c.load(root), [response(), response()])
    assert code == 0 and len(fake.calls) == 2


def test_add_only_and_explicit_refresh_preserve_attempts(tmp_path):
    root, state = collection(tmp_path, pages=('/a',))
    execute(root, state, [response()]); old = state['items'][0]['result'].copy()
    original = (root/old['file']).read_bytes()
    c.add_items(state, c.plan_items({'pages': [BASE+'/a', BASE+'/new']}))
    code, fake = execute(root, state, [response()])
    assert code == 0 and [x[0] for x in fake.calls] == [BASE+'/new']
    noop = Fake(); assert execute(root, c.load(root), noop)[0] == 0 and noop.starts == 0
    c.main(['refresh', '--collection', str(root), '--id', state['items'][0]['id']])
    state = c.load(root); execute(root, state, [response(b'<p>Replacement</p>')])
    assert len(state['items'][0]['attempts']) == 2 and state['items'][0]['result'] != old
    assert (root/old['file']).read_bytes() == original
    with pytest.raises(SystemExit) as exc:
        c.main(['refresh', '--collection', str(root), '--id', 'unknown'])
    assert exc.value.code == 2


def paged(tmp_path, maximum=4):
    return collection(tmp_path, pages=(), rest_entries=[{'url': BASE+'/wp-json/wp/v2/posts?per_page=2', 'paginate': True, 'max_pages': maximum}])


def test_short_intermediate_page_continues_and_exact_unicode_bytes(tmp_path):
    root, state = paged(tmp_path)
    replies = [rest([1], 5, 3), rest([2,3], 5,3), rest([4,5],5,3)]
    code, fake = execute(root, state, replies, gap=.02)
    cov = next(iter(state['coverage'].values()))
    assert code == 0 and len(fake.calls) == 3 and cov['status'] == 'complete'
    assert cov['short_pages'] == [{'page':1,'records':1}] and cov['unique_ids'] == 5
    for item, expected in zip(state['items'], replies):
        meta = c.valid_result(root, item)
        assert (root/meta['body_file']).read_bytes() == expected['body'] and meta['sha256'] == c.sha(expected['body'])
    events = state['runs'][-1]['requests']
    assert all(b['start']-a['completion'] >= .02 for a,b in zip(events,events[1:]))
    with pytest.raises(SystemExit) as exc:
        c.main(['refresh','--collection',str(root),'--id',state['items'][0]['id']])
    assert exc.value.code == 2
    assert all(x['status']=='completed' for x in c.load(root)['items'])


@pytest.mark.parametrize('replies,maximum,gap', [
    ([rest([1],4,2),rest([2],4,2)],4,'count_mismatch'),
    ([rest([1,2],4,2),rest([2,3],4,2)],4,'duplicate_ids'),
    ([rest([1],4,2)],1,'approved_page_limit'),
    ([rest([1],4,2),rest([],4,3)],4,'pagination_totals_changed'),
    ([rest([],4,2)],4,'empty_intermediate_page'),
    ([rest([1])],4,'pagination_headers_missing_or_invalid'),
])
def test_incomplete_coverage_is_explicit(tmp_path, replies, maximum, gap):
    root, state = paged(tmp_path, maximum)
    code, fake = execute(root, state, replies)
    cov = next(iter(state['coverage'].values()))
    assert code == 2 and cov['status'] == 'partial' and gap in cov['gaps']
    assert len(fake.calls) == len(replies)


def test_limit_resume_and_cleanup_separate(tmp_path):
    root, state = collection(tmp_path)
    code, fake = execute(root, state, [response()], max_requests=1)
    assert code == 2 and state['runs'][-1]['stop_reason'] == 'request_limit'
    code, fake = execute(root, c.load(root), Fake([response()], RuntimeError('closed target')))
    final = c.load(root)['runs'][-1]
    assert code == 3 and final['collection_outcome'] == 'complete' and final['cleanup_error']
    assert final['stop_reason'] is None


def test_cleanup_does_not_replace_first_refusal(tmp_path):
    root, state = collection(tmp_path)
    code, _ = execute(root, state, Fake([response(status=429)], RuntimeError('cleanup failure')))
    assert code == 2 and state['runs'][-1]['stop_reason'] == 'http_429' and state['runs'][-1]['cleanup_error']


def test_write_failure_cannot_mark_complete(tmp_path, monkeypatch):
    root, state = collection(tmp_path)
    def denied(*args): raise OSError('synthetic full disk')
    monkeypatch.setattr(c, 'persist_result', denied)
    code, _ = execute(root, state, [response()])
    assert code == 2 and state['items'][0]['status'] == 'failed' and state['items'][0]['result'] is None


def test_cap_preserves_partial_not_complete(tmp_path):
    root, state = collection(tmp_path)
    code, fake = execute(root, state, [response()], response_cap=40)
    assert code == 2 and len(fake.calls)==1 and state['runs'][-1]['stop_reason']=='response_cap'
    meta = json.loads((root/state['items'][0]['result']['file']).read_bytes())
    assert meta['bytes']==40 and not meta['body_complete'] and not meta['ok']


@pytest.mark.parametrize('plan', [{'pages':'not-an-array'}, {'rest':['https://example.org/wp-json/']}, {'rest':[{'url':BASE+'/posts','paginate':True}]}, {'pages':['https://user:secret@example.org']}])
def test_invalid_scope_rejected_before_create(tmp_path, plan):
    with pytest.raises(ValueError): c.create(tmp_path/'bad', plan)
    assert not (tmp_path/'bad').exists()


@contextmanager
def native_fixture():
    events = []
    bodies = {}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_GET(self):
            events.append({'url': self.path, 'at':time.monotonic()})
            status, headers = 200, {'Content-Type':'text/html; charset=utf-8'}
            if self.path.startswith('/wp-json/wp/v2/posts'):
                page = int(dict(c.parse_qsl(c.urlsplit(self.path).query)).get('page', '1'))
                value = rest([1] if page == 1 else [2,3],3,2)
                body = value['body']; headers = value['headers']
            elif self.path == '/deny':
                status, body = 429, b'Too many requests'; headers['Retry-After']='60'
            else:
                body = ARTICLE
            bodies[self.path]=body
            self.send_response(status)
            for k,v in headers.items(): self.send_header(k,v)
            self.send_header('Content-Length',str(len(body))); self.end_headers()
            self.wfile.write(body)
    server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
    thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try: yield f'http://127.0.0.1:{server.server_port}', events, bodies
    finally: server.shutdown(); server.server_close(); thread.join()


def save_native(name, state, events, bodies):
    directory = os.environ.get('SELECTED_COLLECTOR_EVIDENCE')
    if directory:
        destination = Path(directory)/name
        destination.mkdir(parents=True,exist_ok=False)
        c.atomic_json(destination/'timeline.json', {'checklist':state,'server_events':events,
            'served_bodies':{k:{'bytes':len(v),'sha256':c.sha(v)} for k,v in bodies.items()}})


def test_native_browser_html_rest_pagination_and_no_link_crawl(tmp_path):
    with native_fixture() as (base, events, bodies):
        root = tmp_path/'native'
        state=c.create(root,{'pages':[base+'/selected'], 'rest':[{'url':base+'/wp-json/wp/v2/posts?per_page=2','paginate':True,'max_pages':2}]})
        code=asyncio.run(c.run_collection(root,state,gap=.15,transport=c.BrowserTransport(root,fixture_only=True),max_seconds=60))
        save_native('native-success',state,events,bodies)
        assert code==0, state['runs'][-1]
        assert '/unselected' not in [e['url'] for e in events]
        assert len(state['runs'][-1]['requests'])==3
        assert next(iter(state['coverage'].values()))['status']=='complete'
        for item in state['items']:
            meta=c.valid_result(root,item); body=(root/meta['body_file']).read_bytes()
            if item['kind']=='rest':
                path=c.urlsplit(item['url']); expected=bodies[path.path+'?'+path.query]
                assert body==expected and meta['sha256']==c.sha(expected)
                assert 'Response.body' in meta['transport']
            else: assert b'substantive selected article paragraph' in body
        requests=state['runs'][-1]['requests']
        assert all(b['start']-a['completion']>=.15 for a,b in zip(requests,requests[1:]))


def test_native_429_stops_next_planned_request(tmp_path):
    with native_fixture() as (base, events, bodies):
        root=tmp_path/'native-denial'
        state=c.create(root,{'pages':[base+'/deny',base+'/must-not-collect']})
        code=asyncio.run(c.run_collection(root,state,gap=.05,transport=c.BrowserTransport(root,fixture_only=True),max_seconds=60))
        save_native('native-denial',state,events,bodies)
        assert code==2 and state['runs'][-1]['stop_reason']=='http_429'
        assert '/must-not-collect' not in [e['url'] for e in events]
        assert state['items'][1]['status']=='pending'


def test_incomplete_browser_body_and_error_are_preserved(tmp_path):
    root,state=collection(tmp_path)
    r=response(b'partial',status=200); r.update(body_complete=False,transport_error='TimeoutError: synthetic stalled body')
    code,fake=execute(root,state,[r])
    assert code==2 and len(fake.calls)==1
    assert state['runs'][-1]['stop_reason']=='browser_read_failed'
    meta=json.loads((root/state['items'][0]['result']['file']).read_bytes())
    assert not meta['ok'] and not meta['body_complete'] and meta['bytes']==7


def test_single_rest_response_does_not_claim_collection_coverage(tmp_path):
    root,state=collection(tmp_path,pages=(),rest_entries=[BASE+'/wp-json/wp/v2/posts'])
    code,_=execute(root,state,[rest([1],100,10)])
    meta=c.valid_result(root,state['items'][0])
    assert code==0 and meta['coverage_scope']=='selected_response_only'
    assert meta['headers']['x-wp-totalpages']=='10' and 'No claim' in meta['coverage_note']


def test_overlapping_pagination_scope_is_explicit_partial(tmp_path):
    root,state=paged(tmp_path)
    second=BASE+'/wp-json/wp/v2/posts?per_page=2&page=2'
    c.add_items(state,c.plan_items({'rest':[second]}))
    code,_=execute(root,state,[rest([1,2],4,2),rest([3,4],4,2)])
    assert code==2 and len({x['id'] for x in state['items']})==len(state['items'])
    assert 'overlapping_explicit_selection' in next(iter(state['coverage'].values()))['gaps']


def test_library_logged_cleanup_error_is_not_silenced(tmp_path):
    browser=c.BrowserTransport(tmp_path)
    async def logged_close():
        browser.logger.error('Error closing context: {error}', params={'error':'synthetic closed context'})
    browser.crawler.close=logged_close
    with pytest.raises(RuntimeError,match='logged cleanup errors'):
        asyncio.run(browser.close())
    assert browser.logger.cleanup_messages[0]['detail']=='synthetic closed context'


def test_cli_add_is_offline_and_retains_completed(tmp_path, monkeypatch):
    root,state=collection(tmp_path,pages=('/a',))
    execute(root,state,[response()])
    plan=tmp_path/'add.json';plan.write_text(json.dumps({'pages':[BASE+'/new']}))
    def forbidden(*args,**kwargs): pytest.fail('add must not start a browser')
    monkeypatch.setattr(c,'BrowserTransport',forbidden)
    c.main(['add','--collection',str(root),'--plan',str(plan)])
    reopened=c.load(root)
    assert [x['status'] for x in reopened['items']]==['completed','pending']


def test_pacing_survives_resume_and_addition(tmp_path):
    root,state=collection(tmp_path,pages=('/a',))
    execute(root,state,[response()])
    completed=state['runs'][-1]['requests'][-1]['completion']
    reopened=c.load(root)
    c.add_items(reopened,c.plan_items({'pages':[BASE+'/new']}))
    code,_=execute(root,reopened,[response()],gap=.08)
    assert code==0
    assert reopened['runs'][-1]['requests'][0]['start']-completed >= .08
