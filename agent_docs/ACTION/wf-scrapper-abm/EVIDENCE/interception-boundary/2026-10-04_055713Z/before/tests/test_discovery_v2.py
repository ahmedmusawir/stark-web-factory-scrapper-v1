"""F-01 facts: six healthy routes, required 404 route, aliases and off-host drops."""
import asyncio
import hashlib
from discover_site.sitemap_utils import discover, canonical_url


def test_f01_discovery_facts(tmp_path):
    root='https://example.com'
    healthy=['/','/about/','/services/','/contact/','/article/','/rendered-only/']
    paths=healthy+['/missing/']
    def xml(kind, entries):
        child='sitemap' if kind=='sitemapindex' else 'url'
        return ('<'+kind+' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<{child}><loc>{u}</loc></{child}>' for u in entries)+'</'+kind+'>').encode()
    bodies={root+'/robots.txt':b'User-agent: *\nDisallow: /private/\nSitemap: https://example.com/sitemap.xml\n',
            root+'/sitemap.xml':xml('sitemapindex',[root+'/a.xml',root+'/b.xml']),
            root+'/a.xml':xml('urlset',[root+p for p in paths]),
            root+'/b.xml':xml('urlset',[root+'/about/?utm_source=duplicate','https://outside.invalid/path'])}
    class Browser:
        calls=[]
        def scoped(self,url): return url.startswith(root+'/')
        async def read(self,url):
            self.calls.append(url)
            return {'status':200,'body':bodies[url],'transport':'fixture browser adapter','boundary':'fixture bytes'}
    browser=Browser()
    routes,absences,state=asyncio.run(discover(root,browser,tmp_path))
    assert state=='complete' and [r['url'] for r in routes['routes']]==[root+p for p in paths]
    assert routes['counts']=={'loc_total':9,'routes':7,'dropped':2}
    assert routes['routes'][1]['aliases']==[root+'/about/?utm_source=duplicate']
    assert [d['reason'] for d in routes['dropped']]==['duplicate','off_host']
    assert absences[0]['reason']=='off_host' and len(browser.calls)==4
    for source in routes['sources']:
        assert (tmp_path/source['file']).read_bytes()==bodies[source['url']]
        assert hashlib.sha256((tmp_path/source['file']).read_bytes()).hexdigest()==source['sha256']


def test_canonical_identity():
    assert canonical_url('HTTPS://Example.com:443//a/%7e?q=%2F&utm_source=x#f')=='https://example.com/a/~/?q=%2F'
    assert canonical_url('http://example.com/a.xml')=='http://example.com/a.xml'
    assert canonical_url('https://example.com/?utm=x')=='https://example.com/?utm=x'


def test_first_valid_fallback_wins_without_erasing_failed_attempts(tmp_path):
    origin='https://example.com'
    class Browser:
        calls=[]
        def scoped(self,url):return url.startswith(origin+'/')
        async def read(self,url):
            self.calls.append(url)
            if url.endswith('robots.txt'):return {'status':404,'body':b'no robots'}
            if url.endswith('sitemap.xml'):return {'status':200,'body':b'not XML'}
            if url.endswith('sitemap_index.xml'):return {'status':200,'body':b'<urlset><url><loc>https://example.com/about/</loc></url></urlset>'}
            raise AssertionError('unexpected fallback request')
    browser=Browser();routes,absences,state=asyncio.run(discover(origin,browser,tmp_path))
    assert state=='complete' and [r['url'] for r in routes['routes']]==[origin+'/about/']
    assert browser.calls==[origin+'/robots.txt',origin+'/sitemap.xml',origin+'/sitemap_index.xml']
    assert routes['sitemap_url_used']==origin+'/sitemap_index.xml'
    assert [a['reason'] for a in absences]==['robots_unavailable','malformed_sitemap']
    assert len(routes['sources'])==3 and all((tmp_path/s['file']).exists() for s in routes['sources'])


def test_selected_index_failed_child_stays_partial_without_root_fallback(tmp_path):
    origin='https://example.com'
    class Browser:
        calls=[]
        def scoped(self,url):return url.startswith(origin+'/')
        async def read(self,url):
            self.calls.append(url)
            return {origin+'/robots.txt':{'status':200,'body':b'User-agent: *'},
                    origin+'/sitemap.xml':{'status':200,'body':b'<sitemapindex><sitemap><loc>https://example.com/child.xml</loc></sitemap></sitemapindex>'},
                    origin+'/child.xml':{'status':404,'body':b'child missing'}}[url]
    browser=Browser();routes,absences,state=asyncio.run(discover(origin,browser,tmp_path))
    assert state=='partial' and not routes['routes']
    assert browser.calls==[origin+'/robots.txt',origin+'/sitemap.xml',origin+'/child.xml']
    assert absences[0]['reason']=='sitemap_unavailable'
