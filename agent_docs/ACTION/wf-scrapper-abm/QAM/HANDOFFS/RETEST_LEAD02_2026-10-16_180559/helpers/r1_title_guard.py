"""LEAD-02 R1 instrument: independent title-guard verification on the repaired snapshot.

Executor: Claudy (Claude Code, Claude Fable 5). Imports decide ONLY from the fresh
snapshot of the repaired committed candidate (never the old pre-repair Q2 snapshot).
Cases are authored here independently of engineering's r1_reproduction.json:
supply/replacement with the exact 'Read more →' (U+2192), both orders, the recorded
Q2 control variants, decoration/emoji/double-arrow variants, informative Unicode
titles kept byte-exact (Bengali, CJK, accents, emoji, informative punctuation,
longer labels containing CTA words), stable IDs, UNDECIDED selection, provenance
(sources retained when the weak label is declined), and no slug-derived title.
Offline; zero network. Writes argv[1].
"""
import json
import sys
import unicodedata
from pathlib import Path

SNAP = '/tmp/claudy-lead02-retest-20261016/snapshot-repaired'
sys.path.insert(0, SNAP)
from recon_pipeline import decide as dmod  # noqa: E402

URL = 'http://127.0.0.1/post-one'


def fresh_inv():
    return {'schema': dmod.SCHEMA, 'origin': 'http://127.0.0.1/', 'mode': 'qa',
            'created_at': '', 'context': {}, 'items': [], 'requests': [], 'gaps': [],
            'wordpress': {'status': 'not_attempted', 'collections': []},
            'stop_reason': None, 'cleanup_error': None}


GENERIC = ['Read more →', 'Read more ›', 'READ MORE…', '?!...', '   ',
           '→→', '→ Read more', 'Read  more \U0001f449',
           'Continue reading »', '» Learn More !', 'Read Post', 'read more...',
           'LEARN MORE', 'View post', 'CONTINUE READING', 'Read more →']
INFORMATIVE = ['How to Regain Search Visibility After the Andromeda Update',
               'Read more about the Andromeda recovery process',
               'Learn More: 5 Tactics That Actually Work',
               'Café SEO \U0001f680', 'বাংলা শিরোনাম →',
               '工場の自動化 2026', 'Pricing?!', '1 + 1 = 2 Growth Math']


def main():
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)', 'snapshot': SNAP,
           'decide_module': dmod.__file__,
           'generic_label_set': sorted(dmod.GENERIC_LINK_LABELS)}
    import hashlib
    out['instrument_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out['decide_py_sha256'] = hashlib.sha256(Path(dmod.__file__).read_bytes()).hexdigest()

    # supply: generic variants must not supply an unknown title; sources retained
    supply = []
    for label in GENERIC:
        iv = fresh_inv()
        row = dmod.candidate(iv, URL, 'synthetic:a[href][0]', title=label)
        supply.append({'label': label, 'accepted_title': row['title'],
                       'declined': row['title'] is None,
                       'source_retained': row['sources'] == ['synthetic:a[href][0]'],
                       'selection': row['selection']})
    out['supply_generic'] = supply
    out['supply_all_declined'] = all(c['declined'] and c['source_retained'] for c in supply)

    # informative labels kept byte-exact
    kept = []
    for label in INFORMATIVE:
        iv = fresh_inv()
        row = dmod.candidate(iv, URL, 'synthetic:h2', title=label)
        kept.append({'label': label, 'accepted_title': row['title'],
                     'exact': row['title'] == label})
    out['informative_exact'] = kept
    out['informative_all_exact'] = all(c['exact'] for c in kept)

    # replacement: informative then arrow CTA
    seq = fresh_inv()
    dmod.candidate(seq, URL, 'synthetic:h2[0]', title='Informative Title Kept')
    dmod.candidate(seq, URL, 'synthetic:a[href][1]', title='Read more →')
    row = seq['items'][0]
    out['informative_then_arrow'] = {
        'final_title': row['title'], 'kept': row['title'] == 'Informative Title Kept',
        'single_row': len(seq['items']) == 1,
        'both_sources': row['sources'] == ['synthetic:h2[0]', 'synthetic:a[href][1]'],
        'selection': row['selection']}

    # order: arrow CTA first, informative later
    seq2 = fresh_inv()
    r_first = dmod.candidate(seq2, URL, 'synthetic:a[href][0]', title='Read more →')
    id_first = r_first['id']
    dmod.candidate(seq2, URL, 'synthetic:h2[1]', title='Informative Title Kept')
    row2 = seq2['items'][0]
    out['arrow_then_informative'] = {
        'title_after_cta_only': None if row2 is not r_first else 'same-row',
        'final_title': row2['title'], 'informative_accepted': row2['title'] == 'Informative Title Kept',
        'single_row': len(seq2['items']) == 1, 'stable_id': row2['id'] == id_first,
        'both_sources': row2['sources'] == ['synthetic:a[href][0]', 'synthetic:h2[1]'],
        'selection': row2['selection']}

    # no slug-derived title: declined label leaves title None, never from URL path
    iv = fresh_inv()
    row3 = dmod.candidate(iv, 'http://127.0.0.1/informative-slug-words', 'synthetic:a[href][0]',
                          title='Read more →')
    out['no_slug_title'] = {'title': row3['title'], 'ok': row3['title'] is None}

    # generic_label unit behavior: decoration-only stripping, not substring
    gl = dmod.generic_label
    out['generic_label_unit'] = {
        'arrow': gl('Read more →'), 'stripped': gl('Read more ›'),
        'emoji': gl('Read  more \U0001f449'), 'leading': gl('→ Read more'),
        'sentence_with_cta_words': gl('Read more about the Andromeda recovery process'),
        'learn_more_colon': gl('Learn More: 5 Tactics That Actually Work'),
        'bengali_with_arrow': gl('বাংলা শিরোনাম →'),
        'expected': 'first four True; last three False'}
    out['generic_label_unit']['ok'] = (
        out['generic_label_unit']['arrow'] and out['generic_label_unit']['stripped']
        and out['generic_label_unit']['emoji'] and out['generic_label_unit']['leading']
        and not out['generic_label_unit']['sentence_with_cta_words']
        and not out['generic_label_unit']['learn_more_colon']
        and not out['generic_label_unit']['bengali_with_arrow'])

    out['verdict_r1'] = ('PASS' if out['supply_all_declined'] and out['informative_all_exact']
                         and out['informative_then_arrow']['kept']
                         and out['arrow_then_informative']['informative_accepted']
                         and out['arrow_then_informative']['stable_id']
                         and out['no_slug_title']['ok'] and out['generic_label_unit']['ok']
                         else 'FAIL')
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_r1': out['verdict_r1'],
                      'supply_all_declined': out['supply_all_declined'],
                      'informative_all_exact': out['informative_all_exact'],
                      'replacement_kept': out['informative_then_arrow']['kept'],
                      'order_ok': out['arrow_then_informative']['informative_accepted'],
                      'generic_label_unit_ok': out['generic_label_unit']['ok']}, indent=1))
    return 0 if out['verdict_r1'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
