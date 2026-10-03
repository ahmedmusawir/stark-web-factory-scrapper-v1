from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess,sys,time,stat,signal,os
r=Path.cwd();e=Path('/tmp/abm_repair_evidence').read_text().strip();tag=sys.argv[1]
d=Path(e)/tag;d.mkdir(exist_ok=False)
def identity():
 paths=[]
 for name in ['smart_crawler','discover_site','prepare','recon_pipeline','tests']:
  if (r/name).exists(): paths += [p for p in (r/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 paths += [r/name for name in ['requirements.txt','requirements-lock.txt','CLAUDE.md','README.md','RUN_NOTES.md']]
 paths += [p for p in (r/'agent_docs/ACTION/wf-scrapper-abm').rglob('*.md') if not any(x in p.parts for x in ['EVIDENCE','REFERENCES']) and p.name not in ['ENGINEERING_LOG.md','ABM_LEDGER.md','ABM_CAMPAIGN_JOURNAL.md']]
 return {str(p.relative_to(r)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode),'symlink':str(p.readlink()) if p.is_symlink() else None} for p in sorted(set(paths))}
before=identity();(d/'source-before.json').write_text(json.dumps(before,indent=2)+'\n')
(d/'git-status.txt').write_bytes(subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all']))
(d/'scoped-diff.patch').write_bytes(subprocess.check_output(['git','diff','--binary','HEAD','--',*before.keys()]))
api=['crawl4ai/async_crawler_strategy.py','crawl4ai/async_configs.py','crawl4ai/browser_manager.py','crawl4ai/models.py','playwright/async_api/_generated.py','playwright/driver/package/lib/server/chromium/crNetworkManager.js','playwright/driver/package/types/protocol.d.ts']
(d/'installed-api-hashes.json').write_text(json.dumps({x:hashlib.sha256((r/'venv/lib/python3.12/site-packages'/x).read_bytes()).hexdigest() for x in api},indent=2)+'\n')
start=datetime.now(timezone.utc).isoformat();t=time.monotonic()
cmd=sys.argv[2:]
log_limit=1_000_000;log_bytes=0;log_stopped=False
with (d/'command.log').open('xb') as out:
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 while chunk:=os.read(proc.stdout.fileno(),8192):
  room=max(0,log_limit-log_bytes);out.write(chunk[:room]);log_bytes+=min(room,len(chunk))
  if len(chunk)>room and not log_stopped:
   log_stopped=True
   proc.send_signal(signal.SIGINT)
 proc.wait()
after=identity();(d/'source-after.json').write_text(json.dumps(after,indent=2)+'\n')
meta={'command':cmd,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'elapsed_s':time.monotonic()-t,'exit_code':proc.returncode,'command_log_bytes':log_bytes,'command_log_ceiling':log_limit,'command_log_limit_hit':log_stopped,'source_unchanged':before==after,'base_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_inventory_sha256':hashlib.sha256((d/'source-before.json').read_bytes()).hexdigest(),'excluded':'runtime/cache/output/evidence; mutable campaign journal, ledger, engineering log; historical references'}
(d/'result.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
if os.environ.get('ABM_QUIET_LOG')!='1':print((d/'command.log').read_text()[-8000:])
sys.exit(98 if log_stopped else proc.returncode if before==after else 99)
