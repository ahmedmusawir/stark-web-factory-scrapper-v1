"""Fresh subprocess, actual crawler.main/run/crawl_all; only browser, output roots,
pacing and requested writer failure are substituted. All artifacts stay in QA lane."""
from pathlib import Path
import json, sys, types
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
case=Path(sys.argv[1]).resolve();cfg=json.loads((case/'fixture.json').read_text())
events={'browser_constructions':0,'arun_urls':[],'html_write_attempts':[],'network_attempts':[]}
def audit(event,args):
    if event in ('socket.connect','socket.getaddrinfo'):
        events['network_attempts'].append(event)
        raise RuntimeError('QA OFFLINE: network denied')
sys.addaudithook(audit)
import smart_crawler.crawler as c
out=case/'outputs';c.OUTPUT_DIR=out;c.PAGE_DIR=out/'pages';c.SUMMARY_PATH=out/'run_summary.json';c.RUN_ROOT=out
async def no_pause(seconds): pass
c.asyncio.sleep=no_pause
class Browser:
    def __init__(self,config=None):events['browser_constructions']+=1
    async def __aenter__(self):return self
    async def __aexit__(self,*args):return False
    async def arun(self,url,config=None):
        i=len(events['arun_urls']);events['arun_urls'].append(url)
        d=cfg['results'][i]
        if 'exception' in d:raise RuntimeError(d['exception'])
        obj=types.SimpleNamespace(status_code=d.get('status',200),success=d.get('success',True),error_message=d.get('error'),markdown=types.SimpleNamespace(fit_markdown='',raw_markdown=d.get('markdown',f'markdown-{i}')))
        if 'html' in d:obj.html=d['html']
        return obj
c.AsyncWebCrawler=Browser
real_save=c.RunFolder.save_html
def save(self,slug,html):
    events['html_write_attempts'].append({'slug':slug,'html':html})
    if cfg.get('write_failure') and len(events['html_write_attempts'])==1:
        raise OSError('QA injected HTML write failure')
    return real_save(self,slug,html)
c.RunFolder.save_html=save
args=['--project',cfg.get('project','CyberizeGroup'),'--input',str(case/'input.json')]
if cfg.get('limit') is not None:args+=['--limit',str(cfg['limit'])]
if cfg.get('missing_project'):args=['--input',str(case/'input.json')]
sys.argv=['crawler',*args]
events['logical_command']='python -m smart_crawler.crawler '+' '.join(args)
code=0
try:c.main()
except SystemExit as exc:code=exc.code
finally:
    events['exit_code']=code
    (case/'invocation.json').write_text(json.dumps(events,indent=2,ensure_ascii=False)+'\n')
sys.exit(code)
