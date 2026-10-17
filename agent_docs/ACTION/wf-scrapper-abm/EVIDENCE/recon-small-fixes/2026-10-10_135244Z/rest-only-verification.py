"""One authorized REST-only check; delegates every read to existing Recon/BrowserTransport."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()))
import argparse,asyncio,json,re,time
from urllib.parse import urlencode
from recon_pipeline.decide import Recon,TYPE_PROPERTIES,FIELDS
from recon_pipeline.collector import BrowserTransport,now

async def verify(out):
    engine=Recon(out,'https://cyberizegroup.com/','default',gap=5,max_requests=3,
                 max_rest_pages=1,per_page=1,max_seconds=180)
    out.mkdir(exist_ok=False);(out/'evidence').mkdir()
    engine.inv['origin']='REST_ONLY_METADATA_VERIFICATION'
    engine.inv['context']['discovery_pages_read']=0
    engine.deadline=time.monotonic()+180
    report={'started_utc':now(),'public_types':None,'type_descriptions':None,'samples':[],
            'advertised_totals_are_not_enumerated_counts':True,'runtime':None}
    start=time.monotonic()
    try:
        engine.browser=BrowserTransport(out)
        async with asyncio.timeout_at(engine.deadline):await engine.browser.start()
        report['runtime']=engine.browser.runtime
        answer=await engine.read('https://cyberizegroup.com/wp-json/wp/v2/types','wp_types')
        if answer is None:return
        try:types=json.loads(answer[0])
        except (ValueError,UnicodeError):types=None
        if not isinstance(types,dict) or not types:
            engine.inv['stop_reason']=engine.inv['stop_reason'] or 'unusable_types_map';return
        report['public_types']=sorted(types)
        report['type_descriptions']={kind:{key:typ[key] for key in TYPE_PROPERTIES if key in typ}
                                     for kind,typ in types.items() if isinstance(typ,dict)}
        for kind in ('page','post'):
            sample={'type':kind,'attempted':False,'advertised_total':None,'advertised_pages':None,
                    'enumerated_records':0,'enumerated_unique':0,'fetched_pages':[],
                    'coverage':'not_sampled','reason':None}
            report['samples'].append(sample)
            if engine.inv['stop_reason']:
                sample['reason']='earlier_stop';continue
            typ=report['type_descriptions'].get(kind)
            if not typ:sample['reason']='type_not_exposed';continue
            namespace=typ.get('rest_namespace');base=typ.get('rest_base')
            if not isinstance(namespace,str) or not isinstance(base,str) or not re.fullmatch(r'[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*',namespace) or not re.fullmatch(r'[A-Za-z0-9_-]+',base):
                sample['reason']='exposed_endpoint_not_established; no guessing';continue
            address='https://cyberizegroup.com/wp-json/'+namespace+'/'+base+'?'+urlencode({'per_page':1,'page':1,'_fields':FIELDS})
            sample['url']=address
            before=len(engine.inv['requests'])
            result=await engine.read(address,'wp_metadata:'+kind)
            sample['attempted']=len(engine.inv['requests'])>before
            if result is None:
                sample['reason']='read_unavailable'
                engine.inv['stop_reason']=engine.inv['stop_reason'] or 'metadata_read_failed';continue
            body,event=result
            try:objects=json.loads(body)
            except (ValueError,UnicodeError):objects=None
            if not isinstance(objects,list) or any(not isinstance(o,dict) or type(o.get('id')) is not int or o['id']<=0 for o in objects):
                sample['reason']='malformed_metadata';engine.inv['stop_reason']=engine.inv['stop_reason'] or 'malformed_metadata';continue
            for header,key in [('x-wp-total','advertised_total'),('x-wp-totalpages','advertised_pages')]:
                try:sample[key]=int(event['headers'][header])
                except (KeyError,ValueError):pass
            ids=[o['id'] for o in objects]
            sample.update(enumerated_records=len(objects),enumerated_unique=len(set(ids)),fetched_pages=[1],
                          coverage='bounded_one_page_metadata_sample',ids=ids,
                          field_keys=[sorted(o) for o in objects],projection_honored=all(set(o)<=set(FIELDS.split(',')) for o in objects),
                          content_requested=False,body_bytes=event['body_bytes'],sha256=event['sha256'],
                          body_complete=event['body_complete'],status=event['status'],
                          final_url=event['final_url'],title_populated=[bool((o.get('title') or {}).get('rendered')) for o in objects])
    except (Exception,asyncio.CancelledError) as exc:
        engine.inv['stop_reason']=engine.inv['stop_reason'] or type(exc).__name__+': '+str(exc)[:150]
    finally:
        if engine.browser is not None:
            try:await asyncio.wait_for(engine.browser.close(),10)
            except (Exception,asyncio.CancelledError) as exc:engine.inv['cleanup_error']=type(exc).__name__+': '+str(exc)[:150]
            engine.inv['browser_traffic']=dict(engine.browser.traffic)
        engine.inv['finished_at']=now();engine.checkpoint()
        report.update(ended_utc=now(),elapsed_seconds=time.monotonic()-start,
                      requests=engine.inv['requests'],planned_calls=len(engine.inv['requests']),
                      stop_reason=engine.inv['stop_reason'],cleanup_error=engine.inv['cleanup_error'],
                      browser_traffic=engine.inv.get('browser_traffic',{}),
                      limit={'planned_calls':3,'work_seconds':180,'completion_gap_seconds':5,'per_page':1,'page':1},
                      unused_calls=3-len(engine.inv['requests']),no_discovery_or_collection=True)
        with (out/'result.json').open('x') as f:json.dump(report,f,indent=2,ensure_ascii=False);f.write('\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    report=asyncio.run(verify(Path(a.out)))
    # Early returns still persist their complete finally-block report.
    if report is None:report=json.loads((Path(a.out)/'result.json').read_text())
    print(json.dumps({'planned_calls':report['planned_calls'],'stop_reason':report['stop_reason'],
                      'cleanup_error':report['cleanup_error'],'public_types':report['public_types'],
                      'samples':[{'type':s['type'],'attempted':s['attempted'],'advertised_total':s['advertised_total'],'enumerated_records':s['enumerated_records']} for s in report['samples']]}))
    sys.exit(2 if report['stop_reason'] or report['cleanup_error'] else 0)
