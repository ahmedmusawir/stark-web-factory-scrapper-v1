"""DECIDE: bounded browser reconnaissance, version-bound human choices, plan export.

Separate from COLLECT: recon never creates a collector checklist or runs capture.
"""
import argparse
import asyncio
from collections import Counter, deque
import hashlib
import json
import math
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlsplit, urlunsplit, urlencode
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from discover_site.sitemap_utils import parse_sitemap
from recon_pipeline.collector import (BrowserTransport, atomic_json, now, sha, load as load_collection,
                                      valid_result, plan_items)
from recon_pipeline.offline_inventory import item_id, digest, display, build_inventory
from smart_crawler.browser_session import challenge_reason
from smart_crawler.rest_client import parse_source

SCHEMA = 'web-recon-review-v1'
FIELDS = 'id,link,title,type,slug,date,date_gmt,modified,modified_gmt'
TYPES_FIELDS = 'name,slug,rest_base,rest_namespace'
ASSET = re.compile(r'\.(?:png|jpe?g|gif|webp|svg|ico|css|js|woff2?|ttf|mp[34]|zip)(?:$)', re.I)


def normalize(value, base=None):
    if not isinstance(value, str): raise ValueError('URL must be text')
    p = urlsplit(urljoin(base, value) if base else value)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('absolute public HTTP(S) URL required')
    port = p.port
    host = p.hostname.lower()
    if ':' in host: host = '['+host+']'
    if port and (p.scheme, port) not in [('http',80),('https',443)]: host += ':'+str(port)
    return urlunsplit((p.scheme,host,p.path or '/',p.query,''))


def same_site(a, b):
    a,b = urlsplit(a),urlsplit(b)
    return (a.scheme,a.netloc)==(b.scheme,b.netloc)


def fresh_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f: f.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def blank(origin, mode, context=None):
    return {'schema':SCHEMA,'origin':origin,'mode':mode,'created_at':now(),
            'context':context or {},'items':[],'requests':[],'gaps':[],
            'wordpress':{'status':'not_attempted','collections':[]},'stop_reason':None,'cleanup_error':None}


def candidate(inv, address, source, *, kind='document', title=None, mime=None, dates=None):
    address=normalize(address)
    ident=item_id(address) if kind=='document' else 'rest-'+sha(address.encode())[:20]
    row=next((x for x in inv['items'] if x['id']==ident),None)
    if row is None:
        row={'id':ident,'kind':kind,'url':address,'title':None,'content_type':None,
             'dates':{},'sources':[],'rest_items':[],'gaps':[],'selection':'UNDECIDED'}
        inv['items'].append(row)
    if source not in row['sources']: row['sources'].append(source)
    if title: row['title']=BeautifulSoup(title,'html.parser').get_text(' ',strip=True) or None
    if mime: row['content_type']=mime
    if dates: row['dates'].update({k:v for k,v in dates.items() if isinstance(v,str) and v})
    return row


def listing(inv):
    lines=['# DECIDE — numbered review inventory','',f"**{inv['origin']}**; mode `{inv['mode']}`.",
           f"Version: `{inv['inventory_id']}`. All choices initially UNDECIDED.",'',
           'Row numbers refer ONLY to this saved version. HTML and REST require separate choices.',
           f"Stop: {inv['stop_reason'] or 'none'}; coverage gaps: {display('; '.join(inv['gaps']) or 'none recorded; bounded scope only')}.",
           '', '## WordPress metadata coverage','']
    for col in inv['wordpress']['collections']:
        lines.append(f"- {display(col['type'])}: advertised {col.get('advertised_total')} records / {col.get('advertised_pages')} pages; "
                     f"enumerated {col.get('enumerated_unique',0)} unique; status {display(col['status'])}; gaps {display(col.get('gaps',[]))}.")
    lines+=['','## Candidates','']
    for row in inv['items']:
        lines += [f"{row['row']}. **{display(row['title'] or '[title unknown]')}** — `{row['id']}` — {row['kind']}",
                  f"   - URL: {display(row['url'])}",
                  f"   - HTTP content type: {display(row['content_type'] or 'unknown')}; WordPress type: {display(row.get('wordpress_type') or 'unknown')}; dates: {display(row['dates'] or 'unknown')}",
                  f"   - REST item scope: {display([x['url'] for x in row['rest_items']] or 'not established')}",
                  f"   - Gaps: {display(', '.join(row['gaps']) or 'none recorded')}."]
        lines += [f"   - Evidence: {display(x['file'])} — {display(x.get('locator',''))}" for x in row['sources']]
    return '\n'.join(lines)+'\n'


def html_dates(soup):
    return {m.get('property') or m.get('name'):m.get('content') for m in soup.select(
        'meta[property="article:published_time"], meta[property="article:modified_time"], meta[name="date"]')}


def seal(root, inv):
    inv['items'].sort(key=lambda x:(x['kind'],x['url']))
    for n,row in enumerate(inv['items'],1):
        row['row']=n
        row['gaps']=sorted(set(row['gaps']+[label for field,label in
            [('title','title_unknown'),('content_type','content_type_unknown'),('dates','dates_unknown')] if not row[field]]))
    inv.pop('inventory_id',None);inv['inventory_id']=digest(inv)
    atomic_json(root/'inventory.json',inv)
    (root/'INVENTORY.md').write_text(listing(inv))
    return inv


def read_review(path):
    data=Path(path).read_bytes();inv=json.loads(data);identity=inv.get('inventory_id')
    if inv.get('schema')!=SCHEMA or identity!=digest({k:v for k,v in inv.items() if k!='inventory_id'}):
        raise ValueError('inventory binding mismatch')
    ids=set()
    for n,row in enumerate(inv['items'],1):
        expected=item_id(row['url']) if row['kind']=='document' else 'rest-'+sha(row['url'].encode())[:20]
        if row['id'] in ids or row['id']!=expected or row['row']!=n: raise ValueError('invalid row/ID mapping')
        ids.add(row['id'])
    return inv,sha(data)


def known_content_gaps(path):
    """Read historical content observations; never fetch content during recon."""
    if path is None:return []
    root=Path(path).resolve();state=load_collection(root);observations=[]
    for item in state['items']:
        if item['kind']!='rest' or item['status']!='completed':continue
        meta=valid_result(root,item)
        if meta is None:raise ValueError('known collection result is missing/corrupt')
        value=parse_source((root/meta['body_file']).read_bytes())
        for obj in value if isinstance(value,list) else [value]:
            if not isinstance(obj,dict) or not isinstance(obj.get('link'),str):continue
            content=obj.get('content');rendered=content.get('rendered') if isinstance(content,dict) else None
            if isinstance(rendered,str) and not BeautifulSoup(rendered,'html.parser').get_text(' ',strip=True):
                observations.append({'url':normalize(obj['link']),'id':obj['id'],
                    'source':{'file':str(root/meta['body_file']),'sha256':meta['sha256'],
                              'locator':'historical REST content.rendered','saved_at':meta['saved_at']}})
    return observations


class Recon:
    """Small sequential recon runner using the unchanged collector transport."""
    def __init__(self, root, base, mode, *, sitemap=None, wp_base=None, gap=5,
                 max_requests=12,max_pages=3,max_depth=1,max_rest_pages=1,
                 per_page=20,max_candidates=5000,max_seconds=300,known_collection=None,transport=None):
        if mode not in ('sitemap','default'): raise ValueError('choose --mode sitemap or default explicitly')
        if mode=='default' and sitemap: raise ValueError('--sitemap requires sitemap mode')
        if not math.isfinite(gap) or gap<0 or not math.isfinite(max_seconds) or max_seconds<1:
            raise ValueError('invalid time bounds')
        if any(type(x) is not int or x<1 for x in (max_requests,max_pages,max_rest_pages,max_candidates)) or not 1<=per_page<=100 or max_depth<0:
            raise ValueError('invalid request/page/depth bounds')
        self.root=Path(root);self.base=normalize(base);self.mode=mode
        self.sitemap=normalize(sitemap,self.base) if sitemap else None
        self.wp_base=normalize(wp_base or urljoin(self.base,'/wp-json/')).rstrip('/')+'/'
        if urlsplit(self.wp_base).query:raise ValueError('WP API base must not contain a query')
        if any(not same_site(x,self.base) for x in [self.wp_base]+([self.sitemap] if self.sitemap else [])):
            raise ValueError('sitemap and WP API base must be same-origin')
        self.delay=gap;self.max_requests=max_requests;self.max_pages=max_pages;self.max_depth=max_depth
        self.max_rest_pages=max_rest_pages;self.per_page=per_page;self.max_candidates=max_candidates
        self.seconds=max_seconds;self.browser=transport;self.last=None;self.deadline=None
        self.known_gaps=known_content_gaps(known_collection)
        self.inv=blank('FRESH_BOUNDED_RECON',mode,{'base':self.base,'wp_api_base':self.wp_base,
            'bounds':{'requests':max_requests,'discovery_pages':max_pages,'depth':max_depth,
                      'rest_pages_per_type':max_rest_pages,'per_page':per_page,'candidates':max_candidates,
                      'seconds':max_seconds,'gap_seconds':gap},
            'scope':'same-origin planned URLs; ordinary browser redirects/resources add traffic',
            'purpose':'recon metadata only; never marks full collector tasks complete',
            'known_collection':str(Path(known_collection).resolve()) if known_collection else None})

    def gap(self, reason):
        if reason not in self.inv['gaps']: self.inv['gaps'].append(reason)

    def checkpoint(self):
        atomic_json(self.root/'recon-progress.json',self.inv)

    async def read(self, address, purpose, page=False):
        address=normalize(address)
        if self.inv['stop_reason']: return None
        if not same_site(address,self.base):
            self.gap('off_origin_url_skipped');return None
        if len(self.inv['requests'])>=self.max_requests:
            self.inv['stop_reason']='request_limit';return None
        if self.last is not None:
            await asyncio.sleep(min(max(0,self.last+self.delay-time.monotonic()),max(0,self.deadline-time.monotonic())))
        if time.monotonic()>=self.deadline:
            self.inv['stop_reason']='time_limit';return None
        event={'url':address,'purpose':purpose,'started':time.monotonic(),'preceding_completion':self.last}
        self.inv['requests'].append(event);self.checkpoint()
        try:
            async with asyncio.timeout_at(self.deadline):
                response=await self.browser.get({'kind':'page' if page else 'rest','url':address})
            self.last=event['completed']=time.monotonic()
            body=response.get('body',b'');limit=10*1024*1024
            headers=response.get('headers',{});status=response.get('status')
            reason=challenge_reason(status,headers,'' if 'json' in headers.get('content-type','') else body[:limit].decode('utf-8',errors='replace'))
            if status==401: reason='http_401_access_denied'
            if reason:self.inv['stop_reason']=reason
            error=reason or response.get('transport_error')
            if len(body)>limit: error=error or 'response_cap';self.inv['stop_reason']=self.inv['stop_reason'] or 'response_cap'
            if not response.get('body_complete',True):error=error or 'incomplete_body'
            if status!=200:error=error or 'http_'+str(status)
            if page and not response.get('library_success',True):error=error or 'page_read_failed'
            final=response.get('final_url') or address
            if not same_site(normalize(final),self.base):error='redirect_out_of_origin';self.inv['stop_reason']=self.inv['stop_reason'] or error
            filename=f'evidence/{len(self.inv["requests"]):04d}.body';data=body[:limit]
            with (self.root/filename).open('xb') as stream:stream.write(data)
            event.update(status=status,headers=headers,final_url=final,error=error,
                         body_file=filename,body_bytes=len(data),sha256=sha(data),
                         body_complete=len(body)<=limit and response.get('body_complete',True),
                         transport=response.get('transport'),redirect_from=response.get('redirect_from',[]))
            self.checkpoint()
            if error:self.gap(purpose+':'+str(error));return None
            return body,event
        except (Exception,asyncio.CancelledError) as exc:
            event['error']=type(exc).__name__+': '+str(exc)[:150]
            self.inv['stop_reason']=self.inv['stop_reason'] or ('interrupted' if isinstance(exc,asyncio.CancelledError) else 'read_failed')
            self.checkpoint();return None

    def add(self, address, event, **kwargs):
        try:address=normalize(address,self.base)
        except ValueError:return None
        if not same_site(address,self.base):return None
        if not any(x['url']==address for x in self.inv['items']) and len(self.inv['items'])>=self.max_candidates:
            self.gap('candidate_limit');return None
        return candidate(self.inv,address,{'file':event['body_file'],'sha256':event['sha256'],
                         'discovered_from':event['url'],'locator':kwargs.pop('locator','')},**kwargs)

    async def discovery(self):
        queue=deque();seen=set();reads=0
        if self.mode=='sitemap':
            if self.sitemap:queue.append((self.sitemap,0))
            else:
                answer=await self.read(urljoin(self.base,'/robots.txt'),'sitemap_location')
                if answer:
                    for line in answer[0].decode('utf-8',errors='replace').splitlines():
                        if line.lower().startswith('sitemap:'):
                            try:queue.append((normalize(line.split(':',1)[1].strip(),self.base),0))
                            except ValueError:self.gap('invalid_sitemap_directive')
                if not queue:self.gap('no_sitemap_declared_supply_explicit_sitemap')
        else:queue.append((self.base,0))
        while queue and not self.inv['stop_reason']:
            address,depth=queue.popleft()
            if address in seen:continue
            seen.add(address)
            if not same_site(address,self.base):self.gap('off_origin_discovery_source_skipped');continue
            if depth>self.max_depth:self.gap('discovery_depth_limit');continue
            if reads>=self.max_pages:self.gap('discovery_page_limit');break
            before=len(self.inv['requests'])
            answer=await self.read(address,'sitemap' if self.mode=='sitemap' else 'link_page',page=self.mode=='default')
            reads+=len(self.inv['requests'])>before
            if not answer:continue
            body,event=answer
            if self.mode=='sitemap':
                try:kind,entries=parse_sitemap(body)
                except (ValueError,ET.ParseError):self.gap('invalid_sitemap');continue
                for n,entry in enumerate(entries):
                    try:loc=normalize(entry['loc'],address)
                    except ValueError:continue
                    if kind=='sitemapindex':queue.append((loc,depth+1))
                    else:self.add(loc,event,dates={'sitemap_lastmod':entry.get('lastmod')},locator=f'XML loc[{n}]')
            else:
                soup=BeautifulSoup(body,'html.parser')
                self.add(event['final_url'],event,title=soup.title.get_text() if soup.title else None,
                         mime=event['headers'].get('content-type'),dates=html_dates(soup),locator='html/title and date metadata')
                for n,a in enumerate(soup.select('a[href]')):
                    try:loc=normalize(a['href'],event['final_url'])
                    except ValueError:continue
                    if not same_site(loc,self.base) or ASSET.search(urlsplit(loc).path) or '/wp-json/' in urlsplit(loc).path:continue
                    self.add(loc,event,title=a.get_text(' ',strip=True),locator=f'a[href][{n}]')
                    if loc not in seen:queue.append((loc,depth+1))
        self.inv['context']['discovery_pages_read']=reads

    async def wordpress(self):
        wp=self.inv['wordpress'];wp['status']='partial'
        response=await self.read(self.wp_base+'wp/v2/types?'+urlencode({'_fields':TYPES_FIELDS}),'wp_types')
        if not response:
            wp['status']='unavailable' if not self.inv['stop_reason'] else 'skipped_or_blocked'
            wp['gaps']=['Public types/counts not established; no root enumeration or fallback.'];return
        body,event=response
        try:
            types=parse_source(body)
            if not isinstance(types,dict):raise ValueError()
        except (ValueError,UnicodeError):wp['status']='malformed';self.gap('malformed_wp_types');return
        wp['types_response']=event['body_file'];wp['excluded_types']=[]
        for kind,typ in sorted(types.items(),key=lambda kv:(kv[0] not in ('page','post'),kv[0])):
            if not isinstance(typ,dict):self.gap('malformed_wp_type');continue
            rest_base=typ.get('rest_base');namespace=typ.get('rest_namespace','wp/v2')
            if kind=='attachment' or rest_base=='media':wp['excluded_types'].append({'type':kind,'reason':'media_not_enumerated_for_review'});continue
            if not isinstance(rest_base,str) or not isinstance(namespace,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',rest_base) or not re.fullmatch(r'[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*',namespace):
                self.gap('type_endpoint_not_established:'+kind);continue
            endpoint=self.wp_base+namespace+'/'+rest_base
            col={'type':kind,'endpoint':endpoint,'status':'skipped','advertised_total':None,'advertised_pages':None,
                 'fetched_pages':[],'enumerated_records':0,'enumerated_unique':0,'duplicates':[],'short_pages':[],'gaps':[]}
            wp['collections'].append(col)
            scope=self.add(endpoint,event,kind='rest_collection',title='REST collection: '+str(typ.get('name',kind)),locator='types.'+kind)
            if scope:scope['wordpress_type']=kind
            ids=[]
            for page in range(1,self.max_rest_pages+1):
                before=len(self.inv['requests'])
                result=await self.read(endpoint+'?'+urlencode({'per_page':self.per_page,'page':page,'_fields':FIELDS}),'wp_metadata:'+kind)
                if not result:
                    col['status']='unavailable' if len(self.inv['requests'])>before else 'skipped'
                    if ids:col['status']='partial'
                    col['gaps'].append('metadata_read_unavailable');break
                data,source=result
                try:
                    objects=parse_source(data)
                    if not isinstance(objects,list) or any(not isinstance(o,dict) or type(o.get('id')) is not int or o['id']<=0 for o in objects):raise ValueError()
                except (ValueError,UnicodeError):col['status']='partial';col['gaps'].append('malformed_metadata');break
                col['fetched_pages'].append(page);col['status']='partial'
                projection_ignored=any(set(o)-set(FIELDS.split(',')) for o in objects)
                if projection_ignored:col['gaps'].append('projection_not_honored_no_further_enumeration')
                for n,obj in enumerate(objects):
                    ids.append(obj['id'])
                    address=obj.get('link')
                    if not isinstance(address,str):col['gaps'].append('object_link_missing');continue
                    row=self.add(address,source,title=(obj.get('title') or {}).get('rendered') if isinstance(obj.get('title'),dict) else None,
                        dates={k:obj.get(k) for k in ('date','date_gmt','modified','modified_gmt')},locator=f'$[{n}]')
                    if row:
                        row['wordpress_type']=kind
                        ref={'id':obj['id'],'type':kind,'url':endpoint+'/'+str(obj['id'])}
                        if ref not in row['rest_items']:row['rest_items'].append(ref)
                        if 'content' not in obj:row['gaps'].append('content_not_requested_in_recon')
                counts=Counter(ids);col.update(enumerated_records=len(ids),enumerated_unique=len(counts),duplicates=[i for i,n in counts.items() if n>1])
                try:
                    total=int(source['headers']['x-wp-total']);pages=int(source['headers']['x-wp-totalpages'])
                    if total<0 or pages<0:raise ValueError()
                except (KeyError,ValueError):col['gaps'].append('advertised_counts_unknown');break
                if page==1:col.update(advertised_total=total,advertised_pages=pages)
                elif (total,pages)!=(col['advertised_total'],col['advertised_pages']):col['gaps'].append('advertised_counts_changed');break
                if len(objects)<self.per_page and page<pages:col['short_pages'].append(page)
                if page>=max(1,pages):
                    if len(counts)!=total:col['gaps'].append('advertised_count_mismatch')
                    if col['duplicates']:col['gaps'].append('duplicate_ids')
                    col['status']='enumerated_metadata' if not col['gaps'] else 'partial';break
                if projection_ignored:break
                if not objects:col['gaps'].append('empty_intermediate_page');break
                if page==self.max_rest_pages:col['gaps'].append('metadata_page_limit')
            self.checkpoint()
        for expected in ('page','post'):
            if expected not in types:wp.setdefault('gaps',[]).append(expected+'_type_not_exposed')
        wp['status']='bounded' if not self.inv['stop_reason'] else 'partial'

    async def run(self):
        self.root.mkdir(parents=True,exist_ok=False);(self.root/'evidence').mkdir()
        self.deadline=time.monotonic()+self.seconds
        try:
            if self.browser is None:self.browser=BrowserTransport(self.root)
            async with asyncio.timeout_at(self.deadline):await self.browser.start()
            await self.discovery()
            await self.wordpress()
        except (Exception,asyncio.CancelledError) as exc:
            self.inv['stop_reason']=self.inv['stop_reason'] or type(exc).__name__+': '+str(exc)[:150]
        finally:
            if self.browser is not None:
                try:await asyncio.wait_for(self.browser.close(),10)
                except (Exception,asyncio.CancelledError) as exc:self.inv['cleanup_error']=type(exc).__name__+': '+str(exc)[:150]
                self.inv['browser_traffic']=dict(getattr(self.browser,'traffic',{}))
            self.inv['finished_at']=now();self.checkpoint()
            for observation in self.known_gaps:
                for row in self.inv['items']:
                    if row['kind']=='document' and row['url']==observation['url']:
                        row['gaps']+=['historical_rest_content_rendered_empty','needs_HTML_review_if_selected']
                        row['sources'].append(observation['source'])
            seal(self.root,self.inv)
        return self.inv


def import_saved(out, *, collection=None, raw=None):
    source=Path(collection or raw).resolve();out=Path(out).resolve()
    if out==source or out.is_relative_to(source):raise ValueError('cannot write review into original capture')
    inv=blank('IMPORTED_CAPTURE_INVENTORY','imported',{'input':str(source),'fresh_recon':False})
    inv['gaps']=['Historical saved evidence only; no current accessibility or complete-site claim.']
    if raw:
        old=build_inventory(source)  # existing validated RawRun adapter; read-only
        inv['context']['historical_capture']=old['context']
        index=json.loads((source/'rest/index.json').read_bytes())
        endpoints={x['type']:x['endpoint'] for x in index['collections']}
        for item in old['items']:
            references=[dict(x,file=str(source/x['file'])) for x in item['sources']]
            row=candidate(inv,item['url'],references[0],title=item['title'],dates={d['kind']:d['value'] for d in item['dates']})
            row['sources']=references;row['gaps']=item['gaps'].copy()
            row['wordpress_type']=', '.join(item['content_types']) or None
            for ref in item['sources']:
                if ref.get('wp_id') and ref.get('collection') in endpoints:
                    row['rest_items'].append({'id':ref['wp_id'],'type':ref['collection'],'url':endpoints[ref['collection']]+'/'+str(ref['wp_id'])})
            if 'rest_content_rendered_empty' in row['gaps']:row['gaps'].append('needs_HTML_review_if_selected')
        inv['wordpress']={'status':'imported_historical','collections':[dict(col,
            enumerated_records=col['saved_records'],enumerated_unique=col['unique_ids'],
            gaps=['historical_record_gap:'+str(col['record_gap'])] if col.get('record_gap') else [])
            for col in old['context']['collections']]}
    else:
        state=load_collection(source)
        inv['context']['collection_runs']=state['runs']
        inv['context']['collection_coverage']=state['coverage']
        for item in state['items']:
            meta=valid_result(source,item) if item['status']=='completed' else None
            if not meta:
                inv['gaps'].append('saved_item_unavailable:'+item['id']);continue
            body=(source/meta['body_file']).read_bytes()
            ref={'file':str(source/meta['body_file']),'sha256':meta['sha256'],'locator':'saved '+item['kind']}
            if item['kind']=='page':
                soup=BeautifulSoup(body,'html.parser')
                candidate(inv,item['url'],ref,title=soup.title.get_text() if soup.title else None,mime=meta['headers'].get('content-type'),dates=html_dates(soup))
                # A saved listing supplies linked headings; no linked page is fetched.
                for n,h in enumerate(soup.select('h1,h2,h3,h4')):
                    a=h.find_parent('a') or h.find('a') or h.parent.find('a')
                    if a and a.get('href'):
                        try:address=normalize(a['href'],item['url'])
                        except ValueError:continue
                        if same_site(address,item['url']):candidate(inv,address,dict(ref,locator=f'linked heading[{n}]'),title=h.get_text(' ',strip=True))
            else:
                value=parse_source(body)
                values=value if isinstance(value,list) else [value]
                for n,obj in enumerate(values):
                    if not isinstance(obj,dict) or not isinstance(obj.get('link'),str):continue
                    row=candidate(inv,obj['link'],dict(ref,locator=f'JSON object {n}'),title=(obj.get('title') or {}).get('rendered'),
                        dates={k:obj.get(k) for k in ('date','date_gmt','modified','modified_gmt')})
                    parsed=urlsplit(item['url']);path=parsed.path.rstrip('/')
                    endpoint=item['url'] if not isinstance(value,list) else urlunsplit((parsed.scheme,parsed.netloc,path+'/'+str(obj['id']),'',''))
                    row['wordpress_type']=obj.get('type')
                    row['rest_items'].append({'id':obj['id'],'type':obj.get('type'),'url':endpoint})
                    content=obj.get('content');rendered=content.get('rendered') if isinstance(content,dict) else None
                    if rendered is None:row['gaps'].append('rest_content_unknown')
                    elif not BeautifulSoup(rendered,'html.parser').get_text(' ',strip=True):row['gaps']+=['rest_content_rendered_empty','needs_HTML_review_if_selected']
                inv['wordpress']['status']='imported_selected_responses_only'
        inv['gaps'].append('REST type availability and current advertised totals were not established by this import.')
    out.mkdir(parents=True,exist_ok=False)
    return seal(out,inv)


def save_selection(inventory, output, *, html=(), rest=(), exclude=(), actor, example=False, collection_max_pages=None):
    inv,binding=read_review(inventory);by_id={x['id']:x for x in inv['items']};by_row={str(x['row']):x['id'] for x in inv['items']}
    def resolve(values):
        ids={by_row.get(str(v),str(v)) for v in values}
        if ids-by_id.keys():raise ValueError('unknown row or stable ID: '+', '.join(sorted(ids-by_id.keys())))
        return ids
    html_ids,rest_ids,excluded=resolve(html),resolve(rest),resolve(exclude)
    if not html_ids and not rest_ids and not excluded:raise ValueError('provide explicit inclusions/exclusions')
    if (html_ids|rest_ids)&excluded:raise ValueError('conflicting inclusion/exclusion')
    if any(by_id[i]['kind']!='document' for i in html_ids):raise ValueError('HTML selection must name a document row')
    scopes={}
    for ident in rest_ids:
        row=by_id[ident]
        if row['kind']=='rest_collection':
            if type(collection_max_pages) is not int or collection_max_pages<1:raise ValueError('whole REST collection needs explicit --collection-max-pages')
            scopes[ident]=[{'url':row['url'],'paginate':True,'max_pages':collection_max_pages}]
        else:
            if not row['rest_items']:raise ValueError('no evidenced REST item endpoint for '+ident)
            scopes[ident]=[{'url':x['url'],'paginate':False} for x in row['rest_items']]
    decision={'schema':'web-recon-selection-v1','inventory_id':inv['inventory_id'],'inventory_file_sha256':binding,
        'recorded_at':now(),'recorded_by':actor,'example_only':bool(example),
        'include_html':sorted(html_ids),'include_rest':sorted(rest_ids),'exclude':sorted(excluded),'rest_scopes':scopes,
        'note':'Unspecified rows remain undecided; no model exclusions or collection execution.'}
    fresh_json(output,decision);return decision


def export_plan(inventory, decision_path, output):
    inv,binding=read_review(inventory);decision=json.loads(Path(decision_path).read_text());by_id={x['id']:x for x in inv['items']}
    if decision.get('schema')!='web-recon-selection-v1' or decision.get('inventory_file_sha256')!=binding or decision.get('inventory_id')!=inv['inventory_id']:
        raise ValueError('selection belongs to a different inventory version')
    selected=set(decision['include_html'])|set(decision['include_rest']);excluded=set(decision['exclude'])
    if (selected|excluded)-by_id.keys() or selected&excluded:raise ValueError('unknown or conflicting selection')
    plan={'pages':[],'rest':[]}
    for ident in decision['include_html']:
        if by_id[ident]['kind']!='document':raise ValueError('non-document HTML selection')
        plan['pages'].append(by_id[ident]['url'])
    for ident in decision['include_rest']:
        row=by_id[ident];scopes=decision['rest_scopes'][ident]
        for spec in scopes:
            if row['kind']=='document':
                if spec.get('paginate') is not False or spec['url'] not in [x['url'] for x in row['rest_items']]:raise ValueError('REST item scope was broadened')
            elif spec['url']!=row['url'] or spec.get('paginate') is not True or type(spec.get('max_pages')) is not int or spec['max_pages']<1:raise ValueError('invalid collection scope')
            if spec not in plan['rest']:plan['rest'].append(spec)
    if plan['pages'] or plan['rest']:plan_items(plan)  # exact existing collector plan validator; does not run it
    else:raise ValueError('no inclusions; no collector plan exported')
    output=Path(output);review=output.with_name(output.stem+'.review.json')
    if output.exists() or review.exists():raise FileExistsError('export requires new paths')
    notes={i:by_id[i]['gaps'] for i in selected if by_id[i]['gaps']}
    fresh_json(output,plan)
    fresh_json(review,{'inventory_file_sha256':binding,'decision_sha256':sha(Path(decision_path).read_bytes()),
        'recorded_by':decision['recorded_by'],'example_only':decision['example_only'],
        'selected_html_urls':plan['pages'],'selected_rest_scope':plan['rest'],'selected_gaps':notes,
        'collection_executed':False,'note':'This export cannot mark metadata reconnaissance as complete capture. Human approval is a recorded assertion, not authenticated by the CLI.'})
    return plan


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    recon=commands.add_parser('recon');recon.add_argument('--mode',choices=['sitemap','default'],required=True)
    recon.add_argument('--url',required=True);recon.add_argument('--out',type=Path,required=True)
    recon.add_argument('--sitemap');recon.add_argument('--wp-base');recon.add_argument('--known-collection',type=Path)
    for name,default in [('max-requests',12),('max-pages',3),('max-depth',1),('max-rest-pages',1),('per-page',20),('max-candidates',5000)]:recon.add_argument('--'+name,type=int,default=default)
    recon.add_argument('--gap',type=float,default=5);recon.add_argument('--max-seconds',type=float,default=300)
    imp=commands.add_parser('import');inputs=imp.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--collection',type=Path);inputs.add_argument('--raw',type=Path);imp.add_argument('--out',type=Path,required=True)
    show=commands.add_parser('list');show.add_argument('--inventory',type=Path,required=True)
    choose=commands.add_parser('select');choose.add_argument('--inventory',type=Path,required=True);choose.add_argument('--out',type=Path,required=True)
    for flag in ('include-html','include-rest','exclude'):choose.add_argument('--'+flag,action='append',default=[])
    choose.add_argument('--by',required=True);choose.add_argument('--example',action='store_true');choose.add_argument('--collection-max-pages',type=int)
    export=commands.add_parser('export');export.add_argument('--inventory',type=Path,required=True);export.add_argument('--decision',type=Path,required=True);export.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='recon':
            values=vars(args).copy();values.pop('command');root=values.pop('out');base=values.pop('url')
            inv=asyncio.run(Recon(root,base,**values).run())
            print(json.dumps({'inventory':str(root/'inventory.json'),'candidates':len(inv['items']),'stop_reason':inv['stop_reason'],'cleanup_error':inv['cleanup_error'],'gaps':inv['gaps']}))
            if inv['stop_reason'] or inv['cleanup_error']:raise SystemExit(2)
        elif args.command=='import':
            inv=import_saved(args.out,collection=args.collection,raw=args.raw);print(f'IMPORTED_CAPTURE_INVENTORY: {len(inv["items"])} candidates; {args.out}')
        elif args.command=='list':print(listing(read_review(args.inventory)[0]),end='')
        elif args.command=='select':
            save_selection(args.inventory,args.out,html=args.include_html,rest=args.include_rest,exclude=args.exclude,actor=args.by,example=args.example,collection_max_pages=args.collection_max_pages)
            print(f'Explicit choices saved: {args.out}; no collection executed')
        else:
            export_plan(args.inventory,args.decision,args.out);print(f'Collector plan exported: {args.out}; no collection executed')
    except (ValueError,OSError,KeyError,TypeError) as exc:parser.exit(2,'DECIDE refused: '+str(exc)+'\n')


if __name__=='__main__':main()
