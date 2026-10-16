"""R2 renderer-boundary instrument. Builds a fresh synthetic saved collection from
the exact LEAD-02 B1/B2 fragments (+ controls), runs the product helper, and writes
derived Markdown, markdown-it tokens, rendered HTML, parser settings and hashes.
Usage: renderer_boundary.py <phase> <scratch-root> <lane-out-dir>. No network."""
import hashlib, importlib.util, json, sys
from pathlib import Path
from bs4 import BeautifulSoup
import markdown_it
from markdown_it import MarkdownIt
REPO = Path(__file__).resolve().parents[7]; sys.path.insert(0, str(REPO))
from recon_pipeline.collector import create, persist_result, atomic_json
spec = importlib.util.spec_from_file_location('prepare_saved', REPO/'agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py')
helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
B1 = "<p>Escaped markup text: &lt;script&gt;alert('t23-escaped-text')&lt;/script&gt; shown as characters.</p>"
B2 = "<p>Markdown-shaped text: [click me](javascript:alert('t23-md-inject')) should remain plain text.</p>"
CONTROLS = ('<h1>Καλημέρα heading</h1><h2>Second heading</h2><p>Plain <strong>bold</strong> and <em>emphasis</em> text with café, 1 &lt; 2.</p>'
            '<ul><li>One</li><li>Two</li></ul><ol><li>First</li><li>Second</li></ol><p><a href="/call/">Book a call</a> and <a href="https://example.test/x">Absolute</a>.</p>'
            '<img src="javascript:alert(\'t23-img-src\')" alt="B3 image stays JSON provenance">')
HTML = f'<html><body><header id="thrive-header"><a href="/">Home</a>{B1}{B2}</header><main>{CONTROLS}{B1}{B2}</main></body></html>'
CONFIGS = {'commonmark html=True': ('commonmark', {'html': True}), 'default html=True': ('default', {'html': True}), 'default html=False': ('default', {'html': False})}
sha = lambda b: hashlib.sha256(b).hexdigest()
phase, scratch, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=False)
root = scratch/'input'; (scratch).mkdir(parents=True, exist_ok=False)
state = create(root, {'pages': ['https://example.test/page'], 'rest': []}); item = state['items'][0]
persist_result(root, item, {'body': HTML.encode(), 'status': 200, 'headers': {}, 'final_url': item['url'], 'redirect_from': [],
                            'body_complete': True, 'ok': True, 'error': None, 'saved_at': '2026-10-16T00:00:00+00:00'})
item['status'] = 'completed'; atomic_json(root/'checklist.json', state)
tree = lambda: {str(p.relative_to(root)): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size} for p in root.rglob('*') if p.is_file()}
before = tree(); (out/'synthetic_input.html').write_text(HTML)
index = helper.prepare(root, scratch/'derived', repo=scratch); after = tree()
page = (scratch/index['pages'][0]['prepared']['file']).read_bytes(); boiler = (scratch/index['boilerplate']['file']).read_bytes()
(out/'derived_page.md').write_bytes(page); (out/'derived_BOILERPLATE.md').write_bytes(boiler); (out/'SOURCE_INDEX.json').write_text(json.dumps(index, ensure_ascii=False, indent=1))
report = {'phase': phase, 'helper_sha256': sha((REPO/'agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py').read_bytes()),
          'markdown_it_py': markdown_it.__version__, 'html_parser_for_assertions': 'bs4 html.parser (beautifulsoup4 '+__import__('bs4').__version__+')',
          'raw_tree_before': before, 'raw_tree_after': after, 'raw_unchanged': before == after,
          'derived': {'page': {'sha256': sha(page), 'bytes': len(page), 'index_sha256': index['pages'][0]['prepared']['sha256']},
                      'boilerplate': {'sha256': sha(boiler), 'bytes': len(boiler), 'index_sha256': index['boilerplate']['sha256']}},
          'b3_source_src': index['pages'][0]['content']['images'], 'configs': {}, 'markdown_boundary': {}}
for label, text in (('page', page.decode()), ('boilerplate', boiler.decode())):
    report['markdown_boundary'][label] = {'raw_script_element_present': '<script>' in text, 'link_syntax_to_javascript_present': '](javascript:' in text,
                                          'marker_t23-escaped-text': 't23-escaped-text' in text, 'marker_t23-md-inject': 't23-md-inject' in text}
for name, (preset, opts) in CONFIGS.items():
    md = MarkdownIt(preset, opts); settings = {'preset': preset, 'options': dict(md.options), 'validateLink("javascript:alert(1)")': md.validateLink('javascript:alert(1)'),
                                             'linkify': md.options.get('linkify'), 'custom_link_validator': None}
    entry = {'settings': settings}
    for label, text in (('page', page.decode()), ('boilerplate', boiler.decode())):
        tokens = []
        def walk(ts):
            for t in ts:
                tokens.append(t); walk(t.children or [])
        walk(md.parse(text)); html = md.render(text); dom = BeautifulSoup(html, 'html.parser')
        (out/f'tokens_{label}_{preset}_html{opts["html"]}.json').write_text(json.dumps([{'type': t.type, 'tag': t.tag, 'markup': t.markup, 'info': t.info, 'attrs': dict(t.attrs), 'content': t.content} for t in tokens], ensure_ascii=False, indent=0))
        (out/f'rendered_{label}_{preset}_html{opts["html"]}.html').write_text(html)
        entry[label] = {'html_tokens': [t.content for t in tokens if t.type in ('html_inline', 'html_block')],
                        'link_hrefs': [t.attrGet('href') for t in tokens if t.type == 'link_open'],
                        'dom_script_elements': len(dom.find_all('script')), 'dom_javascript_hrefs': [a['href'] for a in dom.select('a[href]') if a['href'].lower().startswith('javascript:')],
                        'rendered_text_has_B1_literal': "Escaped markup text: <script>alert('t23-escaped-text')</script> shown as characters." in ' '.join(dom.get_text(' ').split()),
                        'rendered_text_has_B2_literal': "Markdown-shaped text: [click me](javascript:alert('t23-md-inject')) should remain plain text." in ' '.join(dom.get_text(' ').split())}
    report['configs'][name] = entry
(out/'boundary_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1)+'\n')
print(json.dumps({'phase': phase, 'raw_unchanged': report['raw_unchanged'], 'markdown_boundary': report['markdown_boundary'],
                  'summary': {n: {l: {'html_tokens': len(e[l]['html_tokens']), 'js_hrefs': e[l]['dom_javascript_hrefs'], 'scripts': e[l]['dom_script_elements'], 'B1_literal': e[l]['rendered_text_has_B1_literal'], 'B2_literal': e[l]['rendered_text_has_B2_literal']} for l in ('page', 'boilerplate')} for n, e in report['configs'].items()}}, ensure_ascii=False, indent=1))
