import sys,asyncio,json,hashlib
from pathlib import Path
sys.path[:0]=[str(Path.cwd()),str(Path.cwd()/'tests')]
from smart_crawler.browser_session import BrowserSession,Bounds
from fixture_server import fixture_server
E=Path(Path('/tmp/abm_repair_evidence').read_text());out=E/'correlation-probe.json'
async def main(origin,timeline):
 async with BrowserSession(origin,bounds=Bounds(seconds=60,finalization_reserve=5),runtime_dir=E/'probe-runtime',loopback_only=True) as s:
  assert (await s.capture(origin+'/article/'))['ok']
  rows=[]
  def seen(p):
   stack=p.get('initiator',{}).get('stack',{}).get('callFrames',[])
   rows.append({'id':p['requestId'],'frame':p.get('frameId'),'type':p.get('type'),'method':p['request']['method'],'url':p['request']['url'],'initiator_type':p.get('initiator',{}).get('type'),'script_ids':[f['scriptId'] for f in stack]})
  s.cdp.on('Network.requestWillBeSent',seen)
  await s.cdp.send('Runtime.enable')
  world=await s.cdp.send('Page.createIsolatedWorld',{'frameId':s.main_frame,'worldName':'abm-read-identity','grantUniveralAccess':False})
  ctx=world['executionContextId'];compiled=[]
  for method in ['GET','HEAD']:
   url=origin+'/data'
   script='(async()=>{ const r=await window.fetch('+json.dumps(url)+',{method:'+json.dumps(method)+'});return {status:r.status};})()'
   c=await s.cdp.send('Runtime.compileScript',{'expression':script,'sourceURL':'abm-coordinator-read','persistScript':True,'executionContextId':ctx})
   assert c.get('scriptId'),c
   await s.page.evaluate('([u,m])=>fetch(u,{method:m}).then(r=>r.status)',[url,method])
   r=await s.cdp.send('Runtime.runScript',{'scriptId':c['scriptId'],'executionContextId':ctx,'awaitPromise':True,'returnByValue':True})
   assert r['result']['value']['status']==200,r
   compiled.append({'script_id':c['scriptId'],'context_id':ctx,'method':method})
  out.write_text(json.dumps({'compiled':compiled,'network':rows,'main_frame':s.main_frame,'runtime':s.runtime,'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
  for c in compiled:
   same=[r for r in rows if r['method']==c['method']]
   assert len(same)==2 and all(r['type']=='Fetch' and r['frame']==s.main_frame for r in same)
   assert same[0]['script_ids'][0]!=c['script_id'] and same[1]['script_ids'][0]==c['script_id'],same
  print('PASS native GET/HEAD same URL/method/type/frame distinguished by compiled initiator scriptId in same-frame isolated execution context; universal access false')
with fixture_server() as (origin,timeline):asyncio.run(main(origin,timeline))
