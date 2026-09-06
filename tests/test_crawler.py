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


def test_empty_input_writes_truthful_summary_without_crawling(sandbox, tmp_path, monkeypatch, capsys):
    """AC-21: a valid `[]` input is a run — zero crawls, summary written, stale records gone."""
    empty = tmp_path / "empty.json"
    empty.write_text("[]")
    crawler.SUMMARY_PATH.write_text(json.dumps({"pages": [{"url": "https://example.com/stale"}]}))

    async def no_crawl(urls):
        pytest.fail("run() must not be called for empty input")

    monkeypatch.setattr(crawler, "run", no_crawl)
    monkeypatch.setattr(sys, "argv", ["crawler", "--project", "TestProj", "--input", str(empty)])  # bim001 AC-71(b)
    crawler.main()  # the real application path

    summary = json.loads(crawler.SUMMARY_PATH.read_text())
    assert set(summary) == {"started_at", "finished_at", "crawl4ai_version", "pause_range_s", "pages"}
    assert summary["pages"] == []
    assert summary["crawl4ai_version"] and summary["pause_range_s"] == [2, 5]
    assert summary["started_at"] and summary["finished_at"]
    assert "No URLs found" in capsys.readouterr().out
    assert list(crawler.PAGE_DIR.iterdir()) == []


# ---------------------------------------------------------------------------
# bim001 — chunk 1: CLI + project identity (AC-01..08, AC-11, AC-63 partial)
# ---------------------------------------------------------------------------

def _one_url_input(tmp_path):
    f = tmp_path / "in" / "one.json"
    f.parent.mkdir()
    f.write_text(json.dumps([{"url": "https://example.com/a"}]))
    return f


def _run_main(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["crawler", *argv])
    with pytest.raises(SystemExit) as exc:
        crawler.main()
    return exc.value.code


def test_ac01_project_flag_optional_to_parser(capsys):
    args = crawler.parse_args(["--limit", "3"])  # no --project: parser does not complain
    assert args.project is None and args.limit == 3
    with pytest.raises(SystemExit) as exc:
        crawler.parse_args(["--help"])
    assert exc.value.code == 0
    assert "--project" in capsys.readouterr().out


def test_ac02_missing_project_refuses_before_crawl(sandbox, tmp_path, monkeypatch):
    src = _one_url_input(tmp_path)
    monkeypatch.setattr(crawler, "AsyncWebCrawler", lambda *a, **k: pytest.fail("browser constructed"))
    monkeypatch.setattr(crawler, "read_urls", lambda p: pytest.fail("input read before validation"))
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert _run_main(monkeypatch, ["--input", str(src)]) == 2
    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before == after  # nothing created under the (redirected) outputs root


def test_ac03_04_05_missing_project_message_lines(sandbox, tmp_path, monkeypatch, capsys):
    src = _one_url_input(tmp_path)
    assert _run_main(monkeypatch, ["--input", str(src)]) == 2
    out = capsys.readouterr()
    text = out.out + out.err
    assert "--project is required" in text
    assert "python -m smart_crawler.crawler --project CyberizeGroup --limit 10" in text
    assert "python -m smart_crawler.crawler --help" in text


@pytest.mark.parametrize("bad", ["Cyberize Group", "../x"])
def test_ac06_invalid_project_space_and_dotdot(sandbox, tmp_path, monkeypatch, capsys, bad):
    src = _one_url_input(tmp_path)
    before = sorted(tmp_path.rglob("*"))
    assert _run_main(monkeypatch, ["--project", bad, "--input", str(src)]) == 2
    text = "".join(capsys.readouterr())
    assert "--project is invalid" in text
    assert "python -m smart_crawler.crawler --project CyberizeGroup --limit 10" in text
    assert "python -m smart_crawler.crawler --help" in text
    assert sorted(tmp_path.rglob("*")) == before
    assert crawler.validate_project("CyberizeGroup") is None
    assert crawler.validate_project("a" * 64) is None and crawler.validate_project("a" * 65) == "invalid"


def test_ac08_help_and_limit_zero_preserved(capsys):
    with pytest.raises(SystemExit) as exc:
        crawler.parse_args(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "--input" in out and "--limit" in out
    with pytest.raises(SystemExit) as exc:
        crawler.parse_args(["--limit", "0"])
    assert exc.value.code == 2
    assert "--limit must be >= 1" in capsys.readouterr().err


def test_ac11_run_id_format_matches_started_at():
    import re
    started = "2026-09-06T14:30:00+00:00"
    run_id = crawler.make_run_id(started)
    assert run_id == "2026-09-06T14-30-00Z"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z", run_id)
    assert run_id[:10] == started[:10] and run_id[11:19].replace("-", ":") == started[11:19]


def test_ac63_exit_codes_missing_input_and_project(sandbox, tmp_path, monkeypatch):
    # input file missing (valid project) -> exit 1, as bim000
    assert _run_main(monkeypatch, ["--project", "TestProj", "--input", str(tmp_path / "nope.json")]) == 1
    # read_urls / load_urls preserve bim000 error behaviour
    with pytest.raises(SystemExit) as exc:
        crawler.read_urls(tmp_path / "nope.json")
    assert exc.value.code == 1
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    with pytest.raises(SystemExit) as exc:
        crawler.load_urls(bad, 3)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# bim001 — chunk 2: RunFolder (AC-10, 21, 23, 30, 31, 34, 40, 50)
# ---------------------------------------------------------------------------
import re

STARTED = "2026-09-06T14:30:00+00:00"


def _folder(tmp_path, project="Proj"):
    return crawler.RunFolder(project, STARTED, root=tmp_path).create()


def _rec(url, status=200, ok=True, elapsed=1.0, error=None):
    return {"url": url, "status": status, "ok": ok, "elapsed_s": elapsed, "error": error}


def _finish(rf, **kw):
    args = dict(command="python -m smart_crawler.crawler --project Proj", input_path=Path("/in.json"),
                input_total=0, limit=None, input_hosts=[], finished_at=STARTED, stopped_early=False)
    args.update(kw)
    return rf.write_manifest(**args)


def test_ac10_run_folder_layout_exact(tmp_path):
    rf = _folder(tmp_path)
    rf.log("run start project=Proj run_id=" + rf.run_id)
    _finish(rf)
    rf.write_absences([])
    assert rf.dir == tmp_path / "Proj" / "runs" / "2026-09-06T14-30-00Z"
    assert sorted(p.name for p in rf.dir.iterdir()) == ["absences.json", "html", "manifest.json", "stage_log.txt"]
    assert rf.html_dir.is_dir() and list(rf.html_dir.iterdir()) == []
    assert rf.run_dir_rel == "outputs/Proj/runs/2026-09-06T14-30-00Z"


def test_ac21_html_byte_for_byte(tmp_path):
    rf = _folder(tmp_path)
    html = "<html><body>É &amp; ok</body></html>"
    rel, n = rf.save_html("page", html)
    data = (rf.dir / rel).read_bytes()
    assert data == html.encode("utf-8") and n == len(data) == 37  # É is 2 bytes in UTF-8
    html2 = "a\r\n b  \n"
    rel2, _ = rf.save_html("crlf", html2)
    assert (rf.dir / rel2).read_bytes() == html2.encode("utf-8")  # no newline/whitespace normalisation


def test_ac23_collision_suffix(tmp_path):
    rf = _folder(tmp_path)
    urls = ["https://example.com/x/", "https://example.com/x", "https://EXAMPLE.com/X"]
    base = crawler.slugify("example.com/x")
    written = []
    for i, u in enumerate(urls):
        slug = rf.allocate_slug(crawler.slugify(u.replace("https://", "")))
        rel, _ = rf.save_html(slug, f"<p>{i}</p>")
        rf.record_page(_rec(u), slug=slug, outcome="captured", html_file=rel, html_bytes=8)
        written.append(rel)
    assert written == [f"html/{base}.html", f"html/{base}-2.html", f"html/{base}-3.html"]
    assert sorted(p.name for p in rf.html_dir.iterdir()) == sorted(Path(w).name for w in written)
    assert [(rf.dir / w).read_text() for w in written] == ["<p>0</p>", "<p>1</p>", "<p>2</p>"]
    assert [p["html_file"] for p in rf.pages] == written and [p["url"] for p in rf.pages] == urls
    with pytest.raises(FileExistsError):
        rf.save_html(base, "dup")  # never overwrite


def test_ac30_manifest_top_level_keys_exact(tmp_path):
    rf = _folder(tmp_path)
    manifest = json.loads(_finish(rf).read_text())
    assert sorted(manifest) == [
        "access_rung", "command", "crawl4ai_version", "delay_before_return_html_s",
        "fallbacks_fired", "finished_at", "input_hosts", "input_path", "input_total",
        "limit", "page_timeout_ms", "pages", "pause_range_s", "playwright_version",
        "project_name", "python_version", "run_dir", "run_id", "schema",
        "started_at", "stopped_early", "summary_path", "wait_for_images"]
    assert len(manifest) == 23


def test_ac31_manifest_fixed_values(tmp_path):
    m = json.loads(_finish(_folder(tmp_path)).read_text())
    assert m["schema"] == "bim001-manifest-v1" and m["access_rung"] == "a" and m["fallbacks_fired"] == []
    assert m["wait_for_images"] is True and m["delay_before_return_html_s"] == 3.0
    assert m["page_timeout_ms"] == 90000 and m["pause_range_s"] == [2, 5]
    assert m["crawl4ai_version"] == "0.9.3" and m["playwright_version"] == "1.52.0"
    assert m["python_version"].startswith("3.12")
    assert m["summary_path"] == "outputs/run_summary.json"


def test_ac34_manifest_page_keys_exact(tmp_path):
    rf = _folder(tmp_path)
    rf.record_page(_rec("https://example.com/a"), slug="example-com-a", outcome="captured",
                   html_file="html/example-com-a.html", html_bytes=10, md_file="pages/example-com-a.md")
    rf.record_page(_rec("https://example.com/b", 403, False, 0.5, "blocked"), slug="example-com-b",
                   outcome="blocked", reason="blocked")
    m = json.loads(_finish(rf).read_text())
    for entry in m["pages"]:
        assert sorted(entry) == ["elapsed_s", "error", "html_bytes", "html_file", "md_file", "ok",
                                 "outcome", "reason", "slug", "status", "url"]
    assert m["pages"][1]["html_file"] is None and m["pages"][1]["html_bytes"] is None
    with pytest.raises(AssertionError):
        rf.record_page(_rec("https://example.com/c"), slug="c", outcome="weird")


def test_ac40_absences_shape(tmp_path):
    rf = _folder(tmp_path)
    rf.record_page(_rec("https://example.com/a"), slug="a", outcome="captured", html_file="html/a.html", html_bytes=1)
    rf.record_page(_rec("https://example.com/b", 500, False, 0.5, "HTTP 500"), slug="b", outcome="failed", reason="HTTP 500")
    absences = crawler.build_absences(rf.pages, attempted=["https://example.com/a", "https://example.com/b"],
                                      all_urls=["https://example.com/a", "https://example.com/b", "https://example.com/c"])
    path = rf.write_absences(absences)
    loaded = json.loads(path.read_text())
    assert isinstance(loaded, list) and len(loaded) == 2
    for e in loaded:
        assert sorted(e) == ["outcome", "reason", "url"]
        assert e["outcome"] in {"blocked", "failed", "unsupported", "skipped"}
    assert loaded[0] == {"url": "https://example.com/b", "outcome": "failed", "reason": "HTTP 500"}
    assert loaded[1] == {"url": "https://example.com/c", "outcome": "skipped", "reason": "limit"}


def test_ac50_stage_log_lines_start_with_timestamp(tmp_path):
    rf = _folder(tmp_path)
    rf.log("run start project=Proj run_id=" + rf.run_id)
    rf.log("captured https://example.com/a")
    rf.log("run end")
    lines = (rf.dir / "stage_log.txt").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    for line in lines:
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", line), line
    assert lines[0].endswith("run start project=Proj run_id=2026-09-06T14-30-00Z") and lines[-1].endswith("run end")
