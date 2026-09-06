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


def _result(status, success=True, raw="body " * 200, error=None, html=None):
    """Shape of what crawl4ai 0.9.x arun() hands back, reduced to the fields the crawler reads.
    bim001 AC-71(c): `html` is optional; the attribute is set only when provided (absent by default)."""
    result = types.SimpleNamespace(
        status_code=status,
        success=success,
        error_message=error,
        markdown=types.SimpleNamespace(fit_markdown="", raw_markdown=raw),
    )
    if html is not None:
        result.html = html
    return result


class FakeCrawler:
    def __init__(self, results):
        self._results = list(results)
        self.calls = []

    async def arun(self, url, config=None):
        self.calls.append(url)
        result = self._results.pop(0)
        if isinstance(result, Exception):  # bim001 tests: simulate arun raising
            raise result
        return result


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Redirect outputs to tmp and make pacing instant."""
    monkeypatch.setattr(crawler, "PAGE_DIR", tmp_path / "pages")
    monkeypatch.setattr(crawler, "SUMMARY_PATH", tmp_path / "run_summary.json")
    monkeypatch.setattr(crawler, "RUN_ROOT", tmp_path)  # bim001 AC-71(a): run folders land in tmp
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


# ---------------------------------------------------------------------------
# bim001 — chunk 3: capture in the crawl loop (AC-20, 22, 24, 25, 26, 27, 28)
# ---------------------------------------------------------------------------

def _crawl(sandbox, results, urls=None, project="Proj"):
    rf = crawler.RunFolder(project, STARTED, root=sandbox.dir / "runs").create()
    urls = urls or _urls(len(results))
    pages, stopped = asyncio.run(crawler.crawl_all(urls, FakeCrawler(results), run=rf))
    return rf, pages, stopped


def test_ac20_captured_for_successful_fetch(sandbox):
    rf, pages, _ = _crawl(sandbox, [_result(200, html="<html>a</html>"), _result(200, html="<html>b</html>")])
    assert [e["outcome"] for e in rf.pages] == ["captured", "captured"]
    for e in rf.pages:
        assert (rf.dir / e["html_file"]).exists() and e["html_file"] == f"html/{e['slug']}.html"
        assert e["html_bytes"] == (rf.dir / e["html_file"]).stat().st_size and e["reason"] is None
        assert e["md_file"] == f"pages/{e['slug']}.md" and (crawler.PAGE_DIR / f"{e['slug']}.md").exists()
    assert [p["ok"] for p in pages] == [True, True]


def test_ac22_html_stem_equals_md_stem(sandbox):
    rf, _, _ = _crawl(sandbox, [_result(200, html="<p>x</p>")], urls=["https://example.com/About-Us/"])
    html_stem = Path(rf.pages[0]["html_file"]).stem
    md_stem = next(crawler.PAGE_DIR.iterdir()).stem
    assert html_stem == md_stem == crawler.slugify("example.com/About-Us/") == "example-com-about-us"
    source = (REPO_ROOT / "smart_crawler" / "crawler.py").read_text()
    assert source.count("def slugify") == 1


def test_ac24_blocked_no_html(sandbox):
    rf, pages, _ = _crawl(sandbox, [_result(403, success=False, raw="", html="<html>blocked page</html>")])
    assert rf.pages[0]["outcome"] == "blocked" and rf.pages[0]["reason"] == "blocked"
    assert rf.pages[0]["html_file"] is None and list(rf.html_dir.iterdir()) == []
    assert pages[0]["error"] == "blocked"


def test_ac25_failed_and_exception_no_html(sandbox):
    rf, pages, _ = _crawl(sandbox, [_result(500, success=False, raw="", html="<html>err</html>"),
                                    RuntimeError("boom")])
    assert [e["outcome"] for e in rf.pages] == ["failed", "failed"]
    assert rf.pages[0]["reason"] == "HTTP 500"
    assert rf.pages[1]["reason"].startswith("exception:") and "boom" in rf.pages[1]["reason"]
    assert list(rf.html_dir.iterdir()) == [] and all(e["html_file"] is None for e in rf.pages)
    assert pages[1]["error"].startswith("exception:")


def test_ac26_unsupported_when_html_absent(sandbox):
    stub = _result(200)  # no html attribute at all
    assert not hasattr(stub, "html")
    rf, pages, _ = _crawl(sandbox, [stub])
    assert rf.pages[0]["outcome"] == "unsupported" and "html" in rf.pages[0]["reason"]
    assert rf.pages[0]["html_file"] is None and list(rf.html_dir.iterdir()) == []
    assert pages[0]["ok"] is True  # markdown side untouched


def test_ac27_html_independent_of_markdown(sandbox):
    rf, pages, _ = _crawl(sandbox, [_result(200, raw="", html="<p>x</p>")])
    assert rf.pages[0]["outcome"] == "captured" and (rf.dir / rf.pages[0]["html_file"]).read_text() == "<p>x</p>"
    assert pages[0]["ok"] is False and pages[0]["error"] == "empty markdown"  # bim000 behavior preserved
    assert rf.pages[0]["ok"] is False and rf.pages[0]["error"] == "empty markdown"
    assert rf.pages[0]["md_file"] is None and list(crawler.PAGE_DIR.iterdir()) == []


def test_ac28_write_failure_is_failure_not_crash(sandbox, monkeypatch):
    rf = crawler.RunFolder("Proj", STARTED, root=sandbox.dir / "runs").create()
    real_save = rf.save_html
    calls = []

    def flaky_save(slug, html):
        calls.append(slug)
        if len(calls) == 1:
            raise OSError("disk full")
        return real_save(slug, html)

    monkeypatch.setattr(rf, "save_html", flaky_save)
    pages, stopped = asyncio.run(crawler.crawl_all(_urls(2), FakeCrawler([_result(200, html="<p>1</p>"), _result(200, html="<p>2</p>")]), run=rf))
    assert stopped is False and len(pages) == 2
    assert rf.pages[0]["outcome"] == "failed" and "write" in rf.pages[0]["reason"] and rf.pages[0]["html_file"] is None
    assert rf.pages[1]["outcome"] == "captured"
    assert [p["ok"] for p in pages] == [True, True]  # run_summary unaffected by the HTML write failure


# ---------------------------------------------------------------------------
# bim001 — chunk 4: main() wired (AC-07, 13, 14, 32, 33, 35, 36, 37, 41, 42, 43, 51)
# ---------------------------------------------------------------------------

class FakeBrowser:
    """Stands in for crawl4ai.AsyncWebCrawler: constructed with config=..., used as `async with`."""

    def __init__(self, results):
        self.fake = FakeCrawler(results)

    def __call__(self, config=None):
        return self

    async def __aenter__(self):
        return self.fake

    async def __aexit__(self, *exc):
        return False


def _main(sandbox, monkeypatch, results, urls, extra=(), project="Proj"):
    """Drive the real main(): input json in tmp, argv patched, browser faked. Returns (exit_code, run_dir)."""
    src = sandbox.dir / "in" / "input.json"
    src.parent.mkdir(exist_ok=True)
    src.write_text(json.dumps([{"url": u} for u in urls]))
    monkeypatch.setattr(crawler, "AsyncWebCrawler", FakeBrowser(results))
    monkeypatch.setattr(sys, "argv", ["crawler", "--project", project, "--input", str(src), *extra])
    try:
        crawler.main()
        code = 0
    except SystemExit as exc:
        code = exc.code
    runs = sorted((sandbox.dir / project / "runs").iterdir()) if (sandbox.dir / project / "runs").exists() else []
    return code, (runs[-1] if runs else None)


def _load(run_dir):
    return (json.loads((run_dir / "manifest.json").read_text()),
            json.loads((run_dir / "absences.json").read_text()),
            (run_dir / "stage_log.txt").read_text().splitlines())


def test_ac07_project_case_preserved(sandbox, monkeypatch):
    code, run_dir = _main(sandbox, monkeypatch, [_result(200, html="<p>x</p>")], _urls(1), project="CyberizeGroup")
    assert code == 0 and run_dir.parent.parent.name == "CyberizeGroup"
    assert (sandbox.dir / "CyberizeGroup").is_dir() and not (sandbox.dir / "cyberizegroup").exists()


def test_ac13_empty_input_creates_run_folder(sandbox, monkeypatch):
    monkeypatch.setattr(crawler, "run", lambda *a, **k: pytest.fail("run() must not be called"))
    code, run_dir = _main(sandbox, monkeypatch, [], [], project="CyberizeGroup")
    assert code == 0 and run_dir is not None
    manifest, absences, log = _load(run_dir)
    assert sorted(p.name for p in run_dir.iterdir()) == ["absences.json", "html", "manifest.json", "stage_log.txt"]
    assert list((run_dir / "html").iterdir()) == []
    assert manifest["pages"] == [] and manifest["input_total"] == 0 and absences == [] and len(log) >= 1
    summary = json.loads(crawler.SUMMARY_PATH.read_text())
    assert summary["pages"] == [] and set(summary) == {"started_at", "finished_at", "crawl4ai_version", "pause_range_s", "pages"}


def test_ac14_two_runs_two_folders(sandbox, monkeypatch):
    code1, run1 = _main(sandbox, monkeypatch, [_result(200, html="<p>1</p>")], _urls(1))
    first_bytes = (run1 / "manifest.json").read_bytes()
    code2, run2 = _main(sandbox, monkeypatch, [_result(200, html="<p>2</p>")], _urls(1))
    assert code1 == code2 == 0 and run1 != run2
    assert (run1 / "manifest.json").read_bytes() == first_bytes
    assert len(list((sandbox.dir / "Proj" / "runs").iterdir())) == 2


def test_ac32_manifest_identity_values(sandbox, monkeypatch):
    urls = ["https://b.example.com/x", "https://a.example.com/y", "https://b.example.com/z"]
    code, run_dir = _main(sandbox, monkeypatch, [_result(200, html="<p>x</p>")] * 3, urls, extra=["--limit", "2"], project="CyberizeGroup")
    manifest, _, _ = _load(run_dir)
    assert manifest["project_name"] == "CyberizeGroup"
    assert manifest["run_id"] == run_dir.name
    assert manifest["run_dir"] == f"outputs/CyberizeGroup/runs/{run_dir.name}" and not manifest["run_dir"].endswith("/")
    assert manifest["command"].startswith("python -m smart_crawler.crawler") and "--project CyberizeGroup" in manifest["command"] and "--limit 2" in manifest["command"]
    assert manifest["input_path"] == str((sandbox.dir / "in" / "input.json").resolve())
    assert manifest["input_hosts"] == ["a.example.com", "b.example.com"]
    assert manifest["summary_path"] == "outputs/run_summary.json"


def test_ac33_manifest_counts(sandbox, monkeypatch):
    # 6 inputs, --limit 5, stop rule after 3 blocked -> attempted 3
    results = [_result(429, success=False, raw="")] * 3
    code, run_dir = _main(sandbox, monkeypatch, results, _urls(6), extra=["--limit", "5"])
    manifest, _, _ = _load(run_dir)
    assert code == 2 and manifest["input_total"] == 6 and manifest["limit"] == 5 and len(manifest["pages"]) == 3
    code, run_dir = _main(sandbox, monkeypatch, [_result(200, html="<p>x</p>")] * 2, _urls(2))
    manifest, _, _ = _load(run_dir)
    assert manifest["input_total"] == 2 and manifest["limit"] is None and len(manifest["pages"]) == 2


def test_ac35_page_values_match_run_summary(sandbox, monkeypatch):
    results = [_result(200, html="<p>ok</p>"), _result(403, success=False, raw=""), _result(200), _result(200, raw="", html="<p>nomd</p>")]
    code, run_dir = _main(sandbox, monkeypatch, results, _urls(4))
    manifest, _, _ = _load(run_dir)
    summary = json.loads(crawler.SUMMARY_PATH.read_text())
    for m, s in zip(manifest["pages"], summary["pages"]):
        assert {k: m[k] for k in ("url", "status", "ok", "elapsed_s", "error")} == s
        assert m["outcome"] in {"captured", "blocked", "failed", "unsupported"}
        if m["outcome"] == "captured":
            assert m["html_file"] == f"html/{m['slug']}.html" and m["reason"] is None
            assert m["html_bytes"] == (run_dir / m["html_file"]).stat().st_size
        else:
            assert m["html_file"] is None and m["html_bytes"] is None and m["reason"]
    assert [m["outcome"] for m in manifest["pages"]] == ["captured", "blocked", "unsupported", "captured"]
    assert [m["md_file"] for m in manifest["pages"]] == ["pages/example-com-p0.md", None, "pages/example-com-p2.md", None]


def test_ac36_timestamps_identical(sandbox, monkeypatch):
    code, run_dir = _main(sandbox, monkeypatch, [_result(200, html="<p>x</p>")], _urls(1))
    manifest, _, _ = _load(run_dir)
    summary = json.loads(crawler.SUMMARY_PATH.read_text())
    assert manifest["started_at"] == summary["started_at"] and manifest["finished_at"] == summary["finished_at"]
    assert crawler.make_run_id(manifest["started_at"]) == manifest["run_id"]


def test_ac37_manifest_on_early_stop_exit_2(sandbox, monkeypatch):
    results = [_result(200, html="<p>x</p>")] + [_result(429, success=False, raw="")] * 3
    code, run_dir = _main(sandbox, monkeypatch, results, _urls(6))
    manifest, absences, log = _load(run_dir)
    assert code == 2 and manifest["stopped_early"] is True and len(manifest["pages"]) == 4
    assert any("stop rule" in line for line in log)
    code, run_dir = _main(sandbox, monkeypatch, [_result(200, html="<p>x</p>")], _urls(1))
    manifest, _, _ = _load(run_dir)
    assert code == 0 and manifest["stopped_early"] is False


def test_ac41_absences_completeness_and_order(sandbox, monkeypatch):
    # inputs p0..p7, limit 6; p0 captured, p1 failed, p2 unsupported, p3 p4 p5 blocked -> stop; p6 p7 limit
    results = [_result(200, html="<p>x</p>"), _result(500, success=False, raw=""), _result(200),
               _result(403, success=False, raw=""), _result(429, success=False, raw=""), _result(403, success=False, raw="")]
    code, run_dir = _main(sandbox, monkeypatch, results, _urls(8), extra=["--limit", "6"])
    manifest, absences, _ = _load(run_dir)
    captured = {p["url"] for p in manifest["pages"] if p["outcome"] == "captured"}
    absent = {e["url"] for e in absences}
    assert captured == {"https://example.com/p0"} and captured.isdisjoint(absent)
    assert captured | absent == set(_urls(8))
    assert [e["url"] for e in absences] == _urls(8)[1:]  # attempted-and-absent in attempt order, then skipped in input order
    assert [e["outcome"] for e in absences] == ["failed", "unsupported", "blocked", "blocked", "blocked", "skipped", "skipped"]


def test_ac42_skipped_reasons_limit_and_stop_rule(sandbox, monkeypatch):
    results = [_result(429, success=False, raw="")] * 3
    code, run_dir = _main(sandbox, monkeypatch, results, _urls(7), extra=["--limit", "5"])
    _, absences, _ = _load(run_dir)
    by_url = {e["url"]: e for e in absences}
    assert by_url["https://example.com/p3"] == {"url": "https://example.com/p3", "outcome": "skipped", "reason": "stop_rule"}
    assert by_url["https://example.com/p4"]["reason"] == "stop_rule"
    assert by_url["https://example.com/p5"]["reason"] == "limit" and by_url["https://example.com/p6"]["reason"] == "limit"
    assert len(absences) == 7


def test_ac43_absence_reason_matches_manifest(sandbox, monkeypatch):
    results = [_result(500, success=False, raw=""), _result(200), _result(403, success=False, raw=""), _result(200, html="<p>x</p>")]
    code, run_dir = _main(sandbox, monkeypatch, results, _urls(4))
    manifest, absences, _ = _load(run_dir)
    reasons = {p["url"]: p["reason"] for p in manifest["pages"]}
    for e in absences:
        assert e["outcome"] in {"blocked", "failed", "unsupported"} and e["reason"] == reasons[e["url"]]
    assert len(absences) == 3


def test_ac51_stage_log_contents(sandbox, monkeypatch):
    results = [_result(200, html="<p>x</p>"), _result(500, success=False, raw="")] + [_result(429, success=False, raw="")] * 3
    code, run_dir = _main(sandbox, monkeypatch, results, _urls(6), project="CyberizeGroup")
    manifest, _, log = _load(run_dir)
    assert "run start" in log[0] and "CyberizeGroup" in log[0] and manifest["run_id"] in log[0]
    for p in manifest["pages"]:
        matching = [line for line in log if p["url"] in line]
        assert len(matching) == 1 and p["outcome"] in matching[0]
    assert sum("stop rule" in line for line in log) == 1
    assert "run end" in log[-1]
