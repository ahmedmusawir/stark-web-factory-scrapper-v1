"""Two-arm diagnostic instrumentation only; no source/dependency edits."""
import asyncio,hashlib,io,json,os,sys,threading,time
from pathlib import Path
sys.path.insert(0,str(Path.cwd()));sys.path.insert(0,str(Path.cwd()/'tests'))
import fixture_server as fixtures
from smart_crawler.browser_session import BrowserSession,Bounds
from http.server import ThreadingHTTPServer

ARM=sys.argv[1];OUT=Path(sys.argv[2]);OUT.mkdir(exist_ok=False)
lock=threading.Lock();trace=(OUT/'observations.jsonl').open('x');sequence=0;trace_bytes=0

def emit(event,**values):
    global sequence,trace_bytes
    with lock:
        sequence+=1;row={'sequence':sequence,'monotonic':time.monotonic(),'event':event,**values}
        data=json.dumps(row,separators=(',',':'))+'\n';trace_bytes+=len(data.encode())
        if trace_bytes>2_000_000 or sequence>10000:raise BufferError('diagnostic_trace_ceiling')
        trace.write(data);trace.flush()
    return row

class RecvRaw(io.RawIOBase):
    def __init__(self,sock,conn):self.sock=sock;self.conn=conn
    def readable(self):return True
    def readinto(self,buffer):
        started=time.monotonic();n=self.sock.recv_into(buffer)
        data=bytes(memoryview(buffer)[:n]);line=data.split(b'\r\n',1)[0]
        request_line=line.decode('ascii','replace') if line.startswith((b'GET ',b'POST ',b'HEAD ',b'OPTIONS ')) else None
        emit('server_socket_read_return',connection_id=self.conn,read_started=started,bytes=n,
             sha256=hashlib.sha256(data).hexdigest(),request_line=request_line)
        return n

class SocketView:
    def __init__(self,sock,conn):self.sock=sock;self.conn=conn
    def __getattr__(self,name):return getattr(self.sock,name)
    def makefile(self,mode='r',buffering=None,**kwargs):
        if mode=='rb':return io.BufferedReader(RecvRaw(self.sock,self.conn),buffering if buffering and buffering>0 else io.DEFAULT_BUFFER_SIZE)
        return self.sock.makefile(mode,buffering if buffering is not None else -1,**kwargs)

class ObservedServer(ThreadingHTTPServer):
    def __init__(self,address,handler,*args,**kwargs):
        self.connections={};self.next_conn=0
        class ObservedHandler(handler):
            def __init__(h,request,client_address,server):
                h.observed_conn=server.connections[request.fileno()]
                super().__init__(SocketView(request,h.observed_conn),client_address,server)
            def emit(h,event,**values):
                emit('server_handler_'+event,connection_id=h.observed_conn,path=h.path,method=h.command,**values)
                return super().emit(event,**values)
        super().__init__(address,ObservedHandler,*args,**kwargs)
    def get_request(self):
        sock,addr=super().get_request();self.next_conn+=1;conn=f'connection-{self.next_conn}'
        self.connections[sock.fileno()]=conn;emit('server_connection_accepted',connection_id=conn,peer_host=addr[0],peer_port=addr[1]);return sock,addr

class RouteView:
    def __init__(self,route):self.route=route
    def __getattr__(self,name):return getattr(self.route,name)
    async def continue_(self,*args,**kwargs):
        req=self.route.request;emit('context_route_continue_attempt',route_guid=self.route._impl_obj._guid,request_guid=req._impl_obj._guid,url=req.url,method=req.method)
        try:
            value=await self.route.continue_(*args,**kwargs);emit('context_route_continue_return',route_guid=self.route._impl_obj._guid);return value
        except Exception as exc:emit('context_route_continue_error',route_guid=self.route._impl_obj._guid,error=type(exc).__name__,detail=str(exc)[:1000]);raise
    async def abort(self,*args,**kwargs):
        req=self.route.request;emit('context_route_abort_attempt',route_guid=self.route._impl_obj._guid,request_guid=req._impl_obj._guid,url=req.url,method=req.method)
        try:
            value=await self.route.abort(*args,**kwargs);emit('context_route_abort_return',route_guid=self.route._impl_obj._guid);return value
        except Exception as exc:emit('context_route_abort_error',route_guid=self.route._impl_obj._guid,error=type(exc).__name__,detail=str(exc)[:1000]);raise

class ObservedSession(BrowserSession):
    async def created(self,page,context,**kwargs):
        original_route=context.route
        async def register(pattern,handler,**options):
            async def observed(route):
                req=route.request
                emit('context_guard_invocation',route_guid=route._impl_obj._guid,request_guid=req._impl_obj._guid,url=req.url,method=req.method,stop_reason=self.stop_reason,closing=self.closing)
                try:return await handler(RouteView(route))
                finally:emit('context_guard_return',route_guid=route._impl_obj._guid,stop_reason=self.stop_reason)
            return await original_route(pattern,observed,**options)
        context.route=register
        original_close=page.close
        async def close(*args,**options):
            emit('page_close_invocation',stop_reason=self.stop_reason,closing=self.closing)
            try:
                result=await original_close(*args,**options);emit('page_close_return',is_closed=page.is_closed());return result
            except Exception as exc:emit('page_close_error',error=type(exc).__name__,detail=str(exc)[:1000]);raise
        page.close=close
        result=await super().created(page,context,**kwargs)
        original_send=self.cdp.send
        async def send(method,params=None):
            relevant=method in ['Fetch.continueRequest','Fetch.failRequest','Fetch.disable','Target.detachFromTarget','Page.close','Target.closeTarget']
            if relevant:emit('python_cdp_send_attempt',method=method,params=params,owner_guid=self.cdp._impl_obj._guid)
            try:
                result=await original_send(method,params)
                if relevant:emit('python_cdp_send_return',method=method,request_id=(params or {}).get('requestId'),owner_guid=self.cdp._impl_obj._guid)
                return result
            except Exception as exc:
                if relevant:emit('python_cdp_send_error',method=method,request_id=(params or {}).get('requestId'),error=type(exc).__name__,detail=str(exc)[:1000],owner_guid=self.cdp._impl_obj._guid)
                raise
        self.cdp.send=send
        emit('custom_session_python_identity',owner_guid=self.cdp._impl_obj._guid,main_frame=self.main_frame)
        return result
    def paused_event(self,owner,params):
        emit('native_fetch_pause_observed',request_id=params['requestId'],network_id=params.get('networkId'),frame_id=params.get('frameId'),resource_type=params['resourceType'],native_predecessor=params.get('redirectedRequestId'),url=params['request']['url'],method=params['request']['method'],owner_guid=owner._impl_obj._guid)
        super().paused_event(owner,params)
        entry=self.interceptions.get(params['requestId'])
        emit('interception_registration_observed',registered=entry is not None,details=entry.details if entry else None,state=entry.state if entry else None)
    async def paused(self,params):
        if params['request']['url'].endswith('/cleanup-held'):
            self.held_params=params;emit('fixture_hold_enter',request_id=params['requestId'],network_id=params.get('networkId'),operation_id=self.op.operation_id if self.op else None)
            self.held.set();await self.release.wait();emit('fixture_hold_exit',request_id=params['requestId'])
        await super().paused(params)
    def page_closed(self,*args):
        emit('page_closed_observed',closing=self.closing,active_operation=self.op.operation_id if self.op else None)
        super().page_closed(*args)
    async def __aexit__(self,*args):
        emit('cleanup_invocation',stop_reason=self.stop_reason)
        try:return await super().__aexit__(*args)
        finally:emit('cleanup_return',stop_reason=self.stop_reason,pending_tasks=len(self.tasks))

async def main():
    fixtures.ThreadingHTTPServer=ObservedServer
    result={'arm':ARM,'read_result':None,'control_received_while_held':None,'errors':[]}
    with fixtures.fixture_server() as (origin,timeline):
        s=ObservedSession(origin,bounds=Bounds(operations=3,seconds=60,document_slots=1),runtime_dir=OUT/'runtime',loopback_only=True,log=lambda row:emit('controller',row=row))
        s.held,s.release=asyncio.Event(),asyncio.Event();task=None
        try:
            async with s:
                emit('bootstrap_invocation',url=origin+'/background');bootstrap=await s.capture(origin+'/background');emit('bootstrap_return',ok=bootstrap['ok'],status=bootstrap['status'],html_bytes=len(bootstrap.get('html','').encode()))
                if not bootstrap['ok']:raise RuntimeError('bootstrap failed; no read attempted')
                task=asyncio.create_task(s.read(origin+'/cleanup-held'));await asyncio.wait_for(s.held.wait(),10)
                emit('hold_interval_start',seconds=1.0)
                await asyncio.sleep(1.0)
                received=any(x['event']=='request_received' and x['path']=='/cleanup-held' for x in timeline)
                result['control_received_while_held']=received;emit('hold_interval_end',received_while_held=received)
                if ARM=='B':await s.page.close()
                emit('fixture_release_invocation');s.release.set();read=await asyncio.wait_for(task,30)
                result['read_result']={k:v for k,v in read.items() if k!='body'};result['read_result']['body_bytes']=len(read['body']);result['read_result']['sha256']=hashlib.sha256(read['body']).hexdigest();result['read_result']['matches_fixture_article']=read['body']==fixtures.ARTICLE
                emit('read_return',incomplete=read.get('incomplete'),error=read.get('error'),body_bytes=len(read['body']))
                await asyncio.gather(*list(s.tasks),return_exceptions=True)
        except Exception as exc:
            result['errors'].append({'type':type(exc).__name__,'detail':str(exc)[:1000]});emit('arm_error',error=type(exc).__name__,detail=str(exc)[:1000])
        finally:
            s.release.set()
            if task and not task.done():task.cancel()
            result.update(dispatches=s.dispatches,stop_reason=s.stop_reason,runtime=s.runtime,server_events=timeline,held_params={k:v for k,v in getattr(s,'held_params',{}).items() if k!='request'})
    result['clock']={'name':'time.monotonic','info':str(time.get_clock_info('monotonic'))};(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');emit('arm_finished',dispatches=result['dispatches'],stop_reason=result['stop_reason']);trace.close()

asyncio.run(main())
