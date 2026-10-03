"""C1 independent raw skeleton and corrupt-package negatives (AC-004/008/009/016).

Static stream facts model work not collected yet, never a completed REST stream.
No browser or HTTP calls occur here.
"""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from smart_crawler.validate import InvalidRaw, validate_run

NOW = '2026-01-01T00:00:00+00:00'
HTML = b'<html><body><p>Exact source \xc3\xa9\r\n</p></body></html>'


def raw_fixture(root):
    def write(name, value):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(value if isinstance(value, bytes) else (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode())
    pages = []
    for slug, outcome, status, reason in [('one','captured',200,None),('missing','failed',404,'HTTP 404'),('later','skipped',None,'limit')]:
        url = f'https://example.com/{slug}/'
        pages.append({'url':url,'input_url':url,'final_url':url if status else None,'redirect_chain':[],
            'slug':slug,'status':status,'outcome':outcome,'reason':reason,'fetched_at':NOW if status else None,
            'elapsed_s':0.1 if status else 0,'retries':0,'html_file':'html/one.html' if outcome=='captured' else None,
            'block_file':None,'html_bytes':len(HTML) if outcome=='captured' else None,
            'sha256':hashlib.sha256(HTML).hexdigest() if outcome=='captured' else None,
            'rest_ref':None,'rest_outcome':'rest_unavailable'})
    manifest = {'schema':'abm-raw-v2','project_name':'Static','run_id':'2026-01-01T00-00-00Z',
        'started_at':NOW,'finished_at':NOW,'command':'python -m smart_crawler.crawler --project Static',
        'input':{'url':'https://example.com/','mode':'routes','limit':2},
        'scope':{'hosts_allowed':['example.com','www.example.com'],'redirect_max_hops':5,'robots_policy':'recorded_not_enforced'},
        'access':{'rung':'a','operation_gap_after_completion_s':5.0,'retry_max':0,'stop_on_first_intentional_refusal':True,
                  'automatic_restart':False,'background_resources_paced':False,'page_timeout_ms':90000,
                  'delay_before_return_html_s':3.0,'wait_for_images':True,'cache_mode':'BYPASS','headless':True,
                  'discovery_rest_transport':'chromium_page_window_fetch','user_agent':'fixture identity'},
        'versions':{'python':'3.12.3','crawl4ai':'0.9.3','playwright':'1.52.0','requests':'2.32.3','tool_commit':'unknown'},
        'streams':{'discovery':'partial','html':'partial','rest':'skipped','media':'skipped','screenshots':'empty'},
        'counts':{'routes':3,'captured':1,'failed':1,'blocked':0,'unsupported':0,'skipped':1,
                  'rest_objects':0,'rest_mapped_routes':0,'media_items':0},
        'stopped_early':False,'fallbacks_fired':[],'pages':pages}
    write('manifest.json',manifest)
    write('html/one.html',HTML)
    write('absences.json',[{'stream':'html','ref':p['url'],'outcome':p['outcome'],'reason':p['reason'],'at':NOW}
                          for p in pages if p['outcome']!='captured'])
    write('stage_log.txt', (NOW+' fixture static facts\n').encode())
    write('screenshots/README.md', b'Director-authored evidence slot.\n')
    write('discovery/routes.json', {'schema':'abm-routes-v1','mode':'routes','sources':[],
        'routes':[{'url':p['url'],'input_urls':[p['url']],'aliases':[],'source_file':None,'lastmod':None} for p in pages],
        'dropped':[],'counts':{'loc_total':3,'routes':3,'dropped':0}})
    write('rest/index.json',{'schema':'abm-rest-index-v1','transport':None,
        'collections':[{'type':x,'status':'skipped','response_refs':[]} for x in ['pages','posts','media','categories','tags','users']],
        'responses':[],'objects':[],'absences_file':'../absences.json'})
    write('rest/map.json',{'schema':'abm-rest-map-v1','by_route':{p['url']:{'outcome':'rest_unavailable','reason':'not_collected'} for p in pages},
                          'unrouted_objects':[],'content_rendered_empty':[]})
    write('media/inventory.json',{'schema':'abm-media-v1','items':[],'counts':{'items':0,'internal':0,'external':0,'staging_domain':0}})
    return manifest


def test_static_three_route_raw_skeleton(tmp_path):
    raw_fixture(tmp_path)
    before = {str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert len(validate_run(tmp_path)) == 4
    assert before == {str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}


@pytest.mark.parametrize('corruption', ['hash','count','duplicate','missing_map','path','schema','missing_absence'])
def test_invalid_raw_rejected(tmp_path, corruption):
    m = raw_fixture(tmp_path)
    if corruption == 'hash': m['pages'][0]['sha256'] = '0'*64
    if corruption == 'count': m['counts']['routes'] = 4
    if corruption == 'duplicate': m['pages'].append(copy.deepcopy(m['pages'][0]))
    if corruption == 'path': m['pages'][0]['html_file'] = '/etc/passwd'
    if corruption == 'schema': m['schema'] = 'bim001-manifest-v1'
    if corruption == 'missing_map': (tmp_path/'rest/map.json').write_text('{}')
    if corruption == 'missing_absence': (tmp_path/'absences.json').write_text('[]')
    (tmp_path/'manifest.json').write_text(json.dumps(m))
    with pytest.raises(InvalidRaw): validate_run(tmp_path)


def test_source_strings_are_not_authored_paths(tmp_path):
    m = raw_fixture(tmp_path)
    m['pages'][0]['input_url']='https://example.com/one/?source=/home/example'
    (tmp_path/'manifest.json').write_text(json.dumps(m))
    assert validate_run(tmp_path)
