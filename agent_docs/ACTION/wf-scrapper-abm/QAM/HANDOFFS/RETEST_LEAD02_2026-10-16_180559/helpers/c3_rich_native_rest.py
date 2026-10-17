"""LEAD-02 C3 instrument: one controlled loopback native REST capture, rich payload.

Executor: Claudy (Claude Code, Claude Fable 5).
Existing-measurement check (recorded in the result): LEAD-02 §4 C3 adjudicated the
Q2 handoff's native evidence as NOT DEMONSTRATED for this obligation (T-21's native
REST object is a simple 143-byte fixture; helpers/t21_flow.py constructs
id/link/title/type/date only), and the engineering handoff §5 assigns C3 to QA
untouched. No existing exact measurement satisfies the obligation, so this ONE
capture is performed.

Served entity (defined here, independent of any collector code path): deliberately
formatted UTF-8 JSON — 4-space indentation, trailing newline, non-ASCII text
(Bengali, CJK, accents, emoji), embedded tabs/blank lines inside strings, a
'content.rendered' HTML body, optional SEO fields (yoast_head, yoast_head_json,
og metadata), and nested unknown keys with precise values. The loopback server
also sends a synthetic Set-Cookie header (value marked synthetic, no real
credential) to verify metadata exclusion.

Run: the snapshot's real CLI `-m recon_pipeline collect` (native Chromium
transport) against 127.0.0.1 with the REST item selected WITHOUT _fields.
Checks: saved body bytes == served bytes (sha256 + byte compare); recorded
result sha256 matches; requested URL and all server-observed queries carry no
_fields; 'set-cookie' absent from saved result metadata headers (allowlist);
exactly the planned loopback requests; server owned and closed. Writes argv[1].
"""
import hashlib
import json
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SNAP = Path('/tmp/claudy-lead02-retest-20261016/snapshot-repaired')
VENV = '/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python'

RICH = {
    'id': 1101,
    'date': '2026-10-01T10:00:00',
    'type': 'post',
    'link': None,  # filled with the loopback origin
    'title': {'rendered': 'Café বাংলা 工場 \U0001f680 — rich fixture'},
    'content': {'rendered': '<p>Whole rendered content with\ttab,\n\nblank line and '
                            'Unicode: Ünïcode 中文 \U0001f98a.</p>',
                'protected': False},
    'excerpt': {'rendered': '<p>Excerpt text …</p>'},
    'yoast_head': '<meta property="og:title" content="Café SEO fixture" />',
    'yoast_head_json': {'title': 'Café SEO fixture', 'og_locale': 'en_US',
                        'twitter_misc': {'Est. reading time': '3 minutes'}},
    'unknown_top_level': {'precise': 'retained', 'nested': {'deeper': ['a', 'b', {'k': 1.5}],
                                                            'emoji': '\U0001f9ea'}},
    '_embedded_like_unknown': [{'anything': True, 'count': 3}],
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path, _, query = self.path.partition('?')
        self.server.events.append({'epoch': time.time(), 'method': self.command,
                                   'path': path, 'query': query})
        route = self.server.routes.get(path)
        if route is None:
            body, ctype, extra, status = b'missing', 'text/plain; charset=utf-8', {}, 404
        else:
            ctype, body, extra = route
            status = 200
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        for k, v in extra.items():
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    origin = f'http://127.0.0.1:{server.server_port}'
    RICH['link'] = origin + '/rich-fixture-post'
    served = (json.dumps(RICH, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
    rest_url = origin + '/wp-json/wp/v2/posts/1101'
    server.routes = {'/wp-json/wp/v2/posts/1101': (
        'application/json; charset=utf-8', served,
        {'Set-Cookie': 'qa_synthetic_cookie=synthetic-not-a-credential; Path=/'})}
    server.events = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'existing_measurement_check': (
               'LEAD-02 §4 C3: the rich-native obligation is NOT DEMONSTRATED by the Q2 handoff '
               '(T-21 native object is a simple 143-byte id/link/title/type/date fixture per '
               'helpers/t21_flow.py); engineering handoff §5 leaves C3 to QA. No existing exact '
               'measurement satisfies the obligation, so this single controlled capture closes it.'),
           'origin': origin, 'rest_url': rest_url,
           'served_bytes': len(served), 'served_sha256': sha(served),
           'served_properties': {'indent': 4, 'ensure_ascii': False, 'trailing_newline': True,
                                 'non_ascii': True, 'content_field': True,
                                 'seo_fields': ['yoast_head', 'yoast_head_json'],
                                 'nested_unknown': ['unknown_top_level', '_embedded_like_unknown'],
                                 'synthetic_set_cookie_served': True}}
    coll = SNAP/'outputs/collections/qa-c3-rich-rest'
    plan = SNAP/'outputs/qa-c3-plan.json'
    plan.parent.mkdir(exist_ok=True)
    plan.write_text(json.dumps({'pages': [], 'rest': [rest_url]})+'\n')
    argv = [VENV, '-m', 'recon_pipeline', 'collect', '--collection', str(coll),
            '--plan', str(plan), '--gap', '0', '--max-requests', '5',
            '--max-seconds', '120', '--max-bytes', '10000000']
    start = datetime.now(timezone.utc).isoformat()
    proc = subprocess.run(argv, cwd=SNAP, capture_output=True, text=True, timeout=300)
    out['cli'] = {'argv': argv, 'cwd': str(SNAP), 'start': start,
                  'end': datetime.now(timezone.utc).isoformat(), 'exit': proc.returncode,
                  'stdout': proc.stdout, 'stderr': proc.stderr[-2000:]}
    server.shutdown()
    server.server_close()
    out['server_closed'] = True
    out['server_events'] = server.events
    state = json.loads((coll/'checklist.json').read_text())
    item = state['items'][0]
    meta = json.loads((coll/item['result']['file']).read_text())
    body = (coll/meta['body_file']).read_bytes()
    checks = {
        'collect_exit_0': proc.returncode == 0,
        'item_completed': item['status'] == 'completed',
        'saved_equals_served_bytes': body == served,
        'saved_sha_matches_metadata': sha(body) == meta['sha256'] and len(body) == meta['bytes'],
        'selected_url_no_fields': '_fields' not in item['url'],
        'no_fields_in_any_server_query': all('_fields' not in e['query'] for e in server.events),
        'only_planned_loopback_requests': (all(e['path'] == '/wp-json/wp/v2/posts/1101'
                                               for e in server.events) and len(server.events) >= 1),
        'set_cookie_absent_from_metadata': all('set-cookie' not in k.lower()
                                               for k in meta.get('headers', {})),
        'synthetic_cookie_value_absent_from_result': 'qa_synthetic_cookie' not in json.dumps(meta),
        'body_complete': meta.get('body_complete') is True,
    }
    out['saved'] = {'body_file': meta['body_file'], 'bytes': len(body), 'sha256': sha(body),
                    'metadata_headers': meta.get('headers', {}),
                    'transport': meta.get('transport')}
    out['checks'] = checks
    out['verdict_c3'] = 'PASS' if all(checks.values()) else 'FAIL'
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_c3': out['verdict_c3'], **checks,
                      'server_requests': len(server.events)}, indent=1))
    return 0 if out['verdict_c3'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
