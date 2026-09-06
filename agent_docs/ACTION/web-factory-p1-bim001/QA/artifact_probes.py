"""Independent assertions against persisted artifacts. Known discrepancies are
recorded as observations, not hidden by rewritten expectations."""
from offline_driver import *
from datetime import datetime
from urllib.parse import urlparse
import shutil
BASE=EV/'artifact_cases';BASE.mkdir(exist_ok=True)
def urls(n):return [f'https://example.invalid/page{i}' for i in range(n)]
def ok(html='<p>ok</p>',**kw):return {'html':html,**kw}
CASES={
 'normal':dict(urls=urls(2),results=[ok('<html><body>É &amp; ok</body></html>'),ok('a\r\n b  \n')]),
 'empty':dict(urls=[],results=[]),
 'limit':dict(urls=urls(4),results=[ok(),ok()],limit=2),
 'stop':dict(urls=urls(7),results=[dict(status=429,success=False,html='<p>block</p>')]*3,limit=5),
 'mixed':dict(urls=urls(7),results=[ok(),dict(status=403,success=False,html='<p>block</p>'),dict(status=500,success=False,html='<p>fail</p>'),{'exception':'QA arun exception'},dict(status=200,success=True),ok('<p>x</p>',markdown=''),dict(status=200,success=False,html='<p>not successful</p>')]),
 'collision':dict(urls=['https://example.invalid/x/','https://example.invalid/x','http://example.invalid/x'],results=[ok('<p>first É</p>',markdown=' first markdown '),ok('<p>second\r\n</p>',markdown='second markdown'),ok('<p>third</p>',markdown='third markdown')]),
 'write_failure':dict(urls=urls(2),results=[ok('<p>first</p>'),ok('<p>next</p>')],write_failure=True),
 'port':dict(urls=['https://example.invalid:8443/port','https://example.invalid/plain'],results=[ok(),ok()]),
 'empty_html':dict(urls=urls(1),results=[ok('')]),
 'missing_project_seam':dict(urls=urls(1),results=[ok()],missing_project=True),
 'two_runs':dict(urls=urls(1),results=[ok('<p>repeat</p>')])}
TOP=['access_rung','command','crawl4ai_version','delay_before_return_html_s','fallbacks_fired','finished_at','input_hosts','input_path','input_total','limit','page_timeout_ms','pages','pause_range_s','playwright_version','project_name','python_version','run_dir','run_id','schema','started_at','stopped_early','summary_path','wait_for_images']
PAGE=['elapsed_s','error','html_bytes','html_file','md_file','ok','outcome','reason','slug','status','url']
SUM=['crawl4ai_version','finished_at','pages','pause_range_s','started_at'];SP=['elapsed_s','error','ok','status','url']
FIXED=dict(schema='bim001-manifest-v1',access_rung='a',fallbacks_fired=[],wait_for_images=True,delay_before_return_html_s=3.0,page_timeout_ms=90000,pause_range_s=[2,5],crawl4ai_version='0.9.3',playwright_version='1.52.0')
results={}
def inspect(name,cfg,case,run,code):
    m=json.loads((run/'manifest.json').read_text());a=json.loads((run/'absences.json').read_text());s=json.loads((case/'outputs/run_summary.json').read_text());ev=json.loads((case/'invocation.json').read_text());log=(run/'stage_log.txt').read_bytes().decode('utf-8').splitlines()
    checks={};observations=[]
    def check(k,v):checks[k]=bool(v)
    check('layout',sorted(p.name for p in run.iterdir())==['absences.json','html','manifest.json','stage_log.txt'])
    check('manifest_keys',sorted(m)==TOP)
    check('page_keys',all(sorted(p)==PAGE for p in m['pages']))
    check('summary_keys',sorted(s)==SUM and all(sorted(p)==SP for p in s['pages']))
    check('fixed_values',all(m[k]==v and type(m[k]) is type(v) for k,v in FIXED.items()) and m['python_version'].startswith('3.12'))
    check('project',m['project_name']=='CyberizeGroup' and run.parent.parent.name=='CyberizeGroup')
    check('run_id',bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z',m['run_id'])) and m['run_id']==run.name and datetime.strptime(m['run_id'],'%Y-%m-%dT%H-%M-%SZ')==datetime.fromisoformat(m['started_at']).replace(tzinfo=None))
    check('run_dir',m['run_dir']==f"outputs/CyberizeGroup/runs/{run.name}")
    check('command',m['command']==ev['logical_command'])
    check('input_path',m['input_path']==str((case/'input.json').resolve()))
    check('summary_path',m['summary_path']=='outputs/run_summary.json')
    check('counts',m['input_total']==len(cfg['urls']) and m['limit']==cfg.get('limit') and len(m['pages'])==len(ev['arun_urls']))
    expected_hosts=sorted({urlparse(u).hostname for u in cfg['urls']})
    checks['literal_input_hosts']=m['input_hosts']==expected_hosts
    if not checks['literal_input_hosts']:observations.append(dict(ac='32',actual=m['input_hosts'],literal_expected=expected_hosts))
    check('timestamps',m['started_at']==s['started_at'] and m['finished_at']==s['finished_at'])
    check('stopped_exit',m['stopped_early'] is (name=='stop') and code==(2 if name=='stop' else 0))
    check('summary_values',len(m['pages'])==len(s['pages']) and all({k:p[k] for k in SP}==q for p,q in zip(m['pages'],s['pages'])))
    htmlproof=[];mdrules=[];bytechecks=[];pagerules=[]
    for i,p in enumerate(m['pages']):
        captured=p['outcome']=='captured'
        valid=p['outcome'] in ['captured','blocked','failed','unsupported']
        if captured:
            data=(run/p['html_file']).read_bytes();expected=cfg['results'][i]['html'].encode('utf-8')
            bytechecks.append(data==expected)
            valid=valid and p['html_file']==f"html/{p['slug']}.html" and type(p['html_bytes']) is int and p['html_bytes']==len(data) and p['reason'] is None
            htmlproof.append(dict(url=p['url'],html_file=p['html_file'],bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),exact_utf8=data==expected,hex=data.hex()))
        else:valid=valid and p['html_file'] is None and p['html_bytes'] is None and isinstance(p['reason'],str) and bool(p['reason'])
        pagerules.append(valid)
        wanted=f"pages/{p['slug']}.md" if p['ok'] else None
        mdrules.append(p['md_file']==wanted)
        if p['md_file']!=wanted:observations.append(dict(ac='35',url=p['url'],slug=p['slug'],actual_md_file=p['md_file'],literal_expected=wanted))
    check('page_values_except_md_equation',all(pagerules));check('html_exact_bytes',all(bytechecks));check('literal_md_equation',all(mdrules))
    expected_abs=[]
    for p in m['pages']:
        if p['outcome']!='captured':expected_abs.append(dict(url=p['url'],outcome=p['outcome'],reason=p['reason']))
    allowed=cfg['urls'][:cfg['limit']] if cfg.get('limit') is not None else cfg['urls']
    for i,u in enumerate(cfg['urls']):
        if i>=len(m['pages']):expected_abs.append(dict(url=u,outcome='skipped',reason='limit' if i>=len(allowed) else 'stop_rule'))
    check('absences_exact_content_order_reasons',a==expected_abs)
    check('absences_shape',isinstance(a,list) and all(sorted(e)==['outcome','reason','url'] and e['outcome'] in ['blocked','failed','unsupported','skipped'] for e in a))
    captured_urls={p['url'] for p in m['pages'] if p['outcome']=='captured'};absent_urls={p['url'] for p in a}
    check('absences_complete_disjoint',captured_urls|absent_urls==set(cfg['urls']) and captured_urls.isdisjoint(absent_urls))
    check('log_timestamp',bool(log) and all(re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',line) for line in log))
    check('log_start_end','run start' in log[0] and 'CyberizeGroup' in log[0] and run.name in log[0] and 'run end' in log[-1])
    check('log_attempts',all(sum(line.split(' ',2)[1:]==[p['outcome'],p['url']] or (line.split(' ',2)[1:][0]==p['outcome'] and line.split(' ',2)[-1].startswith(p['url']+' (')) for line in log if len(line.split(' ',2))==3)==1 for p in m['pages']))
    check('log_stop',sum('stop rule' in line for line in log)==(1 if name=='stop' else 0))
    check('log_line_count',len(log)==2+len(m['pages'])+(1 if name=='stop' else 0))
    check('no_network_attempts',ev['network_attempts']==[])
    if name=='collision':
        files=[p['html_file'] for p in m['pages']]
        check('collision_exact_three_files',files==['html/example-invalid-x.html','html/example-invalid-x-2.html','html/example-invalid-x-3.html'] and len(list((run/'html').iterdir()))==3)
        check('three_writes',len(ev['html_write_attempts'])==3)
        check('manifest_url_mapping',[p['url'] for p in m['pages']]==cfg['urls'])
        check('markdown_legacy_overwrite',sorted(p.name for p in (case/'outputs/pages').iterdir())==['example-invalid-x.md'] and (case/'outputs/pages/example-invalid-x.md').read_bytes()==b'third markdown')
    if name=='write_failure':
        check('write_failure_continues',m['pages'][0]['outcome']=='failed' and 'write' in m['pages'][0]['reason'] and m['pages'][1]['outcome']=='captured' and ev['arun_urls']==cfg['urls'] and code==0)
    if name=='empty_html':
        observations.append(dict(ac='20',html_attribute_present='html' in cfg['results'][0],html_value=cfg['results'][0]['html'],status=200,success=True,actual_outcome=m['pages'][0]['outcome'],reason=m['pages'][0]['reason'],html_files=list(p.name for p in (run/'html').iterdir()),literal_presence_file_exists=False))
    if name=='empty':check('empty_artifacts',m['pages']==[] and a==[] and list((run/'html').iterdir())==[] and ev['browser_constructions']==0)
    dump(case/f'verification_{run.name}.json',dict(checks=checks,observations=observations,html=htmlproof))
    return dict(run_dir=str(run.relative_to(ROOT)),exit_code=code,checks=checks,observations=observations)
for name,cfg in CASES.items():
    case=BASE/name;case.mkdir(exist_ok=True);dump(case/'fixture.json',cfg);dump(case/'input.json',[{'url':u} for u in cfg['urls']])
    p=command('probe_'+name,[str(ROOT/'venv/bin/python'),str(QA/'offline_probe.py'),str(case)])
    expected=2 if name in ['stop','missing_project_seam'] else 0
    assert p.returncode==expected,(name,p.returncode)
    if name=='missing_project_seam':
        events=json.loads((case/'invocation.json').read_text())
        results[name]=dict(no_browser=events['browser_constructions']==0,no_arun=events['arun_urls']==[],no_outputs=not (case/'outputs').exists(),exit_code=p.returncode)
        continue
    run=sorted((case/'outputs/CyberizeGroup/runs').iterdir())[-1]
    results[name]=inspect(name,cfg,case,run,p.returncode)
    if name=='two_runs':
        first_bytes=(run/'manifest.json').read_bytes();(case/'first_manifest_before.json').write_bytes(first_bytes)
        shutil.copyfile(case/'outputs/run_summary.json',case/'first_run_summary.json')
        p2=command('probe_two_runs_second',[str(ROOT/'venv/bin/python'),str(QA/'offline_probe.py'),str(case)])
        second=sorted((case/'outputs/CyberizeGroup/runs').iterdir())[-1]
        results['two_runs_second']=inspect(name,cfg,case,second,p2.returncode)
        results['two_runs']['second_distinct']=second!=run
        results['two_runs']['first_manifest_unchanged']=(run/'manifest.json').read_bytes()==first_bytes
        (case/'first_manifest_after.json').write_bytes((run/'manifest.json').read_bytes())
        dump(case/'two_run_proof.json',{'first_run_id':run.name,'second_run_id':second.name,'distinct':second!=run,'first_manifest_unchanged':(run/'manifest.json').read_bytes()==first_bytes,'before_sha256':hashlib.sha256(first_bytes).hexdigest(),'after_sha256':hashlib.sha256((run/'manifest.json').read_bytes()).hexdigest()})
dump(EV/'artifact_results.json',results)
print(json.dumps({n:dict(exit=r['exit_code'],false_checks=[k for k,v in r.get('checks',{}).items() if not v],observations=r.get('observations',[])) for n,r in results.items()},indent=2))
