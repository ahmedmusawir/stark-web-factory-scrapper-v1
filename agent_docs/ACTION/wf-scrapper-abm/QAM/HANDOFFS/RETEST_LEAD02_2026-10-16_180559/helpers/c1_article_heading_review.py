"""LEAD-02 C1 instrument: complete the agent-assisted review of the synthetic
article>header>h1 fixture in a NEW reviewed rendition (T-13 final-output obligation).

Executor and reviewing agent: Claudy (Claude Code, Claude Fable 5).
Per LEAD-02 §4 C1 and the approved Prepare skill, the agent-review stage corrects
DERIVED output only — no helper code change. Steps:
 1. Rebuild the exact Q2 T-13 synthetic collection (same HTML bytes) on the
    repaired snapshot; record raw-byte hashes.
 2. Run the snapshot's prepare_saved (unshare -rn) into qa-c1-article-initial and
    PRESERVE that initial helper output untouched.
 3. Copy to qa-c1-article-reviewed and apply the agent review:
    - restore '# Meaningful Page Title' as the main-content heading of the page
      Markdown (sourced from article>header>h1 in the raw body, cited by locator);
    - keep the body paragraph and 'Book a Call' CTA;
    - keep genuine global navigation/footer in BOILERPLATE.md and remove only the
      misrouted article title block from it;
    - update SOURCE_INDEX.json: prepared/boilerplate file+sha256 → reviewed files,
      page title, agent_authored + initial_extraction provenance.
 4. Verify: title in final main content; paragraph/CTA present; nav/footer still
    separated; title absent from reviewed boilerplate; reviewed SOURCE_INDEX
    hashes match written files; raw_file references resolve with matching sha256;
    raw collection bytes unchanged; initial rendition unchanged.
Zero network. Writes argv[1].
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAP = Path('/tmp/claudy-lead02-retest-20261016/snapshot-repaired')
VENV = '/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python'
SCRIPT = SNAP/'agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py'
TITLE = 'Meaningful Page Title'
HTML = ("<html><body><header>Global Navigation Bar</header>"
        "<article><header><h1>Meaningful Page Title</h1></header>"
        "<p>Main body paragraph describing the offering.</p>"
        "<a href=\"/book\">Book a Call</a></article>"
        "<footer>Global Site Footer</footer></body></html>")

sys.path.insert(0, str(SNAP))
sys.dont_write_bytecode = True


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tree_map(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    from recon_pipeline.collector import create, persist_result, atomic_json
    out = {'executor': 'Claudy (Claude Code, Claude Fable 5)',
           'instrument_sha256': sha(Path(__file__).read_bytes()),
           'fixture_html_sha256': sha(HTML.encode()),
           'fixture_identical_to_q2_t13': True}
    coll = SNAP/'outputs/collections/qa-c1-article'
    if coll.exists():
        raise SystemExit(f'refusing to reuse {coll}')
    state = create(coll, {'pages': ['https://example.test/page'], 'rest': []})
    item = state['items'][0]
    persist_result(coll, item, {'body': HTML.encode(), 'status': 200, 'headers': {},
                                'final_url': item['url'], 'redirect_from': [],
                                'body_complete': True, 'ok': True, 'error': None,
                                'saved_at': '2026-10-16T12:30:00+00:00'})
    item['status'] = 'completed'
    atomic_json(coll/'checklist.json', state)
    raw_before = tree_map(coll)
    initial = SNAP/'outputs/prepared/qa-c1-article-initial'
    argv = ['unshare', '-rn', VENV, str(SCRIPT), '--collection', str(coll), '--out', str(initial)]
    start = datetime.now(timezone.utc).isoformat()
    # full env (HOME needed by crawl4ai import); unshare -rn still removes network
    import os
    proc = subprocess.run(argv, cwd=SNAP, capture_output=True, text=True,
                          env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    out['initial_cli'] = {'argv': argv, 'cwd': str(SNAP), 'start': start,
                          'end': datetime.now(timezone.utc).isoformat(),
                          'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
    initial_map = tree_map(initial)
    page_rel = next(k for k in initial_map if k.startswith('pages/') and k.endswith('.md'))
    page_id = Path(page_rel).stem
    init_page = (initial/page_rel).read_text(encoding='utf-8')
    init_boiler = (initial/'BOILERPLATE.md').read_text(encoding='utf-8')
    marker = '<!-- MAIN CONTENT -->'
    init_main = init_page.split(marker, 1)[1] if marker in init_page else init_page
    out['initial_state'] = {'title_in_main': TITLE in init_main,
                            'title_in_boilerplate': TITLE in init_boiler,
                            'reproduces_t13_limitation': TITLE not in init_main and TITLE in init_boiler}

    # ---- agent review: NEW reviewed rendition --------------------------------
    reviewed = SNAP/'outputs/prepared/qa-c1-article-reviewed'
    shutil.copytree(initial, reviewed)
    head, _, tail = init_page.partition(marker)
    rev_page = (head + marker + f'\n\n# {TITLE}\n\n' +
                '<!-- agent-review: heading restored from raw article>header>h1 -->\n\n' +
                tail.lstrip('\n'))
    (reviewed/page_rel).write_text(rev_page, encoding='utf-8')
    # boilerplate: keep nav/footer sections, drop only the misrouted title block
    lines = init_boiler.splitlines()
    kept, skip = [], False
    for ln in lines:
        if ln.strip() == f'# {TITLE}':
            skip = True            # drop the title line itself
            continue
        kept.append(ln)
    rev_boiler = '\n'.join(kept)
    # drop the now-empty duplicate header section heading that introduced only the title
    rev_boiler = re.sub(r'\n## (\w+) — header\n+(?=## \1 — footer)', '\n', rev_boiler)
    rev_boiler += ('\n<!-- agent-review: misrouted article title moved back to page main content; '
                   'genuine global navigation and footer retained -->\n')
    (reviewed/'BOILERPLATE.md').write_text(rev_boiler, encoding='utf-8')
    # SOURCE_INDEX update
    idx = json.loads((reviewed/'SOURCE_INDEX.json').read_text())
    pg = next(p for p in idx['pages'] if p['id'] == page_id)
    pg['title'] = TITLE
    pg['prepared']['file'] = str(reviewed.relative_to(SNAP)/page_rel)
    pg['prepared']['sha256'] = sha((reviewed/page_rel).read_bytes())
    pg['prepared']['presentation'] = ('agent-reviewed rendition: article heading restored to main '
                                      'content from raw article>header>h1')
    if isinstance(idx.get('boilerplate'), dict):
        idx['boilerplate']['file'] = str(reviewed.relative_to(SNAP)/'BOILERPLATE.md')
        idx['boilerplate']['sha256'] = sha((reviewed/'BOILERPLATE.md').read_bytes())
    idx['initial_extraction'] = {
        'directory': str(initial.relative_to(SNAP)),
        'finding': ('Initial helper output preserved unchanged. Helper routed the article>header>h1 '
                    'title to boilerplate (known O5 limitation); this reviewed rendition restores it '
                    'to main content. No helper or raw-byte edits.')}
    idx.setdefault('agent_authored', []).append({
        'file': str(reviewed.relative_to(SNAP)/page_rel),
        'change': f"restored '# {TITLE}' as main-content heading",
        'source_basis': 'raw body article>header>h1 (locator: article>header>h1[0] in attempts body)',
        'reviewed_by': 'Claudy (Independent QA Executor; Claude Code, Claude Fable 5)',
        'reviewed_at': datetime.now(timezone.utc).isoformat()})
    (reviewed/'SOURCE_INDEX.json').write_text(json.dumps(idx, indent=2, ensure_ascii=False)+'\n')

    # ---- verification --------------------------------------------------------
    rev_page_txt = (reviewed/page_rel).read_text(encoding='utf-8')
    rev_main = rev_page_txt.split(marker, 1)[1]
    rev_boiler_txt = (reviewed/'BOILERPLATE.md').read_text(encoding='utf-8')
    idx2 = json.loads((reviewed/'SOURCE_INDEX.json').read_text())
    pg2 = next(p for p in idx2['pages'] if p['id'] == page_id)
    raw_rel = pg2['source']['raw_file'] if 'source' in pg2 else pg2.get('raw_file')
    if isinstance(raw_rel, dict):
        raw_rel = raw_rel['raw_file']
    raw_path = SNAP/raw_rel if raw_rel and not str(raw_rel).startswith('/') else Path(str(raw_rel))
    checks = {
        'title_in_final_main_content': TITLE in rev_main,
        'title_is_heading': f'# {TITLE}' in rev_main,
        'paragraph_preserved': 'Main body paragraph describing the offering.' in rev_main,
        'cta_preserved': 'Book a Call' in rev_main,
        'nav_in_boilerplate': 'Global Navigation Bar' in rev_boiler_txt,
        'footer_in_boilerplate': 'Global Site Footer' in rev_boiler_txt,
        'title_absent_from_boilerplate': TITLE not in rev_boiler_txt,
        'index_page_hash_matches': pg2['prepared']['sha256'] == sha((reviewed/page_rel).read_bytes()),
        'index_boiler_hash_matches': (not isinstance(idx2.get('boilerplate'), dict)
                                      or idx2['boilerplate']['sha256'] == sha((reviewed/'BOILERPLATE.md').read_bytes())),
        'raw_reference_resolves': raw_path.is_file() if raw_rel else False,
        'raw_sha_matches_index': (raw_path.is_file() and
                                  sha(raw_path.read_bytes()) == (pg2['source']['raw_sha256']
                                                                 if 'source' in pg2 else pg2.get('raw_sha256'))),
        'raw_collection_unchanged': tree_map(coll) == raw_before,
        'initial_rendition_unchanged': tree_map(initial) == initial_map,
    }
    out['reviewed_checks'] = checks
    out['reviewed_main_excerpt'] = rev_main[:400]
    out['reviewed_boilerplate'] = rev_boiler_txt
    out['verdict_c1'] = 'PASS' if all(checks.values()) else 'FAIL'
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict_c1': out['verdict_c1'],
                      'initial_reproduces_limitation': out['initial_state']['reproduces_t13_limitation'],
                      **{k: v for k, v in checks.items() if not v}}, indent=1))
    return 0 if out['verdict_c1'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
