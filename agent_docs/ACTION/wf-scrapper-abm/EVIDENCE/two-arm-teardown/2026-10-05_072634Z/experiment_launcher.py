"""Run each arm exactly once; bound time/output and retain filtered CDP trace."""
from pathlib import Path
import subprocess,sys,os,time,json,threading,re,signal,hashlib
E=Path(__file__).resolve().parent
METHODS={'Fetch.enable','Fetch.disable','Fetch.continueRequest','Fetch.failRequest','Fetch.requestPaused','Target.closeTarget','Target.detachFromTarget','Target.detachedFromTarget','Target.attachedToTarget','Page.close','Inspector.detached','Network.requestWillBeSent'}

def sanitize(obj):
    if isinstance(obj,dict):return {k:sanitize(v) for k,v in obj.items() if k not in ['headers','postData','postDataEntries','associatedCookies','cookies','authorization','cookie','set-cookie','stack']}
    if isinstance(obj,list):return [sanitize(v) for v in obj]
    return obj

for arm in ('A','B'):
    folder=E/('arm-'+arm);assert not folder.exists(),'Never repeat an arm'
    start=time.monotonic();env=os.environ.copy();env.update(DEBUG='pw:protocol',PYTHONDONTWRITEBYTECODE='1')
    proc=subprocess.Popen([str(Path.cwd()/'venv/bin/python'),str(E/'experiment_worker.py'),arm,str(folder)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    while not folder.exists() and proc.poll() is None:time.sleep(.01)
    if not folder.exists():folder.mkdir()
    byte_total=[0];exceeded=threading.Event();pending={};counts={'protocol_rows':0,'stderr_unretained_lines':0};threads=[]
    def stream(pipe,name):
        limit=1_000_000
        with (folder/name).open('x') as out:
            for line in iter(pipe.readline,b''):
                byte_total[0]+=len(line)
                if byte_total[0]>8_000_000:exceeded.set();continue
                if name=='driver-protocol.jsonl':
                    clean=re.sub(r'\x1b\[[0-9;]*m','',line.decode('utf-8','replace'));pos=clean.find('{')
                    if 'pw:protocol' not in clean or pos<0:counts['stderr_unretained_lines']+=1;continue
                    try:message,_=json.JSONDecoder().raw_decode(clean[pos:])
                    except Exception:counts['stderr_unretained_lines']+=1;continue
                    direction='send' if 'SEND' in clean[:pos] else 'receive'
                    key=(message.get('sessionId'),message.get('id'));method=message.get('method')
                    if direction=='send' and method in METHODS:pending[key]=method
                    if method not in METHODS and key not in pending:continue
                    row={'python_observed_monotonic':time.monotonic(),'direction':direction,'correlated_method':method or pending.get(key),'message':sanitize(message),'driver_log_prefix':clean[:pos].strip()}
                    data=json.dumps(row,separators=(',',':'))+'\n';counts['protocol_rows']+=1
                else:data=line.decode('utf-8','replace')[:4096]
                if out.tell()+len(data.encode())>limit:exceeded.set();continue
                out.write(data);out.flush()
    for pipe,name in [(proc.stdout,'console.log'),(proc.stderr,'driver-protocol.jsonl')]:
        t=threading.Thread(target=stream,args=(pipe,name),daemon=True);t.start();threads.append(t)
    stop=None
    while proc.poll() is None:
        if exceeded.is_set() or time.monotonic()-start>=55:
            stop='evidence_limit' if exceeded.is_set() else 'arm_finalization_deadline';proc.send_signal(signal.SIGINT)
            try:proc.wait(timeout=max(.01,60-(time.monotonic()-start)))
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            break
        time.sleep(.05)
    for t in threads:t.join(timeout=1)
    meta={'arm':arm,'command':[str(Path.cwd()/'venv/bin/python'),str(E/'experiment_worker.py'),arm,str(folder)],'exit_code':proc.returncode,'elapsed_s':time.monotonic()-start,'supervisor_stop':stop,**counts,'observed_driver_console_bytes':byte_total[0],'limits':{'total_seconds':60,'intentional_dispatches':3,'retained_driver_or_console_file_bytes':1000000,'decoded_response_bytes':10485760},'clock_note':'Worker/server and parent observations use OS CLOCK_MONOTONIC. Driver protocol timestamps are log metadata, not calibrated transmit time.'}
    (folder/'launcher-result.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)
    if stop:break
