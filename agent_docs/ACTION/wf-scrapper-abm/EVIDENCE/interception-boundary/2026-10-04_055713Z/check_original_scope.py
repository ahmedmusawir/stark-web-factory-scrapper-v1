"""Run the unchanged new scope assertion against the preserved original controller."""
from pathlib import Path
import importlib.util
import json
import sys
import traceback

root=Path.cwd();e=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'tests'))
sys.path.insert(0,str(root))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    return value
baseline=module('preserved_controller',e/'before/smart_crawler/browser_session.py')
checks=module('boundary_assertions',root/'tests/test_interception_boundary.py')
checks.BrowserSession=baseline.BrowserSession
results=[]
for method in ['GET','HEAD']:
    tmp=e/'original-scope-controls'/method;tmp.mkdir(parents=True,exist_ok=False)
    try:
        checks.test_narrow_read_redirect_scope_prevents_target_dispatch(tmp,method)
        outcome='unexpected_pass'
    except AssertionError:
        outcome='required_scope_assertion_failed'
        (tmp/'assertion.txt').write_text(traceback.format_exc())
    data=json.loads((tmp/('narrow-scope-'+method+'.json')).read_text())
    redirected=[x for x in data['browser_events'] if x['event']=='request_classified' and '/never-boundary' in x['url']]
    denied=[x for x in data['browser_events'] if x['event']=='intentional_prevented' and x.get('reason')=='redirect_out_of_scope']
    assert outcome=='required_scope_assertion_failed'
    assert len(redirected)==1 and redirected[0]['classification']=='incidental' and redirected[0]['predecessor'] is None
    assert not denied
    assert any(x['event']=='incidental_prevented' and x['reason']=='fixture_egress' for x in data['browser_events'])
    assert not any(x['path']=='/never-boundary' for x in data['server_events'])
    results.append({'method':method,'scope_assertion':outcome,'classification':redirected[0],
                    'stop_reason':data['stop_reason'],'intentional_dispatches':data['dispatches'],
                    'destination_received':False,'blocked_by':'fixture-only incidental egress guard',
                    'evidence':str(tmp.relative_to(root))})
(e/'original-scope-results.json').write_text(json.dumps(results,indent=2)+'\n')
print('CONFIRMED: original controller has the same GET/HEAD redirect-classification gap; no target dispatch.')
