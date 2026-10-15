"""Engineering inspection of accepted saved packages; offline, no outputs overwritten."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,sys,socket,importlib.util
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

c=json.loads(Path('/tmp/web-recon-readiness-config.json').read_bytes());root=Path(c['root']);e=Path(c['evidence']);sys.path.insert(0,str(root))
def forbidden(*a,**kw):raise AssertionError('Offline source checks attempted network')
socket.socket.connect=forbidden;socket.create_connection=forbidden
from recon_pipeline.collector import load,valid_result
spec=importlib.util.spec_from_file_location('current_prepare_helper',root/'agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
def sha(data):return hashlib.sha256(data).hexdigest()
def text(node):return ' '.join(node.get_text(' ',strip=True).split())
results=[];refs={};links=[]
def check(name,work):
 try:
  details=work();results.append({'name':name,'status':'PASS','details':details})
 except Exception as ex:results.append({'name':name,'status':'FAIL','error':type(ex).__name__+': '+str(ex)[:500]})
def walk(value):
 if isinstance(value,dict):
  for a,b in [('file','sha256'),('raw_file','raw_sha256'),('metadata_file','metadata_sha256'),('summary_file','summary_sha256')]:
   if a in value and b in value:
    assert (root/value[a]).is_file(),value[a]
    assert sha((root/value[a]).read_bytes())==value[b],value[a]
    refs[value[a]]=value[b]
  for item in value.values():walk(item)
 elif isinstance(value,list):
  for item in value:walk(item)
first=root/'outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01'
growth=root/'outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed'
for package in [first,growth]:
 def references(package=package):
  index=json.loads((package/'SOURCE_INDEX.json').read_bytes());walk(index)
  state=load(root/index['source_collection'])
  for item in state['items']:
   assert item['status']=='completed' and valid_result(root/index['source_collection'],item),item['id']
  for row in index['pages']:
   item=next(i for i in state['items'] if i['id']==row['id']);meta=valid_result(root/index['source_collection'],item)
   assert row['url']==item['url'] and row['capture_saved_at']==meta['saved_at']
   assert row['source']['raw_sha256']==meta['sha256'] and row['source']['raw_bytes']==meta['bytes']
   assert BeautifulSoup((root/row['source']['raw_file']).read_bytes().decode('utf-8'),'html.parser').select(row['extraction']['css_selector'])
  return {'package':str(package.relative_to(root)),'pages':len(index['pages']),'all_completed_refs_valid':True,'hashes_and_css_locators_valid':True}
 check('saved references: '+package.name,references)

index=json.loads((first/'SOURCE_INDEX.json').read_bytes())
for row in index['pages']:
 def content(row=row):
  raw=BeautifulSoup((root/row['source']['raw_file']).read_bytes().decode('utf-8'),'html.parser')
  node=raw.select(row['extraction']['css_selector'])[0]
  for b in node.select(helper.BOILERPLATE):b.decompose()
  generated=(root/row['prepared']['file']).read_text().split('<!-- MAIN CONTENT -->',1)[1]
  md=BeautifulSoup(MarkdownIt().render(generated),'html.parser')
  heads=[text(n) for n in node.select('h1,h2,h3,h4,h5,h6')]
  assert heads==[text(n) for n in md.select('h1,h2,h3,h4,h5,h6')],'heading mismatch'
  paragraphs=[text(p) for p in node.select('p') if text(p)]
  rendered=[text(p) for p in md.select('p')]
  assert all(p in rendered for p in paragraphs),'paragraph loss'
  items=[text(li) for li in node.select('li') if text(li)]
  assert items==[text(li) for li in md.select('li')],'list order/value mismatch'
  meaningful={(text(a),urljoin(row['final_url'],a['href'])) for a in node.select('a[href]') if text(a) and a['href'].startswith(('/','http','mailto:','tel:','#'))}
  retained={(text(a),a['href']) for a in md.select('a[href]')}
  assert meaningful<=retained,'CTA/link destination loss'
  assert not md.select('script,style'),'active source script/style in prepared main'
  kind=row['document_type']
  if kind=='landing page':assert len(paragraphs)==15 and len(items)==3 and len(heads)==13
  elif kind=='category/article listing':
   assert 'category-agency-services' in raw.body['class']
   assert len(paragraphs)==22 and len(items)==2 and len(heads)==7
   assert 'Page 1 of 7' in text(md)
  elif kind=='article':assert len(paragraphs)==7 and len(items)==15 and len(heads)==6
  else:raise AssertionError('unexpected sample type')
  return {'id':row['id'],'url':row['url'],'classification':kind,'headings':len(heads),'paragraphs':len(paragraphs),'list_items':len(items),'meaningful_links_retained':len(meaningful),'source_fidelity':True,'no_viewport_image_or_hidden_content_claim':True}
 check('content fidelity: '+row['url'],content)

def selection():
 folder=root/'outputs/selections/CyberizeGroup-first-selected-2026-10-11_203505'
 decision=json.loads((folder/'tony-decision.json').read_bytes());plan=json.loads((folder/'collector-plan.json').read_bytes())
 saved=root/'agent_docs/RESPONSES/response_2026-10-11_001956_label-cleanup-tony-choices_review/inventory.json'
 inventory=json.loads(saved.read_bytes());by_id={i['id']:i for i in inventory['items']}
 assert sha(saved.read_bytes())==decision['inventory_file_sha256']
 assert inventory['inventory_id']==decision['inventory_id']
 assert sorted(by_id[i]['row'] for i in decision['include_html'])==[1,3,9]
 assert not decision['include_rest'] and not plan['rest']
 assert set(plan['pages'])=={by_id[i]['url'] for i in decision['include_html']}=={p['url'] for p in index['pages']}
 assert all(row['selection']=='UNDECIDED' for row in inventory['items'])
 return {'recorded_by':decision['recorded_by'],'rows':[1,3,9],'html_scope':plan['pages'],'rest_scope':[],'inventory_unchanged_and_bound':True}
check('exact selected sample binding',selection)

def historical():
 entry=next(x for x in index['historical_context'] if x['kind']=='historical_single_post_rest')
 obj=json.loads((root/entry['source']['raw_file']).read_bytes())
 assert obj['id']==11945 and obj['content']['rendered']=='' and entry['capture_saved_at'].startswith('2026-10-07')
 meta=next(x for x in index['historical_context'] if x['kind']=='historical_wordpress_metadata')
 observed=[]
 for response in meta['responses']:
  data=json.loads((root/response['raw_file']).read_bytes())
  if response['purpose']=='wp_types':assert isinstance(data,dict) and len(data)==33
  else:
   assert isinstance(data,list) and len(data)==1 and 'content' not in data[0]
   expected='42' if response['purpose'].endswith('page') else '166'
   assert response['headers']['x-wp-total']==expected
   observed.append({'type':response['purpose'],'advertised_total':int(expected),'sampled_metadata_records':1,'full_content_requested':False})
 assert 'UNVERIFIED' in index['image_completeness']
 return {'post':11945,'rest_content':'present empty string, not missing/null','rest_date':entry['capture_saved_at'],'html_date':next(p['capture_saved_at'] for p in index['pages'] if p['document_type']=='article'),'types':33,'metadata':observed,'images':'UNVERIFIED'}
check('separately dated REST/context and honest unknowns',historical)

def embedded():
 ix=json.loads((growth/'SOURCE_INDEX.json').read_bytes());row=ix['pages'][0]
 raw=BeautifulSoup((root/row['source']['raw_file']).read_bytes().decode('utf-8'),'html.parser');main=raw.select(row['extraction']['css_selector'])[0]
 assert not text(main) and not main.select('h1,h2,h3,h4,h5,h6,p,li,a[href]')
 assert not raw.select('form,label')
 booking=next(n for n in main.select('iframe[src]') if '/widget/booking/' in n['src'])
 obs=json.loads((growth/'EMBEDS_AND_FORM_LABELS.json').read_bytes())
 assert booking['src']==obs['booking_iframe']['source_url'] and booking.get('style')==obs['booking_iframe']['style']
 assert raw.title.get_text(' ',strip=True)==obs['page_title']
 assert raw.select_one('meta[name="description"]')['content']==obs['source_metadata_description']
 assert obs['form_interactions']==obs['booking_attempts']==0
 assert 'booking' in row['document_type'].lower() or 'consultation' in row['document_type'].lower()
 assert helper.boundary(raw)[0]=='article'  # known unchanged hint, not a repaired capability
 md=(root/row['prepared']['file']).read_text()
 assert not md.split('<!-- MAIN CONTENT -->')[1].split('<!-- END MAIN CONTENT -->')[0].strip()
 assert booking['src'] in md and 'agent-authored' in md and 'unavailable' in md
 assert any('child' in gap for gap in row['gaps'])
 original=root/ix['initial_extraction']['directory']/'SOURCE_INDEX.json'
 assert json.loads(original.read_bytes())['pages'][0]['document_type']=='article'
 return {'url':row['url'],'delivered_classification':row['document_type'],'helper_hint':'article (known limitation; unchanged)','native_main_text':'empty','forms_and_labels_in_parent':0,'booking_source_url':booking['src'],'child_form_labels':'UNKNOWN','automatically_fetched_iframe':False,'new_capture_or_form_action':False,'initial_and_reviewed_packages_preserved':True}
check('Growth Call source interpretation',embedded)

def authored():
 for package in [first,growth]:
  brief=(package/'ARCHITECT_BRIEF.md').read_text();gaps=(package/'GAPS_AND_REQUESTS.md').read_text()
  assert re.search(r'^## .*source facts',brief,re.M|re.I)
  assert 'Agent interpretation' in brief and gaps.strip()
  for path in package.rglob('*.md'):
   for target in re.findall(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)',path.read_text()):
    if target.startswith(('http:','https:','mailto:','tel:','#')):continue
    dest=(path.parent/target.split('#')[0]).resolve();assert dest.is_file(),str(path.relative_to(root))+': '+target
    links.append({'owner':str(path.relative_to(root)),'target':str(dest.relative_to(root)),'resolves':True})
 return {'briefs':2,'gaps_documents':2,'source_and_interpretation_sections_distinct':True,'relative_links':len(links),'links_resolve':True}
check('authored briefs/gaps and package links',authored)
result={'verified_at':datetime.now(timezone.utc).isoformat(),'kind':'Engineering offline accepted-source checks','status':'FAIL' if any(r['status']=='FAIL' for r in results) else 'PASS','checks':results,'reference_count':len(refs),'references':[{'file':p,'sha256':h} for p,h in refs.items()],'package_links':links,'network_calls':0,'independent_qa':'NOT RUN'}
(e/'offline-content-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(results),'failures':[r for r in results if r['status']=='FAIL'],'references':len(refs),'relative_links':len(links),'network_calls':0},indent=2))
