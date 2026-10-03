"""Inventory received media references; only scoped HEAD is intentional traffic."""
import json
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from discover_site.sitemap_utils import canonical_url
from smart_crawler.browser_session import CollectionStopped
from smart_crawler.crawler import utc_now


def srcset_urls(value):
    """URL-token/descriptor scan; keep commas inside data URLs intact."""
    pos=0
    while pos<len(value):
        while pos<len(value) and (value[pos].isspace() or value[pos]==','):pos+=1
        start=pos
        while pos<len(value) and not value[pos].isspace():pos+=1
        token=value[start:pos]
        if not token:break
        yield token.rstrip(',')
        if token.endswith(','):continue
        while pos<len(value) and value[pos]!=',':pos+=1


def scan_media(run, objects):
    items={}
    def add(value, *, base, file, locator, context, slug=None, obj=None, rest_ref=None):
        if not isinstance(value,str) or not value.strip():return
        url=urljoin(base,value.strip())
        try: canonical=canonical_url(url)
        except ValueError:canonical=url
        host=urlsplit(url).hostname
        allowed=run.hosts_allowed
        origin='staging_domain' if host and host.endswith('.mystagingwebsite.com') else 'internal' if host in allowed else 'external'
        item=items.setdefault(url,{'url':url,'canonical_url':canonical,'origin':origin,'host':host,
            'wp_media_id':None,'type':None,'width':None,'height':None,'alt':None,'caption':None,'title':None,
            'source_pages':[],'seo_social_usage':[],'rest_ref':None,'retrieval':{'method':'skipped','status':'skipped','reason':'not_attempted'},
            'provenance':[]})
        if file not in item['provenance']:item['provenance'].append(file)
        if slug:
            entry={'slug':slug,'locator':locator,'context':context}
            if entry not in item['source_pages']:item['source_pages'].append(entry)
        if context in ('og:image','twitter:image') and context not in item['seo_social_usage']:item['seo_social_usage'].append(context)
        if obj:
            details=obj.get('media_details') or {}
            def rendered(name):
                v=obj.get(name);return v.get('rendered') if isinstance(v,dict) else v
            item.update(wp_media_id=obj['id'],type=obj.get('mime_type'),width=details.get('width'),height=details.get('height'),
                        alt=obj.get('alt_text'),caption=rendered('caption'),title=rendered('title'),rest_ref=rest_ref)
    for ref,obj in objects.items():
        if not ref.startswith('objects/media-'):continue
        file='../rest/'+ref
        source=obj.get('source_url')
        add(source,base='',file=file,locator='jsonpath:$.source_url',context='rest',obj=obj,rest_ref=file)
        sizes=(obj.get('media_details') or {}).get('sizes') or {}
        for name,size in sizes.items():
            if isinstance(size,dict):
                add(size.get('source_url'),base=source or '',file=file,locator=f'jsonpath:$.media_details.sizes.{name}.source_url',context='rest_size',obj=obj,rest_ref=file)
    for page in run.pages:
        if page['outcome']!='captured':continue
        html=(run.dir/page['html_file']).read_bytes();soup=BeautifulSoup(html,'html.parser')
        base=page['final_url'] or page['url'];file='../'+page['html_file'];slug=page['slug']
        def observed(value,loc,context):add(value,base=base,file=file,locator=loc,context=context,slug=slug)
        for i,tag in enumerate(soup.find_all('img')):
            observed(tag.get('src'),f'tag:img[{i}]@src','img')
            for url in srcset_urls(tag.get('srcset','')):observed(url,f'tag:img[{i}]@srcset','srcset')
        for i,tag in enumerate(soup.select('picture source')):
            for url in srcset_urls(tag.get('srcset','')):observed(url,f'tag:picture/source[{i}]@srcset','srcset')
        for i,tag in enumerate(soup.find_all('video')):observed(tag.get('poster'),f'tag:video[{i}]@poster','poster')
        for i,tag in enumerate(soup.find_all('link')):
            if 'icon' in tag.get('rel',[]):observed(tag.get('href'),f'tag:link[{i}]@href','link_icon')
        for i,tag in enumerate(soup.find_all('meta')):
            name=tag.get('property') or tag.get('name','')
            if name in ('og:image','og:image:url','og:image:secure_url','twitter:image','twitter:image:src'):
                observed(tag.get('content'),f'tag:meta[{i}]@content','og:image' if name.startswith('og:') else 'twitter:image')
        for i,tag in enumerate(soup.select('[style]')):
            for match in re.finditer(r'url\(\s*[\'\"]?(.*?)[\'\"]?\s*\)',tag['style'],re.I):
                observed(match.group(1),f'tag:style_attribute[{i}]','css_bg')
        def json_images(value,locator):
            if isinstance(value,dict):
                for key,child in value.items():
                    if key in ('image','logo'):
                        candidates=child if isinstance(child,list) else [child]
                        for candidate in candidates:
                            url=candidate.get('url',candidate.get('@id')) if isinstance(candidate,dict) else candidate
                            observed(url,locator+'.'+key,'jsonld')
                    json_images(child,locator+'.'+key)
            elif isinstance(value,list):
                for i,child in enumerate(value):json_images(child,locator+f'[{i}]')
        for i,tag in enumerate(soup.find_all('script',type='application/ld+json')):
            try:json_images(json.loads(tag.string or tag.get_text()),f'tag:jsonld[{i}]$')
            except (ValueError,TypeError):pass # Raw markup remains available; no invented URL.
    return list(items.values())


async def collect_media(browser,run,objects, *, no_head=False):
    run.hosts_allowed=sorted(browser.hosts)
    items=scan_media(run,objects);absences=[]
    def absent(item,outcome,reason):
        absences.append({'stream':'media','ref':item['url'],'outcome':outcome,'reason':reason,'at':utc_now()})
    for item in items:
        if not browser.scoped(item['url']):
            reason='off_scope_untested'
        elif no_head:reason='disabled'
        elif browser.stop_reason or run.limit_hit:reason='stop_rule'
        else:reason=None
        if reason:
            item['retrieval']={'method':'skipped','status':'skipped','reason':reason}
            absent(item,'skipped',reason);continue
        start=utc_now()
        try:response=await browser.read(item['url'],method='HEAD')
        except CollectionStopped:
            item['retrieval']={'method':'skipped','status':'skipped','reason':'stop_rule'}
            absent(item,'skipped','stop_rule');continue
        if response.get('status') in (403,429):browser.stop('http_'+str(response['status']))
        headers=response.get('headers',{})
        length=headers.get('content-length')
        item['retrieval']={'method':'HEAD','status':response.get('status'),'content_type':headers.get('content-type'),
            'content_length':int(length) if length and length.isdigit() else None,'headers':headers,
            'transport':response.get('transport'),'started_at':start,'finished_at':utc_now(),
            'final_url':response.get('url'),'redirect_chain':response.get('redirect_chain',[]),'error':response.get('error')}
        if response.get('status') in (403,429) or browser.stop_reason:
            absent(item,'blocked' if response.get('status') in (403,429) else 'failed',browser.stop_reason or 'refused')
        elif response.get('status') is None or response['status']>=400 or response.get('error'):
            absent(item,'failed',response.get('error') or 'head_http_failure')
    run.media={'schema':'abm-media-v1','items':items,'counts':{'items':len(items),**{origin:sum(x['origin']==origin for x in items)
        for origin in ('internal','external','staging_domain')}}}
    required_gaps=[a for a in absences if a['reason']!='off_scope_untested']
    run.streams['media']='complete' if not required_gaps else 'skipped' if no_head else 'partial'
    return absences
