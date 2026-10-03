"""Only localhost fixture traffic. These checks are not the product test suite."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import threading
import time
import traceback
from coordinator import Coordinator, Stopped, HERE, LIMIT, user_agent, versions, write_json, utc

XML = b'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://not-fetched.invalid/child.xml</loc></sitemap></sitemapindex>'
HITS = []
ACTIVE = 0
PEAK = 0
LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        global ACTIVE, PEAK
        with LOCK:
            ACTIVE += 1
            PEAK = max(PEAK, ACTIVE)
            hit = {'path': self.path, 'start': time.monotonic(), 'end': None,
                   'user_agent': self.headers.get('User-Agent'), 'cookie_present': 'Cookie' in self.headers,
                   'authorization_present': 'Authorization' in self.headers}
            HITS.append(hit)
        try:
            status, body, headers = 200, XML, {'Content-Type': 'application/xml'}
            if self.path == '/refuse':
                status, body = 429, b'<html><title>429 Too Many Requests</title></html>'
                headers['Retry-After'] = '120'
            elif self.path == '/forbid':
                status, body = 403, b'<html><title>Access Denied</title></html>'
            elif self.path == '/redirect':
                status, body = 301, b'redirect'
                headers['Location'] = '/target'
            elif self.path == '/other-redirect':
                status, body = 302, b'redirect'
                headers['Location'] = 'https://never-contact.invalid/'
            elif self.path == '/challenge':
                body = b'<html><title>Just a moment...</title><p>Verify you are human</p></html>'
                headers['Content-Type'] = 'text/html'
            elif self.path == '/bad':
                body = b'not XML'
            elif self.path == '/large':
                body = b'x' * (LIMIT + 4096)
            elif self.path == '/slow':
                time.sleep(2)
            elif self.path == '/empty':
                body = b'[]'
                headers['Content-Type'] = 'application/json'
            elif self.path == '/delay':
                time.sleep(.3)
            headers['Set-Cookie'] = 'LOCAL_CHECK_ONLY=never_share'
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            with LOCK:
                hit['end'] = time.monotonic()
                ACTIVE -= 1


def run():
    root = HERE/('local-' + str(time.time_ns()))
    root.mkdir(exist_ok=False)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    paths = ['/ok','/refuse','/forbid','/redirect','/target','/other-redirect','/challenge','/bad','/large','/slow','/empty','/delay']
    allowed = {base+p for p in paths}
    results = []
    def coordinator(name, **kw):
        args = {'gap': 0, 'stage_seconds': 300, 'transfer_seconds': 3, 'local': True}
        args.update(kw)
        return Coordinator(root/name, allowed, **args)
    def record(name, **detail):
        results.append({'check': name, 'status': 'PASS', **detail})
        print('PASS ' + name, flush=True)
    def stopped(c, client, path, expected_reason=None, kind='xml', redirect=None):
        try:
            c.request(client, base+path, 'case', kind, redirect)
        except Stopped as e:
            if expected_reason:
                assert str(e) == expected_reason, (str(e), expected_reason)
            return
        raise AssertionError('expected a sticky stop')
    status = 'FAIL'
    failure = None
    try:
        # Actual 15-second shared gap, including a response delayed by the server.
        c = coordinator('shared-gap', gap=15)
        c.request('curl', base+'/delay', 'first', 'xml')
        m = c.request('python', base+'/ok', 'second', 'xml')
        assert m['preceding_gap_s'] >= 15
        assert HITS[1]['start'] - HITS[0]['end'] >= 15
        assert HITS[0]['user_agent'] == HITS[1]['user_agent'] == user_agent()
        record('15-second response-completion pacing across curl and Python', measured_gap_s=m['preceding_gap_s'])

        for client in ('curl','python'):
            c = coordinator('stop-'+client)
            n = len(HITS)
            stopped(c, client, '/refuse', 'HTTP_429_refusal')
            assert c.records[0]['headers']['Retry-After'] == '120'
            stopped(c, 'python' if client == 'curl' else 'curl', '/ok', 'HTTP_429_refusal')
            assert len(HITS) == n+1 and c.count == 1
            record('sticky 429 stops both clients: '+client)
            c = coordinator('redirect-'+client)
            n = len(HITS)
            m = c.request(client, base+'/redirect', 'redirect', 'xml_or_redirect', base+'/target')
            assert m['status'] == 301 and m['validation']['redirect'] and len(HITS) == n+1
            assert HITS[-1]['path'] == '/redirect'
            record('no automatic redirect follow: '+client)
            c = coordinator('wrong-redirect-'+client)
            stopped(c, client, '/other-redirect', 'unexpected_redirect')
            record('unexpected redirect stops without external hop: '+client)
            c = coordinator('body-cap-'+client)
            stopped(c, client, '/large', 'body_ceiling_exceeded')
            assert c.records[0]['body_bytes'] == LIMIT and not c.records[0]['body_complete']
            record('streaming 2 MiB ceiling: '+client)
            c = coordinator('timeout-'+client, transfer_seconds=.5)
            start = time.monotonic()
            stopped(c, client, '/slow')
            assert time.monotonic()-start < 1.2 and c.records[0]['transfer_error'] is not None
            record('hard wall timeout: '+client)

        c = coordinator('budget', max_requests=6)
        n = len(HITS)
        for i in range(6):
            c.request('curl' if i%2 == 0 else 'python', base+'/ok', 'budget'+str(i), 'xml')
        stopped(c, 'curl', '/ok', 'request_budget_exhausted')
        assert len(HITS)==n+6 and c.count==6
        record('six-request shared budget refuses seventh dispatch')

        n = len(HITS)
        c = coordinator('deadline-before', stage_seconds=0)
        stopped(c, 'curl', '/ok', 'live_deadline_insufficient_budget')
        c = coordinator('mission-before', mission_deadline=time.time()-1)
        stopped(c, 'python', '/ok', 'mission_deadline_insufficient_budget')
        assert len(HITS)==n
        record('stage and total mission deadlines before dispatch')

        c = coordinator('deadline-after-wait', gap=.4, transfer_seconds=2)
        c.request('python', base+'/ok', 'first', 'xml')
        n = len(HITS)
        def expire():
            c.deadline = time.monotonic()-1
        timer = threading.Timer(.1, expire); timer.start()
        stopped(c, 'curl', '/ok', 'live_deadline_insufficient_budget')
        timer.join()
        assert len(HITS)==n
        record('deadline rechecked after pacing wait')

        for path, reason in [('/forbid','HTTP_403_refusal'),('/challenge','detected_challenge_or_block_page'),('/bad','invalid_expected_XML_or_JSON')]:
            c = coordinator(path[1:])
            stopped(c,'python',path,reason)
            record('stop condition '+path)
        c = coordinator('empty')
        m = c.request('python',base+'/empty','empty','json_collection')
        assert m['validation']['passed'] and m['validation']['data_gap']=='empty_collection'
        record('empty REST collection is a data gap')

        c = coordinator('scope')
        n=len(HITS)
        try:
            c.request('curl','https://never-contact.invalid/','forbidden','xml')
        except Stopped as e:
            assert str(e)=='URL_not_authorized'
        else:
            raise AssertionError('external URL accepted by local checker')
        assert len(HITS)==n
        record('external destinations rejected before subprocess dispatch')

        c = coordinator('overwrite')
        c.request('curl',base+'/ok','first','xml')
        hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'overwrite').rglob('*') if p.is_file()}
        try:
            coordinator('overwrite')
        except FileExistsError:
            pass
        else:
            raise AssertionError('evidence folder reused')
        assert hashes=={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'overwrite').rglob('*') if p.is_file()}
        record('exclusive evidence directory; existing bytes unchanged')
        assert all(not h['cookie_present'] and not h['authorization_present'] for h in HITS)
        assert all('Set-Cookie' not in p.read_text() and 'never_share' not in p.read_text() for p in root.rglob('metadata.json'))
        record('cookies/auth not sent; sensitive response headers not persisted')
        # Timeout fixtures may continue locally after client termination; serialized client calls
        # are guaranteed by lock and no-overlap is separately checked on normal responses.
        c = coordinator('concurrent-callers')
        errors=[]
        n=len(HITS)
        def call(client):
            try:
                c.request(client,base+'/delay',client,'xml')
            except Exception as e:
                errors.append(type(e).__name__)
        t1=threading.Thread(target=call,args=('curl',)); t2=threading.Thread(target=call,args=('python',))
        t1.start(); t2.start(); t1.join(); t2.join()
        assert not errors and len(HITS)==n+2 and HITS[-1]['start'] >= HITS[-2]['end']
        record('concurrent callers serialized to one in-flight request')
        status='PASS'
    except Exception as e:
        failure={'type':type(e).__name__, 'traceback':traceback.format_exc()}
        print('LOCAL CHECKS FAILED: '+type(e).__name__,flush=True)
    finally:
        server.shutdown(); server.server_close()
        write_json(HERE/'local-check-results.json',{'status':status,'utc_end':utc(),'checks':results,
                   'local_HTTP_requests':len(HITS),'external_HTTP_requests':0,'failure':failure,
                   'coordinator_sha256':hashlib.sha256((HERE/'coordinator.py').read_bytes()).hexdigest()})
        write_json(HERE/'local-server-log.json',HITS)
        write_json(HERE/'versions.json',versions())
    raise SystemExit(0 if status=='PASS' else 1)


if __name__=='__main__':
    run()
