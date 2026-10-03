"""Single Crawl4AI-owned Chromium session for intentional collection.

No alternate HTTP client. Crawl4AI hooks provide all browser objects. Events for
incidental resources are separate from intentional admission/pacing evidence.
"""
import asyncio
import hashlib
from pathlib import Path
import platform
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
    chain: list = field(default_factory=list)
    requests: dict = field(default_factory=dict)
    finished: dict = field(default_factory=dict)
    response_headers: dict = field(default_factory=dict)
    status: int | None = None
    final_url: str | None = None
    error: str | None = None
    started: float = field(default_factory=time.monotonic)


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
        await self.crawler.__aexit__(*exc)
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
        self.cdp.on('Fetch.requestPaused', lambda params:self.spawn(self.paused(params)))
        self.cdp.on('Network.requestWillBeSent', self.network_request)
        self.cdp.on('Network.loadingFinished', self.network_finished)
        self.cdp.on('Network.dataReceived', self.network_data)
        self.cdp.on('Network.loadingFailed', lambda p:self.event('cdp_loading_failed', request_id=p['requestId']))
        self.cdp.on('Network.responseReceived', lambda p:self.event('cdp_response_headers',
            request_id=p['requestId'],url=p['response']['url'],status=p['response']['status']))
        await self.cdp.send('Network.enable')
        await self.cdp.send('Fetch.enable', {'patterns':[{'urlPattern':'*','requestStage':'Request'}]})
        self.event('controls_installed', transport='Chromium CDP Fetch.requestPaused')
        return page

    def network_request(self, params):
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
                   browser_timestamp=params['timestamp'])

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

    def relevant(self, request):
        if not self.op:
            return False
        try:
            frame = request.frame
        except Exception:
            return False
        if frame != self.page.main_frame:
            return False
        return request.url in [self.op.url, *self.op.chain] and request.method == self.op.method and (
            request.is_navigation_request() if self.op.kind == 'document' else request.resource_type in ('fetch','xhr'))

    def request_seen(self, request):
        host = urlsplit(request.url).hostname
        self.resources[(host, request.resource_type)] += 1
        self.event('browser_request', url=request.url, method=request.method, resource_type=request.resource_type)
        if self.relevant(request):
            old = self.op.requests.get(request.url)
            if old is not None and old is not request:
                self.stop('ambiguous_intentional_request')
            self.op.requests[request.url] = request

    def request_finished(self, request):
        self.event('browser_request_finished', url=request.url, resource_type=request.resource_type)
        if self.op and self.op.requests.get(request.url) is request:
            self.op.finished[request.url] = time.monotonic()
            # browser_request_finished above is unconditional. Redirect proof
            # emits its explicit correlated boundary in paused(), not here.

    def request_failed(self, request):
        self.event('browser_request_failed', url=request.url, resource_type=request.resource_type)
        if self.op and self.op.requests.get(request.url) is request:
            self.op.error = self.op.error or 'network_error'

    def response_seen(self, response):
        self.statuses[response.status] += 1
        headers = {k:v for k,v in response.headers.items() if k.lower() in HEADER_ALLOWLIST}
        self.event('browser_response', url=response.url, status=response.status, headers=headers,
                   resource_type=response.request.resource_type)
        if self.relevant(response.request):
            self.op.status = response.status
            self.op.final_url = response.url
            self.op.response_headers = headers
            reason = challenge_reason(response.status, headers, '')
            if reason:
                self.stop(reason)
                self.spawn(self.page.close())

    async def paused(self, params):
        rid = params['requestId']
        url = params['request']['url']
        method = params['request']['method']
        op = self.op
        parent = params.get('redirectedRequestId')
        main = params['resourceType'] == 'Document' and params['frameId'] == self.main_frame
        intended = bool(op and ((url == op.url and method == op.method and not op.chain) or
                                 parent in getattr(op,'fetch_ids',{})))
        try:
            if self.loopback_only and urlsplit(url).scheme in ('http','https') and urlsplit(url).hostname != '127.0.0.1':
                # F-05/07 contain external public resource markup. Test egress
                # prevention is incidental; it does not claim document refusal.
                if not intended and not main:
                    self.event('fixture_resource_prevented', url=url, request_id=rid)
                    await self.cdp.send('Fetch.failRequest', {'requestId':rid,'errorReason':'Aborted'})
                    return
            if self.stop_reason:
                raise CollectionStopped(self.stop_reason)
            if main and not intended:
                self.stop('unexpected_top_level_navigation')
                raise CollectionStopped(self.stop_reason)
            if not intended:
                await self.cdp.send('Fetch.continueRequest', {'requestId':rid})
                return
            self.event('intentional_intercepted', url=url, request_id=rid, predecessor=parent)
            if not self.scoped(url):
                op.error = 'redirect_out_of_scope'
                raise CollectionStopped(op.error)
            if not parent and getattr(op,'fetch_ids',{}):
                self.stop('ambiguous_intentional_request')
                raise CollectionStopped(self.stop_reason)
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
                       request_id=rid, preceding_completion=op.finished.get(op.fetch_ids.get(parent)) if parent else self.last_completion)
            await self.cdp.send('Fetch.continueRequest', {'requestId':rid})
        except CollectionStopped as exc:
            if op:
                op.error = op.error or str(exc)
            self.event('intentional_prevented', url=url, reason=str(exc))
            await self.cdp.send('Fetch.failRequest', {'requestId':rid,'errorReason':'Aborted'})
        except Exception as exc:
            self.stop('interception_error:'+type(exc).__name__)
            self.event('control_error', error=type(exc).__name__, detail=str(exc))
            try:
                await self.cdp.send('Fetch.failRequest', {'requestId':rid,'errorReason':'Aborted'})
            except Exception:
                pass

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
            self.op = Operation(url,'GET','document')
            self.event('operation_start', url=url, deadline=time.monotonic()+self.timeout(self.bounds.document_seconds))
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
                self.event('operation_complete', url=url, kind='document', error=self.op.error)
                self.op = None

    async def read(self, url, method='GET'):
        if method not in ('GET','HEAD'):
            raise ValueError('intentional reads are GET or HEAD')
        async with self.lock:
            self.check()
            if self.page is None or self.page.is_closed():
                raise CollectionStopped('browser_session_not_bootstrapped')
            if not self.scoped(url):
                raise CollectionStopped('off_scope')
            self.op = Operation(url,method,'read')
            self.event('operation_start', url=url, deadline=time.monotonic()+self.timeout(self.bounds.read_seconds))
            try:
                read_timeout=self.timeout(self.bounds.read_seconds)
                result = await asyncio.wait_for(self.page.evaluate('''async ({url,method,cap,timeout}) => {
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
                }''', {'url':url,'method':method,'cap':self.bounds.response_bytes,
                        'timeout':max(1,int(read_timeout*1000)-100)}), read_timeout)
                body = bytes(x for chunk in result.pop('chunks') for x in chunk)
                result.update(body=body,sha256=hashlib.sha256(body).hexdigest(),headers=dict(self.op.response_headers),
                              redirect_chain=list(self.op.chain),transport='Chromium same-page window.fetch / Response.body.getReader',
                              boundary='browser-decoded entity bytes',error=self.op.error or result.get('error'))
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
                self.event('operation_complete', url=url, kind='read', error=self.op.error)
                self.op = None
