from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,re,subprocess
from bs4 import BeautifulSoup
from recon_pipeline.collector import load,valid_result
root=Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1');os.chdir(root)
c=json.loads(Path('/tmp/webfactory_growth_context.json').read_bytes());e=Path(c['evidence']);out=Path(c['prepared']);index=json.loads((out/'SOURCE_INDEX.json').read_bytes());collection=Path(c['collection']);state=load(collection)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
item=state['items'][0];meta=valid_result(collection,item)
assert len(state['items'])==1 and meta and item['status']=='completed' and item['url']==c['target'] and item['kind']=='page'
assert len(state['runs'])==1 and len(state['runs'][0]['requests'])==1
assert json.loads(Path(c['plan']).read_bytes())=={'pages':[c['target']],'rest':[]}
refs=[]
def check(path,expected):
 assert Path(path).is_file() and sha(path)==expected,path
 refs.append({'file':path,'sha256':expected,'bytes':Path(path).stat().st_size,'PASS':True})
check(index['checklist']['file'],index['checklist']['sha256'])
p=index['pages'][0]
for field,hfield in [('raw_file','raw_sha256'),('metadata_file','metadata_sha256')]:check(p['source'][field],p['source'][hfield])
check(p['prepared']['file'],p['prepared']['sha256']);check(index['boilerplate']['file'],index['boilerplate']['sha256'])
for entry in index['agent_authored']+index['supporting_evidence']:check(entry['file'],entry['sha256'])
h=BeautifulSoup(Path(p['source']['raw_file']).read_bytes().decode('utf-8'),'html.parser');main=h.select(p['extraction']['css_selector'])[0]
assert not main.get_text(' ',strip=True) and not main.select('h1,h2,h3,h4,h5,h6,p,li,a[href]')
assert not h.select('form,label')
booking=next(n for n in main.select('iframe[src]') if '/widget/booking/' in n['src'])
obs=json.loads((out/'EMBEDS_AND_FORM_LABELS.json').read_bytes());assert booking['src']==obs['booking_iframe']['source_url'] and booking.get('style')==obs['booking_iframe']['style']
assert h.title.get_text(' ',strip=True)==obs['page_title']
assert h.select_one('meta[name="description"]')['content']==obs['source_metadata_description']
assert obs['form_interactions']==obs['booking_attempts']==0 and obs['parent_document_forms']==obs['parent_document_labels']==0
md=Path(p['prepared']['file']).read_text();native=md.split('<!-- MAIN CONTENT -->')[1].split('<!-- END MAIN CONTENT -->')[0];assert not native.strip()
assert booking['src'] in md and 'unavailable' in md
links=[]
for path in out.rglob('*.md'):
 for target in re.findall(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)',path.read_text()):
  if target.startswith(('http:','https:','mailto:','tel:','#')):continue
  resolved=(path.parent/target.split('#')[0]).resolve();assert resolved.exists(),(path,target)
  links.append({'owner':str(path),'target':str(resolved.relative_to(root)),'resolves':True})
old=json.loads((e/'preservation-before.json').read_bytes());differences=[]
for path,expected in old.items():
 pth=Path(path)
 if not pth.is_file() or pth.stat().st_size!=expected['bytes'] or sha(pth)!=expected['sha256']:differences.append(path)
assert not differences,differences
source={p:sha(p) for p in c['source']['files']};assert source==c['source']['files'];assert hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()==c['source']['sha256']
run=state['runs'][0]
result={'verified_at':datetime.now(timezone.utc).isoformat(),'branch':c['branch'],'head':c['head'],'source_inventory_sha256':c['source']['sha256'],'source_files':52,'source_unchanged':True,'selection':{'html_urls':[c['target']],'rest':[],'selection_file':c['selection'],'selection_sha256':sha(c['selection']),'plan_file':c['plan'],'plan_sha256':sha(c['plan']),'reuse':'No prior valid completed HTML; one fresh attempt'},'collection':c['collection'],'run':run,'collect_command':json.loads((e/'collect-command.json').read_bytes()),'prepare_command':json.loads((e/'prepare-command.json').read_bytes()),'prepared':str(out),'initial_prepared':c['initial_prepared'],'collection_outcome':run['collection_outcome'],'cleanup_error':run['cleanup_error'],'preparation_coverage':'Parent-page evidence prepared; child booking details UNKNOWN / PARTIAL','items':[{'id':item['id'],'status':meta['status'],'final_url':meta['final_url'],'saved_at':meta['saved_at'],'html_bytes':meta['bytes'],'body_sha256':meta['sha256'],'body_complete':meta['body_complete'],'valid_result':True}],'observations':obs,'verified_references':refs,'reference_count':len(refs),'document_links':links,'actual_source_comparison':{'main_headings':0,'main_paragraphs':0,'main_list_items':0,'main_links':0,'parent_forms':0,'parent_labels':0,'booking_iframe_present':True,'title_description_style_source_match':True,'child_form_labels':'UNKNOWN, not saved','annotation_headings':'agent-authored, not source headings'},'focused_checks':json.loads((e/'focused-prepare/result.json').read_bytes()),'preservation':{'existing_files':len(old),'changed_or_missing':differences,'accepted_baseline_unchanged':True,'collector_recon_prepare_skill_unchanged':True},'collection_persisted_bytes':sum(p.stat().st_size for p in collection.rglob('*') if p.is_file()),'rest_requests':0,'additional_planned_calls':0,'form_submissions':0,'bookings':0,'independent_qa':'NOT RUN'}
(e/'verification-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'references':len(refs),'previous_files_preserved':len(old),'html_bytes':meta['bytes'],'body_sha256':meta['sha256'],'collection_persisted_bytes':result['collection_persisted_bytes'],'main_text_empty':True,'booking_iframe_present':True,'parent_form_labels':0,'inner_form_labels':'UNKNOWN','source_unchanged':True},indent=2))
