"""F-05: all declared source surfaces, off-scope inventory and scoped HEAD only."""
import asyncio
from smart_crawler.crawler import RunFolder, utc_now, record_capture
from smart_crawler.media_inventory import collect_media,srcset_urls

HTML='''<html><head><link rel="icon" href="/icon.ico"><meta property="og:image" content="/social.jpg">
<meta name="twitter:image" content="https://stage.mystagingwebsite.com/twitter.jpg"></head>
<body><img src="/image.png" srcset="/small.png 1x, /large.png 2x"><picture><source srcset="/picture.webp 1x"></picture>
<video poster="/poster.jpg"></video><div style="background-image:url('/background.jpg')"></div>
<script type="application/ld+json">{"image":"/ld-image.jpg","logo":{"url":"https://outside.invalid/logo.svg"}}</script></body></html>'''


class Browser:
    hosts={'example.com','www.example.com'}
    stop_reason=None
    def __init__(self):self.calls=[]
    def stop(self,reason):self.stop_reason=self.stop_reason or reason
    def scoped(self,url):return url.startswith('https://example.com/')
    async def read(self,url,method='GET'):
        assert method=='HEAD';self.calls.append(url)
        return {'status':200,'url':url,'body':b'','headers':{'content-type':'image/png','content-length':'200'},'transport':'fixture HEAD adapter'}


def fixture(tmp_path):
    run=RunFolder('Media',utc_now(),root=tmp_path).create();url='https://example.com/'
    record_capture(run,{'url':url,'status':200,'ok':True,'error':None,'elapsed_s':0},url,HTML,True)
    obj={'id':1,'source_url':'https://example.com/image.png','mime_type':'image/png','alt_text':'Image',
         'media_details':{'width':20,'height':10,'sizes':{'small':{'source_url':'https://example.com/small.png'}}},
         'title':{'rendered':'Image'},'caption':{'rendered':'Caption'}}
    return run,{'objects/media-1.json':obj}


def test_all_sources_unique_scoped_heads_and_staging_inventory(tmp_path):
    run,objects=fixture(tmp_path);browser=Browser()
    absences=asyncio.run(collect_media(browser,run,objects))
    items={x['url']:x for x in run.media['items']}
    expected_internal={f'https://example.com/{name}' for name in ('image.png','small.png','large.png','picture.webp','poster.jpg','icon.ico','social.jpg','background.jpg','ld-image.jpg')}
    assert set(items)==expected_internal|{'https://stage.mystagingwebsite.com/twitter.jpg','https://outside.invalid/logo.svg'}
    assert set(browser.calls)==expected_internal and len(browser.calls)==9
    assert set(x['origin'] for x in items.values())=={'internal','external','staging_domain'}
    assert items['https://example.com/image.png']['wp_media_id']==1
    assert len(items['https://example.com/image.png']['provenance'])==2
    assert items['https://example.com/background.jpg']['source_pages'][0]['context']=='css_bg'
    for url in ('https://stage.mystagingwebsite.com/twitter.jpg','https://outside.invalid/logo.svg'):
        assert items[url]['retrieval']=={'method':'skipped','status':'skipped','reason':'off_scope_untested'}
        assert url not in browser.calls
    assert len(absences)==2 and run.streams['media']=='complete'
    assert not list(run.dir.rglob('*.png')) and not list(run.dir.rglob('*.jpg'))


def test_no_media_head_and_srcset_data_url(tmp_path):
    run,objects=fixture(tmp_path);browser=Browser()
    absences=asyncio.run(collect_media(browser,run,objects,no_head=True))
    assert not browser.calls and run.streams['media']=='skipped'
    assert len([a for a in absences if a['reason']=='disabled'])==9
    assert list(srcset_urls('data:image/png;base64,AAAA 1x, /other.png 2x'))==['data:image/png;base64,AAAA','/other.png']


def test_media_refusal_stops_later_heads(tmp_path):
    run,objects=fixture(tmp_path)
    class Refusing(Browser):
        async def read(self,url,method='GET'):
            self.calls.append(url)
            return {'status':429,'headers':{'retry-after':'17'},'transport':'fixture HEAD adapter'}
    browser=Refusing();absences=asyncio.run(collect_media(browser,run,objects))
    assert len(browser.calls)==1 and browser.stop_reason=='http_429'
    assert run.streams['media']=='partial'
    assert sum(a['outcome']=='blocked' for a in absences)==1
    assert sum(a['reason']=='stop_rule' for a in absences)==8
