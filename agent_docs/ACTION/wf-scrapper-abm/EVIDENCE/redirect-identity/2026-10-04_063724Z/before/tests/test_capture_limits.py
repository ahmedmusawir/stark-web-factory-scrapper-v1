"""C3 durable partial evidence, no overwrite, interrupt and persistence limits."""
import json
import asyncio
import sys
from pathlib import Path

import pytest

from smart_crawler import crawler
from smart_crawler.validate import validate_run


def test_sigint_finalizes_structurally_valid_partial(tmp_path,monkeypatch):
    source=tmp_path/'urls.json';source.write_text(json.dumps(['http://127.0.0.1/one/','http://127.0.0.1/two/']))
    monkeypatch.setattr(crawler,'RUN_ROOT',tmp_path/'outputs')
    monkeypatch.setattr(sys,'argv',['crawler','--project','Fix','--input',str(source)])
    async def interrupted(urls,run):
        crawler.record_capture(run,{'url':urls[0],'status':200,'error':None,'elapsed_s':.1,'ok':True},
                               urls[0],'<p>saved first page</p>',True)
        raise KeyboardInterrupt
    monkeypatch.setattr(crawler,'run',interrupted)
    with pytest.raises(SystemExit) as exc: crawler.main()
    assert exc.value.code==130
    run=next((tmp_path/'outputs/Fix/runs').iterdir())
    assert validate_run(run)
    manifest=json.loads((run/'manifest.json').read_text())
    assert manifest['stopped_early'] and [p['outcome'] for p in manifest['pages']]==['captured','skipped']
    assert (run/manifest['pages'][0]['html_file']).read_text()=='<p>saved first page</p>'


def test_byte_guard_preserves_prior_bytes_and_metadata_reserve(tmp_path):
    run=crawler.RunFolder('Fix',crawler.utc_now(),root=tmp_path).create()
    run.max_bytes=100;run.metadata_reserve=30
    run.save_bytes('html/one.html',b'a'*60)
    with pytest.raises(BufferError):run.save_bytes('html/two.html',b'b'*20)
    assert run.limit_hit and (run.dir/'html/one.html').read_bytes()==b'a'*60
    assert not (run.dir/'html/two.html').exists()
    run.save_bytes('final.json',b'{"stopped":true}',finalization=True)
    assert run.persisted_bytes()<=100
    with pytest.raises(FileExistsError):run.save_bytes('html/one.html',b'changed',finalization=True)
    assert (run.dir/'html/one.html').read_bytes()==b'a'*60
