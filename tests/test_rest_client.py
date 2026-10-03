"""F-02 REST fidelity/provenance and separate fault variants. No live network."""
import asyncio
import hashlib
import json
from decimal import Decimal

import pytest
from fixture_server import wp_inputs, HEALTHY_PATHS
from smart_crawler.crawler import RunFolder, utc_now, record_capture, build_absences
from smart_crawler.rest_client import collect_rest, parse_source, source_json
from smart_crawler.validate import validate_run, InvalidRaw

ORIGIN='http://127.0.0.1:8765'


class Browser:
    stop_reason=None
    def __init__(self,inputs):self.inputs=inputs;self.calls=[]
    async def read(self,url):
        assert url in self.inputs
        self.calls.append(url)
        return self.inputs[url]
    def stop(self,reason):self.stop_reason=self.stop_reason or reason


def collect(tmp_path,variant='complete'):
    run=RunFolder('Fix',utc_now(),root=tmp_path).create()
    for path in HEALTHY_PATHS:
        url=ORIGIN+path
        record_capture(run,{'url':url,'status':200,'ok':True,'elapsed_s':.1,'error':None},url,'<p>'+('rendered '*400)+'</p>',True)
    browser=Browser(wp_inputs(ORIGIN,variant))
    objects,absences=asyncio.run(collect_rest(browser,ORIGIN,run))
    run.write_absences(absences)
    run.write_manifest(command='',input_path=tmp_path/'unused.json',input_total=6,limit=None,input_hosts=['127.0.0.1'],finished_at=utc_now(),stopped_early=False)
    return run,browser,objects,absences


def test_pagination_response_bytes_derivatives_and_unknown_fields(tmp_path):
    run,browser,objects,absences=collect(tmp_path)
    assert len(browser.calls)==7 and len(objects)==204
    assert all('/wp-json/wp/v2/' in u and '_fields' not in u for u in browser.calls)
    assert len([u for u in browser.calls if '/users?' in u])==1
    assert all(p['rest_outcome']=='mapped' for p in run.pages)
    assert len(run.rest_map['unrouted_objects'])==198
    assert run.rest_map['content_rendered_empty']==['objects/pages-105.json']
    for response in run.rest_index['responses']:
        body=(run.dir/'rest'/response['file']).read_bytes()
        assert body==browser.inputs[response['url']]['body']
        assert hashlib.sha256(body).hexdigest()==response['sha256']
    for item in run.rest_index['objects']:
        saved=parse_source((run.dir/'rest'/item['file']).read_bytes())
        source=parse_source((run.dir/'rest'/item['response_file']).read_bytes())[item['array_position']]
        assert saved==source
    unknown=objects['objects/pages-100.json']['unknown']
    assert unknown['large']==900719925474099312345
    assert unknown['fraction']==Decimal('0.12345678901234567890123456789')
    assert unknown['source_path']=='/home/source/value'
    assert validate_run(run.dir)


def test_optional_missing_and_null_are_distinct(tmp_path):
    run,_,_,absences=collect(tmp_path,'optional_absences')
    gaps=run.rest_index['optional_field_absences']
    assert {'object':'objects/pages-100.json','field':'content.rendered','state':'missing'} in gaps
    assert {'object':'objects/pages-101.json','field':'content.rendered','state':'null'} in gaps
    assert {'object':'objects/pages-103.json','field':'yoast_head_json','state':'missing'} in gaps
    assert {'object':'objects/pages-104.json','field':'yoast_head_json','state':'null'} in gaps
    assert all(c['status']=='complete' for c in run.rest_index['collections'] if c['type']!='users')
    assert validate_run(run.dir)


@pytest.mark.parametrize('variant,route,outcome',[('ambiguous','/article/','ambiguous'),('unmapped','/services/','unmapped')])
def test_mapping_gap_variants(tmp_path,variant,route,outcome):
    run,_,_,_=collect(tmp_path,variant)
    assert run.rest_map['by_route'][ORIGIN+route]['outcome']==outcome
    assert validate_run(run.dir)


@pytest.mark.parametrize('variant',['malformed_identity','malformed_container'])
def test_malformed_response_is_archived_without_fabricated_objects(tmp_path,variant):
    run,_,objects,absences=collect(tmp_path,variant)
    assert any(a['reason']=='malformed_response' for a in absences)
    assert not any(k.startswith('objects/pages-') for k in objects)
    assert run.rest_index['responses'][0]['outcome']=='malformed'
    assert validate_run(run.dir)


def test_validator_detects_fractional_value_change_even_when_float_rounds_equal(tmp_path):
    run,_,_,_=collect(tmp_path)
    item=run.rest_index['objects'][0];path=run.dir/'rest'/item['file']
    changed=path.read_bytes().replace(b'0.12345678901234567890123456789',b'0.12345678901234567890123456788')
    path.write_bytes(changed);item['sha256']=hashlib.sha256(changed).hexdigest()
    (run.dir/'rest/index.json').write_text(json.dumps(run.rest_index))
    with pytest.raises(InvalidRaw,match='changed source values'):validate_run(run.dir)


def test_refusal_preserves_response_and_skips_remaining_collections(tmp_path):
    run=RunFolder('Fix',utc_now(),root=tmp_path).create()
    inputs=wp_inputs(ORIGIN)
    first=ORIGIN+'/wp-json/wp/v2/pages?per_page=100&page=1'
    inputs[first]={'status':429,'body':b'refused','headers':{'retry-after':'8'},'incomplete':False}
    browser=Browser(inputs)
    objects,absences=asyncio.run(collect_rest(browser,ORIGIN,run))
    assert browser.calls==[first] and not objects and browser.stop_reason=='http_429'
    assert (run.dir/'rest/responses/pages-1.body').read_bytes()==b'refused'
    assert [c['status'] for c in run.rest_index['collections']]==['unavailable']+['skipped']*5
    assert len([a for a in absences if a['reason']=='stop_rule'])==5


def test_missing_totals_never_claims_complete(tmp_path):
    run=RunFolder('Fix',utc_now(),root=tmp_path).create();inputs=wp_inputs(ORIGIN)
    inputs[ORIGIN+'/wp-json/wp/v2/pages?per_page=100&page=1']['headers'].pop('x-wp-totalpages')
    browser=Browser(inputs);_,absences=asyncio.run(collect_rest(browser,ORIGIN,run))
    assert run.rest_index['collections'][0]['status']=='partial'
    assert any(a['reason']=='pagination_totals_unknown' for a in absences)
    assert not any('pages?per_page=100&page=2' in url for url in browser.calls)


def test_duplicate_id_different_values_are_retained(tmp_path):
    inputs=wp_inputs(ORIGIN)
    key=ORIGIN+'/wp-json/wp/v2/posts?per_page=100&page=1'
    inputs[key]['body']=b'[{"id":900,"link":"http://127.0.0.1:8765/dup/","title":{"rendered":"one"}},{"id":900,"link":"http://127.0.0.1:8765/dup/","title":{"rendered":"two"}}]'
    inputs[key]['headers']['x-wp-total']='2'
    run=RunFolder('Fix',utc_now(),root=tmp_path).create();browser=Browser(inputs)
    objects,_=asyncio.run(collect_rest(browser,ORIGIN,run))
    assert objects['objects/posts-900.json']['title']['rendered']=='one'
    assert objects['objects/posts-900-2.json']['title']['rendered']=='two'
    assert len([o for o in run.rest_index['objects'] if o['file'].startswith('objects/posts-900')])==2
