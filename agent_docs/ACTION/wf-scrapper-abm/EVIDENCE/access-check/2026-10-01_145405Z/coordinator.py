"""Bounded, single-use access diagnostic. Never imports or runs the product.

Only `local_checks.py` may choose local policy overrides. Live policy is fixed.
Raw bodies remain local. Only an allowlist of response headers is persisted.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'discover_site/sitemap_utils.py').is_file())
HEAD = '3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f'
INDEX = 'https://cyberizegroup.com/sitemap_index.xml'
SITEMAP = 'https://cyberizegroup.com/sitemap.xml'
PAGES = 'https://cyberizegroup.com/wp-json/wp/v2/pages?per_page=1'
POSTS = 'https://cyberizegroup.com/wp-json/wp/v2/posts?per_page=1'
ALLOWED = {INDEX, SITEMAP, PAGES, POSTS}
HEADER_NAMES = ['Location', 'Content-Type', 'Retry-After', 'X-ac', 'X-WP-Total', 'X-WP-TotalPages']
LIMIT = 2 * 1024 * 1024


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=True)
        f.write('\n')


def user_agent():
    tree = ast.parse((ROOT / 'discover_site/sitemap_utils.py').read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'USER_AGENT' for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError('USER_AGENT unavailable')


def versions():
    import requests
    curl = shutil.which('curl')
    if not curl:
        raise RuntimeError('curl unavailable')
    return {'python': sys.version, 'python_executable': str(Path(sys.executable).relative_to(ROOT)),
            'requests': requests.__version__, 'curl': subprocess.check_output([curl, '--version'], text=True).splitlines()[0],
            'user_agent': user_agent()}


def safe_headers(headers):
    lower = {str(k).lower(): str(v) for k, v in headers.items()}
    return {k: lower.get(k.lower()) for k in HEADER_NAMES}


class Stopped(RuntimeError):
    pass


def python_worker(url, ua):
    """One request, no env auth/proxy/netrc/cookies/retries/redirects, verified TLS."""
    import requests
    try:
        with requests.Session() as s:
            s.trust_env = False
            s.mount('https://', requests.adapters.HTTPAdapter(max_retries=0))
            s.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
            with s.get(url, headers={'User-Agent': ua, 'Accept': '*/*', 'Accept-Encoding': 'identity'},
                       allow_redirects=False, stream=True, timeout=30, verify=True) as r:
                meta = {'status': r.status_code, 'headers': safe_headers(r.headers)}
                sys.stdout.buffer.write(json.dumps(meta).encode() + b'\n')
                sys.stdout.buffer.flush()
                # raw.read avoids content decoding; preserve payload bytes after HTTP framing.
                total = 0
                while True:
                    chunk = r.raw.read(min(16384, LIMIT + 1 - total), decode_content=False)
                    if not chunk:
                        break
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                    total += len(chunk)
                    if total > LIMIT:
                        break
        return 0
    except Exception:
        # Do not serialize request/response objects, headers, bodies or exception text.
        return 20


def transfer(client, url, ua, body_path, wall_limit):
    """Parent enforces one hard wall deadline and streaming body ceiling for both clients."""
    if client == 'curl':
        proto = '=http' if urlsplit(url).hostname == '127.0.0.1' else '=https'
        argv = [shutil.which('curl'), '-q', '--silent', '--include', '--request', 'GET',
                '--proxy', '', '--noproxy', '*', '--proto', proto, '--proto-redir', proto,
                '--retry', '0', '--max-redirs', '0', '--max-time', str(wall_limit),
                '--connect-timeout', str(wall_limit), '--user-agent', ua,
                '--header', 'Accept: */*', '--header', 'Accept-Encoding: identity', url]
    elif client == 'python':
        argv = [sys.executable, '-B', str(Path(__file__).resolve()), '_worker', url, ua]
    else:
        raise ValueError('unknown client')
    started = time.monotonic()
    meta = {'status': None, 'headers': {k: None for k in HEADER_NAMES}, 'transfer_error': None,
            'body_complete': False, 'body_bytes_observed': 0}
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    pending = b''
    header_done = False
    size = 0
    digest = hashlib.sha256()
    try:
        with body_path.open('xb') as out:
            while True:
                remaining = wall_limit - (time.monotonic() - started)
                if remaining <= 0:
                    meta['transfer_error'] = 'hard_wall_timeout'
                    break
                ready = sel.select(min(0.1, remaining))
                if not ready:
                    continue
                chunk = os.read(proc.stdout.fileno(), 65536)
                if not chunk:
                    break
                if not header_done:
                    pending += chunk
                    delimiter = b'\r\n\r\n' if client == 'curl' else b'\n'
                    while delimiter in pending and not header_done:
                        block, pending = pending.split(delimiter, 1)
                        if client == 'python':
                            data = json.loads(block)
                        else:
                            lines = block.decode('iso-8859-1').split('\r\n')
                            status = int(lines[0].split()[1])
                            if 100 <= status < 200:
                                continue
                            headers = dict(line.split(':', 1) for line in lines[1:] if ':' in line)
                            data = {'status': status, 'headers': safe_headers({k: v.strip() for k, v in headers.items()})}
                        meta.update(data)
                        header_done = True
                    if not header_done:
                        if len(pending) > 65536:
                            meta['transfer_error'] = 'header_ceiling'
                            break
                        continue
                    chunk, pending = pending, b''
                meta['body_bytes_observed'] += len(chunk)
                kept = chunk[:max(0, LIMIT - size)]
                out.write(kept)
                digest.update(kept)
                size += len(kept)
                if meta['body_bytes_observed'] > LIMIT:
                    meta['transfer_error'] = 'body_ceiling_exceeded'
                    break
        if meta['transfer_error'] and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            code = proc.wait(timeout=max(0.01, wall_limit - (time.monotonic() - started)))
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait()
            meta['transfer_error'] = 'hard_wall_timeout'
        meta['client_exit_code'] = code
        if not meta['transfer_error'] and (code != 0 or not header_done):
            meta['transfer_error'] = 'client_network_or_transfer_error'
        meta['body_complete'] = meta['transfer_error'] is None
    except Exception as exc:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        meta['transfer_error'] = 'coordinator_transfer_error:' + type(exc).__name__
    finally:
        sel.close()
        proc.stdout.close()
    meta.update(body_bytes=size, sha256=digest.hexdigest())
    return meta


def validate(meta, body, url, kind, permitted_redirect=None):
    check = {'expected': kind, 'passed': False, 'reason': None}
    if meta.get('transfer_error'):
        check['reason'] = meta['transfer_error']
        return check
    status = meta['status']
    if status in (403, 429):
        check['reason'] = f'HTTP_{status}_refusal'
        return check
    if status in (301, 302, 303, 307, 308):
        location = meta['headers'].get('Location')
        destination = urljoin(url, location) if location else None
        check['resolved_location'] = destination
        if kind == 'xml_or_redirect' and permitted_redirect and destination == permitted_redirect:
            check.update(passed=True, reason='permitted_redirect_not_followed', redirect=True)
        else:
            check['reason'] = 'unexpected_redirect'
        return check
    if status != 200:
        check['reason'] = 'unexpected_status'
        return check
    low = body[:262144].lower()
    markers = [b'<title>just a moment', b'<title>access denied', b'<title>attention required',
               b'cf-chl-', b'/cdn-cgi/challenge-platform', b'verify you are human',
               b'checking your browser', b'you have been rate-limited', b'captcha',
               b'<title>403', b'<title>429', b'<title>request blocked']
    # HTML denial content, not ordinary escaped HTML fields inside successful REST JSON.
    html_like = b'<html' in low[:4096] or b'<!doctype html' in low[:4096]
    if html_like and any(m in low for m in markers):
        check['reason'] = 'detected_challenge_or_block_page'
        return check
    try:
        if kind.startswith('xml'):
            if b'<!doctype' in body.lower() or b'<!entity' in body.lower():
                raise ValueError('XML declaration not allowed')
            element = ET.fromstring(body)
            if element.tag not in ('{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex',
                                   '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset'):
                raise ValueError('not a sitemap root')
            check['xml_root'] = element.tag
            check['xml_children'] = len(element)
        elif kind == 'json_collection':
            value = json.loads(body)
            if not isinstance(value, list) or not all(isinstance(o, dict) for o in value):
                raise ValueError('not a collection of objects')
            check['collection_length'] = len(value)
            check['data_gap'] = 'empty_collection' if not value else None
        else:
            raise ValueError('unknown expectation')
    except Exception:
        check['reason'] = 'invalid_expected_XML_or_JSON'
        return check
    check.update(passed=True, reason='expected_payload_valid')
    return check


class Coordinator:
    def __init__(self, directory, allowed, *, gap=15.0, max_requests=6, stage_seconds=600,
                 mission_deadline=None, transfer_seconds=30.0, local=False):
        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=False)
        if not local and (set(allowed) != ALLOWED or gap != 15 or max_requests != 6 or stage_seconds != 600 or transfer_seconds != 30):
            raise ValueError('live policy cannot be changed')
        if local and any(urlsplit(u).hostname != '127.0.0.1' or urlsplit(u).scheme != 'http' for u in allowed):
            raise ValueError('local checks restricted to literal loopback')
        self.allowed = set(allowed)
        self.gap, self.max_requests, self.transfer_seconds = gap, max_requests, transfer_seconds
        self.deadline = time.monotonic() + stage_seconds
        self.mission_deadline = mission_deadline or time.time() + 1800
        self.last_end = None
        self.count = 0
        self.stopped = None
        self.records = []
        self.lock = threading.Lock()
        self.ua = user_agent()
        self.version_info = versions()
        self.logpath = self.directory / 'events.jsonl'
        self.logpath.touch(exist_ok=False)
        self.log('coordinator_start', {'local_only': local, 'gap_s': gap, 'max_requests': max_requests,
                                     'transfer_limit_s': transfer_seconds, 'body_ceiling': LIMIT})

    def log(self, event, data):
        with self.logpath.open('a') as f:
            f.write(json.dumps({'utc': utc(), 'event': event, **data}) + '\n')

    def stop(self, reason):
        if self.stopped is None:
            self.stopped = reason
            write_json(self.directory / 'STOP.json', {'utc': utc(), 'reason': reason, 'requests_dispatched': self.count})
            self.log('sticky_stop', {'reason': reason, 'requests_dispatched': self.count})
        raise Stopped(self.stopped)

    def guard(self, wait=0):
        if self.stopped:
            raise Stopped(self.stopped)
        if self.count >= self.max_requests:
            self.stop('request_budget_exhausted')
        # Reserve the whole hard transfer limit before dispatch, including after pacing.
        if time.monotonic() + wait + self.transfer_seconds >= self.deadline:
            self.stop('live_deadline_insufficient_budget')
        if time.time() + wait + self.transfer_seconds >= self.mission_deadline:
            self.stop('mission_deadline_insufficient_budget')

    def request(self, client, url, label, kind, permitted_redirect=None):
        with self.lock:
            self.guard()
            if url not in self.allowed:
                self.stop('URL_not_authorized')
            delay = max(0, self.gap - (time.monotonic() - self.last_end)) if self.last_end else 0
            self.guard(delay)
            if delay:
                self.log('shared_pacing_wait', {'seconds': delay})
                time.sleep(delay)
            self.guard()
            target = self.directory / f'{self.count + 1:02d}_{label}_{client}'
            target.mkdir(exist_ok=False)
            start = time.monotonic()
            preceding = start - self.last_end if self.last_end else None
            meta = {'sequence': self.count + 1, 'label': label, 'utc_start': utc(), 'client': client,
                    'client_version': self.version_info['curl'] if client == 'curl' else self.version_info['requests'],
                    'python_version': self.version_info['python'] if client == 'python' else None,
                    'user_agent': self.ua, 'url': url, 'method': 'GET', 'preceding_gap_s': preceding,
                    'tls_verification': True, 'automatic_redirects': False, 'automatic_retries': False}
            self.count += 1
            self.log('request_dispatch', {'sequence': self.count, 'url': url, 'client': client})
            result = transfer(client, url, self.ua, target / 'response.body', self.transfer_seconds)
            self.last_end = time.monotonic()
            meta.update(result, utc_end=utc(), elapsed_s=self.last_end-start)
            meta['validation'] = validate(meta, (target/'response.body').read_bytes(), url, kind, permitted_redirect)
            write_json(target / 'metadata.json', meta)
            self.records.append(meta)
            self.log('request_complete', {'sequence': self.count, 'status': meta['status'],
                                          'validation': meta['validation'], 'body_bytes': meta['body_bytes']})
            if not meta['validation']['passed']:
                self.stop(meta['validation']['reason'])
            return meta


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
    def handle_data(self, data):
        self.text.append(data)


def inspect_sample(body):
    collection = json.loads(body)
    if not collection:
        return {'sample_count': 0, 'data_gap': 'empty_collection', 'fields': []}
    obj = collection[0]
    expected = {'id': 'integer', 'type': 'string', 'link': 'string', 'slug': 'string', 'status': 'string',
                'date': 'string', 'modified': 'string', 'title.rendered': 'string', 'excerpt.rendered': 'string',
                'content.rendered': 'string', 'author': 'integer', 'featured_media': 'integer',
                'categories': 'array', 'tags': 'array', 'yoast_head_json': 'object', 'yoast_head': 'string'}
    def typename(v):
        return {type(None): 'null', bool: 'boolean', int: 'integer', float: 'number', str: 'string', list: 'array', dict: 'object'}.get(type(v), 'unknown')
    fields = []
    for name, expected_type in expected.items():
        v, presence = obj, 'present'
        for key in name.split('.'):
            if not isinstance(v, dict) or key not in v:
                presence = 'missing'; break
            v = v[key]
        actual = typename(v) if presence == 'present' else None
        fields.append({'field': name, 'presence': presence, 'type': actual, 'expected_type': expected_type,
                       'type_authority': 'explicit in §2.5' if name in ('yoast_head_json','yoast_head') else 'diagnostic expectation; §2.5 lists field without explicit type',
                       'matches_expectation': presence == 'present' and actual == expected_type})
    content = obj.get('content')
    rendered = content.get('rendered') if isinstance(content, dict) else None
    empty = None
    if isinstance(rendered, str):
        parser = TextOnly(); parser.feed(rendered)
        empty = not ''.join(parser.text).strip()
    yoast = obj.get('yoast_head_json')
    yoast_fields = {k: typename(v) for k, v in yoast.items()} if isinstance(yoast, dict) else None
    return {'sample_count': 1, 'collection_length': len(collection), 'fields': fields,
            'content_rendered_empty_after_tag_strip': empty, 'yoast_field_types': yoast_fields,
            'scope': 'first returned object only; no field values or body excerpts shared'}


def live():
    checks = json.loads((HERE/'local-check-results.json').read_text())
    if checks['status'] != 'PASS' or checks['coordinator_sha256'] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise RuntimeError('local checks missing, failed, or coordinator changed')
    pre = json.loads((HERE/'preflight.json').read_text())
    if subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip() != HEAD or subprocess.check_output(['git','branch','--show-current'], cwd=ROOT, text=True).strip() != 'wf-scrapper-abm':
        raise RuntimeError('repository identity changed')
    deadline = datetime.fromisoformat(pre['mission_deadline_utc']).timestamp()
    if time.time() + 30 >= deadline:
        raise RuntimeError('mission deadline reached before live stage')
    write_json(HERE/'live-started.json', {'utc': utc(), 'coordinator_sha256': checks['coordinator_sha256']})
    c = Coordinator(HERE/'live', ALLOWED, mission_deadline=deadline)
    state = 'COMPLETE'
    try:
        c.request('curl', INDEX, 'step1', 'xml')
        c.request('python', INDEX, 'step2', 'xml')
        third = c.request('python', SITEMAP, 'step3', 'xml_or_redirect', INDEX)
        if third['validation'].get('redirect'):
            c.request('python', INDEX, 'step4', 'xml')
        c.request('python', PAGES, 'step5', 'json_collection')
        c.request('python', POSTS, 'step6', 'json_collection')
    except Stopped:
        state = 'BLOCKED'
    except Exception as exc:
        state = 'BLOCKED'
        try:
            c.stop('internal_error:' + type(exc).__name__)
        except Stopped:
            pass
    comparisons = {}
    for d in sorted((HERE/'live').glob('*_step[56]_python')):
        m = json.loads((d/'metadata.json').read_text())
        if m['validation']['passed']:
            comparisons[m['label']] = inspect_sample((d/'response.body').read_bytes())
    write_json(HERE/'contract-comparison.json', comparisons)
    write_json(HERE/'live-result.json', {'status': state, 'requests_dispatched': c.count,
               'HTTP_responses_received': sum(m['status'] is not None for m in c.records),
               'stop_reason': c.stopped, 'utc_end': utc(), 'steps_completed': [m['label'] for m in c.records if m['validation']['passed']]})
    print(json.dumps({'status': state, 'requests_dispatched': c.count, 'stop_reason': c.stopped}), flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '_worker':
        sys.exit(python_worker(sys.argv[2], sys.argv[3]))
    elif len(sys.argv) == 2 and sys.argv[1] == 'live':
        live()
    else:
        raise SystemExit('Use local_checks.py first; live is a single-use explicitly authorized stage.')
