"""Part A: import saved Capture evidence and persist explicit human choices.

No browser, discovery execution, capture, Prepare construction or ranking.
Document universe = saved discovery routes UNION returned REST pages/posts links.
Other collections and media coverage remain context, never automatic exclusions.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from prepare.reader import RawRun

INVENTORY_SCHEMA = 'web-recon-imported-inventory-v1'
CHOICES_SCHEMA = 'web-recon-human-choices-v1'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def item_id(url):
    return 'doc-' + hashlib.sha256(url.encode('utf-8')).hexdigest()[:20]


def inventory_binding(inv):
    return digest({'source_snapshot_sha256': inv['source_run']['snapshot_sha256'],
                   'context': inv['context'],
                   'items': sorted(inv['items'], key=lambda x: x['id'])})


def build_inventory(root):
    raw = RawRun(root)  # mandatory structural/reference/hash validation; no fetch
    hashes = raw.inventory()
    rows = {}

    def item(url):
        return rows.setdefault(url, {'id': item_id(url), 'url': url, 'title': None,
            'titles': [], 'content_types': [], 'dates': [], 'sources': [],
            'discovery_provenance': [], 'capture_outcome': None, 'gaps': []})

    def source(row, file, locator, **values):
        row['sources'].append({'file': file, 'locator': locator,
                               'sha256': hashes[file], **values})

    def title(row, value, file, locator, preferred=False):
        if not isinstance(value, str) or not value.strip():
            return
        text = BeautifulSoup(value, 'html.parser').get_text(' ', strip=True)
        if not text:
            return
        row['titles'].append({'value': text, 'source_file': file, 'locator': locator})
        if preferred or row['title'] is None:
            row['title'] = text

    def date(row, kind, value, file, locator):
        if isinstance(value, str) and value:
            row['dates'].append({'kind': kind, 'value': value, 'source_file': file,
                                 'locator': locator})

    for i, route in enumerate(raw.routes['routes']):
        row = item(route['url'])
        source(row, 'discovery/routes.json', f'$.routes[{i}]')
        row['discovery_provenance'].append({'route_position': i,
            'source_file': route.get('source_file'), 'input_urls': route.get('input_urls', []),
            'aliases': route.get('aliases', [])})
        if route.get('source_file'):
            file = 'discovery/' + route['source_file']
            source(row, file, 'route source; see $.routes[%d]' % i)
        date(row, 'sitemap_lastmod', route.get('lastmod'), 'discovery/routes.json',
             f'$.routes[{i}].lastmod')

    for i, page in enumerate(raw.manifest['pages']):
        row = item(page['url'])
        source(row, 'manifest.json', f'$.pages[{i}]')
        row['capture_outcome'] = {'outcome': page['outcome'], 'reason': page['reason'],
                                  'status': page['status'], 'final_url': page['final_url']}
        date(row, 'fetched_at', page.get('fetched_at'), 'manifest.json', f'$.pages[{i}].fetched_at')
        if page.get('html_file'):
            file = page['html_file']
            source(row, file, 'rendered HTML; not REST content')
            soup = BeautifulSoup(raw.bytes(file), 'html.parser')
            if soup.title:
                title(row, soup.title.get_text(), file, 'html/title')
        elif page['outcome'] != 'captured':
            row['gaps'].append('rendered_html_' + page['outcome'])

    responses = {x['file']: x for x in raw.rest_index['responses']}
    for i, ref in enumerate(raw.rest_index['objects']):
        response = responses[ref['response_file']]
        if response['collection'] not in ('pages', 'posts'):
            continue
        obj = raw.json(ref['file'], 'rest/index.json')
        row = item(obj['link'])  # exact observed link, no guessed canonical merge
        file = 'rest/' + ref['file']
        source(row, file, '$', wp_id=obj['id'], collection=response['collection'])
        source(row, 'rest/' + ref['response_file'], f'$[{ref["array_position"]}]',
               boundary=response.get('boundary'), body_complete=response.get('body_complete'))
        source(row, 'rest/index.json', f'$.objects[{i}]')
        kind = obj.get('type')
        if isinstance(kind, str) and kind not in row['content_types']:
            row['content_types'].append(kind)
        value = obj.get('title')
        title(row, value.get('rendered') if isinstance(value, dict) else None,
              file, '$.title.rendered', preferred=row['title'] is None or
              not any(t['source_file'].startswith('rest/') for t in row['titles']))
        for name in ('date', 'date_gmt', 'modified', 'modified_gmt'):
            date(row, name, obj.get(name), file, '$.' + name)
        if 'content' not in obj:
            row['gaps'].append('rest_content_missing')
        elif obj['content'] is None:
            row['gaps'].append('rest_content_null')
        elif isinstance(obj['content'], dict):
            if 'rendered' not in obj['content']:
                row['gaps'].append('rest_content_rendered_missing')
            elif obj['content']['rendered'] is None:
                row['gaps'].append('rest_content_rendered_null')
            elif not BeautifulSoup(obj['content']['rendered'], 'html.parser').get_text('', strip=True):
                row['gaps'].append('rest_content_rendered_empty')
        for name in ('yoast_head_json', 'yoast_head'):
            if name not in obj:
                row['gaps'].append(name + '_missing')
            elif obj[name] is None:
                row['gaps'].append(name + '_null')

    items = sorted(rows.values(), key=lambda x: x['url'])
    for row in items:
        if row['title'] is None:
            row['gaps'].append('title_unknown')
        if not row['content_types']:
            row['gaps'].append('wordpress_content_type_unknown')
        if not row['dates']:
            row['gaps'].append('dates_unknown')
        if row['capture_outcome'] is None:
            row['gaps'].append('rendered_capture_not_selected_or_not_known')
        row['gaps'] = sorted(set(row['gaps']))
        row['selection'] = 'UNDECIDED'
    if len({x['id'] for x in items}) != len(items):
        raise ValueError('stable-ID collision; no inventory written')

    collections = []
    for col in raw.rest_index['collections']:
        ids = [raw.json(x['file'], 'rest/index.json')['id'] for x in raw.rest_index['objects']
               if responses[x['response_file']]['collection'] == col['type']]
        pages = [x for x in raw.rest_index['responses'] if x['collection'] == col['type']]
        collections.append({'type': col['type'], 'status': col['status'],
            'advertised_total': col.get('total'), 'advertised_pages': col.get('total_pages'),
            'fetched_pages': [x['page'] for x in pages], 'saved_records': len(ids),
            'unique_ids': len(set(ids)), 'duplicate_records': len(ids)-len(set(ids)),
            'record_gap': col['total']-len(set(ids)) if col.get('total') is not None else None,
            'short_page_anomalies': [{'page': x['page'], 'anomalies': x['pagination_anomalies']}
                                      for x in pages if x.get('pagination_anomalies')]})
    shutdown = None
    for line in raw.bytes('stage_log.txt').decode('utf-8').splitlines():
        if ' browser {' in line:
            event = json.loads(line.split(' browser ', 1)[1])
            if event['event'] == 'shutdown_complete':
                shutdown = {k: event.get(k) for k in
                            ('confirmed_aborts', 'unconfirmed_count', 'stop_reason')}
    inv = {'schema': INVENTORY_SCHEMA, 'origin': 'IMPORTED_CAPTURE_INVENTORY',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'source_run': {'local_input_locator': str(raw.root),
            'locator_role': 'read-only local input, not a raw/pack output reference',
            'run_id': raw.manifest['run_id'], 'project': raw.manifest['project_name'],
            'snapshot_sha256': digest(hashes), 'manifest_sha256': hashes['manifest.json'],
            'capture_source_identity_sha256': hashes.get('source_identity.json')},
        'context': {'candidate_universe': 'discovery routes union returned REST pages/posts links; no automatic exclusions',
            'capture_stopped_early': raw.manifest['stopped_early'],
            'capture_stop_reason': raw.manifest['access'].get('stop_reason'),
            'shutdown': shutdown, 'streams': raw.manifest['streams'],
            'collections': collections, 'media_inventory': raw.media['counts'],
            'source_files': {file: hashes[file] for file in
                             ('manifest.json', 'rest/index.json', 'media/inventory.json', 'stage_log.txt')},
            'unknowns': ['Not a fresh lightweight recon run; no current accessibility claim.',
                'Media/taxonomy/users are context, not document candidates.',
                'Hidden/deferred content completeness unknown; missing metadata is not inferred.',
                'Selection does not authorize or execute capture.',
                'HTTP response MIME is not inferred from WordPress object type.',
                'Independent QA NOT RUN; Prepare ON HOLD.']},
        'items': items}
    inv['inventory_id'] = inventory_binding(inv)
    return inv


def validate_inventory(inv):
    if inv.get('schema') != INVENTORY_SCHEMA or inv.get('origin') != 'IMPORTED_CAPTURE_INVENTORY':
        raise ValueError('not an imported Capture inventory')
    ids = [x['id'] for x in inv['items']]
    if len(ids) != len(set(ids)) or any(x['id'] != item_id(x['url']) for x in inv['items']):
        raise ValueError('invalid/duplicate stable IDs')
    if inv.get('inventory_id') != inventory_binding(inv):
        raise ValueError('inventory content binding mismatch')
    return inv


def load_inventory(path):
    return validate_inventory(json.loads(Path(path).read_text()))


def load_choices(path, inv):
    doc = json.loads(Path(path).read_text())
    if doc.get('schema') != CHOICES_SCHEMA or doc.get('inventory_id') != inv['inventory_id'] or \
            doc.get('source_snapshot_sha256') != inv['source_run']['snapshot_sha256']:
        raise ValueError('choices belong to a different inventory/source snapshot')
    known = {x['id'] for x in inv['items']}
    for key, choice in doc['choices'].items():
        if key not in known or choice.get('decision') not in ('include', 'exclude') or not isinstance(choice.get('note'), str):
            raise ValueError('unknown ID or malformed human choice')
    return doc


def guard_output(path, inv):
    path = Path(path).resolve()
    raw = Path(inv['source_run']['local_input_locator']).resolve()
    if path == raw or path.is_relative_to(raw):
        raise ValueError('cannot write into the original raw run')
    if path.exists():
        raise FileExistsError('output already exists; choose a NEW path')
    return path


def save_choices(inv, output, include=(), exclude=(), previous=None, note=''):
    validate_inventory(inv)
    included, excluded = set(include), set(exclude)
    known = {x['id'] for x in inv['items']}
    if (included | excluded) - known:
        raise ValueError('unknown stable IDs: ' + ', '.join(sorted((included | excluded)-known)))
    if included & excluded:
        raise ValueError('same ID included and excluded in one command')
    if not included and not excluded:
        raise ValueError('provide an explicit human inclusion or exclusion')
    choices = dict(load_choices(previous, inv)['choices']) if previous else {}
    for decision, ids in [('include', included), ('exclude', excluded)]:
        for key in sorted(ids):
            choices[key] = {'decision': decision, 'note': note}
    doc = {'schema': CHOICES_SCHEMA, 'inventory_id': inv['inventory_id'],
        'source_snapshot_sha256': inv['source_run']['snapshot_sha256'],
        'saved_at': datetime.now(timezone.utc).isoformat(), 'actor': 'explicit human choices',
        'previous_file': str(Path(previous).resolve()) if previous else None, 'choices': choices}
    output = guard_output(output, inv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        stream.write(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    return doc


def display(value):
    text = html.escape(str(value), quote=False).replace('\n', ' ').replace('\r', ' ')
    for char in ('\\', '`', '*', '_', '[', ']', '|'):
        text = text.replace(char, '\\' + char)
    return text


def listing(inv, choices=None):
    decisions = choices['choices'] if choices else {}
    lines = ['# Imported Capture document inventory', '',
        '**IMPORTED_CAPTURE_INVENTORY — offline only; all unspecified choices UNDECIDED.**', '',
        f"Source run: `{inv['source_run']['run_id']}`; inventory ID: `{inv['inventory_id']}`.",
        f"Capture stop: `{inv['context']['capture_stop_reason']}`; stopped early: {inv['context']['capture_stopped_early']}.",
        f"Shutdown: `{inv['context']['shutdown']}`.", '', '## Collection coverage', '']
    for col in inv['context']['collections']:
        lines.append(f"- {col['type']}: {col['unique_ids']} unique / {col['advertised_total']} advertised; "
                     f"{len(col['fetched_pages'])}/{col['advertised_pages']} pages; status {col['status']}; "
                     f"record gap {col['record_gap']}; duplicate records {col['duplicate_records']}; "
                     f"short-page anomalies {len(col['short_page_anomalies'])}.")
    lines += ['', '## Document candidates', '',
              'Numbers are display positions only. Save choices using stable IDs.', '']
    for n, row in enumerate(inv['items'], 1):
        decision = decisions.get(row['id'], {}).get('decision', 'UNDECIDED')
        lines += [f"{n}. **{display(row['title']) if row['title'] is not None else '[title unknown]'}** — `{row['id']}` — {decision}",
            f"   - URL: {display(row['url'])}",
            f"   - Type: {display(', '.join(row['content_types']) or 'unknown')}; dates: " +
             display('; '.join(x['kind']+'='+x['value'] for x in row['dates']) or 'unknown'),
            f"   - Sources: " + display('; '.join(x['file']+' '+x['locator'] for x in row['sources'])),
            f"   - Gaps: " + display(', '.join(row['gaps']) or 'none recorded')]
    return '\n'.join(lines) + '\n'


def export_inventory(raw_path, out):
    inv = build_inventory(raw_path)
    out = guard_output(out, inv)
    out.mkdir(parents=True, exist_ok=False)
    for name, value in [('inventory.json', json.dumps(inv, ensure_ascii=False, indent=2)+'\n'),
                        ('INVENTORY.md', listing(inv))]:
        with (out/name).open('x') as stream:
            stream.write(value)
    return inv


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    imp = commands.add_parser('import', help='Validate saved raw, write NEW imported inventory')
    imp.add_argument('--raw', type=Path, required=True);imp.add_argument('--out', type=Path, required=True)
    show = commands.add_parser('list', help='Read inventory and optional saved choices')
    show.add_argument('--inventory', type=Path, required=True);show.add_argument('--choices', type=Path)
    choose = commands.add_parser('choose', help='Save explicit human choices in a NEW file')
    choose.add_argument('--inventory', type=Path, required=True);choose.add_argument('--out', type=Path, required=True)
    choose.add_argument('--include', action='append', default=[]);choose.add_argument('--exclude', action='append', default=[])
    choose.add_argument('--previous', type=Path);choose.add_argument('--note', default='')
    args = parser.parse_args(argv)
    try:
        if args.command == 'import':
            inv = export_inventory(args.raw, args.out)
            print(f"IMPORTED_CAPTURE_INVENTORY: {len(inv['items'])} document candidates; all UNDECIDED; {args.out}")
        else:
            inv = load_inventory(args.inventory)
            if args.command == 'list':
                print(listing(inv, load_choices(args.choices, inv) if args.choices else None), end='')
            else:
                save_choices(inv, args.out, args.include, args.exclude, args.previous, args.note)
                print(f'Explicit choices saved: {args.out}; capture was not started')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, 'Offline inventory refused: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
