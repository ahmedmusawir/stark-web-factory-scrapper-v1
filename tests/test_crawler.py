"""Offline tests for smart_crawler.crawler — crawl4ai results are stubbed, no network, no browser."""
import asyncio
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import smart_crawler.crawler as crawler
from discover_site import sitemap_utils

REPO_ROOT = Path(__file__).resolve().parents[1]


def _result(status, success=True, raw="body " * 200, error=None):
    """Shape of what crawl4ai 0.9.x arun() hands back, reduced to the fields the crawler reads."""
    return types.SimpleNamespace(
        status_code=status,
        success=success,
        error_message=error,
        markdown=types.SimpleNamespace(fit_markdown="", raw_markdown=raw),
    )


class FakeCrawler:
    def __init__(self, results):
        self._results = list(results)
        self.calls = []

    async def arun(self, url, config=None):
        self.calls.append(url)
        return self._results.pop(0)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Redirect outputs to tmp and make pacing instant."""
    monkeypatch.setattr(crawler, "PAGE_DIR", tmp_path / "pages")
    monkeypatch.setattr(crawler, "SUMMARY_PATH", tmp_path / "run_summary.json")
    crawler.PAGE_DIR.mkdir()
    sleeps = []

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr(crawler.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(crawler.random, "uniform", lambda a, b: 2.5)
    return types.SimpleNamespace(dir=tmp_path, sleeps=sleeps)


def _urls(n):
    return [f"https://example.com/p{i}" for i in range(n)]


def test_403_and_500_write_no_file_and_are_recorded(sandbox):
    fake = FakeCrawler([
        _result(403, success=False, raw="", error="Blocked by anti-bot protection: HTTP 403"),
        _result(500, success=False, raw=""),
        _result(200),
    ])
    pages, stopped = asyncio.run(crawler.crawl_all(_urls(3), fake))
    assert stopped is False
    assert [p["ok"] for p in pages] == [False, False, True]
    assert pages[0]["error"] == "blocked"
    assert pages[1]["error"] == "HTTP 500"
    assert pages[2]["error"] is None
    assert sorted(p.name for p in crawler.PAGE_DIR.iterdir()) == ["example-com-p2.md"]

    summary_path = crawler.write_summary(pages, "2026-09-05T00:00:00+00:00", "2026-09-05T00:01:00+00:00")
    summary = json.loads(summary_path.read_text())
    assert set(summary) == {"started_at", "finished_at", "crawl4ai_version", "pause_range_s", "pages"}
    assert summary["pause_range_s"] == [2, 5]
    assert [p["status"] for p in summary["pages"]] == [403, 500, 200]
    assert set(summary["pages"][0]) == {"url", "status", "ok", "elapsed_s", "error"}


def test_three_consecutive_429_stop_the_run(sandbox, capsys):
    fake = FakeCrawler([_result(429, success=False, raw="")] * 3 + [_result(200)])
    pages, stopped = asyncio.run(crawler.crawl_all(_urls(4), fake))
    assert stopped is True
    assert len(pages) == 3 and all(p["error"] == "blocked" for p in pages)
    assert fake.calls == _urls(3)  # 4th URL never attempted
    assert "3 consecutive blocked pages" in capsys.readouterr().out
    assert list(crawler.PAGE_DIR.iterdir()) == []


def test_blocked_counter_resets_on_success(sandbox):
    fake = FakeCrawler([
        _result(429, success=False, raw=""), _result(429, success=False, raw=""),
        _result(200),
        _result(403, success=False, raw=""), _result(403, success=False, raw=""),
        _result(200),
    ])
    pages, stopped = asyncio.run(crawler.crawl_all(_urls(6), fake))
    assert stopped is False and len(pages) == 6


def test_pause_between_pages_not_before_first(sandbox, capsys):
    fake = FakeCrawler([_result(200)] * 3)
    asyncio.run(crawler.crawl_all(_urls(3), fake))
    assert sandbox.sleeps == [2.5, 2.5]
    assert capsys.readouterr().out.count("⏸ pause 2.5s") == 2


def test_limit_and_input_flags(tmp_path):
    custom = tmp_path / "custom.json"
    custom.write_text(json.dumps([{"url": u} for u in _urls(5)]))
    args = crawler.parse_args(["--input", str(custom), "--limit", "3"])
    assert args.input == custom
    assert list(crawler.load_urls(args.input, args.limit)) == _urls(3)
    assert list(crawler.load_urls(custom, None)) == _urls(5)
    assert crawler.parse_args([]).input == REPO_ROOT / "outputs" / "discovered_pages.json"
    with pytest.raises(SystemExit):
        crawler.parse_args(["--limit", "0"])


def test_session_user_agent_on_sitemap_calls(monkeypatch):
    ua = sitemap_utils.USER_AGENT
    assert "Chrome/" in ua and "Safari/537.36" in ua
    assert sitemap_utils.SESSION.headers["User-Agent"] == ua
    assert crawler.USER_AGENT == ua

    seen = []

    def fake_get(url, timeout=10):
        seen.append(url)
        body = '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/a</loc></url></urlset>'
        return types.SimpleNamespace(content=body.encode(), raise_for_status=lambda: None)

    monkeypatch.setattr(sitemap_utils.SESSION, "get", fake_get)
    monkeypatch.setattr(sitemap_utils.requests, "get", lambda *a, **k: pytest.fail("bare requests.get used"))
    assert sitemap_utils.fetch_sitemap_urls("https://example.com/") == ["https://example.com/a"]
    assert seen == ["https://example.com/sitemap.xml"]


def test_import_from_foreign_cwd_creates_no_directory(tmp_path):
    code = f"import sys; sys.path.insert(0, {str(REPO_ROOT)!r}); import smart_crawler.crawler"
    subprocess.run([sys.executable, "-c", code], cwd=tmp_path, check=True)
    assert list(tmp_path.iterdir()) == []
