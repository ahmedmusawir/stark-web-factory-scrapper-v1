"""C6/CHK F-09/10/12/14 boundaries; synthetic source facts, no live traffic."""
import hashlib
import json
import shutil
import pytest
from raw_fixture_factory import build_raw, ORIGIN
from prepare.reader import RawRun
from smart_crawler.validate import InvalidRaw
from fixture_server import fixture_png


def test_complete_and_valid_partial_are_distinct_and_read_only(tmp_path):
    complete=RawRun(build_raw(tmp_path/'complete'))
    partial=RawRun(build_raw(tmp_path/'partial','partial'))
    before=partial.inventory()
    assert complete.manifest['counts']['captured']==6
    assert partial.manifest['counts']['captured']==5
    assert partial.manifest['counts']['routes']==6
    assert partial.manifest['counts']['rest_objects']==203
    assert partial.manifest['counts']['rest_mapped_routes']==5
    losses={(a['stream'],a['ref']) for a in partial.absences if a['stream'] in ('html','rest') and a['ref'].startswith(ORIGIN)}
    assert losses=={('html',ORIGIN+'/about/'),('rest',ORIGIN+'/services/')}
    assert partial.rest_map['by_route'][ORIGIN+'/services/']['outcome']=='rest_unavailable'
    assert partial.manifest['streams']['html']=='partial' and partial.manifest['streams']['rest']=='partial'
    assert before==RawRun(partial.root).inventory()


@pytest.mark.parametrize('fault',['manifest','schema','map','reference'])
def test_invalid_is_refused_instead_of_called_partial(tmp_path,fault):
    valid=build_raw(tmp_path/'valid'); broken=tmp_path/'invalid'
    excluded={'manifest':'manifest.json','map':'map.json'}.get(fault)
    shutil.copytree(valid,broken,ignore=lambda folder,names:[excluded] if excluded in names else [])
    if fault in ('schema','reference'):
        path=broken/'manifest.json';value=json.loads(path.read_bytes())
        if fault=='schema':value['schema']='unknown'
        else:value['pages'][0]['html_file']='../escape.html'
        path.write_text(json.dumps(value))
    with pytest.raises(InvalidRaw):RawRun(broken)


def test_director_authored_screenshot_is_hashed_and_untouched(tmp_path):
    raw=RawRun(build_raw(tmp_path,authored=True))
    expected=fixture_png()
    assert raw.bytes('screenshots/director.png')==expected
    assert raw.manifest['streams']['screenshots']=='authored'
    assert raw.manifest['screenshots']==[{'file':'screenshots/director.png','sha256':hashlib.sha256(expected).hexdigest(),
                                         'bytes':len(expected),'authored_by':'Director'}]
    assert not any(a['stream']=='screenshots' for a in raw.absences)
