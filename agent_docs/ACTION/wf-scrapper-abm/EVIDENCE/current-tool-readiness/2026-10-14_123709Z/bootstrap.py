from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import hashlib, json, subprocess, os, platform, importlib.metadata
from zipfile import ZipFile

root=Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1');os.chdir(root)
now=datetime.now(timezone.utc);tag=now.astimezone(ZoneInfo('Asia/Dhaka')).strftime('%Y-%m-%d_%H%M%S')
evidence=root/'agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/current-tool-readiness'/now.strftime('%Y-%m-%d_%H%M%SZ')
review=root/'agent_docs/RESPONSES'/f'response_{tag}_current-tool-readiness_review'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],text=True,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')).strip()
shot1=root/'agent_docs/RESPONSES/response_2026-10-14_173927_current-tool-completion-plan_review/source-inventory.json'
base=json.loads(shot1.read_bytes());files={p:sha((root/p).read_bytes()) for p in base['files']}
identity=sha(json.dumps(files,sort_keys=True,separators=(',',':')).encode())
changed=[p for p,h in files.items() if h!=base['files'][p]]
assert not changed,changed
assert git('branch','--show-current')=='wf-scrapper-abm'
doc_paths=['CLAUDE.md','README.md','RECOVERY.md','CHANGELOG.md','agent_docs/SESSIONS/session_2026-10-14.md']
module=root/'agent_docs/ACTION/wf-scrapper-abm'
doc_paths += [str((module/p).relative_to(root)) for p in ['AGENTS.md','CLAUDE.md','ABM_ACCEPTANCE_SPEC.md','ABM_CONTRACTS.md','ABM_BRIEF.md','ABM_BUILD_INSTRUCTIONS.md','ABM_LEDGER.md','ABM_CAMPAIGN_JOURNAL.md','ENGINEERING_LOG.md','DECIDE.md','QA/README.md','QA/MASTER_QA_TEST_PLAN.md','QAM/README.md','QAM/MANIFEST.md','QAM/STATE.md','QAM/EXECUTION_INSTRUCTIONS.md','QAM/AGENTS.md','QAM/CLAUDE.md'] if (module/p).is_file()]
evidence.mkdir(parents=True,exist_ok=False);review.mkdir(parents=True,exist_ok=False)
for p in doc_paths:save(evidence/'before'/p,(root/p).read_text())
save(evidence/'source-before.json',{'count':len(files),'sha256':identity,'files':files})
preserved={}
for directory in ['outputs','agent_docs/RESPONSES','agent_docs/SKILLS','agent_docs/ACTION/wf-scrapper-abm/EVIDENCE']:
 for p in (root/directory).rglob('*'):
  if p.is_file() and not p.is_symlink() and not p.is_relative_to(evidence) and not p.is_relative_to(review):preserved[p.relative_to(root).as_posix()]=sha(p.read_bytes())
save(evidence/'preservation-before.json',{'files':preserved,'count':len(preserved)})
archives=[]
for name in ['response_2026-10-11_210309_prepare-v01.zip','response_2026-10-13_223736_growth-call-follow-up.zip']:
 p=root/'agent_docs/RESPONSES'/name
 with ZipFile(p) as z:
  assert z.testzip() is None
  bodies=[a for a in z.infolist() if a.filename.endswith('/body')]
  archives.append({'file':str(p.relative_to(root)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'body_count':len(bodies),'body_bytes':sum(a.file_size for a in bodies)})
preflight={'started_at':now.isoformat(),'repo':str(root),'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'dirty_status_before':git('status','--short').splitlines(),
 'shot1_source_sha256':base['sha256'],'current_source_sha256':identity,'count':len(files),'differences':changed,
 'environment':{'python':platform.python_version(),'platform':platform.platform(),'packages':{n:importlib.metadata.version(n) for n in ['crawl4ai','playwright','beautifulsoup4','pytest','markdown-it-py']},'dependency_hashes':{p:sha((root/p).read_bytes()) for p in ['requirements.txt','requirements-lock.txt']}},'retained_fixture_archives':archives,'independent_qa':'NOT RUN'}
save(evidence/'preflight.json',preflight)
config={'root':str(root),'tag':tag,'evidence':str(evidence),'review':str(review),'report':str(root/'agent_docs/RESPONSES'/f'response_{tag}_current-tool-readiness.md'),
 'zip':str(Path('/home/moose/Downloads')/f'WebFactory_Engineering_Readiness_and_QA_Handoff_{tag}.zip'),'source_sha256':identity,'head':preflight['head'],'doc_paths':doc_paths}
save(Path('/tmp/web-recon-readiness-config.json'),config)
session=root/'agent_docs/SESSIONS/session_2026-10-14.md'
with session.open('a') as f:f.write(f'''\n\n## {now.isoformat()} — Shot 2 engineering readiness APPROVED → IN PROGRESS\n\nJARVIS reviewed Shot1 dated2026-10-14_173927; Tony authorizes current-tool documentation/readiness, retained-fixture verification and reproducible access, one combined three-module engineering run with loopback browser fixtures, accepted-package source checks and one self-contained QA handoff ZIP. No extra planning approval. Source52 `{identity}` matches Shot1; branch wf-scrapper-abm, HEAD `{preflight['head']}` plus preserved dirty work. Growth helper limitation remains agent-reviewed; no product/test/helper repair or automatic iframe collection. Preserve failures and continue safe checks. No external traffic, dependencies/Git/destructive actions/independent QA/final closeout/playbook. Evidence `{evidence.relative_to(root)}`.\n''')
print(json.dumps({'tag':tag,'evidence':str(evidence),'review':str(review),'branch':preflight['branch'],'head':preflight['head'],'source':identity,'retained_archives':archives,'preserved_files':len(preserved)},indent=2))
