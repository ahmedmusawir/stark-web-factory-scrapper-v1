"""Single Crawl4AI-owned Chromium session for intentional collection.

No alternate HTTP client. Crawl4AI hooks provide all browser objects. Events for
incidental resources are separate from intentional admission/pacing evidence.
"""
import asyncio
import hashlib
import json
from pathlib import Path
import platform
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig
from crawl4ai.async_logger import AsyncLogger

from discover_site.sitemap_utils import USER_AGENT

HEADER_ALLOWLIST = frozenset(('content-type','location','retry-after','x-ac','x-wp-total',
                              'x-wp-totalpages','content-length','cf-mitigated'))


class CollectionStopped(RuntimeError):
    pass


def challenge_reason(status, headers, body):
    """Explicit signals only; empty/error content is not inherently a challenge."""
    if status in (403,429):
        return f'http_{status}'
    if headers.get('cf-mitigated','').lower() == 'challenge':
        return 'cf_mitigated_challenge'
    soup = BeautifulSoup(body or '', 'html.parser')
    title = soup.title.get_text(' ', strip=True).lower() if soup.title else ''
    text = soup.get_text(' ', strip=True).lower()
    structural = soup.select_one('script[src*="/cdn-cgi/challenge-platform/"], #challenge-running, #cf-challenge-running')
    if structural:
        return 'challenge_platform_markup'
    if title in ('just a moment...', 'just a moment', 'access denied', 'attention required! | cloudflare'):
        if any(x in text for x in ('verify you are human','checking your browser','you have been blocked',
                                  'access to this page has been denied','enable javascript and cookies to continue')):
            return 'explicit_block_document'
    return None


@dataclass
class Bounds:
    operations: int = 120
    seconds: float = 1800
    persisted_bytes: int = 100_000_000
    response_bytes: int = 10 * 1024 * 1024
    document_seconds: float = 180
    read_seconds: float = 30
    finalization_reserve: float = 30
    document_slots: int | None = 10


@dataclass
class Operation:
    url: str
    method: str
    kind: str
    operation_id: str | None = None
    script_id: str | None = None
    context_id: int | None = None
    initial_claimed: bool = False
    chain: list = field(default_factory=list)
    requests: dict = field(default_factory=dict)
    finished: dict = field(default_factory=dict)
    response_headers: dict = field(default_factory=dict)
    status: int | None = None
    final_url: str | None = None
    error: str | None = None
    started: float = field(default_factory=time.monotonic)


@dataclass
class Interception:
    owner: object
    operation: Operation | None
    details: dict
    seen: float = field(default_factory=time.monotonic)
    classification: str = 'unresolved'
    state: str = 'pending'
    command: str | None = None


def protocol_detail(error):
    # Protocol errors normally contain no URLs. Redact URL userinfo/query/fragment
    # if a driver includes one; never include request headers or post data.
    def public_url(match):
        try:
            p = urlsplit(match.group())
            return f'{p.scheme}://{p.hostname or ""}{p.path}'
        except ValueError:
            return '<redacted URL>'
    text = re.sub(r'https?://[^\s]+', public_url, str(error))
    return text[:2048]


class BrowserSession:
    def __init__(self, origin, *, bounds=None, log=None, runtime_dir=None, loopback_only=False):
        p = urlsplit(origin)
        self.hosts = {p.hostname, p.hostname[4:] if p.hostname.startswith('www.') else 'www.'+p.hostname}
        self.origin = f'{p.scheme}://{p.netloc}'
        self.bounds = bounds or Bounds()
        self.log = log or (lambda row: None)
        self.runtime_dir = runtime_dir
        self.loopback_only = loopback_only
        self.started = time.monotonic()
        self.last_completion = None
        self.dispatches = 0
        self.documents = 0
        self.persisted = 0
        self.stop_reason = None
        self.op = None
        self.page = self.cdp = None
        self.events = []
        self.tasks = set()
        self.resources = Counter()
        self.statuses = Counter()
        self.lock = asyncio.Lock()
        self.session_id = 'abm-' + str(time.time_ns())
        self.runtime = {}
        self.operation_sequence = 0
        self.network_requests = {}
        self.interceptions = {}
        self.cancellations = {}
        self.closing = False
        self.diagnostic_events = 0
        self.interception_owner = None

    def event(self, event_name, **values):
        row = {'event':event_name, 'monotonic':time.monotonic(), **values}
        self.events.append(row)
        try:
            self.log(row)
        except (OSError, BufferError):
            self.stop_reason = self.stop_reason or 'evidence_write_limit'
            if self.page and not self.page.is_closed():self.spawn(self.page.close())

    def stop(self, reason):
        if self.stop_reason is None:
            self.stop_reason = reason
            self.event('stop', reason=reason)

    def check(self):
        if self.stop_reason:
            raise CollectionStopped(self.stop_reason)
        if time.monotonic() - self.started >= self.bounds.seconds - self.bounds.finalization_reserve:
            self.stop('wall_clock_limit')
            raise CollectionStopped(self.stop_reason)
        if self.dispatches >= self.bounds.operations:
            self.stop('operation_limit')
            raise CollectionStopped(self.stop_reason)

    def scoped(self, url):
        try:
            p = urlsplit(url)
            return p.scheme in ('http','https') and p.hostname in self.hosts and not (p.username or p.password)
        except ValueError:
            return False

    async def gap(self, completed):
        self.check()
        if completed is not None:
            delay = max(0, completed + 5.0 - time.monotonic())
            if delay >= self.bounds.seconds - self.bounds.finalization_reserve - (time.monotonic()-self.started):
                self.stop('wall_clock_limit_before_gap')
                raise CollectionStopped(self.stop_reason)
            if delay:
                self.event('pause', seconds=delay, predecessor_completed=completed)
                await asyncio.sleep(delay)
        self.check()

    def spawn(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    async def __aenter__(self):
        config = BrowserConfig(headless=True, user_agent=USER_AGENT)
        # The installed logger supports no file sink. Keep browser/library
        # console diagnostics for the bounded outer recorder; do not allow an
        # independent unbounded .crawl4ai/crawler.log outside the raw byte guard.
        kwargs = {'config':config,'logger':AsyncLogger(log_file=None,verbose=config.verbose)}
        if self.runtime_dir:
            kwargs['base_directory'] = str(self.runtime_dir)
        self.crawler = AsyncWebCrawler(**kwargs)
        self.crawler.crawler_strategy.set_hook('on_page_context_created', self.created)
        self.crawler.crawler_strategy.set_hook('after_goto', self.after_goto)
        self.crawler.crawler_strategy.set_hook('before_return_html', self.before_return_html)
        await self.crawler.__aenter__()
        self.runtime = {'user_agent':USER_AGENT,'headless':True,'ignore_https_errors':config.ignore_https_errors,
                        'page_timeout_ms':90000,'wait_for_images':True,'post_load_delay_s':3.0,'cache_mode':'BYPASS',
                        'library_file_logging':False}
        return self

    async def __aexit__(self, *exc):
        self.closing = True
        try:
            await self.crawler.__aexit__(*exc)
        except Exception as error:
            self.diagnostic('interception_cleanup_error', detail=protocol_detail(error))
            self.stop('browser_cleanup_error')  # Sticky: never replaces the primary stop.
        finally:
            if self.tasks:
                await asyncio.gather(*list(self.tasks), return_exceptions=True)

    async def created(self, page, context, **kwargs):
        if self.page is page:
            return page
        if self.page is not None:
            self.stop('unexpected_page_session')
            raise CollectionStopped(self.stop_reason)
        self.page = page
        self.runtime['browser_version'] = context.browser.version
        # Identify the running executable, not a guessed cache directory. The
        # installed Chromium CDP API supplies its browser PID; /proc is local.
        browser_cdp = await context.browser.new_browser_cdp_session()
        try:
            processes = (await browser_cdp.send('SystemInfo.getProcessInfo'))['processInfo']
            browser_pid = next(p['id'] for p in processes if p['type'] == 'browser')
            binary = Path(f'/proc/{browser_pid}/exe').resolve(strict=True)
            with binary.open('rb') as stream:
                binary_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
            self.runtime.update(browser_executable=binary.name, browser_executable_sha256=binary_hash,
                                platform=platform.platform(), machine=platform.machine(),
                                lock_sha256=hashlib.sha256((Path(__file__).resolve().parents[1]/'requirements-lock.txt').read_bytes()).hexdigest())
        finally:
            await browser_cdp.detach()
        context.on('request', self.request_seen)
        context.on('requestfinished', self.request_finished)
        context.on('requestfailed', self.request_failed)
        context.on('response', self.response_seen)
        context.on('serviceworker', lambda _: self.stop('uncontrolled_service_worker'))
        # Context guard covers new pages; the CDP guard below covers redirect hops.
        async def guard(route):
            req = route.request
            if self.loopback_only and urlsplit(req.url).hostname != '127.0.0.1':
                self.event('external_test_request_prevented', url=req.url)
                if req.is_navigation_request():self.stop('fixture_external_navigation')
                await route.abort()
            else:
                try:
                    frame = req.frame
                except Exception:
                    # Installed API explicitly has no frame for a popup's first
                    # navigation. It cannot be the owned existing main frame.
                    self.stop('unexpected_top_level_page' if req.is_navigation_request() else 'unobservable_request_frame')
                    await route.abort()
                    return
                if self.stop_reason or (req.is_navigation_request() and frame.parent_frame is None and frame != page.main_frame):
                    if not self.stop_reason: self.stop('unexpected_top_level_page')
                    await route.abort()
                else:
                    await route.continue_()
        await context.route('**/*', guard)
        self.cdp = await context.new_cdp_session(page)
        self.main_frame = (await self.cdp.send('Page.getFrameTree'))['frameTree']['frame']['id']
        # One listener set per owned page (created() is idempotent above).
        # Bind the actual CDPSession object, never a request from another session.
        self.interception_owner = self.cdp
        owner = self.cdp
        self.cdp.on('Fetch.requestPaused', lambda params:self.paused_event(owner, params))
        page.on('close', self.page_closed)
        page.on('crash', lambda _: self.stop('browser_page_crashed'))
        self.cdp.on('Page.frameDetached', lambda p:self.diagnostic(
            'interception_frame_detached', session='page-cdp-1', frame_id=p['frameId'], reason=p.get('reason')))
        self.cdp.on('Page.frameNavigated', lambda p:self.diagnostic(
            'interception_frame_navigated', session='page-cdp-1', frame_id=p['frame']['id'],
            loader_id=p['frame'].get('loaderId')))
        await self.cdp.send('Page.enable')
        self.cdp.on('Network.requestWillBeSent', self.network_request)
        self.cdp.on('Network.loadingFinished', self.network_finished)
        self.cdp.on('Network.dataReceived', self.network_data)
        self.cdp.on('Network.loadingFailed', self.network_failed)
        self.cdp.on('Network.responseReceived', self.network_response)
        await self.cdp.send('Network.enable')
        await self.cdp.send('Fetch.enable', {'patterns':[{'urlPattern':'*','requestStage':'Request'}]})
        self.event('controls_installed', transport='Chromium CDP Fetch.requestPaused')
        return page

    def diagnostic(self, name, **values):
        # At most 20,000 small lifecycle rows per run; no header/body fields.
        if self.diagnostic_events >= 20_000:
            self.stop('interception_evidence_limit')
            return
        self.diagnostic_events += 1
        self.event(name, **values)

    def page_closed(self, *_):
        self.diagnostic('interception_page_closed', session='page-cdp-1', cleanup=self.closing)
        if not self.closing:
            self.stop('browser_page_closed')

    def paused_event(self, owner, params):
        rid = params['requestId']
        if owner is not self.interception_owner:
            self.stop('interception_session_mismatch')
            self.diagnostic('interception_owner_rejected', request_id=rid)
            return
        if rid in self.interceptions:
            entry = self.interceptions[rid]
            self.diagnostic('interception_duplicate_event', **entry.details, state=entry.state)
            return
        if len(self.interceptions) >= 10_000:
            self.stop('interception_record_limit')
            return
        op = self.op
        details = {'operation_id':op.operation_id if op else None, 'request_id':rid,
                   'network_id':params.get('networkId'), 'resource_type':params['resourceType'],
                   'frame_id':params.get('frameId'), 'predecessor':params.get('redirectedRequestId'),
                   'session':'page-cdp-1'}
        self.interceptions[rid] = Interception(owner, op, details)
        self.spawn(self.paused(params))

    async def resolve_interception(self, entry, command):
        """One command attempt on the session that emitted this exact Fetch ID."""
        details = entry.details
        if (entry.owner is not self.interception_owner or entry.owner is not self.cdp or
                self.interceptions.get(details['request_id']) is not entry):
            self.stop('interception_session_mismatch')
            self.diagnostic('interception_owner_rejected', **details, command=command)
            return False
        if entry.state != 'pending':
            self.diagnostic('interception_resolution_skipped', **details, command=command,
                            classification=entry.classification, state=entry.state)
            return False
        entry.state, entry.command = 'resolving', command
        self.diagnostic('interception_command', **details, command=command,
                        classification=entry.classification, state=entry.state)
        args = {'requestId':details['request_id']}
        if command == 'Fetch.failRequest': args['errorReason'] = 'Aborted'
        try:
            # Diagnostics can synchronously stop collection (including a failed
            # evidence write). Check at the last boundary before releasing HTTP.
            if command == 'Fetch.continueRequest' and (self.stop_reason or self.closing):
                # No CDP command was sent: keep the held request eligible for
                # one safe abort through the same ownership/resolution guard.
                entry.state, entry.command = 'pending', None
                self.diagnostic('interception_continuation_prevented', **details,
                                classification=entry.classification, state=entry.state,
                                reason=self.stop_reason or 'browser_closing')
                await self.resolve_interception(entry, 'Fetch.failRequest')
                return False
            await entry.owner.send(command, args)
        except Exception as error:
            entry.state = 'error'
            failure = self.cancellations.get(details['network_id'])
            confirmed = bool(failure and failure['canceled'] is True and failure['observed'] >= entry.seen)
            # Native loadingFailed(canceled=true), same session/Network ID, and
            # specifically a stale Fetch ID. Teardown alone is NOT cancellation
            # proof. Unknown/intentional errors and lost page control still stop.
            supported = (str(error).endswith('Invalid InterceptionId.') and
                         f'Protocol error ({command}):' in str(error) and confirmed and
                         entry.classification == 'incidental' and not self.stop_reason and
                         not self.closing and self.page and not self.page.is_closed())
            self.diagnostic('interception_command_error', **details, command=command,
                            classification=entry.classification, state=entry.state,
                            error=type(error).__name__, detail=protocol_detail(error),
                            confirmed_canceled=confirmed, supported_incidental=bool(supported))
            if supported:
                entry.state = 'canceled'
                self.diagnostic('interception_incidental_canceled', **details, command=command,
                                classification=entry.classification, state=entry.state)
            else:
                if entry.operation and entry.classification != 'incidental':
                    entry.operation.error = entry.operation.error or 'interception_error:'+type(error).__name__
                self.stop('interception_error:'+type(error).__name__)
            # Never retry, or failRequest an ID after a failed continueRequest.
            return False
        entry.state = 'resolved'
        self.diagnostic('interception_command_complete', **details, command=command,
                        classification=entry.classification, state=entry.state)
        return True

    def network_request(self, params):
        frames = params.get('initiator', {}).get('stack', {}).get('callFrames', [])
        identity = {'network_id': params['requestId'], 'frame_id': params.get('frameId'),
                    'resource_type': params.get('type'), 'loader_id': params.get('loaderId'),
                    'initiator_type': params.get('initiator', {}).get('type'),
                    'initiator_script_id': frames[0].get('scriptId') if frames else None}
        self.network_requests[(params['requestId'], params['request']['url'])] = identity
        redirect = params.get('redirectResponse')
        # Chromium marks redirect completion on the Network redirect transition.
        # Installed Playwright crNetworkManager.js:255-261,395-402 derives
        # requestFinished from exactly this transition; its public event can be
        # deferred while another CDP session holds the next Fetch request.
        # Correlation with that intercepted next hop is mandatory below. Merely
        # receiving Network.responseReceived headers never sets this boundary.
        if redirect and self.op:
            predecessor = getattr(self.op, 'network_ids', {}).get(params['requestId'])
            if predecessor == redirect['url']:
                headers={k.lower():v for k,v in redirect.get('headers',{}).items() if k.lower() in HEADER_ALLOWLIST}
                self.event('redirect_response',url=predecessor,status=redirect['status'],headers=headers)
                reason=challenge_reason(redirect['status'],headers,'')
                if reason: self.stop(reason)
                self.op.redirect_transition = (params['requestId'], predecessor,
                                               params['request']['url'], time.monotonic())
        self.event('cdp_request_will_be_sent', request_id=params['requestId'],
                   url=params['request']['url'], redirect_from=redirect['url'] if redirect else None,
                   redirect_status=redirect['status'] if redirect else None,
                   browser_timestamp=params['timestamp'], **identity)

    def network_data(self, params):
        if self.op and self.op.kind == 'document' and params['requestId'] in getattr(self.op,'network_ids',{}):
            self.op.decoded_bytes = getattr(self.op,'decoded_bytes',0) + params['dataLength']
            if self.op.decoded_bytes > self.bounds.response_bytes:
                self.stop('document_response_limit')
                self.spawn(self.page.close())

    def network_finished(self, params):
        self.event('cdp_loading_finished', request_id=params['requestId'], browser_timestamp=params['timestamp'])
        # Direct CDP loadingFinished is completion, never responseReceived/headers.
        if self.op:
            url = getattr(self.op, 'network_ids', {}).get(params['requestId'])
            if url:
                self.op.finished[url] = time.monotonic()
                # The unconditional cdp_loading_finished event above is the
                # retained native observation. Do not emit a second annotation
                # whose presence depends on Python operation-cleanup timing.

    def network_operation(self, network_id):
        # Same admission IDs govern status, refusal, failure and completion.
        if self.op and network_id in getattr(self.op, 'network_ids', {}):
            return self.op
        return None

    def network_failed(self, params):
        failure = {'canceled':params.get('canceled', False), 'observed':time.monotonic(),
                   'error_text':protocol_detail(params.get('errorText', ''))}
        if len(self.cancellations) < 10_000:
            self.cancellations[params['requestId']] = failure
        else:
            self.stop('interception_record_limit')
        self.event('cdp_loading_failed', request_id=params['requestId'], session='page-cdp-1',
                   browser_timestamp=params.get('timestamp'), canceled=failure['canceled'],
                   error_text=failure['error_text'], blocked_reason=params.get('blockedReason'),
                   resource_type=params.get('type'))
        op = self.network_operation(params['requestId'])
        if op:
            op.error = op.error or 'network_error'
            # A read's own bounded stream cancellation can precede delivery of
            # its partial bytes/error. The operation lock prevents a next read;
            # settle that result (or its existing deadline) before stopping.
            if op.kind != 'read': self.stop(op.error)

    def network_response(self, params):
        response = params['response']
        headers = {k.lower(): v for k, v in response.get('headers', {}).items()
                   if k.lower() in HEADER_ALLOWLIST}
        self.event('cdp_response_headers', request_id=params['requestId'],
                   url=response['url'], status=response['status'])
        op = self.network_operation(params['requestId'])
        if op:
            op.status = int(response['status'])
            op.final_url = response['url']
            op.response_headers = headers
            reason = challenge_reason(op.status, headers, '')
            if reason:
                self.stop(reason)
                self.spawn(self.page.close())

    def request_seen(self, request):
        host = urlsplit(request.url).hostname
        self.resources[(host, request.resource_type)] += 1
        # Public Playwright Request exposes no CDP network ID. This is a resource
        # observation only; never infer coordinator identity from URL/frame here.
        self.event('browser_request', url=request.url, method=request.method, resource_type=request.resource_type)

    def request_finished(self, request):
        self.event('browser_request_finished', url=request.url, resource_type=request.resource_type)

    def request_failed(self, request):
        self.event('browser_request_failed', url=request.url, resource_type=request.resource_type)

    def response_seen(self, response):
        self.statuses[response.status] += 1
        headers = {k:v for k,v in response.headers.items() if k.lower() in HEADER_ALLOWLIST}
        self.event('browser_response', url=response.url, status=response.status, headers=headers,
                   resource_type=response.request.resource_type)

    async def request_identity(self, params, op):
        """Join the paused Fetch request to native Network evidence before dispatch."""
        network_id = params.get('networkId')
        url = params['request']['url']
        deadline = min(op.started + self.bounds.read_seconds,
                       self.started + self.bounds.seconds - self.bounds.finalization_reserve)
        while network_id and (network_id, url) not in self.network_requests:
            if self.stop_reason or time.monotonic() >= deadline:
                break
            await asyncio.sleep(.001)
        identity = self.network_requests.get((network_id, url))
        # Installed Chromium reports window.fetch as XHR in Fetch.requestPaused
        # and Fetch in Network.requestWillBeSent. Preserve both native types.
        compatible = identity and (identity['resource_type'] == params['resourceType'] or
                                   (params['resourceType'], identity['resource_type']) == ('XHR', 'Fetch'))
        if not compatible or identity['frame_id'] != params.get('frameId'):
            self.stop('ambiguous_request_identity')
            raise CollectionStopped(self.stop_reason)
        return identity

    async def admission_kind(self, params, op):
        parent = params.get('redirectedRequestId')
        if not op:
            return 'incidental', None
        resource = params['resourceType']
        frame = params.get('frameId')
        expected_resources = ('Document',) if op.kind == 'document' else ('Fetch', 'XHR')
        related = parent in getattr(op, 'fetch_ids', {})
        matches = params['request']['url'] == op.url and params['request']['method'] == op.method
        if not related and not matches:
            return 'incidental', None
        if resource not in expected_resources or frame != self.main_frame:
            if related:
                self.stop('ambiguous_redirect_identity')
                raise CollectionStopped(self.stop_reason)
            return 'incidental', None
        identity = await self.request_identity(params, op)
        if related:
            predecessor = op.fetch_ids[parent]
            if op.network_ids.get(identity['network_id']) != predecessor:
                self.stop('ambiguous_redirect_identity')
                raise CollectionStopped(self.stop_reason)
            return 'intentional', identity
        if op.kind == 'read':
            script = identity['initiator_script_id']
            if not script or not op.script_id:
                self.stop('ambiguous_request_identity')
                raise CollectionStopped(self.stop_reason)
            if script != op.script_id:
                return 'incidental', identity
            if identity['resource_type'] != 'Fetch':
                self.stop('ambiguous_request_identity')
                raise CollectionStopped(self.stop_reason)
        elif identity['initiator_type'] != 'other' or not identity['loader_id'] or identity['loader_id'] != identity['network_id']:
            self.stop('ambiguous_document_identity')
            raise CollectionStopped(self.stop_reason)
        return 'intentional', identity

    async def paused(self, params):
        rid = params['requestId']
        url = params['request']['url']
        method = params['request']['method']
        entry = self.interceptions[rid]
        op = entry.operation
        parent = params.get('redirectedRequestId')
        main = params['resourceType'] == 'Document' and params['frameId'] == self.main_frame
        classification = 'unresolved'
        details = entry.details
        try:
            classification, identity = await self.admission_kind(params, op)
            entry.classification = classification
            intended = classification == 'intentional'
            self.event('request_classified', url=url, method=method, classification=classification,
                       initiator_script_id=identity.get('initiator_script_id') if identity else None,
                       network_resource_type=identity.get('resource_type') if identity else None, **details)
            if self.loopback_only and urlsplit(url).scheme in ('http','https') and urlsplit(url).hostname != '127.0.0.1':
                # F-05/07 contain external public resource markup. Test egress
                # prevention is incidental; it does not claim document refusal.
                if not intended and not main:
                    self.event('incidental_prevented', url=url, reason='fixture_egress', **details)
                    await self.resolve_interception(entry, 'Fetch.failRequest')
                    return
            if self.stop_reason:
                raise CollectionStopped(self.stop_reason)
            if main and not intended:
                self.stop('unexpected_top_level_navigation')
                raise CollectionStopped(self.stop_reason)
            if not intended:
                await self.resolve_interception(entry, 'Fetch.continueRequest')
                return
            self.event('intentional_intercepted', url=url, **details)
            if op is not self.op or self.closing:
                self.stop('inactive_operation')
                raise CollectionStopped(self.stop_reason)
            if not self.scoped(url):
                op.error = 'redirect_out_of_scope'
                raise CollectionStopped(op.error)
            if not parent and op.initial_claimed:
                self.stop('ambiguous_intentional_request')
                raise CollectionStopped(self.stop_reason)
            if not parent:
                op.initial_claimed = True
            if parent:
                predecessor = op.fetch_ids[parent]
                if url in [op.url, *op.chain] or len(op.chain) >= 5:
                    op.error = 'redirect_loop'
                    raise CollectionStopped(op.error)
                # Correlate the browser redirect-completion transition to this
                # Fetch hop, by Network ID, predecessor URL and next URL.
                transition = getattr(op, 'redirect_transition', None)
                if transition and transition[:3] == (params.get('networkId'), predecessor, url):
                    op.finished[predecessor] = transition[3]
                    self.event('intentional_browser_completion', url=predecessor,
                               signal='Network.requestWillBeSent.redirectResponse transition',
                               network_id=params.get('networkId'), correlated_next_request_id=rid,
                               completed=transition[3])
                # Headers alone and server body completion are not the boundary.
                deadline = min(op.started + self.bounds.read_seconds, self.started+self.bounds.seconds-self.bounds.finalization_reserve)
                while predecessor not in op.finished:
                    if time.monotonic() >= deadline:
                        self.stop('redirect_completion_unobserved')
                        raise CollectionStopped(self.stop_reason)
                    await asyncio.sleep(0.01)
                completed = op.finished[predecessor]
                op.decoded_bytes = 0
                op.chain.append(url)
                self.event('redirect_correlated', predecessor_url=predecessor, url=url,
                           completed=completed, predecessor_request_id=parent, request_id=rid)
                await self.gap(completed)
            else:
                await self.gap(self.last_completion)
                op.fetch_ids = {}
                op.network_ids = {}
            self.check()
            if not self.scoped(url):
                raise CollectionStopped('redirect_out_of_scope')
            op.fetch_ids[rid] = url
            if params.get("networkId"):
                op.network_ids[params["networkId"]] = url
            self.dispatches += 1
            self.event('intentional_dispatch', url=url, method=method, kind=op.kind, ordinal=self.dispatches,
                       **details, preceding_completion=op.finished.get(op.fetch_ids.get(parent)) if parent else self.last_completion)
            await self.resolve_interception(entry, 'Fetch.continueRequest')
        except CollectionStopped as exc:
            if op and classification != 'incidental':
                op.error = op.error or str(exc)
            self.event(classification+'_prevented', url=url, reason=str(exc), **details)
            await self.resolve_interception(entry, 'Fetch.failRequest')
        except Exception as exc:
            self.stop('interception_error:'+type(exc).__name__)
            self.diagnostic('control_error', **details, classification=classification,
                            state=entry.state, error=type(exc).__name__, detail=protocol_detail(exc))
            await self.resolve_interception(entry, 'Fetch.failRequest')

    async def before_return_html(self, page, html, **kwargs):
        if self.op:
            reason=challenge_reason(self.op.status,self.op.response_headers,html)
            if reason:
                self.op.block_html = html[:self.bounds.response_bytes]
            if reason:
                self.stop(reason)
            if len(html.encode('utf-8')) > self.bounds.response_bytes:
                self.stop('rendered_html_limit')
        return page

    def timeout(self, ceiling):
        self.check()
        return min(ceiling, self.bounds.seconds-self.bounds.finalization_reserve-(time.monotonic()-self.started))

    async def after_goto(self, page, response=None, **kwargs):
        if response and self.op:
            self.op.status = response.status
            self.op.final_url = page.url
        return page

    async def capture(self, url):
        from smart_crawler.crawler import crawl_page
        async with self.lock:
            self.check()
            if self.bounds.document_slots is not None and self.documents >= self.bounds.document_slots:
                self.stop('document_limit')
                raise CollectionStopped(self.stop_reason)
            self.documents += 1
            self.op = self.new_operation(url,'GET','document')
            self.event('operation_start', url=url, operation_id=self.op.operation_id, deadline=time.monotonic()+self.timeout(self.bounds.document_seconds))
            try:
                record = await asyncio.wait_for(crawl_page(self.crawler,url,session_id=self.session_id),
                                                timeout=self.timeout(self.bounds.document_seconds))
                op = self.op
                reason = challenge_reason(op.status,op.response_headers,record.get('html'))
                if reason:
                    self.stop(reason)
                record.update(status=op.status, final_url=op.final_url, redirect_chain=list(op.chain),
                              block_html=getattr(op,'block_html',None))
                if self.stop_reason or op.error:
                    record.update(ok=False, fetched=False, error='blocked' if self.stop_reason and
                                  ('http_' in self.stop_reason or 'challenge' in self.stop_reason or 'block_document' in self.stop_reason)
                                  else op.error or self.stop_reason)
                return record
            except asyncio.TimeoutError:
                self.stop('document_deadline')
                raise CollectionStopped(self.stop_reason)
            finally:
                self.last_completion = time.monotonic()
                self.event('operation_complete', url=url, kind='document', operation_id=self.op.operation_id, error=self.op.error)
                self.op = None

    def new_operation(self, url, method, kind):
        self.operation_sequence += 1
        return Operation(url, method, kind, operation_id=f'op-{self.operation_sequence}')

    async def correlated_read(self, expression):
        await self.cdp.send('Runtime.enable')
        world = await self.cdp.send('Page.createIsolatedWorld', {
            'frameId': self.main_frame, 'worldName': 'abm-read-identity',
            'grantUniveralAccess': False})
        op = self.op
        op.context_id = world['executionContextId']
        compiled = await self.cdp.send('Runtime.compileScript', {
            'expression': expression, 'sourceURL': 'abm-coordinator-read',
            'persistScript': True, 'executionContextId': op.context_id})
        op.script_id = compiled.get('scriptId')
        if not op.script_id:
            self.stop('read_script_identity_unavailable')
            raise CollectionStopped(self.stop_reason)
        self.event('read_identity_bound', operation_id=op.operation_id, script_id=op.script_id,
                   context_id=op.context_id, frame_id=self.main_frame,
                   execution_world='same-frame isolated world', universal_access=False)
        remote = await self.run_read_script(op)
        if not getattr(op, 'network_ids', {}) or self.stop_reason:
            raise CollectionStopped(self.stop_reason or 'read_request_uncorrelated')
        if 'exceptionDetails' in remote or 'value' not in remote.get('result', {}):
            raise CollectionStopped('browser_read_failed')
        return remote['result']['value']

    async def run_read_script(self, op):
        # The native initiator's top scriptId must match the compiled script, not
        # its spoofable sourceURL. Nothing is added to HTTP headers or URLs.
        return await self.cdp.send('Runtime.runScript', {
            'scriptId': op.script_id, 'executionContextId': op.context_id,
            'awaitPromise': True, 'returnByValue': True})

    async def read(self, url, method='GET'):
        if method not in ('GET','HEAD'):
            raise ValueError('intentional reads are GET or HEAD')
        async with self.lock:
            self.check()
            if self.page is None or self.page.is_closed():
                raise CollectionStopped('browser_session_not_bootstrapped')
            if not self.scoped(url):
                raise CollectionStopped('off_scope')
            self.op = self.new_operation(url,method,'read')
            self.event('operation_start', url=url, operation_id=self.op.operation_id, deadline=time.monotonic()+self.timeout(self.bounds.read_seconds))
            try:
                read_timeout=self.timeout(self.bounds.read_seconds)
                args = {'url':url,'method':method,'cap':self.bounds.response_bytes,
                        'timeout':max(1,int(read_timeout*1000)-100)}
                expression = '(' + '''async ({url,method,cap,timeout}) => {
                    const ctl = new AbortController(); const timer=setTimeout(()=>ctl.abort(),timeout);
                    let chunks=[], count=0;
                    try {
                        const r=await window.fetch(url,{method,redirect:'follow',signal:ctl.signal});
                        if(r.body) { const reader=r.body.getReader();
                            while(true) { const {done,value}=await reader.read(); if(done) break;
                                const room=cap-count; chunks.push(Array.from(value.slice(0,room)));
                                count+=Math.min(value.length,room);
                                if(value.length>room) { await reader.cancel(); ctl.abort();
                                    return {status:r.status,url:r.url,chunks,bytes:count,incomplete:true,error:'response_limit'}; }
                            }
                        }
                        return {status:r.status,url:r.url,chunks,bytes:count,incomplete:false};
                    } catch(e) { return {chunks,bytes:count,incomplete:true,error:e.name}; }
                    finally { clearTimeout(timer); }
                }''' + ')(' + json.dumps(args) + ')'
                result = await asyncio.wait_for(self.correlated_read(expression), read_timeout)
                body = bytes(x for chunk in result.pop('chunks') for x in chunk)
                result.update(body=body,sha256=hashlib.sha256(body).hexdigest(),headers=dict(self.op.response_headers),
                              redirect_chain=list(self.op.chain),transport='Chromium same-page window.fetch / Response.body.getReader',
                              boundary='browser-decoded entity bytes',error=result.get('error') or self.op.error)
                if result.get('error'):
                    result['incomplete'] = True
                reason = challenge_reason(result.get('status'), result['headers'], body.decode('utf-8',errors='replace'))
                if reason: self.stop(reason)
                if result.get('incomplete'): self.stop(result.get('error') or 'incomplete_response')
                return result
            except Exception as exc:
                error=self.op.error or ('read_deadline' if isinstance(exc,asyncio.TimeoutError) else 'browser_read_failed')
                self.stop(error)
                return {'body':b'', 'bytes':0,'sha256':hashlib.sha256(b'').hexdigest(),
                        'status':self.op.status,'url':self.op.final_url,'headers':dict(self.op.response_headers),
                        'redirect_chain':list(self.op.chain),'incomplete':True,'error':error,
                        'transport':'Chromium same-page window.fetch / Response.body.getReader',
                        'boundary':'browser-decoded entity bytes',
                        'evidence_gap':'browser read interrupted before available chunks returned'}
            finally:
                self.last_completion = time.monotonic()
                self.event('operation_complete', url=url, kind='read', operation_id=self.op.operation_id, error=self.op.error)
                self.op = None
