"""Sitemap parsing tests for discover_site.sitemap_utils with SESSION.get stubbed — no network."""
import discover_site.sitemap_utils as sitemap_utils

NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'

FLAT = f'<?xml version="1.0"?><urlset {NS}><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>'
INDEX = f'<?xml version="1.0"?><sitemapindex {NS}><sitemap><loc>https://example.com/child.xml</loc></sitemap></sitemapindex>'
CHILD = f'<?xml version="1.0"?><urlset {NS}><url><loc>https://example.com/services</loc></url></urlset>'


class _Resp:
    def __init__(self, body: str):
        self.content = body.encode()

    def raise_for_status(self):
        pass


def _stub(mapping):
    def fake_get(url, timeout=10):
        return _Resp(mapping[url])
    return fake_get


def test_flat_sitemap_returns_all_locs(monkeypatch):
    monkeypatch.setattr(sitemap_utils.SESSION, "get", _stub({"https://example.com/sitemap.xml": FLAT}))
    assert sitemap_utils.fetch_sitemap_urls("https://example.com/") == [
        "https://example.com/",
        "https://example.com/about",
    ]


def test_sitemap_index_follows_child_sitemaps(monkeypatch):
    monkeypatch.setattr(sitemap_utils.SESSION, "get", _stub({
        "https://example.com/sitemap.xml": INDEX,
        "https://example.com/child.xml": CHILD,
    }))
    assert sitemap_utils.fetch_sitemap_urls("https://example.com/") == ["https://example.com/services"]


def test_unparseable_sitemap_returns_empty(monkeypatch):
    monkeypatch.setattr(sitemap_utils.SESSION, "get", _stub({"https://example.com/sitemap.xml": "not xml"}))
    assert sitemap_utils.fetch_sitemap_urls("https://example.com/") == []
