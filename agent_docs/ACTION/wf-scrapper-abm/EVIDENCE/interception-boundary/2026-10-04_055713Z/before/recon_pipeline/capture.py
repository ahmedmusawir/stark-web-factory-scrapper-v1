"""Serial, bounded Capture pipeline with durable raw finalization."""
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

from discover_site.sitemap_utils import canonical_url, discover
from smart_crawler.browser_session import BrowserSession, Bounds, CollectionStopped
from smart_crawler.crawler import RunFolder, utc_now, record_capture, slugify, validate_project, print_project_usage, build_absences
from smart_crawler.rest_client import collect_rest
from smart_crawler.media_inventory import collect_media
from smart_crawler.validate import validate_run, InvalidRaw

REPO=Path(__file__).resolve().parents[1]
STATE_KEYS=('pages','routes','rest_index','rest_map','media','streams','absences','manifest_extra','limit_hit','failure','bootstrap','hosts_allowed')


def source_identity():
    paths=[]
    for folder in ('smart_crawler','discover_site','prepare','recon_pipeline','tests'):
        paths.extend(p for p in (REPO/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend(REPO/name for name in ('requirements.txt','requirements-lock.txt','CLAUDE.md','README.md','RUN_NOTES.md'))
    module=REPO/'agent_docs/ACTION/wf-scrapper-abm'
    paths.extend(p for p in module.rglob('*.md') if not any(x in p.parts for x in ('EVIDENCE','REFERENCES')) and
                 p.name not in ('ENGINEERING_LOG.md','ABM_LEDGER.md','ABM_CAMPAIGN_JOURNAL.md'))
    return {'schema':'abm-source-identity-v1','path_role':'repository-relative input identifiers; not run artifact references',
        'base_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),
        'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=REPO)),
        'files':[{'repository_path':p.relative_to(REPO).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                  'bytes':p.stat().st_size,'mode':p.stat().st_mode & 0o777,'symlink':str(p.readlink()) if p.is_symlink() else None}
                 for p in sorted(set(paths))],
        'excluded':['runtime caches','outputs','evidence','mutable campaign log/ledger/journal','historical references']}


def args_parser(argv=None):
    class ActionableParser(argparse.ArgumentParser):
        def error(self,message):
            print('Error: '+message,file=sys.stderr)
            print('Example: python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com --limit 10 --skip-prepare',file=sys.stderr)
            print('Help: python -m recon_pipeline --help',file=sys.stderr)
            self.exit(2)
    p=ActionableParser(description=__doc__)
    p.add_argument('--project');p.add_argument('--url',required=True)
    p.add_argument('--mode',choices=('sitemap','homepage'),default='sitemap')
    p.add_argument('--limit',type=int)
    p.add_argument('--skip-prepare',action='store_true');p.add_argument('--no-media-head',action='store_true')
    p.add_argument('--max-operations',type=int,default=1200);p.add_argument('--max-seconds',type=float,default=7200)
    p.add_argument('--max-bytes',type=int,default=150_000_000)
    p.add_argument('--max-aggregate-bytes',type=int,default=500_000_000)
    p.add_argument('--output-root',type=Path,default=REPO/'outputs')
    p.add_argument('--fixture-only',action='store_true',help=argparse.SUPPRESS)
    args=p.parse_args(argv)
    problem=validate_project(args.project)
    if problem:p.error('--project is '+problem+'; use letters, digits, hyphens or underscores, without path components')
    try:args.url=canonical_url(args.url)
    except ValueError:p.error('--url must be a public HTTP(S) URL without credentials')
    if args.limit is not None and args.limit<1:p.error('--limit must be >= 1')
    if args.max_operations<1:p.error('--max-operations must be positive')
    if not math.isfinite(args.max_seconds) or args.max_seconds<=35:p.error('--max-seconds must be finite and greater than 35')
    if args.max_bytes<6_000_000:p.error('--max-bytes must reserve at least 6000000 bytes')
    if args.max_aggregate_bytes<args.max_bytes:p.error('aggregate ceiling must cover raw ceiling')
    if args.fixture_only and not args.url.startswith('http://127.0.0.1:'):p.error('--fixture-only requires loopback')
    # Reserved inside the approved persisted ceiling, not added to it. The
    # launch recorder bounds stdout and proves its identity/diff overhead fits.
    args.external_evidence_reserve=min(3_000_000,args.max_bytes//30)
    return args


def snapshot(run):
    return {key:getattr(run,key,None) for key in STATE_KEYS}


def bootstrap_route(input_url,final_url,known):
    """Prefer the requested route when a bootstrap redirected to an alias."""
    original=canonical_url(input_url)
    return original if original in known else canonical_url(final_url or input_url)


def finish_raw(run,args,reason=None):
    """Complete a structural skeleton, including unknown/skipped streams after a stop."""
    if reason:run.failure=reason
    reason=getattr(run,'failure',None)
    if run.routes is None:
        run.routes={'schema':'abm-routes-v1','mode':args.mode,'sitemap_url_used':None,'sources':[],
                    'routes':[],'dropped':[],'counts':{'loc_total':0,'routes':0,'dropped':0}}
    by_url={p['url']:p for p in run.pages}
    for route in run.routes['routes']:
        if route['url'] not in by_url:
            row=run.record_page({'url':route['url'],'input_url':route['input_urls'][0],'status':None,'elapsed_s':0},
                slug=run.allocate_slug(slugify(route['url'].split('://',1)[-1])),outcome='skipped',reason='stop_rule' if reason else 'limit')
            by_url[route['url']]=row
    run.pages=[by_url[r['url']] for r in run.routes['routes']]
    existing={(a['stream'],a['ref'],a['outcome'],a['reason']) for a in run.absences}
    for a in build_absences(run.pages,[],[]):
        if (a['stream'],a['ref'],a['outcome'],a['reason']) not in existing:run.absences.append(a)
    if not run.rest_map:
        run.rest_map={'schema':'abm-rest-map-v1','by_route':{p['url']:{'outcome':'rest_unavailable','reason':'not_collected'} for p in run.pages},
                      'unrouted_objects':[],'content_rendered_empty':[]}
        for page in run.pages:page['rest_ref']=None;page['rest_outcome']='rest_unavailable'
    for page in run.pages:
        if page['rest_outcome']!='mapped' and not any(a['stream']=='rest' and a['ref']==page['url'] for a in run.absences):
            run.absences.append({'stream':'rest','ref':page['url'],'outcome':'skipped' if reason else 'unsupported',
                                 'reason':'stop_rule' if reason else 'no_rest_object','at':utc_now()})
    for collection in run.rest_index['collections']:
        if collection['status']=='skipped':
            run.absences.append({'stream':'rest','ref':collection['type'],'outcome':'skipped','reason':'stop_rule' if reason else 'not_collected','at':utc_now()})
    if not any(p.is_file() and p.name!='README.md' for p in (run.dir/'screenshots').rglob('*')):
        run.absences.append({'stream':'screenshots','ref':'screenshots','outcome':'skipped','reason':'none_supplied','at':utc_now()})
    run.manifest_extra.setdefault('access',{})['stop_reason']=reason
    run.manifest_extra['access']['persisted_bytes_before_finalization']=run.persisted_bytes()
    run.log('pipeline finalization '+(reason or 'completed allocated work'),finalization=True)
    # Exclusive writes preserve any existing/corrupt evidence instead of repairing it.
    run.write_absences(run.absences)
    run.write_manifest(command='',input_path=Path('discovery/routes.json'),input_total=len(run.pages),limit=args.limit,
        input_hosts=run.hosts_allowed,finished_at=utc_now(),stopped_early=bool(reason))
    validate_run(run.dir)
    return 2 if reason else 0


async def capture_pipeline(run,args,send=lambda message:None):
    bounds=Bounds(operations=args.max_operations,seconds=args.max_seconds,persisted_bytes=args.max_bytes,document_slots=args.limit)
    def checkpoint():send({'type':'checkpoint','state':snapshot(run)})
    run.checkpoint=checkpoint
    def event(row):
        run.log('browser '+json.dumps(row,separators=(',',':')))
        if row['event']=='operation_start':send({'type':'operation','deadline':row['deadline']})
        elif row['event']=='operation_complete':send({'type':'operation','deadline':None})
    session=BrowserSession(args.url,bounds=bounds,log=event,runtime_dir=run.dir.parent.parent/'runtime'/run.run_id,loopback_only=args.fixture_only)
    run.hosts_allowed=sorted(session.hosts)
    run.failure=None
    run.manifest_extra={'command':'python -m recon_pipeline --project '+args.project+' --url '+args.url+
        (' --skip-prepare' if args.skip_prepare else '')+(' --no-media-head' if args.no_media_head else '')+
        (f' --limit {args.limit}' if args.limit else ''),
        'input':{'url':args.url,'mode':args.mode,'limit':args.limit},
        'access':{'limits':vars(bounds),'max_aggregate_bytes':args.max_aggregate_bytes,
                  'raw_write_ceiling':run.max_bytes,'external_evidence_reserve_bytes':args.external_evidence_reserve},
        'versions':{'source_inventory':'source_identity.json','source_inventory_sha256':hashlib.sha256((run.dir/'source_identity.json').read_bytes()).hexdigest()}}
    checkpoint()
    try:
        async with session:
            bootstrap=await session.capture(args.url);run.bootstrap=bootstrap
            if not bootstrap['ok']:
                run.failure=session.stop_reason or bootstrap['error'] or 'bootstrap_failed'
                run.streams['discovery']='failed'
                run.absences.append({'stream':'discovery','ref':args.url,'outcome':'blocked' if bootstrap['error']=='blocked' else 'failed','reason':run.failure,'at':utc_now()})
                available=bootstrap.get('block_html') or bootstrap.get('html')
                if available:
                    data=available.encode('utf-8')
                    run.save_bytes('discovery/bootstrap-failed.html',data)
                    run.routes={'schema':'abm-routes-v1','mode':args.mode,'sitemap_url_used':None,
                        'sources':[{'file':'bootstrap-failed.html','url':args.url,'status':bootstrap['status'],
                                    'sha256':hashlib.sha256(data).hexdigest(),'outcome':'failed_bootstrap'}],
                        'routes':[],'dropped':[],'counts':{'loc_total':0,'routes':0,'dropped':0}}
                return
            body=bootstrap['html'].encode();run.save_bytes('discovery/bootstrap.html',body)
            bootstrap_source={'file':'bootstrap.html','url':args.url,'status':bootstrap['status'],
                              'sha256':hashlib.sha256(body).hexdigest(),'role':'origin bootstrap; reused if route matches'}
            run.routes={'schema':'abm-routes-v1','mode':args.mode,'sitemap_url_used':None,
                        'sources':[bootstrap_source],'routes':[],'dropped':[],
                        'counts':{'loc_total':0,'routes':0,'dropped':0}}
            checkpoint()
            session.last_completion=time.monotonic()
            def discovery_progress(routes,absences):
                if bootstrap_source not in routes['sources']:routes['sources'].insert(0,bootstrap_source)
                run.routes=routes;run.absences=list(absences);checkpoint()
            routes,absences,state=await discover(args.url,session,run.dir/'discovery',mode=args.mode,
                bootstrap_html=bootstrap['html'],writer=run.save_bytes,progress=discovery_progress)
            if bootstrap_source not in routes['sources']:routes['sources'].insert(0,bootstrap_source)
            run.routes=routes;run.absences=list(absences);run.streams['discovery']=state;checkpoint()
            if state!='complete':run.failure='discovery_incomplete';return
            known={r['url'] for r in routes['routes']}
            bootstrap_url=bootstrap_route(args.url,bootstrap['final_url'],known)
            remaining=[r['url'] for r in routes['routes'] if r['url']!=bootstrap_url]
            selected=set(remaining[:max(0,args.limit-1)] if args.limit else remaining)
            if bootstrap_url in known:selected.add(bootstrap_url)
            cached={canonical_url(args.url):bootstrap,canonical_url(bootstrap['final_url'] or args.url):bootstrap}
            for route in routes['routes']:
                url=route['url']
                if url not in selected or session.stop_reason:
                    run.record_page({'url':url,'input_url':route['input_urls'][0],'status':None,'elapsed_s':0},
                        slug=run.allocate_slug(slugify(url.split('://',1)[-1])),outcome='skipped',reason='stop_rule' if session.stop_reason else 'limit')
                else:
                    record=cached[url].copy() if url in cached else await session.capture(url)
                    if record.get('ok'):
                        cached[canonical_url(record['final_url'] or url)]=record.copy()
                    record['url']=url
                    record['input_url']=route['input_urls'][0]
                    record_capture(run,record,url,record.get('html'),record.get('fetched',False))
                    session.last_completion=time.monotonic()
                checkpoint()
            objects,absences=await collect_rest(session,args.url,run);run.absences.extend(absences);checkpoint()
            run.absences.extend(await collect_media(session,run,objects,no_head=args.no_media_head));checkpoint()
            selected_ok=all(p['outcome']=='captured' for p in run.pages if p['url'] in selected)
            required_rest=all(c['status']=='complete' for c in run.rest_index['collections'] if c['type']!='users')
            if not selected_ok or not required_rest or (not args.no_media_head and run.streams['media']!='complete'):
                run.failure=session.stop_reason or 'incomplete_allocated_work'
    except CollectionStopped as exc:run.failure=session.stop_reason or str(exc)
    except Exception as exc:
        run.failure='capture_failure:'+type(exc).__name__
        # Collection writes can exhaust their allowance while final metadata
        # still has reserved space. Error logging must use that reserve too.
        run.log('pipeline exception '+repr(exc),finalization=True)
        if run.routes is None:
            run.absences.append({'stream':'discovery','ref':args.url,'outcome':'failed',
                                 'reason':run.failure,'at':utc_now()})
    finally:
        run.failure=session.stop_reason or run.failure
        run.manifest_extra['access'].update(intentional_dispatches=session.dispatches,document_slots_used=session.documents,
            browser_resource_counts=[{'host':h,'resource_type':t,'count':n} for (h,t),n in sorted(session.resources.items(),key=lambda x:str(x[0]))],
            browser_response_statuses={str(k):v for k,v in session.statuses.items()})
        run.manifest_extra['versions'].update(session.runtime)
        checkpoint()


def worker(run,args,pipe):
    os.setsid()
    pipe.send({'type':'ready'})
    if args.fixture_only:
        import smart_crawler.crawler as c
        import smart_crawler.rest_client as rest
        import smart_crawler.media_inventory as media
        fixed=lambda:'2026-01-01T00:00:00+00:00'
        c.utc_now=rest.utc_now=media.utc_now=fixed
        globals()['utc_now']=fixed
    run.hosts_allowed=[];run.absences=[];run.failure=None;run.manifest_extra={} 
    try:
        asyncio.run(capture_pipeline(run,args,pipe.send))
        if source_identity()!=run.initial_identity:run.failure='source_drift'
        code=finish_raw(run,args)
    except KeyboardInterrupt:
        code=finish_raw(run,args,'interrupted')
        code=130
    except BaseException as exc:
        pipe.send({'type':'error','error':type(exc).__name__+': '+str(exc)})
        code=1
    pipe.send({'type':'finished','code':code,'state':snapshot(run)})
    pipe.close()


def supervised_capture(run,args):
    context=multiprocessing.get_context('spawn');parent,child=context.Pipe(duplex=False)
    process=context.Process(target=worker,args=(run,args,child));started=time.monotonic();process.start();child.close()
    operation_deadline=None;ready=False;code=None;reason=None
    try:
        while process.is_alive() or parent.poll():
            if parent.poll(.1):
                try:message=parent.recv()
                except EOFError:break
                if message['type']=='ready':ready=True
                if message['type']=='checkpoint':
                    for key,value in message['state'].items():setattr(run,key,value)
                if message['type']=='operation':operation_deadline=message['deadline']
                if message['type']=='finished':code=message['code']
                if message['type']=='error':run.log('worker error '+message['error'])
            now=time.monotonic()
            if now-started>=args.max_seconds-30:
                reason='global_watchdog';break
            if operation_deadline and now>=operation_deadline:
                reason='operation_watchdog';break
    except KeyboardInterrupt:reason='interrupted'
    finally:
        if reason and process.is_alive():
            if ready:os.killpg(process.pid,signal.SIGINT)
            else:process.terminate()
            process.join(5)
            if process.is_alive():
                if ready:os.killpg(process.pid,signal.SIGKILL)
                else:process.kill()
        process.join(2)
        parent.close()
    if reason:
        run.log('supervisor stop '+reason,finalization=True)
        if not (run.dir/'manifest.json').exists():
            run.hosts_allowed=getattr(run,'hosts_allowed',[])
            code=finish_raw(run,args,reason)
        validate_run(run.dir)
        return 130 if reason=='interrupted' else 2
    return code if code is not None else 1


def main(argv=None):
    args=args_parser(argv)
    if args.fixture_only:
        import smart_crawler.crawler as c
        c.utc_now=lambda:'2026-01-01T00:00:00+00:00'
    started_at='2026-01-01T00:00:00+00:00' if args.fixture_only else utc_now()
    run=RunFolder(args.project,started_at,root=args.output_root).create()
    run.max_bytes=args.max_bytes-args.external_evidence_reserve
    run.hosts_allowed=sorted(BrowserSession(args.url).hosts)
    run.initial_identity=source_identity();run.write_json('source_identity.json',run.initial_identity)
    run.log('pipeline start bounded capture')
    code=supervised_capture(run,args)
    print('RAW RUN: '+str(run.dir))
    if code:raise SystemExit(code)
    if args.skip_prepare:return
    try:
        from prepare.build import build_pack
    except ImportError:
        print('Capture complete; Prepare construction is not implemented at this build milestone. Raw evidence retained.')
        raise SystemExit(3)
    pack=build_pack(run.dir,max_bytes=args.max_aggregate_bytes-run.persisted_bytes()-args.external_evidence_reserve)
    print('ARCHITECT PACK: '+str(pack))


if __name__=='__main__':main()
