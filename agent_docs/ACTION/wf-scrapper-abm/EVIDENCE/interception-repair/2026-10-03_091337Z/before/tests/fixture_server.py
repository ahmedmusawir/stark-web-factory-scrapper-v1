"""Loopback-only deterministic server; request/server event timeline is evidence."""
import gzip
import json
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ARTICLE = ('<!doctype html><html><head><title>Fixture article</title></head><body><h1>Fixture article</h1>'
           '<p>' + 'A substantive local article with public facts and useful information. '*50 + '</p></body></html>').encode()
ENTITY = b'[ {"id": 1, "link": "http://127.0.0.1/article/", "content": {"rendered": ""}, "unknown": [9007199254740993, "\\u00e9"]} ]\r\n'


@contextmanager
def fixture_server(*, mode=None, port=0, variant="complete"):
    timeline=[]
    identity_reads={}
    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.1'
        def log_message(self,*args):
            pass
        def emit(self,event,**kw):
            timeline.append({'event':event,'path':self.path,'method':self.command,'monotonic':time.monotonic(),**kw})
        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length','0')))
            self.respond(204,b'',{})
        def do_HEAD(self):
            if self.path=='/read-identity':
                return self.identity_read()
            if mode=='pipeline' and self.path=='/image.png':
                return self.respond(200,b'',{'Content-Type':'image/png','Content-Length':str(len(fixture_png()))})
            if self.path=='/redirect':
                return self.respond(302,b'',{'Location':'/image.png'})
            if self.path=='/refusal':
                return self.respond(429,b'',{'Retry-After':'42'})
            self.respond(200,b'',{'Content-Type':'image/png','Content-Length':'4096'})
        def do_GET(self):
            if self.path=='/read-identity':
                return self.identity_read()
            if self.path.startswith('/identity/'):
                kind=self.path.rsplit('/',1)[-1]
                dest=self.headers.get('Sec-Fetch-Dest')
                if dest=='style':
                    return self.respond(200,b'body { color: black; }',{'Content-Type':'text/css'})
                if dest=='image':
                    return self.respond(200,fixture_png(),{'Content-Type':'image/png'})
                if dest!='document':
                    return self.respond(200,b'ordinary background response',{'Content-Type':'text/plain'})
                scripts={
                    'stylesheet': "let r=document.createElement('link');r.rel='stylesheet';r.href=location.href;document.head.append(r);",
                    'image': "let r=new Image();r.src=location.href;document.body.append(r);",
                    'fetch': "fetch(location.href);",
                    'xhr': "let r=new XMLHttpRequest();r.open('GET',location.href);r.send();",
                }
                body=ARTICLE.replace(b'</body>',('<script>'+scripts.get(kind,'')+'</script></body>').encode())
                return self.respond(200,body,{'Content-Type':'text/html'})
            if self.path.startswith('/hang'):
                return self.respond(200,ARTICLE,{'Content-Type':'text/html'},delay=45)
            if self.path.startswith('/persistence-cap'):
                body=b'<!doctype html><html><title>Large public fixture</title><body><p>'+b'word '*240000+b'</p></body></html>'
                return self.respond(200,body,{'Content-Type':'text/html'})
            if self.path.startswith('/soft-challenge'):
                return self.respond(200,b'<html><title>Access Denied</title><body>Access to this page has been denied</body></html>',{'Content-Type':'text/html'})
            if mode=='pipeline':
                origin=f'http://127.0.0.1:{self.server.server_port}'
                inputs=wp_inputs(origin,variant)
                if origin+self.path in inputs:
                    r=inputs[origin+self.path]
                    return self.respond(r['status'],r['body'],r['headers'])
                if self.path=='/robots.txt':
                    return self.respond(200,('User-agent: *\nDisallow: /private/\nSitemap: '+origin+'/sitemap.xml\n').encode(),{'Content-Type':'text/plain'})
                if self.path=='/sitemap.xml':
                    return self.respond(200,('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>'+origin+'/pages.xml</loc></sitemap><sitemap><loc>'+origin+'/aliases.xml</loc></sitemap></sitemapindex>').encode(),{'Content-Type':'application/xml'})
                if self.path in ('/pages.xml','/aliases.xml'):
                    paths=HEALTHY_PATHS+(['/missing/'] if variant=='base' else []) if self.path=='/pages.xml' else ['/about/?utm_source=alias']
                    return self.respond(200,('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+origin+x+'</loc></url>' for x in paths)+'</urlset>').encode(),{'Content-Type':'application/xml'})
                if self.path in HEALTHY_PATHS:
                    return self.respond(200,complete_html(origin,self.path),{'Content-Type':'text/html'})
                if self.path=='/image.png':
                    return self.respond(200,fixture_png(),{'Content-Type':'image/png'})
                return self.respond(404,b'<html><body>Not found.</body></html>',{'Content-Type':'text/html'})
            if self.path=='/offscope-resource':
                self.respond(200,ARTICLE.replace(b'</body>',b'<img src="https://outside.invalid/image.png"></body>'),{'Content-Type':'text/html'})
            elif self.path=='/popup-source':
                self.respond(200,ARTICLE.replace(b'</body>',b"<script>window.open('/popup','_blank')</script></body>"),{'Content-Type':'text/html'})
            elif self.path=='/worker-source':
                self.respond(200,ARTICLE.replace(b'</body>',b"<script>navigator.serviceWorker.register('/worker.js')</script></body>"),{'Content-Type':'text/html'})
            elif self.path=='/worker.js':
                self.respond(200,b"self.addEventListener('fetch',function(e){});",{'Content-Type':'application/javascript'})
            elif self.path.startswith('/chain/'):
                n=int(self.path.split('/')[2]); dest=f'/chain/{n-1}' if n else '/article/'
                self.respond(302,b'chain',{'Location':dest})
            elif self.path=='/loop':
                self.respond(302,b'loop',{'Location':'/loop'})
            elif self.path=='/challenge':
                self.respond(200,b'<title>Access Denied</title><body>Access to this page has been denied</body>',{'Content-Type':'text/html','cf-mitigated':'challenge'})
            elif self.path=='/soft-challenge':
                self.respond(200,b'<html><title>Access Denied</title><body>Access to this page has been denied</body></html>',{'Content-Type':'text/html'})
            elif self.path=='/forbidden':
                self.respond(403,b'Forbidden',{'Retry-After':'7'})
            elif self.path=='/slow':
                self.respond(200,b'slow completed body',{'Content-Type':'text/plain'},delay=3.0)
            elif self.path.startswith('/redirect'):
                self.respond(302,b'redirect body delayed',{'Location':'/article/'},delay=2.0)
            elif self.path.startswith('/denied-redirect'):
                self.respond(302,b'out of scope',{'Location':'http://outside.invalid/forbidden'})
            elif self.path.startswith('/data'):
                self.respond(200,gzip.compress(ENTITY,mtime=0),{'Content-Type':'application/json','Content-Encoding':'gzip'})
            elif self.path.startswith('/background'):
                body=ARTICLE.replace(b'</body>',b"<script>fetch('/beacon',{method:'POST',body:'public telemetry'});fetch('/incidental');</script></body>")
                self.respond(200,body,{'Content-Type':'text/html'})
            elif self.path.startswith('/incidental'):
                self.respond(403,b'incidental failure',{})
            elif self.path.startswith('/refusal'):
                self.respond(429,b'too many requests',{'Retry-After':'42'})
            elif self.path.startswith('/large'):
                self.respond(200,b'a'*4096,{})
            else:
                self.respond(200,ARTICLE,{'Content-Type':'text/html'})
        def identity_read(self):
            count=identity_reads.get(self.command,0)+1;identity_reads[self.command]=count
            # Distinguish page-generated refusal from coordinator success using
            # fixture order, never an identification header/query on the request.
            self.respond(403 if count==1 else 200,b'' if self.command=='HEAD' else b'coordinator response',
                         {'Content-Type':'text/plain'})
        def respond(self,status,body,headers,delay=0):
            self.emit('request_received',user_agent=self.headers.get('User-Agent'),resource_destination=self.headers.get('Sec-Fetch-Dest'))
            self.send_response(status)
            if 'Content-Length' not in headers: self.send_header('Content-Length',str(len(body)))
            for k,v in headers.items(): self.send_header(k,v)
            self.end_headers();self.wfile.flush();self.emit('headers_sent',status=status)
            if delay: time.sleep(delay)
            try:
                if self.command!='HEAD': self.wfile.write(body);self.wfile.flush()
                self.emit('body_sent',bytes=len(body))
            except (BrokenPipeError, ConnectionResetError): self.emit('browser_closed_connection')
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.daemon_threads=True
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try: yield f'http://127.0.0.1:{server.server_port}', timeline
    finally: server.shutdown();server.server_close();thread.join(timeout=2)


HEALTHY_PATHS = ['/', '/about/', '/services/', '/contact/', '/article/', '/rendered-only/']


def wp_inputs(origin, variant='complete'):
    """Authored F-02 facts, independent of product serializers or captured output."""
    pages=[]
    for i in range(200):
        path=HEALTHY_PATHS[i] if i<6 else f'/pagination-only-{i}/'
        obj={'id':100+i,'type':'page','link':origin+path,'slug':path.strip('/') or 'home',
             'status':'publish','date':'2026-01-01T00:00:00','modified':'2026-01-01T00:00:00',
             'title':{'rendered':f'Page {i}'},'content':{'rendered':'<p>REST evidence</p>' if i!=5 else ''},
             'excerpt':{'rendered':'Excerpt'},'author':1,'featured_media':500,'categories':[1],'tags':[2],
             'unknown':{'large':900719925474099312345,'fraction':'EXACT_NUMBER','source_path':'/home/source/value',
                        'quoted_advice':'recommend <script>untouched()</script>'}}
        if i<3:
            obj['yoast_head_json']={'title':f'Page {i}','canonical':origin+path,'schema':{'@graph':[{'@type':'WebPage'}]},'unknown_seo':True}
            obj['yoast_head']='<title>SEO source</title>'
        if i==4: obj['yoast_head_json']=None;obj['yoast_head']=None
        pages.append(obj)
    posts=[{'id':900,'type':'post','link':origin+'/unrouted-post/','title':{'rendered':'Post'},'content':{'rendered':'Public article'}}]
    if variant=='ambiguous':posts[0]['link']=origin+'/article/'
    if variant=='unmapped':pages[2]['link']=origin+'/other-service/'
    if variant=='optional_absences':pages[0].pop('content');pages[1]['content']=None
    if variant=='malformed_identity':pages[0]['id']='100'
    if variant=='malformed_container':pages[0]['content']='not an object'
    if variant=='partial':pages=[p for p in pages if p['id']!=102]
    values={'pages':pages,'posts':posts,'media':[{'id':500,'source_url':origin+'/image.png','media_type':'image','mime_type':'image/png',
              'media_details':{'width':20,'height':10},'alt_text':'Fixture image','title':{'rendered':'Image'},'caption':{'rendered':''}}],
            'categories':[{'id':1,'name':'Category','link':origin+'/category/news/'}],
            'tags':[{'id':2,'name':'Tag','link':origin+'/tag/topic/'}]}
    responses={}
    for kind,objects in values.items():
        total=len(objects);total_pages=(total+99)//100
        for page in range(1,total_pages+1):
            # Exact literal number is deliberate input, not generated from product output.
            body=(json.dumps(objects[(page-1)*100:page*100],ensure_ascii=False,indent=1)+'\r\n').replace('"EXACT_NUMBER"','0.12345678901234567890123456789').encode()
            responses[f'{origin}/wp-json/wp/v2/{kind}?per_page=100&page={page}']={
                'status':200,'body':body,'headers':{'content-type':'application/json','x-wp-total':str(total),'x-wp-totalpages':str(total_pages)},
                'transport':'fixture bytes adapter','boundary':'declared fixture entity bytes','incomplete':False}
    responses[f'{origin}/wp-json/wp/v2/users?per_page=100&page=1']={'status':401,'body':b'{"code":"public_users_unavailable"}',
        'headers':{'content-type':'application/json'},'transport':'fixture bytes adapter','boundary':'declared fixture entity bytes','incomplete':False}
    return responses


def complete_html(origin,path):
    """F-09/F-07/F-08 deterministic source; no generated-output acceptance."""
    position=HEALTHY_PATHS.index(path)
    # Exactly 400 body words on rendered-only route; headline/title omitted there
    # from the counted body paragraph assertion to avoid invented completeness.
    words=' '.join(['evidence']*400)
    forms=''
    if path=='/contact/':
        forms=('<form action="/contact/" method="post"><input name="name"><button type="submit">Send</button></form>'
               '<form action="/search/" method="get"><input name="q"></form><a href="mailto:hello@example.invalid">Email</a>'
               '<iframe src="https://maps.example.invalid/embed"></iframe>'
               '<script src="https://widgets.example.invalid/widget.js" data-widget="contact"></script>')
    return ('<!DOCTYPE html><html><head><title>Page '+str(position)+'</title>'
        '<meta name="viewport" content="width=device-width"><link rel="canonical" href="'+origin+path+'">'
        '<style>body {color:#123456;font-family:Arial} h1 {font-size:32px}</style></head>'
        '<body><header class="site-header"><nav class="primary">Navigation</nav></header><main><h1>Page '+str(position)+'</h1>'
        '<article><p>'+words+'</p></article><img src="/image.png" alt="Fixture image">'+forms+
        '</main><footer class="site-footer">Footer</footer></body></html>').encode()


def fixture_png():
    import struct,zlib
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',20,10,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\x00'+b'\x44\x66\x88'*20)*10))+chunk(b'IEND',b'')
