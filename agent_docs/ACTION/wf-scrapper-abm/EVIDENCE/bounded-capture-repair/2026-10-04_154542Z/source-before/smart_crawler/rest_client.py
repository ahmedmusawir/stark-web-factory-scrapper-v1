"""Declared WordPress collections, archived responses and lossless derivatives.

Browser transport is injected from the single owned session. No root enumeration,
field filter, requests/curl fallback, retry, or hidden pagination discovery.
"""
import hashlib
import json
from decimal import Decimal
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from discover_site.sitemap_utils import canonical_url
from smart_crawler.crawler import utc_now
from smart_crawler.browser_session import CollectionStopped, challenge_reason

COLLECTIONS = ('pages','posts','media','categories','tags','users')
OPTIONAL_FIELDS = ('type','link','slug','status','date','modified','title.rendered','excerpt.rendered',
                   'content.rendered','author','featured_media','categories','tags','yoast_head_json','yoast_head')
SERIALIZATION = 'UTF-8 JSON; ensure_ascii=false; indent=2; original key order; trailing LF; exact Decimal values; no injected fields'


def parse_source(body):
    def invalid(value): raise ValueError('nonfinite JSON number')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValueError('duplicate JSON key')
            result[key]=value
        return result
    return json.loads(body,parse_float=Decimal,parse_constant=invalid,object_pairs_hook=unique)


def source_json(value, level=0):
    """Serialize parsed values without IEEE-754 loss or a JavaScript JSON round trip."""
    if isinstance(value,dict):
        if not value:return '{}'
        return '{\n'+',\n'.join('  '*(level+1)+json.dumps(k,ensure_ascii=False)+': '+source_json(v,level+1)
                              for k,v in value.items())+'\n'+'  '*level+'}'
    if isinstance(value,list):
        if not value:return '[]'
        return '[\n'+',\n'.join('  '*(level+1)+source_json(v,level+1) for v in value)+'\n'+'  '*level+']'
    if isinstance(value,Decimal):
        if not value.is_finite():raise ValueError('nonfinite JSON number')
        return str(value)
    return json.dumps(value,ensure_ascii=False,allow_nan=False)


def validate_collection(value,kind):
    if not isinstance(value,list):raise ValueError('collection is not an array')
    for obj in value:
        if not isinstance(obj,dict) or type(obj.get('id')) is not int or obj['id']<=0:
            raise ValueError('invalid object id')
        if kind in ('pages','posts'):
            try: canonical_url(obj['link'])
            except (KeyError,TypeError,ValueError):raise ValueError('invalid object link')
        for name in ('title','content','excerpt'):
            if name in obj and obj[name] is not None:
                if not isinstance(obj[name],dict):raise ValueError('invalid rendered container')
                if obj[name].get('rendered') is not None and not isinstance(obj[name]['rendered'],str):
                    raise ValueError('invalid rendered value')
        if obj.get('yoast_head_json') is not None and not isinstance(obj['yoast_head_json'],dict):
            raise ValueError('invalid yoast_head_json')
        if obj.get('yoast_head') is not None and not isinstance(obj['yoast_head'],str):raise ValueError('invalid yoast_head')
    return value


def optional_absences(obj):
    result=[]
    for field in OPTIONAL_FIELDS:
        value=obj
        for part in field.split('.'):
            if value is None:
                result.append({'field':field,'state':'null'});break
            if not isinstance(value,dict) or part not in value:
                result.append({'field':field,'state':'missing'});break
            value=value[part]
        else:
            if value is None:result.append({'field':field,'state':'null'})
    return result


async def collect_rest(browser, base_url, run):
    index={'schema':'abm-rest-index-v1','transport':{'client':'Chromium','api':'page.window.fetch / Response.body.getReader',
        'session_ref':'../manifest.json','response_boundary':'browser-decoded entity bytes; not compressed wire bytes'},
        'collections':[],'responses':[],'objects':[],'fields_requested':'all; no _fields filter','absences_file':'../absences.json'}
    objects={};absences=[];filenames=set();optional=[]
    run.rest_index=index;run.streams['rest']='partial'
    checkpoint=getattr(run,'checkpoint',lambda:None)
    def absent(ref,outcome,reason):
        absences.append({'stream':'rest','ref':ref,'outcome':outcome,'reason':reason,'at':utc_now()})
    index['collections']=[{'type':kind,'endpoint':urljoin(base_url,'/wp-json/wp/v2/'+kind),'per_page':100,
        'total':None,'total_pages':None,'fetched_objects':0,'status':'skipped','response_refs':[]} for kind in COLLECTIONS]
    checkpoint()
    for col in index['collections']:
        kind,endpoint=col['type'],col['endpoint']
        if browser.stop_reason or run.limit_hit:
            absent(kind,'skipped','stop_rule');continue
        page=1
        while True:
            url=endpoint+f'?per_page=100&page={page}';start=utc_now()
            try: response=await browser.read(url)
            except CollectionStopped:
                absent(kind,'skipped','stop_rule');break
            body=response.get('body',b'');ref=f'responses/{kind}-{page}.body'
            try:run.save_bytes('rest/'+ref,body)
            except (BufferError,OSError) as exc:
                browser.stop('rest_persistence_limit' if isinstance(exc,BufferError) else 'rest_write_failed')
                absent(kind,'failed','response_not_persisted');col['status']='partial';break
            headers=response.get('headers',{})
            refusal=challenge_reason(response.get('status'),headers,body.decode('utf-8',errors='replace'))
            if refusal: browser.stop(refusal)
            row={'file':ref,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'collection':kind,'page':page,
                 'url':url,'method':'GET','started_at':start,'finished_at':utc_now(),'status':response.get('status'),
                 'headers':headers,'content_type':headers.get('content-type'),'location':headers.get('location'),
                 'retry_after':headers.get('retry-after'),'x_wp_total':headers.get('x-wp-total'),
                 'x_wp_total_pages':headers.get('x-wp-totalpages'),'transport':response.get('transport'),
                 'boundary':response.get('boundary'),'outcome':'incomplete' if response.get('incomplete') else 'complete',
                 'redirect_chain':response.get('redirect_chain',[]), 'body_complete':not response.get('incomplete',False),
                 'evidence_gap':response.get('evidence_gap')}
            index['responses'].append(row);col['response_refs'].append(ref);col['status']='partial';checkpoint()
            if response.get('status')!=200 or response.get('incomplete') or response.get('error') or browser.stop_reason:
                col['status']='unavailable' if not col['fetched_objects'] else 'partial'
                reason='http_401' if response.get('status')==401 else response.get('error') or browser.stop_reason or 'http_failure'
                outcome='blocked' if response.get('status') in (403,429) or (browser.stop_reason and 'challenge' in browser.stop_reason) else 'unsupported' if response.get('status')==401 else 'failed'
                row['outcome']='refusal' if outcome=='blocked' else 'unavailable' if not response.get('incomplete') else 'incomplete'
                absent(kind,outcome,reason);break
            try:
                values=validate_collection(parse_source(body),kind)
            except (ValueError,UnicodeError,TypeError) as exc:
                row['outcome']='malformed';col['status']='partial';absent(kind,'failed','malformed_response');break
            col['status']='partial'
            for position,value in enumerate(values):
                base=f'objects/{kind}-{value["id"]}';name=base+'.json';suffix=1
                while name in filenames:
                    suffix+=1;name=base+f'-{suffix}.json'
                encoded=(source_json(value)+'\n').encode('utf-8')
                try:run.save_bytes('rest/'+name,encoded)
                except (BufferError,OSError):
                    browser.stop('rest_object_write_failed');absent(kind,'failed','object_not_persisted');col['status']='partial';break
                filenames.add(name);objects[name]=value
                index['objects'].append({'file':name,'sha256':hashlib.sha256(encoded).hexdigest(),
                    'response_file':ref,'array_position':position,'serialization':SERIALIZATION})
                if kind in ('pages','posts'):
                    for gap in optional_absences(value):
                        optional.append({'object':name,**gap})
                        absent(name+'#'+gap['field'],'unsupported','optional_'+gap['state'])
                col['fetched_objects']+=1
                checkpoint()
            if browser.stop_reason:break
            try:
                total=int(headers['x-wp-total']);total_pages=int(headers['x-wp-totalpages'])
                if total<0 or total_pages<0:raise ValueError()
            except (KeyError,ValueError):
                col['status']='partial';absent(kind,'unsupported','pagination_totals_unknown');break
            if col['total'] is not None and (col['total'],col['total_pages'])!=(total,total_pages):
                col['status']='partial';absent(kind,'failed','pagination_totals_changed');break
            col['total'],col['total_pages']=total,total_pages
            if page>=total_pages:
                col['status']='complete' if col['fetched_objects']==total else 'partial'
                if col['status']=='partial':absent(kind,'failed','pagination_count_mismatch')
                break
            if kind=='users':
                col['status']='partial';absent(kind,'skipped','optional_users_single_attempt');break
            if len(values)!=100:
                col['status']='partial';absent(kind,'failed','short_intermediate_page');break
            page+=1
    index['optional_field_absences']=optional
    mapping={'schema':'abm-rest-map-v1','by_route':{},'unrouted_objects':[],'content_rendered_empty':[]}
    links={}
    for ref,obj in objects.items():
        try:link=canonical_url(obj.get('link',''))
        except (ValueError,TypeError):continue
        links.setdefault(link,[]).append(ref)
        content=obj.get('content')
        if isinstance(content,dict) and isinstance(content.get('rendered'),str) and not BeautifulSoup(content['rendered'],'html.parser').get_text('',strip=True):
            mapping['content_rendered_empty'].append(ref)
    required_available=all(c['status']=='complete' for c in index['collections'] if c['type'] in ('pages','posts'))
    used=set()
    for route in run.pages:
        refs=links.get(route['url'],[])
        if len(refs)==1:
            entry={'outcome':'mapped','object':refs[0],'match':'link'};route['rest_ref']='rest/'+refs[0];used.add(refs[0])
        elif len(refs)>1:
            entry={'outcome':'ambiguous','candidates':refs};used.update(refs);absent(route['url'],'unsupported','ambiguous_rest_mapping')
        else:
            entry={'outcome':'unmapped' if required_available else 'rest_unavailable','reason':'no object with matching link' if required_available else 'collection_unavailable'}
            absent(route['url'],'unsupported','no_rest_object')
        route['rest_outcome']=entry['outcome'];mapping['by_route'][route['url']]=entry
    mapping['unrouted_objects']=[ref for ref in objects if ref not in used]
    run.rest_index=index;run.rest_map=mapping
    run.streams['rest']='complete' if all(c['status']=='complete' for c in index['collections'] if c['type']!='users') else 'partial'
    return objects,absences
