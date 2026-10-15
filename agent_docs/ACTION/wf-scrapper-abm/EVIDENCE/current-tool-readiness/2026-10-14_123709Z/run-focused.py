from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,time,hashlib
import xml.etree.ElementTree as ET
c=json.loads(Path('/tmp/web-recon-readiness-config.json').read_bytes());root=Path(c['root']);e=Path(c['evidence']);out=e/'combined'
assert not out.exists();out.mkdir()
source=json.loads((e/'source-before.json').read_bytes())
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in source['files'].items())
assert json.loads((e/'fixture-checks.json').read_bytes())['status']=='PASS'
cmd=['venv/bin/python','-m','pytest','-q','tests/test_selected_collector.py','tests/test_decide.py','agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py','-p','no:cacheprovider','--basetemp',str(out/'fixtures'),'--junitxml',str(out/'junit.xml')]
overrides={'PYTHONDONTWRITEBYTECODE':'1','SELECTED_COLLECTOR_EVIDENCE':str(out/'collector-native'),'DECIDE_EVIDENCE':str(out/'decide-native')}
record={'command':cmd,'environment_overrides':overrides,'started_at':datetime.now(timezone.utc).isoformat(),'source_inventory_sha256':source['sha256'],'scope':'Engineer combined verification; loopback browser fixtures and offline saved captures only; independent QA NOT RUN','no_source_edits':True}
(out/'command.json').write_text(json.dumps(record,indent=2)+'\n')
started=time.monotonic()
with (out/'pytest.log').open('x') as log:
 result=subprocess.run(cmd,cwd=root,env=dict(os.environ,**overrides),stdout=log,stderr=subprocess.STDOUT)
record.update(exit_code=result.returncode,elapsed_seconds=time.monotonic()-started,finished_at=datetime.now(timezone.utc).isoformat())
if (out/'junit.xml').is_file():
 suites=ET.parse(out/'junit.xml').getroot();suites=list(suites) if suites.tag=='testsuites' else [suites]
 record['junit_totals']={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
 record['failures']=[{'test':t.attrib.get('name'),'class':t.attrib.get('classname'),'kind':child.tag,'message':child.attrib.get('message','')[:400]} for s in suites for t in s.findall('testcase') for child in t if child.tag in ('failure','error')]
 record['per_module']={}
 for s in suites:
  for t in s.findall('testcase'):
   name=t.attrib.get('classname','');row=record['per_module'].setdefault(name,{'tests':0,'failures':0,'errors':0,'skipped':0});row['tests']+=1
   for child in t:
    if child.tag in ('failure','error','skipped'):row[{'failure':'failures','error':'errors','skipped':'skipped'}[child.tag]]+=1
record['source_after_unchanged']=all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in source['files'].items())
(out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
