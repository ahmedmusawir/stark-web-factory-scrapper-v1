"""QA-only orchestration. Never modifies application/tests/contracts. No installs/crawl."""
from pathlib import Path
import ast, hashlib, json, os, re, shlex, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[4]
QA=Path(__file__).resolve().parent
EV=QA/'evidence'
ENV=os.environ.copy()
ENV.update(PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(EV/'tmp'), PIP_DISABLE_PIP_VERSION_CHECK='1')
(EV/'tmp').mkdir(exist_ok=True)
def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def command(name,args,cwd=ROOT,env=None):
    start=time.monotonic()
    p=subprocess.run(args,cwd=cwd,env=env or ENV,capture_output=True)
    (EV/f'{name}.stdout.txt').write_bytes(p.stdout)
    (EV/f'{name}.stderr.txt').write_bytes(p.stderr)
    meta=dict(command=shlex.join(map(str,args)),argv=list(map(str,args)),cwd=str(cwd),exit_code=p.returncode,duration_s=round(time.monotonic()-start,4),environment={k:(env or ENV).get(k) for k in ['PYTHONDONTWRITEBYTECODE','TMPDIR','PYTHONPATH','PYTEST_ADDOPTS','PIP_DISABLE_PIP_VERSION_CHECK']})
    dump(EV/f'{name}.command.json',meta)
    print(name, 'exit',p.returncode, 'duration',meta['duration_s'],flush=True)
    return p

def snapshot():
    result={}
    for p in sorted((ROOT/'outputs').rglob('*')):
        st=p.lstat()
        result[str(p.relative_to(ROOT))]=dict(type='dir' if p.is_dir() else 'file',size=st.st_size,mtime_ns=st.st_mtime_ns,sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
    return result

def static_cli():
    for name,args in [('identity_branch',['git','branch','--show-current']),('identity_head',['git','rev-parse','HEAD']),('identity_status',['git','status','--short']),('surface',['git','diff','--name-status','main','HEAD']),('surface_stat',['git','diff','--stat','main']),('implementation_diff',['git','diff','main','HEAD','--','smart_crawler/crawler.py']),('tests_diff',['git','diff','main','HEAD','--','tests/']),('pin_diff',['git','diff','main','HEAD','--','requirements.txt','requirements-lock.txt']),('authors',['git','log','main..HEAD','--format=%an']),('history',['git','log','main..HEAD','--format=%H %an <%ae> %s']),('mkdir',['grep','-n','mkdir','smart_crawler/crawler.py']),('slugify',['grep','-c','def slugify','smart_crawler/crawler.py']),('forbidden_literal',['grep','-rn',r'litellm\|playwright\|google.generativeai\|genai','smart_crawler/','discover_site/'])]:
        command(name,args)
    for key in ['wait_for_images=True','delay_before_return_html=3.0','page_timeout=90000','CacheMode.BYPASS','PAUSE_RANGE_S = (2, 5)','random.uniform(*PAUSE_RANGE_S)']:
        command('config_'+re.sub(r'\W','_',key),['grep','-nF',key,'smart_crawler/crawler.py'])
    example='python -m smart_crawler.crawler --project CyberizeGroup --limit 10'
    for p in ['README.md','RUN_NOTES.md']:
        command('canonical_'+p,['grep','-ncF',example,p])
    for p in ['README.md','RUN_NOTES.md','CHANGELOG.md','agent_docs/SESSIONS/session_2026-09-06.md','agent_docs/RESPONSES/BIM001_plan_2026-09-06.md','agent_docs/ACTION/web-factory-p1-bim001/BIM001_ACCEPTANCE_SPEC.md']:
        (EV/('source_'+Path(p).name+'.txt')).write_text(''.join(f'{i}: {line}\n' for i,line in enumerate((ROOT/p).read_text().splitlines(),1)))
    src=(ROOT/'smart_crawler/crawler.py').read_text();tree=ast.parse(src)
    baseline=subprocess.check_output(['git','show','main:smart_crawler/crawler.py'],cwd=ROOT,text=True)
    def function(s,name):
        return ast.get_source_segment(s,next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name))
    facts={'save_markdown_source_equal':function(src,'save_markdown')==function(baseline,'save_markdown'),'imports':[ast.get_source_segment(src,n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))],'mkdir_calls':[],'baseline_assertions':[]}
    parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    for n in ast.walk(tree):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='mkdir':
            q=n;anc=[]
            while q in parents:
                q=parents[q]
                if isinstance(q,(ast.FunctionDef,ast.AsyncFunctionDef)):anc.append(q.name)
            facts['mkdir_calls'].append({'line':n.lineno,'function_ancestors':anc})
    for p in sorted((ROOT/'tests').glob('test_*.py')):
        rel=str(p.relative_to(ROOT));old=subprocess.check_output(['git','show',f'main:{rel}'],cwd=ROOT,text=True);new=p.read_text()
        funcs={n.name:n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
        for n in ast.parse(old).body:
            if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'):
                m=funcs[n.name]
                aa=[ast.get_source_segment(old,x) for x in ast.walk(n) if isinstance(x,ast.Assert)]
                bb=[ast.get_source_segment(new,x) for x in ast.walk(m) if isinstance(x,ast.Assert)]
                facts['baseline_assertions'].append(dict(file=rel,name=n.name,line=m.lineno,count=len(aa),exact_equal=aa==bb))
    dump(EV/'static_facts.json',facts)
    reports=[];hits=[]
    for p in sorted((ROOT/'agent_docs/RESPONSES').glob('BIM001_*.md')):
        text=p.read_text();reports.append(f'===== {p.relative_to(ROOT)} =====\n{text}')
        for i,line in enumerate(text.splitlines(),1):
            if re.search(r'\bgit\b|\b(commit|checkout|stash|reset|rebase|merge|push)\b',line,re.I):hits.append(f'{p.relative_to(ROOT)}:{i}: {line}')
    (EV/'claudy_reports_full.txt').write_text('\n'.join(reports))
    (EV/'claudy_git_mentions.txt').write_text('\n'.join(hits)+'\n')
    freeze=command('pip_freeze',['venv/bin/pip','freeze'])
    command('freeze_diff',['diff','-u','requirements-lock.txt',str(EV/'pip_freeze.stdout.txt')])
    command('pip_check',['venv/bin/pip','check'])
    fixture=EV/'one_url.json';dump(fixture,[{'url':'https://example.invalid/offline-only'}])
    cases={'help':['--help'],'missing_project':['--input',str(fixture)],'invalid_space':['--project','Cyberize Group','--input',str(fixture)],'invalid_dotdot':['--project','../x','--input',str(fixture)],'limit_zero':['--project','CyberizeGroup','--limit','0','--input',str(fixture)],'missing_input':['--project','CyberizeGroup','--input',str(EV/'intentionally_missing.json')]}
    res={};dump(EV/'outputs_initial.json',snapshot())
    for name,args in cases.items():
        before=snapshot();dump(EV/f'cli_{name}.before.json',before)
        p=command('cli_'+name,['venv/bin/python','-m','smart_crawler.crawler',*args])
        after=snapshot();dump(EV/f'cli_{name}.after.json',after)
        text=(p.stdout+p.stderr).decode()
        checks={'exit_expected':p.returncode==({'help':0,'missing_input':1}.get(name,2)),'outputs_unchanged':before==after}
        if name=='help': checks['flags']=all(f in text for f in ['--project','--input','--limit'])
        if name in ['missing_project','invalid_space','invalid_dotdot']:
            checks.update(required_or_invalid=('--project is required' if name=='missing_project' else '--project is invalid') in text,example=example in text,help_pointer='python -m smart_crawler.crawler --help' in text)
        if name=='limit_zero':checks['argparse_message']='--limit must be >= 1' in text
        res[name]=checks
    dump(EV/'cli_results.json',res)
    assert all(all(c.values()) for c in res.values()),res

def pytest_stage(stage):
    env=ENV.copy();env['PYTHONPATH']=str(ROOT)
    env['PYTEST_ADDOPTS']=shlex.join(['-p','no:cacheprovider','--basetemp',str(EV/f'pytest_tmp_{stage}'),'--junitxml',str(EV/f'{stage}.xml')])
    if stage=='targeted':
        collect=command('targeted_collect',['venv/bin/pytest','--collect-only','-q','tests/test_crawler.py','-k','test_ac'],env=env)
        # collection junit is overwritten by real execution, command and outputs stay separate.
        assert collect.returncode==0 and b'40/48 tests collected' in collect.stdout,collect.stdout
        args=['venv/bin/pytest','-q','tests/test_crawler.py','-k','test_ac'];cwd=ROOT
    elif stage=='regression_root':args=['venv/bin/pytest','-q'];cwd=ROOT
    else:args=[str(ROOT/'venv/bin/pytest'),'-q',str(ROOT/'tests')];cwd=Path('/tmp')
    p=command(stage,args,cwd=cwd,env=env)
    if p.returncode: sys.exit(p.returncode)
if __name__=='__main__':
    if sys.argv[1]=='static_cli':static_cli()
    else:pytest_stage(sys.argv[1])
