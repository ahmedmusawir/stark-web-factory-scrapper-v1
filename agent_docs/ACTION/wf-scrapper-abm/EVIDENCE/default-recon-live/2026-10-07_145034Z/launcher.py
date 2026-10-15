from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,os,subprocess,time,importlib.metadata
root=Path.cwd()
expected='ebc6e8310ce4aab49a93ec6cc3c2011fbddeb404642362a6fc442a71ae77b864'
def stamp(): return datetime.now(timezone.utc).isoformat()
def source():
    files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for part in ['smart_crawler','recon_pipeline','prepare','discover_site','tests'] for p in (root/part).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    return {'files':files,'count':len(files),'sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
identity=source()
branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip()
if identity['sha256']!=expected or branch!='wf-scrapper-abm':raise SystemExit('Source/branch mismatch: no live launch')
# Hash existing outputs, reports and historical evidence before making any new paths.
baseline={}
for part in ['outputs','agent_docs/ACTION/wf-scrapper-abm/EVIDENCE','agent_docs/RESPONSES']:
    for p in (root/part).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:baseline[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
tag=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%SZ')
ev=root/'agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/default-recon-live'/tag
ev.mkdir(parents=True,exist_ok=False)
out=root/'outputs/recon/CyberizeGroup-default-01'
if out.exists():out=root/('outputs/recon/CyberizeGroup-default-01-'+tag)
if out.exists():raise SystemExit('Fresh output unavailable: no live launch')
def write(name,value):
    with (ev/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
write('source-inventory-before.json',identity)
with gzip.open(ev/'preservation-baseline.json.gz','wt') as f:json.dump(baseline,f,sort_keys=True)
command=['venv/bin/python','-m','recon_pipeline.decide','recon','--mode','default','--url','https://cyberizegroup.com/blog/','--out',str(out.relative_to(root)),'--gap','5','--max-requests','4','--max-pages','1','--max-depth','0','--max-rest-pages','1','--per-page','1','--max-candidates','100','--max-seconds','180','--known-collection','outputs/collections/CyberizeGroup-selected-live-01']
write('preflight.json',{'utc':stamp(),'branch':branch,'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'git_status_before':subprocess.check_output(['git','status','--short'],text=True),'source_count':identity['count'],'source_sha256':identity['sha256'],'matches_reviewed':True,'command':command,'output':str(out.relative_to(root)),'evidence':str(ev.relative_to(root)),'preserved_baseline_files':len(baseline),'runtime':{'python':os.sys.version.split()[0],'crawl4ai':importlib.metadata.version('crawl4ai'),'playwright':importlib.metadata.version('playwright')},'parent_wait_limit_seconds':210,'parent_limit_reason':'CLI 180s collection deadline plus documented 10s cleanup and bounded process exit allowance'})
(ev/'launcher.py').write_bytes(Path(__file__).read_bytes())
with (ev/'LAUNCHED_ONCE').open('x') as f:f.write(stamp()+'\n')
print(json.dumps({'preflight':'MATCH','evidence':str(ev.relative_to(root)),'out':str(out.relative_to(root)),'old_files':len(baseline)}),flush=True)
start=time.monotonic();started=stamp();supervisor=None
with (ev/'stage.log').open('xb') as log:
    try:
        result=subprocess.run(command,cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=log,stderr=subprocess.STDOUT,timeout=210)
        exitcode=result.returncode
    except subprocess.TimeoutExpired:
        exitcode=None;supervisor='parent_wait_timeout; subprocess killed; no repeat'
write('execution.json',{'command':command,'started_utc':started,'ended_utc':stamp(),'elapsed_seconds':time.monotonic()-start,'exit_code':exitcode,'supervisor_action':supervisor,'live_launches':1})
write('source-inventory-after-run.json',source())
print(json.dumps({'exit_code':exitcode,'elapsed_seconds':time.monotonic()-start,'supervisor_action':supervisor,'evidence':str(ev.relative_to(root))}),flush=True)
