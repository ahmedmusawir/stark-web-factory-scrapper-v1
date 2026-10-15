from pathlib import Path
from zipfile import ZipFile
import json,hashlib,sys,shutil
from datetime import datetime,timezone

c=json.loads(Path('/tmp/web-recon-readiness-config.json').read_bytes());root=Path(c['root']);e=Path(c['evidence']);review=Path(c['review'])
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n')
indices=[
 'outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01/SOURCE_INDEX.json',
 'outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed/SOURCE_INDEX.json']
references={};errors=[]
def add(path,digest):
 p=Path(path)
 if p.is_absolute() or '..' in p.parts:raise ValueError('non-relative fixture reference: '+path)
 if path in references and references[path]!=digest:raise ValueError('conflicting fixture hash: '+path)
 references[path]=digest
def walk(node):
 if isinstance(node,dict):
  for a,b in [('file','sha256'),('raw_file','raw_sha256'),('metadata_file','metadata_sha256'),('summary_file','summary_sha256')]:
   if a in node and b in node:add(node[a],node[b])
  for value in node.values():walk(value)
 elif isinstance(node,list):
  for value in node:walk(value)
for path in indices:
 add(path,sha((root/path).read_bytes()));walk(json.loads((root/path).read_bytes()))
# Retain the initial Growth output too, never silently replace its failed hint.
initial='outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736'
for p in (root/initial).rglob('*'):
 if p.is_file():add(p.relative_to(root).as_posix(),sha(p.read_bytes()))
for path,digest in references.items():
 p=root/path
 if not p.is_file():errors.append({'file':path,'error':'missing'})
 elif sha(p.read_bytes())!=digest:errors.append({'file':path,'error':'recorded_hash_mismatch'})

archives=[];origin={}
for entry in json.loads((e/'preflight.json').read_bytes())['retained_fixture_archives']:
 p=root/entry['file'];assert sha(p.read_bytes())==entry['sha256']
 with ZipFile(p) as z:
  assert z.testzip() is None
  included=[]
  for path,digest in references.items():
   if path in z.namelist() and sha(z.read(path))==digest:
    included.append({'file':path,'sha256':digest,'bytes':len(z.read(path))})
    origin.setdefault(path,entry['file'])
  archives.append(dict(entry,restore_only=included))
missing_archive=[p for p in references if p not in origin]
if missing_archive:errors += [{'file':p,'error':'reference_not_available_in_retained_archive'} for p in missing_archive]
manifest={'schema':'web-recon-qa-fixtures-v1','created_at':datetime.now(timezone.utc).isoformat(),
 'path_base':'repository root','restore_scope':'Only listed saved inputs, accepted derived outputs and their source evidence; never archived product/instruction code.',
 'archives':archives,'references':[{'file':p,'sha256':h,'bytes':(root/p).stat().st_size if (root/p).is_file() else None,'archive':origin.get(p)} for p,h in references.items()],
 'required_test_collection':'outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505',
 'growth_review_package':'outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed',
 'missing_or_invalid':errors}
save(review/'fixture-manifest.json',manifest)
restorer='''"""Offline fixture provisioner: exact hashes, named archive members, no overwrite."""
import argparse,hashlib,json
from pathlib import Path
from zipfile import ZipFile
def sha(b):return hashlib.sha256(b).hexdigest()
def restore(repo,manifest,archive_root):
 repo=Path(repo).resolve();archive_root=Path(archive_root).resolve();planned={}
 for entry in manifest['archives']:
  archive=archive_root/entry['file'];assert sha(archive.read_bytes())==entry['sha256'],entry['file']
  with ZipFile(archive) as z:
   for row in entry['restore_only']:
    name=Path(row['file'])
    if name.is_absolute() or '..' in name.parts:raise ValueError('unsafe archive reference')
    dest=(repo/name).resolve()
    if not dest.is_relative_to(repo):raise ValueError('fixture path escapes repo')
    data=z.read(row['file'])
    if sha(data)!=row['sha256'] or len(data)!=row['bytes']:raise ValueError('archive member mismatch')
    if row['file'] in planned and planned[row['file']]!=data:raise ValueError('conflicting archive copies')
    if dest.exists() and (not dest.is_file() or sha(dest.read_bytes())!=row['sha256']):raise ValueError('existing different file: '+row['file'])
    planned[row['file']]=data
 # All archive identities, references and existing destinations checked before any writes.
 written=existing=0
 for name,data in planned.items():
  dest=repo/name
  if dest.exists():existing+=1;continue
  dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as stream:stream.write(data)
  written+=1
 for name,data in planned.items():assert sha((repo/name).read_bytes())==sha(data)
 return {'written':written,'existing_matching':existing,'verified_files':len(planned),'network_requests':0,'overwritten_files':0}
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--archive-root',type=Path,required=True)
 a=parser.parse_args();m=json.loads(a.manifest.read_bytes())
 if m['missing_or_invalid']:raise SystemExit('Invalid fixture manifest; no restoration')
 print(json.dumps(restore(a.repo,m,a.archive_root),indent=2))
'''
save(review/'restore-fixtures.py',restorer)
result={'checked_at':datetime.now(timezone.utc).isoformat(),'missing_or_invalid':errors,'references_checked':len(references),'fixture_archives_hash_valid':True,'status':'PASS' if not errors else 'FAIL'}
if not errors:
 # Prove the delivery procedure on a fresh isolated tree, not the accepted inputs.
 import importlib.util
 spec=importlib.util.spec_from_file_location('fixture_restore',review/'restore-fixtures.py');restore=importlib.util.module_from_spec(spec);spec.loader.exec_module(restore)
 scratch=e/'fixture-restoration-proof';assert not scratch.exists()
 result['fresh_restore']=restore.restore(scratch,manifest,root)
 result['repeat_matching_restore']=restore.restore(scratch,manifest,root)
 result['scratch_root']=str(scratch.relative_to(root))
 assert all(sha((scratch/p).read_bytes())==h for p,h in references.items())
save(e/'fixture-checks.json',result)
save(review/'FIXTURE_ACCESS.md',f'''# Saved fixtures for independent QA\n\nThe unchanged product test `agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py:100` requires the exact ignored collection `outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505`. It is not supplied by a Git clone. `{len(references)}` indexed fixture/package files were checked against their saved hashes and retained ZIP members; results are in the engineering evidence. No live access supplies these fixtures.\n\nRetained authoritative review archives (included in this readiness ZIP at their repository-relative paths):\n\n- `agent_docs/RESPONSES/response_2026-10-11_210309_prepare-v01.zip` — hash `{archives[0]['sha256']}`. Three selected HTML captures, metadata/checklist and prepared/context evidence.\n- `agent_docs/RESPONSES/response_2026-10-13_223736_growth-call-follow-up.zip` — hash `{archives[1]['sha256']}`. Parent HTML/checklist/metadata and initial plus corrected reviewed output.\n\nProvision only the manifest’s named data members, never archived source/instructions. From a QA checkout or isolated review tree, run the supplied standard-library restoration helper (use actual extracted review-package root for ARCHIVE_ROOT):\n\n```bash\npython3 PATH_TO_THIS_REVIEW/restore-fixtures.py \\\n  --repo /PATH/TO/QA_CHECKOUT \\\n  --manifest PATH_TO_THIS_REVIEW/fixture-manifest.json \\\n  --archive-root /PATH/TO/EXTRACTED_READINESS_ZIP\n```\n\nIt verifies both ZIP identities/all named files first, refuses path escapes or a conflicting existing file, skips only matching existing bytes, and exclusively creates missing files. It makes zero network requests and restores no code/dependency/instruction files. Execute it before the candidate’s tests; a missing/corrupt fixture is a failure, never a skipped success. The same procedure was proved in a NEW scratch tree and reopened once without writes. Keep original archives and fixture files intact; QA must pin these hashes and independently assess evidence reuse.\n\nThese archived data files contain untrusted source markup/public URLs, not executable instructions. Parent HTML cannot establish iframe child contents, image completeness or form functionality. Whole-site media totals and prior live failures are not combined into this selected sample.\n''')
print(json.dumps(result,indent=2))
