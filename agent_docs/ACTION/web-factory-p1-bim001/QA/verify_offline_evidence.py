from offline_driver import *
import xml.etree.ElementTree as ET
facts=json.loads((EV/'static_facts.json').read_text())
results={}
for stage in ['targeted','regression_root','regression_tmp']:
    xml=ET.parse(EV/f'{stage}.xml')
    nodes=xml.findall('.//testcase')
    results[stage]={'count':len(nodes),'failures':sum(n.find('failure') is not None for n in nodes),'errors':sum(n.find('error') is not None for n in nodes),'skipped':sum(n.find('skipped') is not None for n in nodes),'cases':[dict(name=n.attrib['name'],classname=n.attrib['classname'],time=n.attrib['time'],passed=not list(n)) for n in nodes]}
    assert results[stage]['count']==(40 if stage=='targeted' else 54)
    assert results[stage]['failures']==results[stage]['errors']==results[stage]['skipped']==0
baseline=[]
for f in facts['baseline_assertions']:
    entry=dict(f)
    for stage in ['regression_root','regression_tmp']:
        found=[n for n in results[stage]['cases'] if n['name']==f['name']]
        entry[stage+'_passed']=len(found)==1 and found[0]['passed']
        assert entry[stage+'_passed'] and f['exact_equal']
    baseline.append(entry)
dump(EV/'pytest_verified.json',results);dump(EV/'bim000_passing_proof.json',baseline)
expected={'normal':['captured','captured'],'empty':[],'limit':['captured','captured'],'stop':['blocked']*3,'mixed':['captured','blocked','failed','failed','unsupported','captured','failed'],'collision':['captured']*3,'write_failure':['failed','captured'],'port':['captured']*2,'empty_html':['unsupported'],'two_runs':['captured']}
extra={}
for name,wanted in expected.items():
    case=EV/'artifact_cases'/name
    run=sorted((case/'outputs/CyberizeGroup/runs').iterdir())[-1]
    manifest=json.loads((run/'manifest.json').read_text());pages=manifest['pages']
    actual=[p['outcome'] for p in pages]
    htmls=sorted(p.name for p in (run/'html').iterdir())
    mapped=sorted(Path(p['html_file']).name for p in pages if p['html_file'])
    checks={'expected_outcomes':actual==wanted,'no_unmapped_html':htmls==mapped}
    if name=='mixed':
        checks.update(http500_no_html=pages[2]['html_file'] is None,exception_prefix=pages[3]['reason'].startswith('exception:'),missing_html_reason='html' in pages[4]['reason'],empty_markdown_independence=pages[5]['outcome']=='captured' and pages[5]['ok'] is False and pages[5]['error']=='empty markdown' and pages[5]['md_file'] is None)
    assert all(checks.values()),(name,checks)
    extra[name]={'checks':checks,'actual_outcomes':actual,'html_files':htmls}
dump(EV/'artifact_supplement.json',extra)
# Explicit frozen key source/AST evidence, without importing application.
src=(ROOT/'smart_crawler/crawler.py').read_text();tree=ast.parse(src)
keys={}
for name in ['write_summary','crawl_page']:
    fn=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    variable='summary' if name=='write_summary' else 'record'
    assignment=next(n for n in ast.walk(fn) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==variable for t in n.targets))
    keys[name]=dict(line=assignment.lineno,keys=sorted(ast.literal_eval(k) for k in assignment.value.keys))
assert keys['write_summary']['keys']==['crawl4ai_version','finished_at','pages','pause_range_s','started_at']
assert keys['crawl_page']['keys']==['elapsed_s','error','ok','status','url']
dump(EV/'frozen_summary_source_keys.json',keys)
notes=(ROOT/'RUN_NOTES.md').read_text();changelog=(ROOT/'CHANGELOG.md').read_text();section=changelog.split('## 2026-09-06 — [CC] Claude Code — bim001 Raw HTML Capture')[1].split('\n## ')[0]
docs={'ac81_sentence':[dict(line=i,text=line) for i,line in enumerate(notes.splitlines(),1) if 'Two-file state:' in line],'ac82_topics':{t:t in section for t in ['--project','outputs/<project>/runs/<run_id>/','HTML capture','manifest.json','absences.json','stage_log.txt','sandbox','test_empty_input_writes_truthful_summary_without_crawling','_result','no pin changes']}}
assert all(docs['ac82_topics'].values()) and len(docs['ac81_sentence'])==1
dump(EV/'docs_verified.json',docs)
final=snapshot();dump(EV/'outputs_final.json',final)
checks={'outputs_unchanged_through_execution':final==json.loads((EV/'outputs_initial.json').read_text()),'candidate_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'tracked_diff_empty':not subprocess.check_output(['git','diff','HEAD','--'],cwd=ROOT),'baseline_functions':len(baseline),'baseline_asserts':sum(x['count'] for x in baseline)}
assert checks['outputs_unchanged_through_execution'] and checks['tracked_diff_empty']
assert checks['candidate_head']=='657e25e9191e5d91a822a49301c0260bde8f1bd4'
dump(EV/'final_integrity.json',checks)
command('final_status',['git','status','--short'])
command('final_head',['git','rev-parse','HEAD'])
print(json.dumps(checks,indent=2))
