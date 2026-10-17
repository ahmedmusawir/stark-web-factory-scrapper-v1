"""Sitemap parsing tests for discover_site.sitemap_utils with browser bytes injected — no network."""
import discover_site.sitemap_utils as sitemap_utils

NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'

FLAT = f'<?xml version="1.0"?><urlset {NS}><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>'
INDEX = f'<?xml version="1.0"?><sitemapindex {NS}><sitemap><loc>https://example.com/child.xml</loc></sitemap></sitemapindex>'
CHILD = f'<?xml version="1.0"?><urlset {NS}><url><loc>https://example.com/services</loc></url></urlset>'


class BrowserStub:
    def __init__(self,mapping): self.mapping=mapping;self.calls=[]
    def scoped(self,url): return url.startswith('https://example.com/')
    async def read(self,url):
        self.calls.append(url)
        return {'status':200,'body':self.mapping[url].encode(),'incomplete':False}


def test_flat_sitemap_returns_all_locs(monkeypatch):
    """E-06 / Contracts §1.1 — injected browser bytes, same XML facts and canonical identity."""
    import asyncio
    browser=BrowserStub({'https://example.com/sitemap.xml':FLAT})
    assert asyncio.run(sitemap_utils.fetch_sitemap_urls('https://example.com/',browser))==['https://example.com/','https://example.com/about/']


def test_sitemap_index_follows_child_sitemaps(monkeypatch):
    """E-06/E-05 — child XML uses the same serialized browser adapter; pacing proven separately."""
    import asyncio
    browser=BrowserStub({'https://example.com/sitemap.xml':INDEX,'https://example.com/child.xml':CHILD})
    assert asyncio.run(sitemap_utils.fetch_sitemap_urls('https://example.com/',browser))==['https://example.com/services/']
    assert browser.calls==['https://example.com/sitemap.xml','https://example.com/child.xml']


def test_unparseable_sitemap_returns_empty(monkeypatch):
    """E-06 — malformed XML is explicit failure, never silently an empty success."""
    import asyncio
    import pytest
    from xml.etree.ElementTree import ParseError
    browser=BrowserStub({'https://example.com/sitemap.xml':'not xml'})
    with pytest.raises(ParseError): asyncio.run(sitemap_utils.fetch_sitemap_urls('https://example.com/',browser))
