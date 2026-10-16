"""Offline fixture provisioner: exact hashes, named archive members, no overwrite."""
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
