"""Offline extraction helper for the agent-led Web Recon Prepare skill."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from bs4 import BeautifulSoup, NavigableString
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from recon_pipeline.collector import load, valid_result, artifact

BOILERPLATE = 'header, footer, nav, #thrive-header, #thrive-footer, [role="navigation"], [role="banner"], [role="contentinfo"]'
NON_CONTENT = 'script, style, noscript, template, svg, input[type="hidden"]'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(path, repo):
    return Path(path).resolve().relative_to(repo.resolve()).as_posix()


def clean(node):
    result = BeautifulSoup(str(node), 'html.parser')
    for element in result.select(NON_CONTENT):
        element.decompose()
    # SVG-only breadcrumb separators otherwise become false nested bullets.
    for element in result.select('li'):
        if not element.get_text(' ', strip=True) and not element.select('a[href], img[alt]'):
            element.decompose()
    for element in result.select('a[href]'):
        if urlsplit(element['href']).scheme.lower() not in ('', 'http', 'https', 'mailto', 'tel'):
            del element['href']  # Keep source label, never output an executable JS/data link.
    return result


ANGLE = re.compile(r'([<>])')


def markdown(node, base):
    # Source text must stay literal through conversion: the converter decodes
    # entities, so text angle brackets would re-emerge as raw HTML and
    # bracket/paren text as link syntax. escape_snob backslash-escapes Markdown
    # punctuation in text only (generated links/emphasis untouched); angle
    # brackets are outside its set, so they are escaped here on a copy.
    literal = BeautifulSoup(str(node), 'html.parser')
    for text in literal.find_all(string=True):
        if type(text) is NavigableString and ANGLE.search(text) and not text.find_parent(['code', 'pre']):
            text.replace_with(ANGLE.sub(r'\\\1', text))
    result = DefaultMarkdownGenerator().generate_markdown(
        str(literal).replace('</li>', '</li>\n'), base_url=base, citations=False,
        html2text_options={'body_width': 0, 'ignore_images': True, 'ignore_links': False, 'single_line_break': False, 'escape_snob': True})
    text = result.raw_markdown.strip('\n\r')  # Retain first-list indentation.
    if text.startswith(('Error converting HTML', 'Error in markdown')):
        raise ValueError(text)
    return text+'\n'


def boundary(soup):
    classes = soup.body.get('class', []) if soup.body else []
    if any(c in classes for c in ('archive', 'category')):
        kind, selectors = 'category/article listing', ('#theme-content-section', 'main')
    elif soup.select_one('.tcb-post-content #tve_editor'):
        kind, selectors = 'article', ('.tcb-post-content #tve_editor',)
    else:
        kind = 'landing page' if soup.select_one('#tcb_landing_page') else 'page'
        selectors = ('#tcb_landing_page #tve_editor',) if kind == 'landing page' else ('main', '#theme-content-section', 'article', '#tve_editor')
    for selector in selectors:
        if soup.select_one(selector):
            return kind, selector, soup.select_one(selector), []
    if not soup.body:
        raise ValueError('HTML has no identifiable body')
    return kind, 'body', soup.body, ['fallback body boundary requires agent review']


def prepare(collection, out, repo=REPO):
    collection, out, repo = Path(collection).resolve(), Path(out).resolve(), Path(repo).resolve()
    relative(collection, repo); relative(out, repo)
    if out.exists() or out.is_relative_to(collection):
        raise ValueError('use a NEW derived directory outside the collection')
    state = load(collection)
    # Validate all completed references before creating any output.
    validated = {}
    for item in state['items']:
        if item['status'] == 'completed':
            meta = valid_result(collection, item)
            if meta is None:
                raise ValueError('invalid completed saved result: '+item['id'])
            validated[item['id']] = meta
    index = {'schema': 'web-recon-prepared-v0.1', 'prepared_at': datetime.now(timezone.utc).isoformat(),
        'path_base': 'repository root (same layout in review ZIP)',
        'source_collection': relative(collection, repo),
        'checklist': {'file': relative(collection/'checklist.json', repo),
                      'sha256': sha((collection/'checklist.json').read_bytes())},
        'scope': 'Selected saved sample; not whole-site coverage', 'pages': [], 'rest_context': [],
        'unavailable_items': [], 'historical_context': [], 'agent_authored': [],
        'image_completeness': 'UNVERIFIED; image references do not prove images loaded'}
    generated, boilers = {}, ['# Separated navigation and footer', '',
        'Observed source text, not verified functionality. Main sales sections remain in page Markdown.', '']
    for item in state['items']:
        if item['id'] not in validated:
            index['unavailable_items'].append({k: item.get(k) for k in ('id', 'url', 'kind', 'status', 'error')})
            continue
        meta = validated[item['id']]
        source = {'raw_file': relative(artifact(collection, meta['body_file']), repo),
                  'raw_sha256': meta['sha256'], 'raw_bytes': meta['bytes'],
                  'metadata_file': relative(artifact(collection, item['result']['file']), repo),
                  'metadata_sha256': item['result']['sha256']}
        if item['kind'] == 'rest':
            index['rest_context'].append({'id': item['id'], 'url': item['url'],
                'capture_saved_at': meta['saved_at'], 'source': source,
                'scope': 'saved selected REST response only; not assumed collection coverage'})
            continue
        soup = BeautifulSoup(artifact(collection, meta['body_file']).read_bytes().decode('utf-8'), 'html.parser')
        kind, selector, node, gaps = boundary(soup)
        main = clean(node)
        for element in main.select(BOILERPLATE):
            element.decompose()
        base = meta['final_url'] or item['url']
        content = markdown(main, base)
        name = 'pages/'+item['id']+'.md'
        generated[name] = (f"Source: <{item['url']}>\n\nCapture saved (UTC): {meta['saved_at']}  \nObserved type: {kind}  \nSource ID: `{item['id']}`\n\n<!-- MAIN CONTENT -->\n\n"+content).encode()
        chosen, parts = [], []
        for element in soup.select(BOILERPLATE):
            if any(id(p) in chosen for p in element.parents):
                continue
            chosen.append(id(element))
            text = markdown(clean(element), base)
            if text.strip():
                locator = element.name+('#'+element['id'] if element.get('id') else '')
                parts.append(locator)
                boilers.extend([f"## {item['id']} — {locator}", '', text])
        links = [{'label': a.get_text(' ', strip=True) or None, 'source_href': a['href'],
                  'resolved_url': urljoin(base, a['href'])} for a in main.select('a[href]')]
        row = {'id': item['id'], 'url': item['url'], 'final_url': meta['final_url'],
            'capture_saved_at': meta['saved_at'], 'document_type': kind,
            'title': soup.title.get_text(' ', strip=True) if soup.title else None, 'source': source,
            'extraction': {'css_selector': selector, 'match_index': 0,
                'removed_markup': NON_CONTENT, 'separated_boilerplate': BOILERPLATE,
                'basis': 'observed semantic/theme container; agent must inspect the boundary'},
            'prepared': {'file': relative(out/name, repo), 'sha256': sha(generated[name])},
            'content': {'headings': [x.get_text(' ', strip=True) for x in main.select('h1,h2,h3,h4,h5,h6')],
                'paragraphs': len([p for p in main.select('p') if p.get_text(' ', strip=True)]),
                'list_items': len([li for li in main.select('li') if li.get_text(' ', strip=True)]),
                'empty_list_items_removed': len([li for li in node.select('li') if not li.get_text(' ', strip=True)]), 'links': links,
                'images': [{'alt': image.get('alt'), 'source_src': image.get('src')}
                           for image in main.select('img')],
                'images_note': 'not included as downloaded image bytes or OCR; loading unverified'},
            'boilerplate_locations': parts, 'gaps': gaps}
        index['pages'].append(row)
    generated['BOILERPLATE.md'] = ('\n'.join(boilers)+'\n').encode()
    index['boilerplate'] = {'file': relative(out/'BOILERPLATE.md', repo), 'sha256': sha(generated['BOILERPLATE.md'])}
    out.mkdir(parents=True, exist_ok=False)
    for name, data in generated.items():
        path = out/name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
    with (out/'SOURCE_INDEX.json').open('x') as stream:
        json.dump(index, stream, ensure_ascii=False, indent=2); stream.write('\n')
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collection', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.collection, args.out)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, 'Prepare refused: '+str(exc)+'\n')
    print(json.dumps({'prepared_pages': len(result['pages']),
        'unavailable_items': len(result['unavailable_items']), 'out': str(args.out),
        'next': 'Agent inspects Markdown/source, writes ARCHITECT_BRIEF.md and GAPS_AND_REQUESTS.md, then verifies references.'}))


if __name__ == '__main__':
    main()
