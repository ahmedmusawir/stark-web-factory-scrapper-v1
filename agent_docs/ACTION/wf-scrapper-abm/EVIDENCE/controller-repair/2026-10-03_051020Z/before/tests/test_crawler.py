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
        return self._results.pop(0)


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
    """E-01/E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    for status in (403,500):
        fake = FakeCrawler([_result(status, success=False, raw=''), _result(200, html='<p>ok</p>')])
        pages, stopped = asyncio.run(crawler.crawl_all(_urls(2),fake))
        assert stopped is (status == 403)
        assert len(fake.calls) == (1 if stopped else 2)
        assert pages[0]['error'] == ('blocked' if stopped else 'HTTP 500')
        assert not pages[0]['ok']
        if not stopped: assert pages[1]['ok'] and pages[1]['error'] is None
    assert list(crawler.PAGE_DIR.iterdir()) == []
    assert not crawler.SUMMARY_PATH.exists()


def test_three_consecutive_429_stop_the_run(sandbox, capsys):
    """E-05 — BUILD_READBACK §5 authorized replacement."""
    fake = FakeCrawler([_result(429,success=False)]*3+[_result(200)])
    pages, stopped = asyncio.run(crawler.crawl_all(_urls(4),fake))
    assert stopped and len(pages) == 1 and pages[0]['error'] == 'blocked'
    assert fake.calls == _urls(1)
    assert 'First intentional refusal' in capsys.readouterr().out
    assert list(crawler.PAGE_DIR.iterdir()) == []


def test_blocked_counter_resets_on_success(sandbox):
    """E-05 — BUILD_READBACK §5 authorized replacement."""
    fake = FakeCrawler([_result(429,success=False),_result(200,html='<p>ok</p>')])
    pages, stopped = asyncio.run(crawler.crawl_all(_urls(2),fake))
    assert stopped and len(pages) == 1 and fake.calls == _urls(1)


def test_pause_between_pages_not_before_first(sandbox, capsys):
    """E-05 — BUILD_READBACK §5 authorized replacement."""
    fake = FakeCrawler([_result(200,html='<p>ok</p>')]*3)
    asyncio.run(crawler.crawl_all(_urls(3),fake))
    assert sandbox.sleeps == [5.0,5.0]


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
    """E-06 — single USER_AGENT in the owned browser, no requests Session transport."""
    from smart_crawler.browser_session import BrowserSession
    assert 'Chrome/' in sitemap_utils.USER_AGENT and 'Safari/537.36' in sitemap_utils.USER_AGENT
    assert crawler.USER_AGENT == sitemap_utils.USER_AGENT
    assert not hasattr(sitemap_utils,'SESSION')
    source=(REPO_ROOT/'smart_crawler/browser_session.py').read_text()
    assert 'BrowserConfig(headless=True, user_agent=USER_AGENT)' in source
    tree = ast.parse(source)
    assert not any(isinstance(n, ast.Import) and any(a.name == 'requests' for a in n.names) or
                   isinstance(n, ast.ImportFrom) and n.module == 'requests' for n in ast.walk(tree))


def test_import_from_foreign_cwd_creates_no_directory(tmp_path):
    code = f"import sys; sys.path.insert(0, {str(REPO_ROOT)!r}); import smart_crawler.crawler"
    subprocess.run([sys.executable, "-c", code], cwd=tmp_path, check=True)
    assert list(tmp_path.iterdir()) == []


def test_empty_input_writes_truthful_summary_without_crawling(sandbox, tmp_path, monkeypatch, capsys):
    """E-01/E-09 — BUILD_READBACK §5 authorized replacement."""
    empty = tmp_path/'empty.json'; empty.write_text('[]')
    crawler.SUMMARY_PATH.write_text('historical summary')
    monkeypatch.setattr(crawler,'run',lambda *a,**kw: pytest.fail('empty input crawled'))
    monkeypatch.setattr(sys,'argv',['crawler','--project','TestProj','--input',str(empty)])
    crawler.main()
    assert crawler.SUMMARY_PATH.read_text() == 'historical summary'
    m=json.loads(next((tmp_path/'TestProj/runs').glob('*/manifest.json')).read_text())
    assert m['pages'] == [] and m['counts']['routes'] == 0
    assert 'No URLs found' in capsys.readouterr().out
    assert list(crawler.PAGE_DIR.iterdir()) == []


# ---------------------------------------------------------------------------
# bim001 — chunk 1: CLI + project identity (AC-01..08, AC-11, AC-63 partial)
# ---------------------------------------------------------------------------

def _one_url_input(tmp_path):
    f = tmp_path / "in" / "one.json"
    f.parent.mkdir(exist_ok=True)
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
    """E-01/E-08 — BUILD_READBACK §5 authorized replacement."""
    rf=_folder(tmp_path);rf.log('run start');_finish(rf);rf.write_absences([])
    assert rf.dir == tmp_path/'Proj/runs/2026-09-06T14-30-00Z'
    assert {p.name for p in rf.dir.iterdir()} == {'absences.json','manifest.json','stage_log.txt','html','rest','discovery','media','screenshots'}
    assert rf.html_dir.is_dir() and not list(rf.html_dir.iterdir())
    assert rf.run_dir_rel == 'outputs/Proj/runs/2026-09-06T14-30-00Z'


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
    """E-01/E-06/E-09 — BUILD_READBACK §5 authorized replacement."""
    m=json.loads(_finish(_folder(tmp_path)).read_text())
    assert set(m) == {'schema','project_name','run_id','started_at','finished_at','command','input','scope','access','versions','streams','counts','stopped_early','fallbacks_fired','pages'}
    assert next(iter(m)) == 'schema'


def test_ac31_manifest_fixed_values(tmp_path):
    """E-01/E-05/E-06 — BUILD_READBACK §5 authorized replacement."""
    m=json.loads(_finish(_folder(tmp_path)).read_text());a=m['access']
    assert m['schema']=='abm-raw-v2' and a['rung']=='a' and m['fallbacks_fired']==[]
    assert a['wait_for_images'] is True and a['page_timeout_ms']==90000 and a['delay_before_return_html_s']==3.0
    assert a['cache_mode']=='BYPASS' and a['user_agent']==sitemap_utils.USER_AGENT
    assert a['operation_gap_after_completion_s']==5 and a['retry_max']==0 and a['stop_on_first_intentional_refusal']
    assert not a['automatic_restart'] and not a['background_resources_paced']
    assert m['versions']['crawl4ai']=='0.9.3' and m['versions']['playwright']=='1.52.0'
    assert m['versions']['python'].startswith('3.12') and len(m['versions']['tool_commit'])==40


def test_ac34_manifest_page_keys_exact(tmp_path):
    """E-01/E-09 — BUILD_READBACK §5 authorized replacement."""
    rf=_folder(tmp_path)
    rf.record_page(_rec('https://example.com/b',403,False,.5,'blocked'),slug='b',outcome='blocked',reason='blocked')
    m=json.loads(_finish(rf).read_text());e=m['pages'][0]
    assert set(e)=={'url','input_url','final_url','redirect_chain','slug','status','outcome','reason','fetched_at','elapsed_s','retries','html_file','block_file','html_bytes','sha256','rest_ref','rest_outcome'}
    assert e['html_file'] is None and e['html_bytes'] is None and e['sha256'] is None and e['retries']==0
    with pytest.raises(AssertionError): rf.record_page(_rec('https://example.com/c'),slug='c',outcome='weird')


def test_ac40_absences_shape(tmp_path):
    """E-09 — BUILD_READBACK §5 authorized replacement."""
    rf=_folder(tmp_path)
    rf.record_page(_rec(_urls(2)[1],500,False,.5,'HTTP 500'),slug='b',outcome='failed',reason='HTTP 500')
    a=crawler.build_absences(rf.pages,_urls(2),_urls(3))
    assert all(set(e)=={'stream','ref','outcome','reason','at'} for e in a)
    assert a[0]['stream']=='html' and a[0]['ref']==_urls(2)[1] and a[0]['reason']=='HTTP 500'
    assert a[-1]['ref']==_urls(3)[2] and a[-1]['reason']=='limit'
    assert json.loads(rf.write_absences(a).read_text()) == a


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

class RaisingFakeCrawler(FakeCrawler):
    """bim001-only test infrastructure: like FakeCrawler, but an Exception instance in the
    results list is raised from arun() instead of returned (simulates a crawl4ai failure)."""

    async def arun(self, url, config=None):
        result = await super().arun(url, config)
        if isinstance(result, Exception):
            raise result
        return result


def _crawl(sandbox, results, urls=None, project="Proj", crawler_cls=FakeCrawler):
    rf = crawler.RunFolder(project, STARTED, root=sandbox.dir / "runs").create()
    urls = urls or _urls(len(results))
    pages, stopped = asyncio.run(crawler.crawl_all(urls, crawler_cls(results), run=rf))
    return rf, pages, stopped


def test_ac20_captured_for_successful_fetch(sandbox):
    """E-01 — BUILD_READBACK §5 authorized replacement."""
    rf,pages,_=_crawl(sandbox,[_result(200,html='<html>a</html>'),_result(200,html='<html>b</html>')])
    assert [e['outcome'] for e in rf.pages]==['captured','captured']
    for e in rf.pages:
        assert e['html_file']==f"html/{e['slug']}.html" and e['reason'] is None
        assert e['html_bytes']==(rf.dir/e['html_file']).stat().st_size
        assert len(e['sha256'])==64 and 'md_file' not in e
    assert [p['ok'] for p in pages]==[True,True] and not list(crawler.PAGE_DIR.iterdir())


def test_ac22_html_stem_equals_md_stem(sandbox):
    """E-01 — BUILD_READBACK §5 authorized replacement."""
    rf,_,_=_crawl(sandbox,[_result(200,html='<p>x</p>')],urls=['https://example.com/About-Us/'])
    assert Path(rf.pages[0]['html_file']).stem == rf.pages[0]['slug'] == crawler.slugify('example.com/About-Us/') == 'example-com-about-us'
    assert not list(crawler.PAGE_DIR.iterdir())
    assert SOURCE_PATH.read_text().count('def slugify')==1


def test_ac24_blocked_no_html(sandbox):
    """E-05/E-19 — BUILD_READBACK §5 authorized replacement."""
    rf,pages,stopped=_crawl(sandbox,[_result(403,success=False,raw='',html='<html>blocked page</html>')])
    assert stopped and rf.pages[0]['outcome']=='blocked' and rf.pages[0]['reason']=='blocked'
    assert rf.pages[0]['html_file'] is None and pages[0]['error']=='blocked'


def test_ac25_failed_and_exception_no_html(sandbox):
    rf, pages, _ = _crawl(sandbox, [_result(500, success=False, raw="", html="<html>err</html>"),
                                    RuntimeError("boom")], crawler_cls=RaisingFakeCrawler)
    assert [e["outcome"] for e in rf.pages] == ["failed", "failed"]
    assert rf.pages[0]["reason"] == "HTTP 500"
    assert rf.pages[1]["reason"].startswith("exception:") and "boom" in rf.pages[1]["reason"]
    assert list(rf.html_dir.iterdir()) == [] and all(e["html_file"] is None for e in rf.pages)
    assert pages[1]["error"].startswith("exception:")


def test_ac26_unsupported_when_html_absent(sandbox):
    """E-01 — BUILD_READBACK §5 authorized replacement."""
    stub=_result(200);assert not hasattr(stub,'html')
    rf,pages,_=_crawl(sandbox,[stub])
    assert rf.pages[0]['outcome']=='unsupported' and 'html' in rf.pages[0]['reason']
    assert rf.pages[0]['html_file'] is None and not list(rf.html_dir.iterdir())
    assert pages[0]['ok'] is False


def test_ac27_html_independent_of_markdown(sandbox):
    """E-01 — BUILD_READBACK §5 authorized replacement."""
    rf,pages,_=_crawl(sandbox,[_result(200,raw='',html='<p>x</p>')])
    assert rf.pages[0]['outcome']=='captured' and (rf.dir/rf.pages[0]['html_file']).read_text()=='<p>x</p>'
    assert pages[0]['ok'] and pages[0]['error'] is None and not list(crawler.PAGE_DIR.iterdir())


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
    # BUILD_READBACK helper adaptation: isolate CLI fixture from the real browser gate.
    async def fixture_run(selected, run_folder):
        return await crawler.crawl_all(selected, FakeCrawler(results), run_folder)
    monkeypatch.setattr(crawler, "run", fixture_run)
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
    """E-01/E-09 — BUILD_READBACK §5 authorized replacement."""
    monkeypatch.setattr(crawler,'run',lambda *a,**kw:pytest.fail('run called'))
    code,d=_main(sandbox,monkeypatch,[],[],project='CyberizeGroup')
    m,a,log=_load(d)
    assert code==0 and m['pages']==[] and m['counts']['routes']==0
    assert not [x for x in a if x['stream']=='html'] and log
    assert not list((d/'html').iterdir()) and not crawler.SUMMARY_PATH.exists()
    from smart_crawler.validate import validate_run
    assert validate_run(d)


def test_ac14_two_runs_two_folders(sandbox, monkeypatch):
    code1, run1 = _main(sandbox, monkeypatch, [_result(200, html="<p>1</p>")], _urls(1))
    first_bytes = (run1 / "manifest.json").read_bytes()
    code2, run2 = _main(sandbox, monkeypatch, [_result(200, html="<p>2</p>")], _urls(1))
    assert code1 == code2 == 0 and run1 != run2
    assert (run1 / "manifest.json").read_bytes() == first_bytes
    assert len(list((sandbox.dir / "Proj" / "runs").iterdir())) == 2


def test_ac32_manifest_identity_values(sandbox, monkeypatch):
    """E-01/E-06/E-18 — BUILD_READBACK §5 authorized replacement."""
    urls=['https://b.example.com/x','https://a.example.com/y','https://b.example.com/z','https://example.invalid:8443/port','https://example.invalid/plain']
    code,d=_main(sandbox,monkeypatch,[_result(200,html='<p>x</p>')]*2,urls,extra=['--limit','2'],project='CyberizeGroup')
    m,_,_=_load(d)
    assert m['project_name']=='CyberizeGroup' and m['run_id']==d.name
    assert '--project CyberizeGroup' in m['command'] and '--limit 2' in m['command']
    assert str(sandbox.dir) not in json.dumps(m)
    # E-06: declared scope must match the actual browser's site + www twin;
    # merely appearing in a legacy input array does not expand that scope.
    assert m['scope']['hosts_allowed']==['b.example.com','www.b.example.com']
    assert crawler.input_hosts(['https://example.invalid:8443/port','https://example.invalid/plain'])==['example.invalid']
    assert crawler.input_hosts(['not a url','https://x.invalid/'])==['x.invalid']


def test_ac33_manifest_counts(sandbox, monkeypatch):
    """E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    code,d=_main(sandbox,monkeypatch,[_result(429,success=False)],_urls(6),extra=['--limit','5'])
    m,_,_=_load(d)
    assert code==2 and m['counts']['routes']==len(m['pages'])==6
    assert m['input']['limit']==5 and m['counts']['blocked']==1 and m['counts']['skipped']==5
    assert [p['reason'] for p in m['pages'][1:]]==['stop_rule']*4+['limit']


def test_ac35_page_values_match_run_summary(sandbox, monkeypatch):
    """E-01/E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    results=[_result(200,html='<p>ok</p>'),_result(200),_result(200,raw='',html='<p>nomd</p>'),_result(403,success=False)]
    code,d=_main(sandbox,monkeypatch,results,_urls(5));m,a,_=_load(d)
    assert code==2 and [p['outcome'] for p in m['pages']]==['captured','unsupported','captured','blocked','skipped']
    assert [(d/p['html_file']).read_text() for p in m['pages'] if p['html_file']]==['<p>ok</p>','<p>nomd</p>']
    from smart_crawler.validate import validate_run
    assert validate_run(d) and not crawler.SUMMARY_PATH.exists()


def test_ac36_timestamps_identical(sandbox, monkeypatch):
    """E-01/E-14 — BUILD_READBACK §5 authorized replacement."""
    _,d=_main(sandbox,monkeypatch,[_result(200,html='<p>x</p>')],_urls(1));m,a,log=_load(d)
    assert crawler.make_run_id(m['started_at'])==m['run_id']
    assert m['started_at']<=m['pages'][0]['fetched_at']<=m['finished_at']
    assert all(x['at']<=m['finished_at'] for x in a)
    assert all(m['started_at']<=x[:25]<=m['finished_at'] for x in log)


def test_ac37_manifest_on_early_stop_exit_2(sandbox, monkeypatch):
    """E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    code,d=_main(sandbox,monkeypatch,[_result(200,html='<p>x</p>'),_result(429,success=False)],_urls(6))
    m,a,log=_load(d)
    assert code==2 and m['stopped_early'] and len(m['pages'])==6
    assert [p['outcome'] for p in m['pages']]==['captured','blocked']+['skipped']*4
    assert any('stop rule' in x for x in log)
    code,d=_main(sandbox,monkeypatch,[_result(200,html='<p>x</p>')],_urls(1))
    assert code==0 and not _load(d)[0]['stopped_early']


def test_ac41_absences_completeness_and_order(sandbox, monkeypatch):
    """E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    results=[_result(200,html='<p>x</p>'),_result(500,success=False),_result(200),_result(403,success=False)]
    code,d=_main(sandbox,monkeypatch,results,_urls(8),extra=['--limit','6']);m,a,_=_load(d)
    a=[e for e in a if e['stream']=='html'];captured={p['url'] for p in m['pages'] if p['outcome']=='captured'}
    assert captured==set(_urls(1)) and captured.isdisjoint({e['ref'] for e in a})
    assert captured|{e['ref'] for e in a}==set(_urls(8))
    assert [e['ref'] for e in a]==_urls(8)[1:]
    assert [e['outcome'] for e in a]==['failed','unsupported','blocked']+['skipped']*4


def test_ac42_skipped_reasons_limit_and_stop_rule(sandbox, monkeypatch):
    """E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    _,d=_main(sandbox,monkeypatch,[_result(429,success=False)],_urls(7),extra=['--limit','5'])
    a=[e for e in _load(d)[1] if e['stream']=='html'];by={e['ref']:e for e in a}
    assert by[_urls(7)[0]]['outcome']=='blocked'
    assert all(by[u]['reason']=='stop_rule' for u in _urls(5)[1:])
    assert all(by[u]['reason']=='limit' for u in _urls(7)[5:]) and len(a)==7


def test_ac43_absence_reason_matches_manifest(sandbox, monkeypatch):
    """E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    _,d=_main(sandbox,monkeypatch,[_result(500,success=False),_result(200),_result(403,success=False)],_urls(4))
    m,a,_=_load(d);by={p['url']:p for p in m['pages']};a=[e for e in a if e['stream']=='html']
    assert len(a)==4
    for e in a:
        assert e['reason']==by[e['ref']]['reason'] and e['outcome']==by[e['ref']]['outcome']


def test_ac51_stage_log_contents(sandbox, monkeypatch):
    """E-05/E-09 — BUILD_READBACK §5 authorized replacement."""
    _,d=_main(sandbox,monkeypatch,[_result(200,html='<p>x</p>'),_result(500,success=False),_result(429,success=False)],_urls(6),project='CyberizeGroup')
    m,_,log=_load(d)
    assert 'run start' in log[0] and 'CyberizeGroup' in log[0] and m['run_id'] in log[0]
    assert sum('intentional captured' in x for x in log)==1
    assert sum('intentional failed' in x for x in log)==1
    assert sum('intentional blocked' in x for x in log)==1
    assert sum('stop rule' in x for x in log)==1 and 'run end' in log[-1]
    assert sum('pause' in x for x in log)==2


# ---------------------------------------------------------------------------
# bim001 — chunk 5: hardening (AC-10 end-to-end, AC-12, AC-60, AC-61/62 source checks, AC-63 complete)
# ---------------------------------------------------------------------------
import ast

SOURCE_PATH = REPO_ROOT / "smart_crawler" / "crawler.py"


def test_ac10_run_folder_layout_end_to_end(sandbox, monkeypatch):
    """E-01/E-05/E-08 — BUILD_READBACK §5 authorized replacement."""
    code,d=_main(sandbox,monkeypatch,[_result(200,html='<p>a</p>'),_result(403,success=False)],_urls(3),project='CyberizeGroup')
    assert code==2 and d.parent==sandbox.dir/'CyberizeGroup/runs'
    assert {p.name for p in d.iterdir()}=={'absences.json','manifest.json','stage_log.txt','html','rest','discovery','media','screenshots'}
    assert [p.name for p in (d/'html').iterdir()]==['example-com-p0.html']
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z',d.name)
    from smart_crawler.validate import validate_run
    assert validate_run(d)


def test_ac12_no_mkdir_at_module_level():
    tree = ast.parse(SOURCE_PATH.read_text())
    top_level_calls = [node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
    assert top_level_calls == []  # nothing is *called* at import time, mkdir or otherwise
    for line in SOURCE_PATH.read_text().splitlines():
        if "mkdir" in line:
            assert line.startswith((" ", "\t")), line  # every mkdir is indented, i.e. inside a function body


def test_ac60_run_summary_contract_unchanged_via_main(sandbox, monkeypatch):
    """E-01/R8 — BUILD_READBACK §5 authorized replacement."""
    crawler.SUMMARY_PATH.write_bytes(b'historical summary')
    old=crawler.PAGE_DIR/'historic.md';old.write_bytes(b'historical markdown')
    code,d=_main(sandbox,monkeypatch,[_result(200,html='<p>a</p>'),_result(500,success=False)],_urls(2))
    assert crawler.SUMMARY_PATH.read_bytes()==b'historical summary' and old.read_bytes()==b'historical markdown'
    assert list(crawler.PAGE_DIR.iterdir())==[old] and _load(d)[0]['counts']['captured']==1


def test_ac61_62_bim000_code_and_config_literals_unchanged():
    """E-01/E-05/E-06 — BUILD_READBACK §5 authorized replacement."""
    src=SOURCE_PATH.read_text()
    for literal in ('wait_for_images=True','delay_before_return_html=3.0','page_timeout=90000','CacheMode.BYPASS'):
        assert src.count(literal)==1
    assert 'random.uniform(' not in src and src.count('def slugify')==1
    with pytest.raises(RuntimeError,match='retired'): crawler.save_markdown('url','text')
    with pytest.raises(RuntimeError,match='retired'): crawler.write_summary([],STARTED,STARTED)


def test_ac63_exit_codes_complete(sandbox, monkeypatch, tmp_path):
    """E-05 — first refusal exits 2; other exit contracts retained."""
    # normal -> 0
    code, _ = _main(sandbox, monkeypatch, [_result(200, html="<p>x</p>")], _urls(1))
    assert code == 0
    # E-05: first blocked -> 2
    code, _ = _main(sandbox, monkeypatch, [_result(429, success=False, raw="")] * 3, _urls(3))
    assert code == 2
    # input file missing (valid project) -> 1
    assert _run_main(monkeypatch, ["--project", "Proj", "--input", str(tmp_path / "missing.json")]) == 1
    # --limit 0 -> argparse 2
    with pytest.raises(SystemExit) as exc:
        crawler.parse_args(["--project", "Proj", "--limit", "0"])
    assert exc.value.code == 2
    # missing / invalid project -> 2
    src = _one_url_input(tmp_path)
    assert _run_main(monkeypatch, ["--input", str(src)]) == 2
    assert _run_main(monkeypatch, ["--project", "bad name", "--input", str(src)]) == 2
