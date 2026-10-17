"""LEAD-02 R2 instrument: inert source text at the Markdown boundary, repaired snapshot.

Executor: Claudy (Claude Code, Claude Fable 5). Independent of engineering's
renderer-boundary records: fresh synthetic collection authored here with the exact
B1/B2 fragments (LEAD-02 §3 R2) placed in BOTH <main> and the shared boilerplate
header, plus positive controls (h1/h2, strong/em, '1 < 2' literal text, ul/ol,
relative + absolute allowed links, Unicode). Prepare runs from the repaired
snapshot inside `unshare -rn` (empty network namespace).
Checks:
  A converter boundary: derived page/BOILERPLATE Markdown contain no raw
    '<script' and no '](javascript:' token; B1/B2 sentences survive as readable
    literal text; controls keep structure/labels/destinations.
  B declared local renderer (markdown-it-py, recorded version): presets
    commonmark html=True, default html=True, default html=False; token stream and
    bs4-parsed DOM inspected for script/active elements and javascript:/data:/
    vbscript: destinations; B1/B2 readable in rendered text.
  C provenance: raw body/metadata/checklist bytes unchanged (before/after
    hashes); SOURCE_INDEX page/boilerplate hashes match written files; B3
    images[].source_src retains the raw javascript: value as untrusted data.
Zero external requests. Writes argv[1].
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAP = Path('/tmp/claudy-lead02-retest-20261016/snapshot-repaired')
SCRATCH = Path('/tmp/claudy-lead02-retest-20261016/r2')
VENV = '/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python'
SCRIPT = SNAP/'agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py'
URL = 'http://synthetic.r2.invalid/inert-page/'
ATT = 'r2attempt00000000000000000000001'
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}

sys.path.insert(0, str(SNAP))
sys.dont_write_bytecode = True
from recon_pipeline.collector import key  # noqa: E402

ID = key('page', URL)
B1_SRC = "Escaped markup text: &lt;script&gt;alert('t23-escaped-text')&lt;/script&gt; shown as characters."
B2_SRC = "Markdown-shaped text: [click me](javascript:alert('t23-md-inject')) should remain plain text."
B1_TEXT = "Escaped markup text: <script>alert('t23-escaped-text')</script> shown as characters."
B2_TEXT = "Markdown-shaped text: [click me](javascript:alert('t23-md-inject')) should remain plain text."

BODY = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>R2 Inert Boundary Page</title></head>
<body class="page">
<header id="thrive-header"><nav><a href="/">Home</a> <a href="/about/">About synthetic studio</a></nav>
<p>{B1_SRC}</p>
<p>{B2_SRC}</p>
</header>
<main id="content" role="main">
<h1>Synthetic Inert Boundary Review Page</h1>
<p>This synthetic page checks that saved source text stays inert through Markdown conversion while real formatting survives.</p>
<p>{B1_SRC}</p>
<p>{B2_SRC}</p>
<h2>Formatting controls</h2>
<p>Math literal: 1 &lt; 2 and 3 &gt; 2. <strong>Bold claim</strong> and <em>soft emphasis</em>. Unicode: Café বাংলা 工場 \U0001f680.</p>
<ul><li>First service: audits</li><li>Second service: migrations</li></ul>
<ol><li>Step one</li><li>Step two</li></ol>
<p>Read the <a href="/case-studies/">case studies archive</a> and the <a href="http://synthetic.r2.invalid/services/">services overview</a>.</p>
<img src="javascript:alert('t23-img-src')" alt="R2 image alt text">
</main>
<footer id="thrive-footer"><p>Synthetic footer for the fictional studio.</p></footer>
</body></html>
""".encode('utf-8')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def build_collection(root):
    if root.exists():
        raise SystemExit(f'refusing to reuse {root}')
    adir = root/'attempts'/ID/ATT
    adir.mkdir(parents=True)
    body_rel = f'attempts/{ID}/{ATT}/body'
    result_rel = f'attempts/{ID}/{ATT}/result.json'
    (root/body_rel).write_bytes(BODY)
    meta = {'url': URL, 'kind': 'page', 'ok': True, 'body_complete': True, 'body_file': body_rel,
            'bytes': len(BODY), 'sha256': sha(BODY), 'saved_at': '2026-10-16T12:20:00+00:00', 'final_url': URL}
    mb = (json.dumps(meta, indent=2)+'\n').encode()
    (root/result_rel).write_bytes(mb)
    checklist = {'schema': 'selected-collection-v1', 'created_at': '2026-10-16T12:20:00+00:00',
                 'items': [{'kind': 'page', 'url': URL, 'id': ID, 'page': 1, 'status': 'completed',
                            'result': {'file': result_rel, 'sha256': sha(mb)},
                            'attempts': [{'file': result_rel, 'sha256': sha(mb)}], 'error': None}]}
    (root/'checklist.json').write_text(json.dumps(checklist, indent=2)+'\n')
    return body_rel, result_rel


def tree_map(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def analyze_markdown(md_text):
    from bs4 import BeautifulSoup
    from markdown_it import MarkdownIt
    import markdown_it
    configs = {'commonmark_htmlTrue': MarkdownIt('commonmark', {'html': True}),
               'default_htmlTrue': MarkdownIt('default', {'html': True}),
               'default_htmlFalse': MarkdownIt('default', {'html': False})}
    out = {'markdown_it_version': markdown_it.__version__,
           'html_assertion_parser': 'bs4 html.parser',
           # G3 instrument correction (run 1 preserved as *.run1): run 1 tested the
           # bare substring '<script', which also matches the backslash-ESCAPED
           # literal '\<script\>' the repair intentionally produces. Active markup
           # means an UNESCAPED '<script' / '](javascript:' token, so occurrences
           # preceded by a backslash are literal text, not raw HTML/link syntax.
           'converter_boundary': {
               'raw_script_substring': bool(re.search(r'(?<!\\)<script', md_text)),
               'escaped_script_literals': md_text.count(r'\<script'),
               'markdown_js_link_token': bool(re.search(r'(?<!\\)\]\(javascript:', md_text)),
               'escaped_js_link_literals': md_text.count(r'\]\(javascript:'),
               'b1_sentence_findable': 't23-escaped-text' in md_text and 'shown as characters' in md_text,
               'b2_sentence_findable': 't23-md-inject' in md_text and 'should remain plain text' in md_text},
           'renders': {}}
    for name, md in configs.items():
        tokens = md.parse(md_text)
        html_out = md.render(md_text)
        soup = BeautifulSoup(html_out, 'html.parser')
        text = soup.get_text(' ', strip=False)
        hrefs = [a.get('href', '') for a in soup.find_all('a')]
        srcs = [t.get('src', '') for t in soup.find_all(('img', 'iframe', 'script'))]
        bad = [u for u in hrefs+srcs if u.strip().lower().startswith(('javascript:', 'data:', 'vbscript:'))]
        out['renders'][name] = {
            'preset_options': {k: v for k, v in md.options.items() if k != 'highlight'},
            'validateLink_javascript': md.validateLink('javascript:alert(1)'),
            'html_token_types': sorted({t.type for t in tokens if 'html' in t.type}),
            'html_token_contents': [t.content for t in tokens if 'html' in t.type],
            'dom_script_elements': len(soup.find_all('script')),
            'active_scheme_destinations': bad,
            'b1_literal_in_rendered_text': B1_TEXT in text.replace('\n', ' '),
            'b2_literal_in_rendered_text': B2_TEXT in text.replace('\n', ' '),
            'controls': {
                'h1': bool(soup.find('h1')), 'h2': bool(soup.find('h2')),
                'strong': bool(soup.find('strong')), 'em': bool(soup.find('em')),
                'ul_items': len(soup.select('ul li')), 'ol_items': len(soup.select('ol li')),
                'math_literal': '1 < 2' in text and '3 > 2' in text,
                'unicode': 'Café' in text and 'বাংলা' in text and '\U0001f680' in text,
                'relative_link': '/case-studies/' in hrefs or any(h.endswith('/case-studies/') for h in hrefs),
                'absolute_link': 'http://synthetic.r2.invalid/services/' in hrefs}}
    return out


def main():
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'snapshot': str(SNAP), 'prepare_script_sha256': sha(SCRIPT.read_bytes()),
           'body_sha256': sha(BODY), 'b1_source': B1_SRC, 'b2_source': B2_SRC}
    # prepare_saved confines --collection/--out to the snapshot root, so the
    # synthetic trees live under the snapshot's outputs/ (same as Q2's method)
    coll = SNAP/'outputs/collections/qa-r2-inert'
    prep = SNAP/'outputs/prepared/qa-r2-inert'
    build_collection(coll)
    before = tree_map(coll)
    argv = ['unshare', '-rn', VENV, str(SCRIPT), '--collection', str(coll), '--out', str(prep)]
    start = now()
    proc = subprocess.run(argv, cwd=SNAP, capture_output=True, text=True, env=ENV)
    out['cli'] = {'argv': argv, 'cwd': str(SNAP), 'start': start, 'end': now(),
                  'exit': proc.returncode, 'stdout': proc.stdout[-2000:], 'stderr': proc.stderr[-2000:]}
    out['raw_collection_unchanged'] = tree_map(coll) == before
    page_md = (prep/'pages'/f'{ID}.md').read_text(encoding='utf-8')
    boiler_md = (prep/'BOILERPLATE.md').read_text(encoding='utf-8')
    out['page'] = analyze_markdown(page_md)
    out['boilerplate'] = analyze_markdown(boiler_md)
    idx = json.loads((prep/'SOURCE_INDEX.json').read_text())
    pages = idx['pages'] if isinstance(idx, dict) and 'pages' in idx else idx
    out['source_index'] = {'raw': 'see file', 'b3_source_src_values': []}
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'source_src':
                    out['source_index']['b3_source_src_values'].append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(idx)
    out['source_index']['b3_retains_raw_javascript_as_data'] = any(
        isinstance(v, str) and v.startswith('javascript:') for v in out['source_index']['b3_source_src_values'])
    # index hashes match written files
    import re
    idx_text = json.dumps(idx)
    hashes_ok = []
    for rel in [f'pages/{ID}.md', 'BOILERPLATE.md']:
        h = sha((prep/rel).read_bytes())
        hashes_ok.append({'file': rel, 'sha256': h, 'listed_in_index': h in idx_text})
    out['index_hashes'] = hashes_ok
    pa, ba = out['page'], out['boilerplate']
    def ok(a):
        c = a['converter_boundary']
        if c['raw_script_substring'] or c['markdown_js_link_token']:
            return False
        if not (c['b1_sentence_findable'] and c['b2_sentence_findable']):
            return False
        for r in a['renders'].values():
            if r['dom_script_elements'] or r['active_scheme_destinations']:
                return False
            if not (r['b1_literal_in_rendered_text'] and r['b2_literal_in_rendered_text']):
                return False
        return True
    page_controls = all(all(v if not isinstance(v, int) or isinstance(v, bool) else v > 0
                            for v in r['controls'].values())
                        for r in pa['renders'].values())
    out['verdict_r2'] = ('PASS' if out['cli']['exit'] == 0 and out['raw_collection_unchanged']
                         and ok(pa) and ok(ba) and page_controls
                         and all(h['listed_in_index'] for h in hashes_ok)
                         and out['source_index']['b3_retains_raw_javascript_as_data']
                         else 'FAIL')
    out['safety_boundary_statement'] = (
        'Verified for the converter output and markdown-it-py '
        f"{pa['markdown_it_version']} under commonmark/default presets with html on and off; "
        'backslash-escape semantics per CommonMark. Not a claim about renderers that ignore '
        'backslash escapes or that serve .md as raw HTML; no browser exploit claimed or tested.')
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_r2': out['verdict_r2'], 'exit': out['cli']['exit'],
                      'raw_unchanged': out['raw_collection_unchanged'],
                      'page_ok': ok(pa), 'boiler_ok': ok(ba), 'controls_ok': page_controls,
                      'b3_data_retained': out['source_index']['b3_retains_raw_javascript_as_data']},
                     indent=1))
    return 0 if out['verdict_r2'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
