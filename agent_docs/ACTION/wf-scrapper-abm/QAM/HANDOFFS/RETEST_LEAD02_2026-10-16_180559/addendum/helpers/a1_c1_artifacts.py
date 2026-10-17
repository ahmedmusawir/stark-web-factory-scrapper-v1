"""LEAD-03 A1 instrument: export C1 artifacts, verify final index, author reviewed-v2.

Executor: Claudy (Claude Code, Claude Fable 5). Per LEAD-03 §3 A1:
- Export retained qa-c1-article collection (checklist + result + body; lock
  excluded), qa-c1-article-initial and qa-c1-article-reviewed UNCHANGED,
  preserving snapshot-relative layout, into the addendum a1/ tree.
- Recompute the checklist → result → raw-body hash chain and every index
  file/hash reference (initial and reviewed).
- Inspect the reviewed index: content.headings and boilerplate_locations were
  confirmed to still describe the INITIAL extraction (headings [], locations
  [header, header, footer]). Per the ruling, author a NEW
  qa-c1-article-reviewed-v2/ with a consistent FINAL index: final headings,
  final boilerplate locations, initial values preserved under
  initial_extraction metadata, authored references hashed and labeled. The
  prior reviewed directory is preserved untouched as the submitted specimen.
- Verify the v2 rendition: heading order, paragraph/list counts, link labels
  AND destinations (CTA /book → https://example.test/book), boilerplate
  separation, provenance, raw/initial unchanged (raw body sha equals the
  fixture sha recorded in the LEAD-02 c1 result).
No Prepare rerun; QA-authored derived-material correction only. Writes argv[1].
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAP = Path('/tmp/claudy-lead02-retest-20261016/snapshot-repaired')
LANE = Path(__file__).resolve().parents[2]
A1 = LANE/'addendum/a1'
COLL = SNAP/'outputs/collections/qa-c1-article'
INITIAL = SNAP/'outputs/prepared/qa-c1-article-initial'
REVIEWED = SNAP/'outputs/prepared/qa-c1-article-reviewed'
V2 = SNAP/'outputs/prepared/qa-c1-article-reviewed-v2'
TITLE = 'Meaningful Page Title'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tree(root, exclude_names=()):
    return {p.relative_to(root).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
            for p in sorted(root.rglob('*'))
            if p.is_file() and p.name not in exclude_names and '.runtime' not in p.parts}


def main():
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'authored_at': datetime.now(timezone.utc).isoformat()}
    # ---- export retained artifacts unchanged -------------------------------
    exports = {}
    for src, name in ((COLL, 'outputs/collections/qa-c1-article'),
                      (INITIAL, 'outputs/prepared/qa-c1-article-initial'),
                      (REVIEWED, 'outputs/prepared/qa-c1-article-reviewed')):
        m = tree(src, exclude_names=('.writer.lock',))
        for rel, info in m.items():
            dst = A1/name/rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src/rel, dst)
        exports[name] = m
    out['exported'] = exports
    out['export_note'] = ('.writer.lock and .runtime excluded from export; retained trees copied '
                          'byte-for-byte, source untouched')

    # ---- hash chain: checklist -> result -> raw body -----------------------
    st = json.loads((COLL/'checklist.json').read_text())
    item = st['items'][0]
    res_rel = item['result']['file']
    res_bytes = (COLL/res_rel).read_bytes()
    meta = json.loads(res_bytes)
    body = (COLL/meta['body_file']).read_bytes()
    c1res = json.loads((LANE/'c1/c1_article_review_result.json').read_text())
    chain = {
        'checklist_records_result_sha': item['result']['sha256'],
        'result_actual_sha': sha(res_bytes),
        'checklist_to_result_ok': sha(res_bytes) == item['result']['sha256'],
        'result_records_body': {'file': meta['body_file'], 'sha256': meta['sha256'], 'bytes': meta['bytes']},
        'body_actual': {'sha256': sha(body), 'bytes': len(body)},
        'result_to_body_ok': sha(body) == meta['sha256'] and len(body) == meta['bytes'],
        'body_equals_lead02_recorded_fixture': sha(body) == c1res['fixture_html_sha256'],
        'attempts_list_consistent': all(a['sha256'] == sha((COLL/a['file']).read_bytes())
                                        for a in item['attempts']),
    }
    out['hash_chain'] = chain

    # ---- index reference checks (initial + reviewed, actual files) ---------
    def index_refs(pkg):
        idx = json.loads((pkg/'SOURCE_INDEX.json').read_text())
        pg = idx['pages'][0]
        prep = SNAP/pg['prepared']['file'] if not pg['prepared']['file'].startswith('/') else Path(pg['prepared']['file'])
        checks = {'prepared_file': pg['prepared']['file'],
                  'prepared_hash_ok': prep.is_file() and sha(prep.read_bytes()) == pg['prepared']['sha256'],
                  'raw_hash_ok': sha(body) == pg['source']['raw_sha256'],
                  'boilerplate_hash_ok': (sha((SNAP/idx['boilerplate']['file']).read_bytes())
                                          == idx['boilerplate']['sha256'])
                  if isinstance(idx.get('boilerplate'), dict) else 'n/a'}
        return idx, pg, checks
    init_idx, init_pg, init_checks = index_refs(INITIAL)
    rev_idx, rev_pg, rev_checks = index_refs(REVIEWED)
    out['initial_index_checks'] = init_checks
    out['reviewed_index_checks'] = rev_checks
    out['lead03_finding_confirmed'] = {
        'reviewed_content_headings': rev_pg['content']['headings'],
        'reviewed_boilerplate_locations': rev_pg['boilerplate_locations'],
        'still_describe_initial_extraction': (rev_pg['content']['headings'] == []
                                              and rev_pg['boilerplate_locations'] == ['header', 'header', 'footer'])}

    # ---- author reviewed-v2 with a consistent FINAL index ------------------
    if V2.exists():
        raise SystemExit(f'refusing to reuse {V2}')
    shutil.copytree(REVIEWED, V2)
    page_rel = next(p.relative_to(REVIEWED).as_posix() for p in (REVIEWED/'pages').glob('*.md'))
    # file references inside the index point at the v2 directory
    idx = json.loads((V2/'SOURCE_INDEX.json').read_text())
    pg = idx['pages'][0]
    v2_rel = V2.relative_to(SNAP).as_posix()
    pg['prepared']['file'] = f'{v2_rel}/{page_rel}'
    pg['prepared']['sha256'] = sha((V2/page_rel).read_bytes())
    idx['boilerplate']['file'] = f'{v2_rel}/BOILERPLATE.md'
    idx['boilerplate']['sha256'] = sha((V2/'BOILERPLATE.md').read_bytes())
    # FINAL content metadata (QA-authored, from the actual reviewed files)
    page_txt = (V2/page_rel).read_text(encoding='utf-8')
    main_txt = page_txt.split('<!-- MAIN CONTENT -->', 1)[1]
    final_headings = re.findall(r'^#+ (.+)$', main_txt, re.M)
    boiler_txt = (V2/'BOILERPLATE.md').read_text(encoding='utf-8')
    pg['initial_extraction_metadata'] = {
        'content_headings': init_pg['content']['headings'],
        'boilerplate_locations': init_pg['boilerplate_locations'],
        'note': ('values produced by the initial helper extraction (title misrouted to a '
                 'boilerplate header block); preserved here as initial-extraction metadata')}
    pg['content']['headings'] = final_headings
    pg['boilerplate_locations'] = ['header', 'footer']
    pg['boilerplate_locations_note'] = ('final reviewed rendition: the misrouted article-title '
                                        'header block was returned to main content; remaining '
                                        'separated blocks are the genuine nav header and footer')
    idx['agent_authored'].append({
        'file': f'{v2_rel}/SOURCE_INDEX.json',
        'change': ('reviewed-v2: content.headings and boilerplate_locations now describe the FINAL '
                   'reviewed rendition; initial values preserved under initial_extraction_metadata'),
        'reviewed_by': 'Claudy (Independent QA Executor; Claude Code, Claude Fable 5)',
        'reviewed_at': datetime.now(timezone.utc).isoformat(),
        'per': 'LEAD-03 §3 A1 (QA-authored derived-material correction under the approved skill)'})
    (V2/'SOURCE_INDEX.json').write_text(json.dumps(idx, indent=2, ensure_ascii=False)+'\n')

    # ---- verify v2 ----------------------------------------------------------
    idx2 = json.loads((V2/'SOURCE_INDEX.json').read_text())
    pg2 = idx2['pages'][0]
    links = pg2['content']['links']
    v2_checks = {
        'final_heading_order': final_headings,
        'heading_first_is_title': bool(final_headings) and final_headings[0] == TITLE,
        'paragraph_count_final': main_txt.count('\n\n'),
        'paragraph_text_present': 'Main body paragraph describing the offering.' in main_txt,
        'list_items_final': len(re.findall(r'^\s*[-*] ', main_txt, re.M)),
        'cta_label_and_destination': any(l['label'] == 'Book a Call'
                                         and l['source_href'] == '/book'
                                         and l['resolved_url'] == 'https://example.test/book'
                                         for l in links),
        'cta_destination_in_markdown': '(https://example.test/book)' in main_txt,
        'nav_in_boilerplate': 'Global Navigation Bar' in boiler_txt,
        'footer_in_boilerplate': 'Global Site Footer' in boiler_txt,
        'title_absent_from_boilerplate': TITLE not in boiler_txt,
        'content_headings_match_final_file': pg2['content']['headings'] == final_headings,
        'boilerplate_locations_final': pg2['boilerplate_locations'] == ['header', 'footer'],
        'initial_metadata_preserved': pg2['initial_extraction_metadata']['boilerplate_locations'] == ['header', 'header', 'footer'],
        'prepared_hash_ok': sha((V2/page_rel).read_bytes()) == pg2['prepared']['sha256'],
        'boilerplate_hash_ok': sha((V2/'BOILERPLATE.md').read_bytes()) == idx2['boilerplate']['sha256'],
        'raw_hash_ok': sha(body) == pg2['source']['raw_sha256'],
        'raw_unchanged': chain['body_equals_lead02_recorded_fixture'],
        'initial_dir_untouched': tree(INITIAL) == exports['outputs/prepared/qa-c1-article-initial'],
        'reviewed_v1_untouched': tree(REVIEWED) == exports['outputs/prepared/qa-c1-article-reviewed'],
    }
    out['v2_checks'] = v2_checks
    # export v2
    m2 = tree(V2)
    for rel in m2:
        dst = A1/'outputs/prepared/qa-c1-article-reviewed-v2'/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(V2/rel, dst)
    out['exported']['outputs/prepared/qa-c1-article-reviewed-v2'] = m2
    hard = {k: v for k, v in v2_checks.items() if isinstance(v, bool)}
    out['verdict_a1'] = ('PASS' if all(chain[k] for k in chain if isinstance(chain[k], bool))
                         and all(v for v in init_checks.values() if isinstance(v, bool))
                         and all(v for v in rev_checks.values() if isinstance(v, bool))
                         and all(hard.values()) else 'FAIL')
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_a1': out['verdict_a1'],
                      'finding_confirmed': out['lead03_finding_confirmed']['still_describe_initial_extraction'],
                      'failed': [k for k, v in {**chain, **hard}.items() if v is False]}, indent=1))
    return 0 if out['verdict_a1'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
