"""Fact-bound Capture snapshot checks (E-14); never accept generated output as truth.

Raw bytes are compared to fixture builders. Structural hashes/references are
validated first. The full canonical record is retained, not written over raw.
Only declared timing fields are projected after timing assertions. No source
value, URL, hash, reference, outcome or count is erased by normalization.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from fixture_server import HEALTHY_PATHS, complete_html, wp_inputs, fixture_png
from prepare.reader import RawRun
from smart_crawler.rest_client import parse_source, source_json
from discover_site.sitemap_utils import USER_AGENT

ORIGIN='http://127.0.0.1:8765'
CLOCK='2026-01-01T00:00:00+00:00'


def compare_capture(root, server=None):
    raw=RawRun(root);m=raw.manifest
    assert m['project_name']=='Fix' and m['run_id']=='2026-01-01T00-00-00Z'
    assert m['started_at']==m['finished_at']==CLOCK
    assert m['counts']==dict(routes=6,captured=6,blocked=0,failed=0,unsupported=0,skipped=0,rest_objects=204,rest_mapped_routes=6,media_items=1)
    assert not m['stopped_early'] and m['fallbacks_fired']==[]
    assert m['streams']==dict(discovery='complete',html='complete',rest='complete',media='complete',screenshots='empty')
    assert m['scope']['hosts_allowed']==['127.0.0.1','www.127.0.0.1']
    assert m['access']['intentional_dispatches']==18 and m['access']['document_slots_used']==6
    assert m['access']['stop_reason'] is None and m['access']['user_agent']==USER_AGENT
    assert m['versions']['python']==platform.python_version()
    for name in ('crawl4ai','playwright','requests'):assert m['versions'][name]==importlib.metadata.version(name)
    source=raw.json('source_identity.json')
    assert source['base_head']==m['versions']['tool_commit']
    repo=Path(__file__).resolve().parents[1]
    for item in source['files']:
        path=repo/item['repository_path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],item['repository_path']
        assert path.stat().st_size==item['bytes'] and path.stat().st_mode & 0o777==item['mode']
    assert m['versions']['lock_sha256']==hashlib.sha256((repo/'requirements-lock.txt').read_bytes()).hexdigest()
    assert len(m['versions']['browser_executable_sha256'])==64
    routes=raw.routes
    assert routes['counts']=={'loc_total':7,'routes':6,'dropped':1}
    assert routes['dropped']==[{'loc':ORIGIN+'/about/?utm_source=alias','reason':'duplicate'}]
    expected_files={'manifest.json','absences.json','stage_log.txt','source_identity.json','discovery/routes.json',
                    'screenshots/README.md','rest/index.json','rest/map.json','media/inventory.json'}
    for pos,(page,path) in enumerate(zip(m['pages'],HEALTHY_PATHS,strict=True)):
        assert page['url']==page['input_url']==page['final_url']==ORIGIN+path
        assert page['outcome']=='captured' and page['status']==200 and page['reason'] is None
        assert page['fetched_at']==CLOCK and 0<=page['elapsed_s']<180
        assert page['redirect_chain']==[] and page['block_file'] is None and page['retries']==0
        assert page['rest_ref']==f'rest/objects/pages-{100+pos}.json' and page['rest_outcome']=='mapped'
        assert raw.bytes(page['html_file'])==complete_html(ORIGIN,path)
        expected_files.add(page['html_file'])
        route=routes['routes'][pos];aliases=[ORIGIN+'/about/?utm_source=alias'] if pos==1 else []
        assert route=={'url':ORIGIN+path,'input_urls':[ORIGIN+path,*aliases],'aliases':aliases,'source_file':'pages.xml','lastmod':None}
    soup=BeautifulSoup(raw.bytes(m['pages'][3]['html_file']),'html.parser')
    assert len(soup.find_all('form'))==2 and len(soup.select('iframe,script[src]'))==2
    assert soup.select_one('a[href^="mailto:"]') is not None
    assert len(BeautifulSoup(raw.bytes(m['pages'][5]['html_file']),'html.parser').article.get_text().split())==400
    discovery={
      'bootstrap.html':complete_html(ORIGIN,'/'),
      'robots.txt':('User-agent: *\nDisallow: /private/\nSitemap: '+ORIGIN+'/sitemap.xml\n').encode(),
      'sitemap.xml':('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>'+ORIGIN+'/pages.xml</loc></sitemap><sitemap><loc>'+ORIGIN+'/aliases.xml</loc></sitemap></sitemapindex>').encode()}
    for name,paths in [('pages.xml',HEALTHY_PATHS),('aliases.xml',['/about/?utm_source=alias'])]:
        discovery[name]=('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+p+'</loc></url>' for p in paths)+'</urlset>').encode()
    for name,data in discovery.items():
        assert raw.bytes('discovery/'+name)==data
        expected_files.add('discovery/'+name)
    assert [s['file'] for s in routes['sources']]==list(discovery)
    inputs=wp_inputs(ORIGIN);expected_objects={};expected_rows=[]
    for response in raw.rest_index['responses']:
        expected=inputs[response['url']]
        assert raw.bytes(response['file'],'rest/index.json')==expected['body']
        assert response['status']==expected['status'] and response['method']=='GET'
        assert response['headers']=={**expected['headers'],'content-length':str(len(expected['body']))}
        assert response['started_at']==response['finished_at']==CLOCK
        assert response['body_complete'] and response['evidence_gap'] is None and response['redirect_chain']==[]
        assert response['transport']=='Chromium same-page window.fetch / Response.body.getReader'
        assert response['boundary']=='browser-decoded entity bytes'
        assert response['outcome']==('unavailable' if expected['status']==401 else 'complete')
        expected_files.add('rest/'+response['file'])
        if expected['status']==200:
            for pos,obj in enumerate(parse_source(expected['body'])):
                name=f"objects/{response['collection']}-{obj['id']}.json"
                expected_objects[name]=obj
                expected_rows.append((name,response['file'],pos))
    assert set(inputs)=={r['url'] for r in raw.rest_index['responses']}
    assert [(o['file'],o['response_file'],o['array_position']) for o in raw.rest_index['objects']]==expected_rows
    for name,obj in expected_objects.items():
        assert raw.json(name,'rest/index.json')==obj
        expected_files.add('rest/'+name)
    mapping=raw.rest_map
    assert mapping['by_route']=={ORIGIN+p:{'outcome':'mapped','object':f'objects/pages-{100+i}.json','match':'link'} for i,p in enumerate(HEALTHY_PATHS)}
    assert mapping['unrouted_objects']==[name for name in expected_objects if name not in [f'objects/pages-{100+i}.json' for i in range(6)]]
    assert mapping['content_rendered_empty']==['objects/pages-105.json']
    for col in raw.rest_index['collections']:
        count=200 if col['type']=='pages' else 0 if col['type']=='users' else 1
        assert col['fetched_objects']==count and col['per_page']==100
        assert col['status']==('unavailable' if col['type']=='users' else 'complete')
        assert col['total']==(None if not count else count)
        assert col['total_pages']==(None if not count else 2 if count==200 else 1)
    item,=raw.media['items']
    assert item['url']==item['canonical_url']==ORIGIN+'/image.png'
    assert (item['wp_media_id'],item['width'],item['height'],item['alt'])==(500,20,10,'Fixture image')
    assert item['retrieval']['status']==200 and item['retrieval']['method']=='HEAD'
    assert item['retrieval']['content_length']==len(fixture_png())
    assert item['provenance']==['../rest/objects/media-500.json',*['../'+p['html_file'] for p in m['pages']]]
    assert [x['slug'] for x in item['source_pages']]==[p['slug'] for p in m['pages']]
    events=[json.loads(line.split(' browser ',1)[1]) for line in raw.bytes('stage_log.txt').decode().splitlines() if ' browser ' in line]
    dispatch=[e for e in events if e['event']=='intentional_dispatch']
    expected_urls=[ORIGIN+'/',*[ORIGIN+'/'+n for n in ('robots.txt','sitemap.xml','pages.xml','aliases.xml')],
                   *[ORIGIN+p for p in HEALTHY_PATHS[1:]],*inputs,ORIGIN+'/image.png']
    assert [e['url'] for e in dispatch]==expected_urls
    assert [e['method'] for e in dispatch]==['GET']*17+['HEAD']
    assert [e['ordinal'] for e in dispatch]==list(range(1,19))
    main_frame=dispatch[0]['frame_id']
    bindings={e['operation_id']:e for e in events if e['event']=='read_identity_bound'}
    for d in dispatch:
        row=next(e for e in events if e['event']=='request_classified' and e['request_id']==d['request_id'])
        assert row['classification']=='intentional' and row['operation_id']==d['operation_id']
        assert row['network_id']==d['network_id'] and row['frame_id']==main_frame
        if d['kind']=='read':
            binding=bindings[d['operation_id']]
            assert binding['frame_id']==main_frame and not binding['universal_access']
            assert row['network_resource_type']=='Fetch' and row['initiator_script_id']==binding['script_id']
        else:assert row['resource_type']==row['network_resource_type']=='Document'
    for d in dispatch[1:]:assert d['monotonic']-d['preceding_completion']>=5
    # Lifecycle observations are compared too; a green package cannot hide a
    # duplicated/failed resolution or associate commands with another operation.
    classified={e['request_id']:e for e in events if e['event']=='request_classified'}
    commands=[e for e in events if e['event']=='interception_command']
    completed=[e for e in events if e['event']=='interception_command_complete']
    assert len(commands)==len(classified)==len(completed)==26
    assert len({e['request_id'] for e in commands})==26
    assert sum(e['command']=='Fetch.continueRequest' for e in commands)==24
    assert sum(e['command']=='Fetch.failRequest' for e in commands)==2
    for command in commands:
        record=classified[command['request_id']]
        done,=[e for e in completed if e['request_id']==command['request_id']]
        for key in ('operation_id','request_id','network_id','resource_type','frame_id','predecessor','session','classification'):
            assert command[key]==record[key]==done[key]
        assert command['session']=='page-cdp-1'
        # F-05's iframe and widget script are intercepted but never dispatched.
        external=record['url'] in ('https://maps.example.invalid/embed',
                                   'https://widgets.example.invalid/widget.js')
        expected='Fetch.failRequest' if external else 'Fetch.continueRequest'
        assert command['command']==done['command']==expected
        if external:
            assert record['classification']=='incidental'
            assert any(e['event']=='incidental_prevented' and e['request_id']==command['request_id']
                       and e['reason']=='fixture_egress' for e in events)
        assert command['state']=='resolving' and done['state']=='resolved'
        assert record['monotonic']<=command['monotonic']<=done['monotonic']
    assert not any(e['event'] in ('interception_command_error','interception_cleanup_error',
                                  'interception_resolution_skipped','interception_owner_rejected',
                                  'interception_duplicate_event') for e in events)
    assert not any(e['event'] in ('stop','control_error','intentional_prevented') for e in events)
    if server is not None:
        received=[e for e in server if e['event']=='request_received']
        assert len(received)==24 # 18 intentional + six ordinary image GETs
        assert all(e['user_agent']==USER_AGENT for e in received)
        assert len([e for e in received if e['path']=='/' and e['method']=='GET'])==1
    assert set(raw.inventory())==expected_files
    # Retain full canonical JSON/source values and every actual hash/ref. This
    # comparison record is evidence; it is not a generated expected/golden file.
    canonical={name:parse_source(raw.bytes(name)) for name in sorted(expected_files) if name.endswith('.json')}
    return {'schema':'abm-capture-fact-comparison-v1','variant':'F-09-complete',
            'checks':'structure/hash/reference integrity; exact source bytes; all object values; file inventory; fixture outcomes/counts; actual pacing; full canonical JSON retained',
            'file_hashes':raw.inventory(),'canonical_json':canonical,
            'intentional_events':dispatch,'source_identity_verified':True}


def normalized_capture(root):
    """Integrity/facts first, then full metadata comparison with named volatility.

Protocol channels are compared independently to avoid asserting scheduler order
between CDP and Playwright callbacks. Order inside each channel and deliberate
operation order are retained. Raw bytes, source values and references never
undergo string substitutions. No generated output is an automatic golden.
"""
    compared=compare_capture(root);raw=RawRun(root)
    docs=compared['canonical_json']
    events=[];other=[]
    for line in raw.bytes('stage_log.txt').decode().splitlines():
        if ' browser ' in line:events.append(json.loads(line.split(' browser ',1)[1]))
        else:other.append(line)
    names={};seen={};frames={};scripts={};contexts={}
    def bind(mapping, native, label):
        if native and native not in mapping: mapping[native]=label
    for event in events:
        if event['event'] in ('cdp_request_will_be_sent','request_classified','intentional_intercepted','incidental_prevented'):
            channel='network' if event['event'].startswith('cdp') else 'fetch'
            key=(channel,event['url'])
            if event['request_id'] not in names:
                seen[key]=seen.get(key,0)+1
                names[event['request_id']]=f'{channel}:{event["url"]}#{seen[key]}'
            if event.get('frame_id'):
                label='main' if event.get('resource_type')=='Document' and event.get('operation_id') else event['url']
                bind(frames,event['frame_id'],'frame:'+label)
        if event['event']=='read_identity_bound':
            bind(scripts,event['script_id'],'script:'+event['operation_id'])
            bind(contexts,event['context_id'],'context:'+event['operation_id'])
    for event in events:
        # Native ids for prevented incidental requests may have no Network event.
        if event.get('network_id') and event['network_id'] not in names:
            names[event['network_id']]='network-unobserved:'+event['url']
        if event.get('initiator_script_id'):
            bind(scripts,event['initiator_script_id'],'incidental-script:'+event.get('url','session'))
    timing={'monotonic','browser_timestamp','preceding_completion','completed','predecessor_completed','deadline','seconds'}
    identity={'request_id','network_id','loader_id','predecessor_request_id','correlated_next_request_id','predecessor'}
    channels={}
    for event in events:
        row={}
        for key,value in event.items():
            if key in timing:
                assert value is None or isinstance(value,(int,float))
                row[key]=None if value is None else '<measured timing validated separately>'
            elif key in identity:
                assert not value or value in names,(key,value)
                row[key]=names.get(value) if value else value
            elif key in ('frame_id','script_id','initiator_script_id','context_id'):
                mapping=frames if key=='frame_id' else contexts if key=='context_id' else scripts
                assert value is None or value in mapping,(key,value)
                row[key]=mapping.get(value) if value is not None else None
            else:row[key]=value
        family='cdp' if event['event'].startswith('cdp_') else 'browser' if event['event'].startswith('browser_') else 'coordinator'
        # Independent resources may race. Keep every event and per-resource order.
        subject=event.get('url') or names.get(event.get('request_id')) or 'session'
        channels.setdefault(family+':'+subject,[]).append(row)
    logs={'other':other,'channels':channels,'intentional_order':[e['url'] for e in events if e['event']=='intentional_dispatch']}
    final_names={'manifest.json','absences.json','discovery/routes.json','rest/index.json','rest/map.json','media/inventory.json','screenshots/README.md'}
    final_line=raw.bytes('stage_log.txt').splitlines(keepends=True)[-1]
    actual_pre=sum((raw.root/name).stat().st_size for name in raw.inventory() if name not in final_names)-len(final_line)
    assert docs['manifest.json']['access']['persisted_bytes_before_finalization']==actual_pre
    canonical_log=(source_json(logs)+'\n').encode()
    docs['manifest.json']['access']['persisted_bytes_before_finalization']=actual_pre-len(raw.bytes('stage_log.txt'))+len(final_line)+len(canonical_log)
    for page in docs['manifest.json']['pages']:page['elapsed_s']='<measured, range and pacing checked>'
    # This declared reference targets authored metadata. Recompute its comparison
    # digest from that same canonical file; its actual digest was already checked.
    source_bytes=(source_json(docs['source_identity.json'])+'\n').encode()
    docs['manifest.json']['versions']['source_inventory_sha256']=hashlib.sha256(source_bytes).hexdigest()
    view={}
    for name in sorted(raw.inventory()):
        if name=='stage_log.txt':view[name]=logs
        elif name in docs and not name.startswith('rest/objects/'):view[name]=docs[name]
        else:view[name]={'sha256':hashlib.sha256(raw.bytes(name)).hexdigest(),'bytes':len(raw.bytes(name))}
    return view


def compare_two_captures(first,second):
    left,right=normalized_capture(first),normalized_capture(second)
    mismatches=[name for name in sorted(set(left)|set(right)) if left.get(name)!=right.get(name)]
    assert not mismatches,'snapshot differences: '+', '.join(mismatches)
    return {'full_canonical_comparison':'PASS','files':len(left),
            'normalization':'page elapsed; measured protocol times; correlated protocol IDs; independent resource channels; derived metadata byte-count/hash edges only'}
