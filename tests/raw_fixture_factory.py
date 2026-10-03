"""F-09/F-12 structural inputs; no network and no claims of transport proof."""
import asyncio
import json
from types import SimpleNamespace
from pathlib import Path
from fixture_server import HEALTHY_PATHS, complete_html, wp_inputs, fixture_png
from smart_crawler.crawler import RunFolder, record_capture
from smart_crawler.rest_client import collect_rest
from smart_crawler.media_inventory import collect_media
from recon_pipeline.capture import finish_raw

ORIGIN='http://127.0.0.1:8765'


def build_raw(root, variant='complete', authored=False):
    run=RunFolder('Fix','2026-01-01T00:00:00+00:00',root=Path(root)).create()
    run.hosts_allowed=['127.0.0.1'];run.failure=None;run.manifest_extra={}
    run.log('Synthetic raw input assembled from fixture facts; no browser executed')
    for path in HEALTHY_PATHS:
        failed=variant=='partial' and path=='/about/'
        record_capture(run,{'url':ORIGIN+path,'status':500 if failed else 200,'ok':not failed,
                       'error':'fixture_html_failed' if failed else None,'elapsed_s':0},
                       ORIGIN+path,None if failed else complete_html(ORIGIN,path).decode(),not failed)
    run.routes={'schema':'abm-routes-v1','mode':'sitemap','sitemap_url_used':None,'sources':[],
                'routes':[{'url':ORIGIN+p,'input_urls':[ORIGIN+p],'aliases':[], 'source_file':None,'lastmod':None} for p in HEALTHY_PATHS],
                'dropped':[],'counts':{'loc_total':6,'routes':6,'dropped':0}}
    inputs=wp_inputs(ORIGIN,'partial' if variant=='partial' else 'complete')
    class FixtureReads:
        stop_reason=None
        hosts={'127.0.0.1'}
        def stop(self,reason):self.stop_reason=reason
        def scoped(self,url):return url.startswith(ORIGIN+'/')
        async def read(self,url,method='GET'):
            if method=='HEAD':
                assert url==ORIGIN+'/image.png'
                return {'status':200,'url':url,'headers':{'content-type':'image/png','content-length':str(len(fixture_png()))},
                        'transport':'synthetic fixture HEAD; no network'}
            return inputs[url]
    async def assemble():
        browser=FixtureReads()
        objects,absences=await collect_rest(browser,ORIGIN,run);run.absences.extend(absences)
        if variant=='partial':
            route=ORIGIN+'/services/'
            # Explicit F-12 input fact: this required route's REST evidence is
            # unavailable; all remaining returned objects retain source fidelity.
            run.rest_map['by_route'][route]={'outcome':'rest_unavailable','reason':'fixture_required_route_unavailable'}
            next(p for p in run.pages if p['url']==route)['rest_outcome']='rest_unavailable'
            run.streams['rest']='partial'
        run.absences.extend(await collect_media(browser,run,objects))
    asyncio.run(assemble())
    run.streams['discovery']='complete'
    if authored:(run.dir/'screenshots/director.png').write_bytes(fixture_png())
    finish_raw(run,SimpleNamespace(mode='sitemap',limit=None), 'fixture_two_required_losses' if variant=='partial' else None)
    return run.dir
