"""F-11 actionable CLI validation without creating outputs or contacting a host."""
import pytest
from recon_pipeline.capture import args_parser

@pytest.mark.parametrize('arguments,flag',[
    (['--url','https://example.invalid'],'--project'),
    (['--project','../escape','--url','https://example.invalid'],'--project'),
    (['--project','Fix','--url','file:///tmp/source'],'--url'),
    (['--project','Fix','--url','https://user:secret@example.invalid'],'--url'),
    (['--project','Fix','--url','https://example.invalid','--limit','0'],'--limit'),
    (['--project','Fix','--url','https://example.invalid','--max-seconds','nan'],'--max-seconds'),
    (['--project','Fix','--url','https://example.invalid','--max-seconds','inf'],'--max-seconds'),
])
def test_actionable_invalid_inputs(arguments,flag,capsys):
    with pytest.raises(SystemExit) as stopped:args_parser(arguments)
    assert stopped.value.code==2
    captured=capsys.readouterr();lines=captured.err.splitlines()
    assert len(lines)==3 and flag in lines[0]
    assert lines[1].startswith('Example: ') and '--help' in lines[2]
    assert 'secret' not in captured.err and not captured.out


def test_valid_capture_cli_is_parsed_without_execution():
    args=args_parser(['--project','Fix','--url','https://example.invalid','--skip-prepare'])
    assert args.project=='Fix' and args.url=='https://example.invalid/' and args.skip_prepare


def test_crawler_default_resolves_latest_raw_routes_preserving_explicit_input(tmp_path,monkeypatch):
    from smart_crawler import crawler
    monkeypatch.setattr(crawler,'RUN_ROOT',tmp_path)
    paths=[]
    for stamp in ('2026-01-01T00-00-00Z','2026-01-02T00-00-00Z'):
        path=tmp_path/'Fix/runs'/stamp/'discovery/routes.json'
        path.parent.mkdir(parents=True);path.write_text('{"schema":"abm-routes-v1","routes":[]}');paths.append(path)
    assert crawler.resolve_routes_input(crawler.parse_args(['--project','Fix']))==paths[-1]
    assert crawler.resolve_routes_input(crawler.parse_args(['--project','Fix','--input',str(paths[0])]))==paths[0]
    assert crawler.resolve_routes_input(crawler.parse_args(['--project','Fix','--routes',str(paths[0])]))==paths[0]


@pytest.mark.parametrize('known,expected',[
    ({'https://example.invalid/','https://www.example.invalid/'},'https://example.invalid/'),
    ({'https://www.example.invalid/'},'https://www.example.invalid/'),
    ({'https://example.invalid/about/'},'https://www.example.invalid/'),
])
def test_redirected_bootstrap_reuses_requested_or_final_route(known,expected):
    from recon_pipeline.capture import bootstrap_route
    assert bootstrap_route('https://example.invalid','https://www.example.invalid/',known)==expected
