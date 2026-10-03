"""Sitemap parsing and discovery through the owned browser session only."""
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlsplit

# One identity for the whole tool. Complete Chrome-shaped UA (Chrome/ + Safari/537.36 tokens)
# so crawl4ai derives a non-empty sec-ch-ua from it. The crawler imports this constant.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)


def canonical_url(url):
    """Contracts §1.1: retain meaningful query and escaped reserved characters."""
    import re
    from urllib.parse import urlsplit, urlunsplit, unquote
    p = urlsplit(url)
    if p.scheme.lower() not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('invalid public HTTP URL')
    host = p.hostname.lower()
    if ':' in host:
        host = '[' + host + ']'
    port = p.port
    if port and (p.scheme.lower(), port) not in [('http',80),('https',443)]:
        host += ':' + str(port)
    def unreserved(match):
        char = chr(int(match.group()[1:], 16))
        return char if char.isascii() and (char.isalnum() or char in '-._~') else match.group().upper()
    path = re.sub(r'%[0-9a-fA-F]{2}', unreserved, re.sub('/+', '/', p.path or '/'))
    if '.' not in path.rsplit('/',1)[-1] and not path.endswith('/'):
        path += '/'
    query = '&'.join(x for x in p.query.split('&') if x and not
        (unquote(x.split('=',1)[0]).lower().startswith('utm_') or
         unquote(x.split('=',1)[0]).lower() in ('fbclid','gclid','cat_source','cat_medium')))
    return urlunsplit((p.scheme.lower(),host,path,query,''))


def parse_sitemap(body):
    """Reject malformed/non-sitemap XML explicitly; no external entity access."""
    if b'<!DOCTYPE' in body.upper() or b'<!ENTITY' in body.upper():
        raise ValueError('unsupported XML declaration')
    root = ET.fromstring(body)
    kind = root.tag.rsplit('}',1)[-1]
    if kind not in ('urlset','sitemapindex'):
        raise ValueError('not sitemap XML')
    result=[]
    for entry in root:
        fields={child.tag.rsplit('}',1)[-1]:child.text for child in entry}
        if fields.get('loc'):
            result.append({'loc':fields['loc'],'lastmod':fields.get('lastmod')})
    return kind,result


async def fetch_sitemap_urls(base_url, browser):
    """Compatibility parser adapter, explicitly injected browser transport (E-06)."""
    seen=set()
    async def visit(url):
        if url in seen or not browser.scoped(url): return []
        seen.add(url)
        response=await browser.read(url)
        if response.get('incomplete') or response.get('error') or response.get('status')!=200:
            raise ValueError('sitemap response unavailable')
        kind, entries=parse_sitemap(response['body'])
        if kind=='sitemapindex':
            urls=[]
            for item in entries: urls.extend(await visit(item['loc']))
            return urls
        return [canonical_url(x['loc']) for x in entries if browser.scoped(x['loc'])]
    return await visit(urljoin(base_url,'/sitemap.xml'))


async def discover(base_url, browser, out, *, mode='sitemap', bootstrap_html=None, writer=None, progress=None):
    """Save discovery responses once. Return complete route accounting and absences."""
    from smart_crawler.crawler import utc_now
    from bs4 import BeautifulSoup
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    routes=[];by_url={};sources=[];dropped=[];absences=[];loc_total=0;used=None
    filenames=set();seen=set();state='complete'
    def notify():
        if progress:
            progress({'schema':'abm-routes-v1','mode':mode,'sitemap_url_used':used,'sources':sources,'routes':routes,
                      'dropped':dropped,'counts':{'loc_total':loc_total,'routes':len(routes),'dropped':len(dropped)}},absences)
    def absent(ref,outcome,reason):
        absences.append({'stream':'discovery','ref':ref,'outcome':outcome,'reason':reason,'at':utc_now()})
    def save(url,body):
        base=Path(urlsplit(url).path).name or 'homepage.html';name=base;n=1
        while name in filenames or (out/name).exists():
            n+=1;name=f'{Path(base).stem}-{n}{Path(base).suffix}'
        filenames.add(name)
        if writer:writer('discovery/'+name,body)
        else:
            with (out/name).open('xb') as f:f.write(body)
        return name
    def add(loc,source,lastmod=None):
        nonlocal loc_total
        loc_total+=1
        try: key=canonical_url(loc)
        except ValueError:
            dropped.append({'loc':loc,'reason':'invalid'});return
        if not browser.scoped(key):
            dropped.append({'loc':loc,'reason':'off_host'});absent(loc,'unsupported','off_host');return
        if key in by_url:
            by_url[key]['input_urls'].append(loc);by_url[key]['aliases'].append(loc)
            dropped.append({'loc':loc,'reason':'duplicate'});return
        row={'url':key,'input_urls':[loc],'aliases':[],'source_file':source,'lastmod':lastmod}
        by_url[key]=row;routes.append(row)
    if mode=='homepage':
        if bootstrap_html is None: raise ValueError('homepage discovery requires controlled bootstrap capture')
        filename=save(base_url,bootstrap_html.encode())
        sources.append({'file':filename,'url':base_url,'status':200,'sha256':hashlib.sha256(bootstrap_html.encode()).hexdigest()})
        for link in BeautifulSoup(bootstrap_html,'html.parser').select('a[href]'):
            href=link.get('href')
            if href and not href.startswith(('#','mailto:','tel:','javascript:')):
                add(urljoin(base_url,href),filename)
    else:
        robots_url=urljoin(base_url,'/robots.txt')
        response=await browser.read(robots_url)
        body=response.get('body',b'');filename=save(robots_url,body)
        sources.append({'file':filename,'url':robots_url,'status':response.get('status'),'sha256':hashlib.sha256(body).hexdigest(),
                        'transport':response.get('transport'),'boundary':response.get('boundary')})
        notify()
        candidates=[]
        if response.get('status')==200 and not response.get('incomplete'):
            for line in body.decode('utf-8',errors='replace').splitlines():
                if line.lower().startswith('sitemap:'): candidates.append(urljoin(base_url,line.split(':',1)[1].strip()))
        else: absent(robots_url,'failed','robots_unavailable')
        candidates += [urljoin(base_url,path) for path in ('/sitemap.xml','/sitemap_index.xml','/wp-sitemap.xml')]
        async def visit(url, *, required=False):
            nonlocal state
            if url in seen: return False
            seen.add(url)
            if not browser.scoped(url):
                absent(url,'unsupported','off_host');return False
            response=await browser.read(url)
            body=response.get('body',b'');name=save(url,body)
            row={'file':name,'url':url,'status':response.get('status'),'sha256':hashlib.sha256(body).hexdigest(),
                 'transport':response.get('transport'),'boundary':response.get('boundary')};sources.append(row)
            notify()
            if response.get('status')!=200 or response.get('error') or response.get('incomplete'):
                absent(url,'failed',response.get('error') or 'sitemap_unavailable')
                if required:state='partial'
                return False
            try: kind,entries=parse_sitemap(body)
            except (ValueError,ET.ParseError):
                absent(url,'failed','malformed_sitemap')
                if required:state='partial'
                return False
            row['child_count' if kind=='sitemapindex' else 'loc_count']=len(entries)
            if kind=='sitemapindex':
                for entry in entries: await visit(entry['loc'],required=True)
            else:
                for entry in entries: add(entry['loc'],name,entry['lastmod'])
            notify()
            return True
        for candidate in dict.fromkeys(candidates):
            if await visit(candidate): used=candidate;break
        if not used: state='failed'
    return {'schema':'abm-routes-v1','mode':mode,'sitemap_url_used':used,'sources':sources,'routes':routes,
            'dropped':dropped,'counts':{'loc_total':loc_total,'routes':len(routes),'dropped':len(dropped)}},absences,state
