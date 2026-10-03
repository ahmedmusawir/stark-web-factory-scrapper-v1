"""C6 actual CLI/worker/browser integration; Capture-only, no Prepare construction."""
import json
import os
from pathlib import Path
import subprocess
import sys

from fixture_server import fixture_server,HEALTHY_PATHS,wp_inputs
from prepare.reader import RawRun


def test_complete_capture_cli_with_real_browser(tmp_path):
    with fixture_server(mode='pipeline',port=8765) as (origin,timeline):
        command=[sys.executable,'-m','recon_pipeline','--project','Fix','--url',origin,
                 '--skip-prepare','--fixture-only','--max-operations','40','--max-seconds','600',
                 '--max-bytes','20000000','--output-root',str(tmp_path/'output')]
        result=subprocess.run(command,capture_output=True,text=True,timeout=300)
        evidence=os.environ.get('ABM_CONTROL_EVIDENCE')
        if evidence:
            folder=Path(evidence);folder.mkdir(parents=True,exist_ok=True)
            (folder/'capture-cli.log').write_text(result.stdout+result.stderr)
            (folder/'capture-server.json').write_text(json.dumps(timeline,indent=2))
            (folder/'capture-command.json').write_text(json.dumps({'command':command,'exit_code':result.returncode},indent=2))
        assert result.returncode==0,result.stdout+result.stderr
        raw=RawRun(next((tmp_path/'output/Fix/runs').iterdir()))
        assert raw.manifest['run_id']=='2026-01-01T00-00-00Z'
        assert [p['url'] for p in raw.manifest['pages']]==[origin+x for x in HEALTHY_PATHS]
        assert raw.manifest['counts']['captured']==6 and raw.manifest['counts']['routes']==6
        assert raw.manifest['counts']['rest_objects']==204 and raw.manifest['counts']['rest_mapped_routes']==6
        assert raw.manifest['access']['intentional_dispatches']==18
        assert raw.manifest['access']['document_slots_used']==6
        assert raw.manifest['streams']['rest']=='complete' and raw.manifest['streams']['media']=='complete'
        assert not raw.manifest['stopped_early'] and not (tmp_path/'output/Fix/packs').exists()
        assert len([e for e in timeline if e['event']=='request_received' and e['path']=='/' and e['method']=='GET'])==1
        for response in raw.rest_index['responses']:
            assert raw.bytes(response['file'],'rest/index.json')==wp_inputs(origin)[response['url']]['body']
        assert not (raw.root/'runtime').exists()
        assert len(raw.json('source_identity.json')['files'])>10
        from snapshot_compare import compare_capture
        compare_capture(raw.root,timeline)
        if evidence:
            import shutil
            shutil.copytree(raw.root,folder/'complete-raw')
        # E-14: compare the full canonical record, and prove meaningful mutations
        # cannot hide behind timestamp/ID normalization. Every variant is NEW.
        from snapshot_compare import compare_two_captures
        from smart_crawler.validate import InvalidRaw
        import hashlib
        import shutil
        import pytest
        assert compare_two_captures(raw.root,raw.root)['files']==231
        for fault in ('source_byte','object_value','hash','reference','outcome','count','authored_metadata'):
            changed=tmp_path/('negative-'+fault)
            shutil.copytree(raw.root,changed)
            manifest=json.loads((changed/'manifest.json').read_bytes())
            page=manifest['pages'][0]
            if fault=='source_byte':
                path=changed/page['html_file'];body=path.read_bytes()+b' ';path.write_bytes(body)
                page['sha256']=hashlib.sha256(body).hexdigest();page['html_bytes']=len(body)
            elif fault=='object_value':
                index=json.loads((changed/'rest/index.json').read_bytes());obj=index['objects'][0]
                path=changed/'rest'/obj['file'];body=path.read_bytes().replace(b'Page 0',b'Altered 0')
                path.write_bytes(body);obj['sha256']=hashlib.sha256(body).hexdigest()
                (changed/'rest/index.json').write_text(json.dumps(index))
            elif fault=='hash':page['sha256']='0'*64
            elif fault=='reference':
                other=manifest['pages'][1]
                for key in ('html_file','sha256','html_bytes'):page[key]=other[key]
            elif fault=='outcome':
                page.update(outcome='failed',reason='synthetic_failure',html_file=None,sha256=None,html_bytes=None)
                manifest['counts']['captured']-=1;manifest['counts']['failed']+=1
                gaps=json.loads((changed/'absences.json').read_bytes())
                gaps.append(dict(stream='html',ref=page['url'],outcome='failed',reason='synthetic_failure',at=manifest['finished_at']))
                (changed/'absences.json').write_text(json.dumps(gaps))
            elif fault=='count':manifest['counts']['routes']+=1
            else:
                media=json.loads((changed/'media/inventory.json').read_bytes())
                media['items'][0]['title']='Meaningful metadata changed'
                (changed/'media/inventory.json').write_text(json.dumps(media))
            (changed/'manifest.json').write_text(json.dumps(manifest))
            with pytest.raises((AssertionError,InvalidRaw)):
                compare_two_captures(raw.root,changed)
