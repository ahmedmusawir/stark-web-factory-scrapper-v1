from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess,sys,time,stat,signal,os,re
r=Path.cwd();e=Path(__file__).resolve().parent;tag=sys.argv[1]
d=e/tag;d.mkdir(exist_ok=False)
ns=dict(r=r,Path=Path,hashlib=hashlib,stat=stat);exec((e/'identity-function.txt').read_text(),ns)
before=ns['identity']();(d/'source-before.json').write_text(json.dumps(before,indent=2)+'\n')
cmd=sys.argv[2:];env=os.environ.copy();env['ABM_CONTROL_EVIDENCE']=str(e/(tag+'-controls'));env['PYTHONDONTWRITEBYTECODE']='1'
methods={'Fetch.enable','Fetch.disable','Fetch.requestPaused','Fetch.continueRequest','Fetch.failRequest','Target.closeTarget','Target.detachFromTarget','Target.detachedFromTarget','Target.attachedToTarget','Inspector.detached','Network.requestWillBeSent'}
def sanitize(x):
 if isinstance(x,dict):return {k:sanitize(v) for k,v in x.items() if k not in ['headers','postData','postDataEntries','associatedCookies','cookies','authorization','cookie','set-cookie','stack']}
 if isinstance(x,list):return [sanitize(v) for v in x]
 return x
start=datetime.now(timezone.utc).isoformat();t=time.monotonic();counts={'console_bytes':0,'driver_bytes':0,'observed_bytes':0,'protocol_parse_gaps':0};pending={};hit=False
with (d/'command.log').open('x') as out,(d/'driver-protocol.jsonl').open('x') as driver:
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
 for raw in iter(proc.stdout.readline,b''):
  counts['observed_bytes']+=len(raw);line=re.sub(r'\x1b\[[0-9;]*m','',raw.decode('utf-8','replace'))
  if 'pw:protocol' in line:
   pos=line.find('{')
   try:
    message,_=json.JSONDecoder().raw_decode(line[pos:]);direction='send' if 'SEND' in line[:pos] else 'receive';key=(message.get('sessionId'),message.get('id'));method=message.get('method')
    if direction=='send' and method in methods:pending[key]=method
    if method not in methods and key not in pending:continue
    data=json.dumps({'python_observed_monotonic':time.monotonic(),'direction':direction,'correlated_method':method or pending.get(key),'message':sanitize(message),'driver_prefix':line[:pos].strip()})+'\n'
    if counts['driver_bytes']+len(data.encode())<=5_000_000:driver.write(data);driver.flush();counts['driver_bytes']+=len(data.encode())
    else:hit=True
   except (ValueError,TypeError):counts['protocol_parse_gaps']+=1
  else:
   if counts['console_bytes']+len(line.encode())<=1_000_000:out.write(line);out.flush();counts['console_bytes']+=len(line.encode())
   else:hit=True
  if counts['observed_bytes']>100_000_000:hit=True
  if hit and proc.poll() is None:proc.send_signal(signal.SIGINT)
 proc.wait()
after=ns['identity']();(d/'source-after.json').write_text(json.dumps(after,indent=2)+'\n')
meta={'command':cmd,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'elapsed_s':time.monotonic()-t,'exit_code':proc.returncode,'source_unchanged':before==after,'source_inventory_sha256':hashlib.sha256((d/'source-before.json').read_bytes()).hexdigest(),'source_file_count':len(before),'base_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'log_limit_hit':hit,'counts':counts,'control_evidence':env['ABM_CONTROL_EVIDENCE']}
(d/'result.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2));print((d/'command.log').read_text()[-10000:]);sys.exit(98 if hit else proc.returncode if before==after else 99)
