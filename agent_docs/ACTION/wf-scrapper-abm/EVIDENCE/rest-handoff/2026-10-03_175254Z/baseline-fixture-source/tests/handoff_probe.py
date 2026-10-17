"""Bounded native handoff measurements; fixture instrumentation, never live.

Marks report browser performance time and Python delivery time separately. The
compact candidate changes only result encoding, not fetch/identity/interception.
No body or full CDP result is printed or copied into measurement logs.
"""
import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path
import time

from smart_crawler.browser_session import BrowserSession

SIZES=(1_500_000,4_000_000,8_000_000,10*1024*1024+4096)


def rest_payload(size):
    objects=[]
    for i in range(100):
        objects.append({'id':i+1,'type':'post','link':f'http://127.0.0.1/article-{i}/',
            'slug':f'article-{i}','status':'publish','date':'2026-01-01T00:00:00',
            'modified':'2026-01-01T00:00:00','title':{'rendered':'বাংলা café 😀 '+str(i)},
            'content':{'rendered':''},'excerpt':{'rendered':'Unicode résumé — 中文'},
            'author':1,'featured_media':0,'categories':[1,2],'tags':[3],
            'yoast_head':'<title>Preserve source SEO</title>',
            'yoast_head_json':{'title':'বাংলা café 😀','schema':{'@graph':[{'@type':'Article'}]}},
            'unknown':{'large':900719925474099312345,'null':None,'boolean':False,
                       'escaped':'line\nquote"slash\\','padding':''}})
    def encode():return (json.dumps(objects,ensure_ascii=False,indent=1)+'\r\n').encode()
    unit='<p>বাংলা café 😀 中文; public facts, full fields and Unicode survive unchanged.</p>'
    repeats=(size-len(encode()))//(100*len(unit.encode()))
    assert repeats>=0
    for obj in objects:obj['content']['rendered']=unit*repeats
    objects[-1]['unknown']['padding']='x'*(size-len(encode()))
    result=encode();assert len(result)==size
    return result


class MeasuredSession(BrowserSession):
    representation='product'

    async def created(self,*args,**kwargs):
        page=await super().created(*args,**kwargs)
        if not getattr(self,'measurement_listener',False):
            self.measurement_listener=True
            self.cdp.on('Runtime.bindingCalled',self.measurement)
        return page

    def measurement(self,value):
        if value.get('name')!='abmFixtureMark':return
        payload=json.loads(value['payload'])
        self.event('fixture_browser_mark',execution_context=value['executionContextId'],**payload)

    async def correlated_read(self,expression):
        # Assert instrumentation anchors rather than silently dropping measures.
        marker='let chunks=[], count=0;'
        assert expression.count(marker)==1
        expression=expression.replace(marker,marker+"""
            let encodingMs=0;
            const mark=(stage)=>globalThis.abmFixtureMark(JSON.stringify({
                stage,bytes:count,encoding_ms:encodingMs,browser_ms:performance.now(),
                browser_wall_ms:Date.now()}));
            mark('script_entered');
        """)
        array='chunks.push(Array.from(value.slice(0,room)));'
        compact_candidate=self.representation=='compact_candidate'
        if array in expression:
            conversion=array if not compact_candidate else """
                for(let offset=0;offset<Math.min(value.length,room);offset+=32768) {
                    chunks.push(btoa(String.fromCharCode(...value.subarray(
                        offset,Math.min(offset+32768,value.length,room)))));
                }
            """
            expression=expression.replace(array,'const encodingStart=performance.now();'+conversion+
                'encodingMs+=performance.now()-encodingStart;')
        else:
            assert not compact_candidate, 'candidate only compares against the unmodified number-array reader'
            marker='append(value.subarray(0,room));'
            assert expression.count(marker)==1
            expression=expression.replace(marker,'const encodingStart=performance.now();'+marker+
                'encodingMs+=performance.now()-encodingStart;')
        marker='if(done) break;';assert expression.count(marker)==1
        expression=expression.replace(marker,"if(done) {mark('body_consumed'); break;}")
        marker='await reader.cancel(); ctl.abort();';assert expression.count(marker)==1
        expression=expression.replace(marker,"mark('cap_prefix_consumed'); "+marker)
        marker='finally { clearTimeout(timer); }';assert expression.count(marker)==1
        expression=expression.replace(marker,"finally { clearTimeout(timer); mark('result_prepared'); }")
        result=await super().correlated_read(expression)
        self.event('fixture_python_result_received',bytes=result['bytes'],chunks=len(result['chunks']),
                   scalar_items=sum(len(x) for x in result['chunks']),representation=self.representation)
        if compact_candidate:
            result['chunks']=[base64.b64decode(x,validate=True) for x in result['chunks']]
        return result

    async def run_read_script(self,op):
        await self.cdp.send('Runtime.addBinding',{'name':'abmFixtureMark','executionContextId':op.context_id})
        return await super().run_read_script(op)

    async def __aexit__(self,*args):
        self.event('fixture_cleanup_start')
        try:return await super().__aexit__(*args)
        finally:self.event('fixture_cleanup_complete')


def retain_measurement(folder,name,session,timeline,result,expected,elapsed):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    wanted=expected[:session.bounds.response_bytes]
    body=result.get('body',b'') if result else b''
    value={'name':name,'representation':session.representation,'expected_bytes':len(expected),
        'expected_sha256':hashlib.sha256(expected).hexdigest(),'expected_returned_bytes':len(wanted),
        'expected_returned_sha256':hashlib.sha256(wanted).hexdigest(),
        'returned_bytes':len(body),'returned_sha256':hashlib.sha256(body).hexdigest(),
        'exact_bytes':body==wanted,'result':{k:result.get(k) for k in ('status','bytes','incomplete','error','sha256','evidence_gap')} if result else None,
        'elapsed_s':elapsed,'stop_reason':session.stop_reason,'dispatches':session.dispatches,
        'browser_events':session.events,'server_events':timeline,'runtime':session.runtime}
    assert len(session.events)<5000 and len(timeline)<1000
    data=json.dumps(value,indent=2)+'\n';assert len(data.encode())<2_000_000
    with (folder/(name+'.json')).open('x') as f:f.write(data)
    return value
