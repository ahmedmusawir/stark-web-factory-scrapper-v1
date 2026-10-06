"""Structural validation of raw evidence; never fetches or repairs anything."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

SCHEMAS = {'manifest.json': 'abm-raw-v2', 'discovery/routes.json': 'abm-routes-v1',
           'rest/index.json': 'abm-rest-index-v1', 'rest/map.json': 'abm-rest-map-v1',
           'media/inventory.json': 'abm-media-v1'}
OUTCOMES = {'captured', 'blocked', 'failed', 'unsupported', 'skipped'}
COLLECTIONS = {'pages', 'posts', 'media', 'categories', 'tags', 'users'}


class InvalidRaw(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidRaw(message)


def reference(root, owner, value):
    """Check only schema-declared authored references, preserving untouched source values."""
    require(isinstance(value, str) and value and not Path(value).is_absolute(), f'invalid reference in {owner}')
    require('\\' not in value and '\x00' not in value, f'nonportable reference in {owner}')
    path = (root / owner).parent / value
    require(path.resolve().is_relative_to(root.resolve()), f'reference escapes run: {owner} -> {value}')
    require(path.is_file(), f'missing reference: {owner} -> {value}')
    return path


def hashed(path, entry, size_key=None):
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == entry['sha256'], f'hash mismatch: {path.name}')
    if size_key:
        require(type(entry[size_key]) is int and len(data) == entry[size_key], f'byte count mismatch: {path.name}')
    return data


def load(path):
    def no_constants(value):
        raise InvalidRaw(f'invalid JSON constant {value}')
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            require(key not in obj, f'duplicate JSON key in {path.name}: {key}')
            obj[key] = value
        return obj
    return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=no_constants, parse_float=Decimal)


def validate_run(root):
    """Return validation observations or raise InvalidRaw; partial is not malformed."""
    root = Path(root)
    try:
        docs = {}
        for name, schema in SCHEMAS.items():
            path = reference(root, 'manifest.json', name)
            doc = load(path)
            require(isinstance(doc, dict) and next(iter(doc), None) == 'schema' and doc['schema'] == schema,
                    f'invalid schema/envelope: {name}')
            docs[name] = doc
        for name in ('absences.json', 'stage_log.txt', 'screenshots/README.md'):
            reference(root, 'manifest.json', name)
        absent = load(root / 'absences.json')
        require(isinstance(absent, list), 'absences must be an array')
        for a in absent:
            require(set(a) == {'stream', 'ref', 'outcome', 'reason', 'at'}, 'invalid absence fields')
            require(a['outcome'] in OUTCOMES - {'captured'} and a['stream'] in
                    {'html', 'rest', 'media', 'discovery', 'screenshots'}, 'invalid absence type')
            require(all(isinstance(a[k], str) and a[k] for k in a), 'invalid absence value')
        manifest, routes, index, mapping, media = (docs[x] for x in SCHEMAS)
        require(isinstance(manifest['pages'], list), 'pages must be an array')
        mandatory={'schema','project_name','run_id','started_at','finished_at','command','input','scope','access','versions',
                   'streams','counts','stopped_early','fallbacks_fired','pages'}
        require(mandatory <= set(manifest), 'mandatory manifest fields missing')
        require(type(manifest['stopped_early']) is bool and manifest['fallbacks_fired']==[], 'invalid stop/fallback metadata')
        for name in ('project_name','run_id','started_at','finished_at','command'):
            require(isinstance(manifest[name],str) and manifest[name], f'invalid manifest {name}')
        require(manifest['run_id']==manifest['started_at'][:19].replace(':','-')+'Z', 'run ID/time mismatch')
        access=manifest['access']
        for name,value in {'operation_gap_after_completion_s':5.0,'retry_max':0,'stop_on_first_intentional_refusal':True,
                           'automatic_restart':False,'background_resources_paced':False,'wait_for_images':True,
                           'page_timeout_ms':90000,'delay_before_return_html_s':3.0,'cache_mode':'BYPASS','headless':True}.items():
            require(name in access and access[name]==value, f'policy mismatch: {name}')
        require(manifest['scope']['redirect_max_hops']==5 and isinstance(manifest['scope']['hosts_allowed'],list), 'invalid scope')
        require(all(k in manifest['versions'] for k in ('python','crawl4ai','playwright','requests','tool_commit')), 'runtime identity missing')
        require(all(k in manifest['streams'] for k in ('discovery','html','rest','media','screenshots')), 'stream status missing')
        for source in routes['sources']:
            if source.get('file'):
                source_path=reference(root,'discovery/routes.json',source['file'])
                if source.get('sha256'): hashed(source_path, source)
        pages = manifest['pages']
        urls = [p['url'] for p in pages]
        expected = [r['url'] for r in routes['routes']]
        require(len(set(urls)) == len(urls) and urls == expected, 'one outcome per route in route order required')
        require(set(mapping['by_route']) == set(urls), 'REST mapping must account for every route')
        require(routes['counts']['routes'] == len(urls), 'discovery count mismatch')
        require(routes['counts']['dropped'] == len(routes['dropped']), 'dropped count mismatch')
        counts = manifest['counts']
        require(all(type(x) is int and x>=0 for x in counts.values()), 'counts must be nonnegative integers')
        require(counts['routes'] == len(pages), 'route count mismatch')
        for outcome in OUTCOMES:
            require(counts[outcome] == sum(p['outcome'] == outcome for p in pages), f'{outcome} count mismatch')
        required_page = {'url','input_url','final_url','redirect_chain','slug','status','outcome','reason',
                         'fetched_at','elapsed_s','retries','html_file','block_file','html_bytes','sha256',
                         'rest_ref','rest_outcome'}
        for p in pages:
            require(set(p) == required_page, 'page fields mismatch')
            require(p['outcome'] in OUTCOMES and p['retries'] == 0, 'invalid page outcome/retry')
            require(isinstance(p['redirect_chain'], list) and len(p['redirect_chain']) <= 5, 'invalid redirect chain')
            require(urlsplit(p['url']).scheme in ('http','https'), 'invalid route URL')
            require(p['rest_outcome'] == mapping['by_route'][p['url']]['outcome'], 'REST outcome mismatch')
            if p['outcome'] == 'captured':
                require(p['reason'] is None and p['status'] is not None and 200 <= p['status'] < 300,
                        'captured requires successful status/no absence')
                path = reference(root, 'manifest.json', p['html_file'])
                require(path.parent.resolve() == (root / 'html').resolve(), 'HTML outside html directory')
                require(p['html_bytes'] > 0, 'captured HTML empty')
                hashed(path, p, 'html_bytes')
            else:
                require(p['html_file'] is None and p['sha256'] is None and p['html_bytes'] is None,
                        'non-capture cannot claim captured HTML')
                require(any(a['stream'] == 'html' and a['ref'] == p['url'] and a['outcome'] == p['outcome']
                            and a['reason'] == p['reason'] for a in absent), 'page absence missing')
            if p['block_file']:
                require(p['outcome'] == 'blocked', 'block body on nonblocked page')
                reference(root, 'manifest.json', p['block_file'])
            if p['rest_ref']:
                reference(root, 'manifest.json', p['rest_ref'])
        for a in absent:
            if a['stream'] == 'html':
                require(a['ref'] in urls, 'HTML absence has no route outcome')
        require(len(index['collections']) == 6 and {c['type'] for c in index['collections']} == COLLECTIONS,
                'all declared collections required')
        reference(root, 'rest/index.json', index['absences_file'])
        if index['transport'] is not None:
            reference(root, 'rest/index.json', index['transport']['session_ref'])
        responses = {}
        response_values = {}
        for r in index['responses']:
            require(r['file'] not in responses, 'duplicate response reference')
            path = reference(root, 'rest/index.json', r['file'])
            hashed(path, r, 'bytes')
            responses[r['file']] = r
        for c in index['collections']:
            require(c['status'] in ('complete', 'partial', 'unavailable', 'skipped'), 'invalid collection status')
            require(all(ref in responses for ref in c['response_refs']), 'missing collection response')
        objects = {}
        for obj in index['objects']:
            require(obj['file'] not in objects, 'duplicate object file')
            require(obj.get('serialization'), 'object serialization not declared')
            derivative = reference(root, 'rest/index.json', obj['file'])
            hashed(derivative, obj)
            require(obj['response_file'] in responses, 'unknown object response')
            r = responses[obj['response_file']]
            require(r['outcome'] == 'complete' and r.get('body_complete',True), 'object derived from incomplete response')
            if obj['response_file'] not in response_values:
                response_values[obj['response_file']] = load(reference(root, 'rest/index.json', obj['response_file']))
            array = response_values[obj['response_file']]
            pos = obj['array_position']
            require(isinstance(array, list) and type(pos) is int and 0 <= pos < len(array), 'invalid array position')
            value = load(derivative)
            require(value == array[pos], 'object changed source values')
            require(isinstance(value, dict) and type(value.get('id')) is int and value['id'] > 0, 'invalid object identity')
            objects[obj['file']] = value
        require(counts['rest_objects'] == len(objects), 'REST object count mismatch')
        for route, item in mapping['by_route'].items():
            require(item['outcome'] in ('mapped','unmapped','ambiguous','rest_unavailable'), 'invalid mapping outcome')
            page = pages[urls.index(route)]
            if item['outcome'] == 'mapped':
                require(item['object'] in objects and page['rest_ref'] == 'rest/' + item['object'], 'mapped object mismatch')
                # Imported lazily: canonical identity is shared by discovery and raw validation.
                from discover_site.sitemap_utils import canonical_url
                require(canonical_url(objects[item['object']]['link']) == route, 'mapped link identity mismatch')
            elif item['outcome'] == 'ambiguous':
                require(len(item['candidates']) > 1 and all(x in objects for x in item['candidates']), 'invalid ambiguity')
            else:
                require(page['rest_ref'] is None, 'unmapped route has object reference')
        for name in ('unrouted_objects','content_rendered_empty'):
            require(all(x in objects for x in mapping[name]), f'invalid {name} reference')
        require(counts['rest_mapped_routes'] == sum(p['rest_outcome'] == 'mapped' for p in pages), 'mapped count mismatch')
        require(counts['media_items'] == media['counts']['items'] == len(media['items']), 'media count mismatch')
        if manifest['versions'].get('source_inventory'):
            path = reference(root, 'manifest.json', manifest['versions']['source_inventory'])
            require(hashlib.sha256(path.read_bytes()).hexdigest() == manifest['versions']['source_inventory_sha256'],
                    'source identity hash mismatch')
        if manifest['streams']['screenshots'] == 'authored':
            require(bool(manifest.get('screenshots')), 'authored screenshot index missing')
            for item in manifest['screenshots']:
                path = reference(root, 'manifest.json', item['file'])
                require(path.resolve().is_relative_to((root/'screenshots').resolve()), 'screenshot outside slot')
                hashed(path, item, 'bytes')
        for origin in ('internal','external','staging_domain'):
            require(media['counts'][origin] == sum(i['origin'] == origin for i in media['items']), 'media origin count mismatch')
        for item in media['items']:
            for ref in item['provenance']:
                reference(root, 'media/inventory.json', ref)
            if item.get('rest_ref'):
                reference(root, 'media/inventory.json', item['rest_ref'])
        return ['schemas and mandatory files valid', 'references and byte hashes valid',
                'route outcomes/counts/absences reconciled', 'REST derivatives and mappings valid']
    except (KeyError, TypeError, ValueError, OSError, IndexError) as exc:
        if isinstance(exc, InvalidRaw):
            raise
        raise InvalidRaw(f'invalid raw structure: {exc}') from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--run', required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1] / 'outputs')
    args = parser.parse_args()
    try:
        root = args.root / args.project / 'runs' / args.run
        require(root.resolve().is_relative_to(args.root.resolve()), 'invalid run path')
        for line in validate_run(root):
            print('OK ' + line)
    except InvalidRaw as exc:
        print('FAIL ' + str(exc))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
