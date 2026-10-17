"""Offline behavioral checks for the Prepare skill; no browser or live traffic."""
import importlib.util
from pathlib import Path
import json
import socket
from urllib.parse import urljoin
import pytest
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[2]
spec = importlib.util.spec_from_file_location('prepare_saved', SKILL/'scripts/prepare_saved.py')
helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
from recon_pipeline.collector import create, persist_result, atomic_json, load


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Prepare attempted network access')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(socket, 'create_connection', forbidden)


def saved(tmp_path, html):
    collection = tmp_path/'input'
    state = create(collection, {'pages': ['https://example.test/page'], 'rest': []})
    item = state['items'][0]
    persist_result(collection, item, {'body': html.encode(), 'status': 200, 'headers': {},
        'final_url': item['url'], 'redirect_from': [], 'body_complete': True, 'ok': True,
        'error': None, 'saved_at': '2026-10-11T00:00:00+00:00'})
    item['status'] = 'completed'; atomic_json(collection/'checklist.json', state)
    return collection, state


def document(index, repo):
    text = (repo/index['pages'][0]['prepared']['file']).read_text().split('<!-- MAIN CONTENT -->', 1)[1]
    return BeautifulSoup(MarkdownIt().render(text), 'html.parser')


def test_landing_page_not_newsletter_and_boilerplate_separated(tmp_path):
    html = '<html><body><div id="tcb_landing_page"><div id="tve_editor"><div id="thrive-header">Shared Navigation</div><h1>Core offering</h1><p>Useful main text.</p><a href="/call">Book call</a><div id="thrive-footer">Shared Footer</div></div></div><article><p>Unrelated newsletter</p></article></body></html>'
    root, _ = saved(tmp_path, html)
    result = helper.prepare(root, tmp_path/'derived', repo=tmp_path)
    rendered = document(result, tmp_path)
    assert rendered.h1.get_text() == 'Core offering'
    assert rendered.find('a')['href'] == 'https://example.test/call'
    assert 'Unrelated newsletter' not in rendered.get_text()
    assert 'Shared Navigation' not in rendered.get_text() and 'Shared Footer' not in rendered.get_text()
    boiler = (tmp_path/result['boilerplate']['file']).read_text()
    assert 'Shared Navigation' in boiler and 'Shared Footer' in boiler


def test_unicode_paragraphs_lists_links_cta_and_scripts(tmp_path):
    html = '<html><body><main><h1>Καλημέρα 世界</h1><p>First paragraph: café.</p><p>Second paragraph.</p><ul><li>One</li><li>Two</li></ul><a href="/call?source=saved">Book my call</a><script>unwanted_script()</script><style>.secret{}</style></main></body></html>'
    root, _ = saved(tmp_path, html)
    result = helper.prepare(root, tmp_path/'derived', repo=tmp_path);h = document(result,tmp_path)
    assert h.h1.get_text() == 'Καλημέρα 世界'
    assert [p.get_text() for p in h.select('p')][:2] == ['First paragraph: café.', 'Second paragraph.']
    assert [p.get_text() for p in h.select('li')] == ['One','Two']
    assert h.find('a', string='Book my call')['href'] == 'https://example.test/call?source=saved'
    assert 'unwanted_script' not in h.get_text() and '.secret' not in h.get_text()


@pytest.mark.parametrize('corruption',['body','metadata','escaping_reference'])
def test_invalid_completed_reference_refused_before_output(tmp_path,corruption):
    root,state = saved(tmp_path,'<html><body><main><p>Original</p></main></body></html>')
    item=state['items'][0];meta_path=root/item['result']['file'];meta=json.loads(meta_path.read_bytes())
    if corruption=='body':(root/meta['body_file']).write_bytes(b'altered')
    elif corruption=='metadata':meta_path.write_text('{}')
    else:
        item['result']['file']='../outside.json';atomic_json(root/'checklist.json',state)
    with pytest.raises(ValueError,match='invalid completed saved result'):
        helper.prepare(root,tmp_path/'derived',repo=tmp_path)
    assert not (tmp_path/'derived').exists()


@pytest.mark.parametrize('destination',['existing','inside'])
def test_preserves_existing_packages_and_input(tmp_path,destination):
    root,_=saved(tmp_path,'<html><body><main><p>Useful</p></main></body></html>')
    before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
    out=tmp_path/'existing' if destination=='existing' else root/'derived'
    if destination=='existing':out.mkdir();(out/'keep.txt').write_text('Preserve me')
    with pytest.raises(ValueError,match='NEW derived directory'):helper.prepare(root,out,repo=tmp_path)
    assert before=={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
    if destination=='existing':assert (out/'keep.txt').read_text()=='Preserve me'


def test_pending_item_is_gap_not_fabricated_page(tmp_path):
    root=tmp_path/'input';create(root,{'pages':['https://example.test/missing']})
    result=helper.prepare(root,tmp_path/'derived',repo=tmp_path)
    assert result['pages']==[] and result['unavailable_items'][0]['status']=='pending'


def text(node):return ' '.join(node.get_text(' ',strip=True).split())


def test_actual_three_page_capture_exact_content(tmp_path):
    root=REPO/'outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505'
    # Keep the real inputs untouched; output only in the test directory.
    result=helper.prepare(root,tmp_path/'actual',repo=Path('/'))
    assert [p['document_type'] for p in result['pages']]==['landing page','category/article listing','article']
    for row in result['pages']:
        raw=BeautifulSoup((Path('/')/row['source']['raw_file']).read_bytes().decode('utf-8'),'html.parser')
        node=raw.select(row['extraction']['css_selector'])[0]
        for boiler in node.select(helper.BOILERPLATE):boiler.decompose()
        generated=(Path('/')/row['prepared']['file']).read_text().split('<!-- MAIN CONTENT -->',1)[1]
        md=BeautifulSoup(MarkdownIt().render(generated),'html.parser')
        assert [text(n) for n in node.select('h1,h2,h3,h4,h5,h6')]==[text(n) for n in md.select('h1,h2,h3,h4,h5,h6')]
        paragraphs=[text(p) for p in node.select('p') if text(p)]
        rendered_paragraphs=[text(p) for p in md.select('p')]
        assert all(p in rendered_paragraphs for p in paragraphs)
        assert [text(n) for n in node.select('li')]==[text(n) for n in md.select('li')]
        meaningful={(text(a),urljoin(row['final_url'],a['href'])) for a in node.select('a[href]') if text(a) and a['href'].startswith(('/', 'http','mailto:','tel:','#'))}
        rendered={(text(a),a['href']) for a in md.select('a[href]')}
        assert meaningful <= rendered
        if row['document_type']=='article':
            assert len(paragraphs)==7 and len(md.select('li'))==15
            assert len(node.select('h1,h2,h3,h4,h5,h6'))==6
        if row['document_type']=='landing page':
            assert 'We provide Digital Solutions for growing your business' in [text(h) for h in md.select('h1')]
        if row['document_type']=='category/article listing':
            assert 'category-agency-services' in raw.body['class']
            assert 'Page 1 of 7' in md.get_text(' ',strip=True)
