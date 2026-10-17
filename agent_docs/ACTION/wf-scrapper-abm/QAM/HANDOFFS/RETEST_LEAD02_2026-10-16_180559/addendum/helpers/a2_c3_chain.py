"""LEAD-03 A2 instrument: export and verify C3's original saved response chain.

Executor: Claudy (Claude Code, Claude Fable 5). Per LEAD-03 §3 A2:
- From retained outputs/collections/qa-c3-rich-rest/, export checklist.json,
  the result metadata RESOLVED FROM THE CHECKLIST (never guessed) and the
  original saved body, preserving relative layout. Lock/runtime excluded.
- Verify: checklist→result digest, result→body length+sha, body_complete,
  item status/scope, selected URL without _fields, metadata headers within the
  allowlist, synthetic cookie value absent from saved metadata.
- Reconstruct the served fixture INDEPENDENTLY: the RICH definition is
  re-declared here verbatim from the C3 instrument with link origin
  http://127.0.0.1:37785 (the recorded origin), serialized with the recorded
  json.dumps(..., ensure_ascii=False, indent=4) + newline. The reconstruction
  must be 1,104 bytes with SHA-256 743103072c2e8e88f682b11c4a6fa8f671b9cbf0
  0202c66e29d1965697f83525 (LEAD-03 §1) and byte-equal to the ORIGINAL saved
  body. The reconstruction is labeled reconstructed; the exported body is the
  original capture. No server, browser or recapture. Writes argv[1].
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

SNAP = Path('/tmp/claudy-lead02-retest-20261016/snapshot-repaired')
COLL = SNAP/'outputs/collections/qa-c3-rich-rest'
LANE = Path(__file__).resolve().parents[2]
A2 = LANE/'addendum/a2'
ORIGIN = 'http://127.0.0.1:37785'
EXPECT_SHA = '743103072c2e8e88f682b11c4a6fa8f671b9cbf00202c66e29d1965697f83525'
EXPECT_BYTES = 1104
ALLOWED_HEADERS = {'content-type', 'location', 'retry-after', 'x-ac', 'x-wp-total',
                   'x-wp-totalpages', 'content-length', 'cf-mitigated'}

RICH = {
    'id': 1101,
    'date': '2026-10-01T10:00:00',
    'type': 'post',
    'link': ORIGIN + '/rich-fixture-post',
    'title': {'rendered': 'Café বাংলা 工場 \U0001f680 — rich fixture'},
    'content': {'rendered': '<p>Whole rendered content with\ttab,\n\nblank line and '
                            'Unicode: Ünïcode 中文 \U0001f98a.</p>',
                'protected': False},
    'excerpt': {'rendered': '<p>Excerpt text …</p>'},
    'yoast_head': '<meta property="og:title" content="Café SEO fixture" />',
    'yoast_head_json': {'title': 'Café SEO fixture', 'og_locale': 'en_US',
                        'twitter_misc': {'Est. reading time': '3 minutes'}},
    'unknown_top_level': {'precise': 'retained', 'nested': {'deeper': ['a', 'b', {'k': 1.5}],
                                                            'emoji': '\U0001f9ea'}},
    '_embedded_like_unknown': [{'anything': True, 'count': 3}],
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'collection': str(COLL)}
    checklist_bytes = (COLL/'checklist.json').read_bytes()
    st = json.loads(checklist_bytes)
    item = st['items'][0]
    res_rel = item['result']['file']          # resolved from the checklist
    res_bytes = (COLL/res_rel).read_bytes()
    meta = json.loads(res_bytes)
    body_rel = meta['body_file']
    body = (COLL/body_rel).read_bytes()
    # export originals, relative layout preserved
    for rel, data in (('checklist.json', checklist_bytes), (res_rel, res_bytes), (body_rel, body)):
        dst = A2/'outputs/collections/qa-c3-rich-rest'/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    out['exported'] = {'checklist.json': {'sha256': sha(checklist_bytes), 'bytes': len(checklist_bytes)},
                       res_rel: {'sha256': sha(res_bytes), 'bytes': len(res_bytes)},
                       body_rel: {'sha256': sha(body), 'bytes': len(body)}}
    # reconstruction (labeled; exported separately, NOT in the collection layout)
    recon = (json.dumps(RICH, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
    (A2/'reconstructed_reference.json').write_bytes(recon)
    (A2/'reconstructed_reference.NOTE.txt').write_text(
        'reconstructed_reference.json is the INDEPENDENTLY RECONSTRUCTED served fixture '
        f'(RICH definition with recorded origin {ORIGIN}), labeled per LEAD-03 §3 A2. '
        'It is NOT the original capture; the original saved body is under '
        'outputs/collections/qa-c3-rich-rest/.\n')
    headers = {k.lower(): v for k, v in meta.get('headers', {}).items()}
    checks = {
        'result_path_resolved_from_checklist': res_rel,
        'checklist_result_digest_ok': sha(res_bytes) == item['result']['sha256'],
        'attempts_consistent': all(a['sha256'] == sha((COLL/a['file']).read_bytes())
                                   for a in item['attempts']),
        'metadata_body_sha_ok': sha(body) == meta['sha256'],
        'metadata_body_bytes_ok': len(body) == meta['bytes'],
        'body_complete_true': meta.get('body_complete') is True,
        'item_status_completed': item['status'] == 'completed',
        'item_kind_rest': item['kind'] == 'rest',
        'selected_url_no_fields': '_fields' not in item['url'],
        'url_is_recorded_origin': item['url'] == ORIGIN + '/wp-json/wp/v2/posts/1101',
        'headers_within_allowlist': sorted(set(headers) - ALLOWED_HEADERS) == [],
        'metadata_headers_present': sorted(headers),
        'set_cookie_absent': all('set-cookie' not in k for k in headers),
        'synthetic_cookie_value_absent_from_metadata': 'qa_synthetic_cookie' not in res_bytes.decode('utf-8'),
        'reconstruction_bytes': len(recon),
        'reconstruction_sha256': sha(recon),
        'reconstruction_matches_lead03_expectation': len(recon) == EXPECT_BYTES and sha(recon) == EXPECT_SHA,
        'original_body_byte_equals_reconstruction': body == recon,
        'original_body_sha256': sha(body),
    }
    out['checks'] = checks
    hard = [v for v in checks.values() if isinstance(v, bool)]
    out['verdict_a2'] = 'PASS' if all(hard) else 'FAIL'
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_a2': out['verdict_a2'],
                      'failed': [k for k, v in checks.items() if v is False]}, indent=1))
    return 0 if out['verdict_a2'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
