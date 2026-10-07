"""Part A offline engineering checks; no browser/HTTP fixture is executed."""
import copy
import hashlib
import json
import socket

import pytest
from test_raw_v2 import raw_fixture
from raw_fixture_factory import build_raw
from prepare.reader import RawRun
from recon_pipeline.offline_inventory import (
    build_inventory, export_inventory, inventory_binding, item_id, listing,
    load_choices, load_inventory, main, save_choices,
)


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('offline inventory attempted socket connection')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(socket.socket, 'connect_ex', forbidden)


@pytest.fixture
def imported(tmp_path):
    root = tmp_path/'raw'
    root.mkdir()
    raw_fixture(root)
    return build_inventory(root)


def test_real_raw_reader_traceability_and_preservation(tmp_path):
    root = build_raw(tmp_path/'input', 'partial')  # synthetic byte-faithful input; no traffic
    raw = RawRun(root)
    before = raw.inventory()
    inv = export_inventory(root, tmp_path/'review')
    assert inv['origin'] == 'IMPORTED_CAPTURE_INVENTORY'
    assert inv['context']['capture_stopped_early']
    assert all(x['selection'] == 'UNDECIDED' for x in inv['items'])
    assert len(inv['items']) >= len(raw.routes['routes'])
    objects = 0
    for row in inv['items']:
        assert row['id'] == item_id(row['url'])
        for source in row['sources']:
            assert hashlib.sha256(raw.bytes(source['file'])).hexdigest() == source['sha256']
            if source.get('wp_id'):
                assert raw.json(source['file'])['id'] == source['wp_id']
                assert raw.json(source['file'])['link'] == row['url']
                objects += 1
    assert objects > 0
    assert RawRun(root).inventory() == before
    assert load_inventory(tmp_path/'review/inventory.json') == inv


def test_reordering_and_reopening_preserve_choices(imported, tmp_path):
    a, b = imported['items'][:2]
    chosen = tmp_path/'choices-v1.json'
    save_choices(imported, chosen, [a['id']], [b['id']], note='synthetic test choices')
    reopened = load_choices(chosen, imported)
    rearranged = copy.deepcopy(imported)
    rearranged['items'].reverse()
    assert inventory_binding(rearranged) == imported['inventory_id']
    path = tmp_path/'reordered.json'
    path.write_text(json.dumps(rearranged))
    assert load_choices(chosen, load_inventory(path)) == reopened
    assert reopened['choices'][a['id']]['decision'] == 'include'
    assert reopened['choices'][b['id']]['decision'] == 'exclude'
    assert 'include' in listing(rearranged, reopened)


@pytest.mark.parametrize('argument', ['include', 'exclude'])
def test_unknown_id_is_rejected_without_output(imported, tmp_path, argument):
    path = tmp_path/'unknown.json'
    with pytest.raises(ValueError, match='unknown stable IDs'):
        save_choices(imported, path, **{argument: ['doc-unknown']})
    assert not path.exists()


def test_conflicting_or_empty_choices_are_rejected(imported, tmp_path):
    key = imported['items'][0]['id']
    with pytest.raises(ValueError, match='included and excluded'):
        save_choices(imported, tmp_path/'bad.json', [key], [key])
    with pytest.raises(ValueError, match='explicit human'):
        save_choices(imported, tmp_path/'empty.json')


def test_choice_revision_keeps_previous_and_unspecified_ids(imported, tmp_path):
    a, b, c = [x['id'] for x in imported['items']]
    old = tmp_path/'v1.json'
    save_choices(imported, old, [a], [b])
    before = old.read_bytes()
    new = tmp_path/'v2.json'
    doc = save_choices(imported, new, [b], previous=old)
    assert doc['choices'][a]['decision'] == 'include'
    assert doc['choices'][b]['decision'] == 'include'
    assert c not in doc['choices']
    assert old.read_bytes() == before


def test_existing_inventory_and_raw_outputs_are_protected(imported, tmp_path):
    invpath = tmp_path/'inventory.json'
    invpath.write_text(json.dumps(imported))
    before = invpath.read_bytes()
    key = imported['items'][0]['id']
    with pytest.raises(FileExistsError):
        save_choices(imported, invpath, [key])
    raw = imported['source_run']['local_input_locator']
    with pytest.raises(ValueError, match='original raw'):
        save_choices(imported, raw+'/choices.json', [key])
    with pytest.raises(ValueError, match='original raw'):
        export_inventory(raw, raw+'/review')
    out = tmp_path/'export'
    export_inventory(raw, out)
    with pytest.raises(FileExistsError):
        export_inventory(raw, out)
    assert invpath.read_bytes() == before


def test_binding_rejects_changed_content_and_mismatched_choices(imported, tmp_path):
    key = imported['items'][0]['id']
    path = tmp_path/'choices.json'
    save_choices(imported, path, [key])
    changed = copy.deepcopy(imported)
    changed['items'][0]['title'] = 'Different evidence-derived metadata'
    corrupt = tmp_path/'changed.json'
    corrupt.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match='binding mismatch'):
        load_inventory(corrupt)
    changed['inventory_id'] = inventory_binding(changed)
    with pytest.raises(ValueError, match='different inventory'):
        load_choices(path, changed)


def test_missing_metadata_and_partial_state_are_visible(imported):
    assert all(x['title'] is None for x in imported['items'])
    assert all('title_unknown' in x['gaps'] for x in imported['items'])
    assert all('wordpress_content_type_unknown' in x['gaps'] for x in imported['items'])
    assert '[title unknown]' in listing(imported)
    media = next(x for x in imported['context']['collections'] if x['type'] == 'media')
    # Authored synthetic context tests display; actual imported run gap is verified separately.
    media.update(unique_ids=1661, advertised_total=1753, record_gap=92, status='partial')
    imported['context']['shutdown'] = {'confirmed_aborts': 0, 'unconfirmed_count': 2}
    imported['inventory_id'] = inventory_binding(imported)
    text = listing(imported)
    assert '1661 unique / 1753 advertised' in text and 'record gap 92' in text
    assert "'unconfirmed_count': 2" in text


def test_cli_round_trip_and_unknown_id_exit(tmp_path, capsys):
    root = tmp_path/'raw'
    root.mkdir();raw_fixture(root)
    out = tmp_path/'review'
    main(['import', '--raw', str(root), '--out', str(out)])
    inv = load_inventory(out/'inventory.json')
    selected = tmp_path/'choices.json'
    main(['choose', '--inventory', str(out/'inventory.json'), '--include', inv['items'][0]['id'], '--out', str(selected)])
    main(['list', '--inventory', str(out/'inventory.json'), '--choices', str(selected)])
    assert 'include' in capsys.readouterr().out
    with pytest.raises(SystemExit) as ex:
        main(['choose', '--inventory', str(out/'inventory.json'), '--include', 'unknown', '--out', str(tmp_path/'invalid.json')])
    assert ex.value.code == 2 and not (tmp_path/'invalid.json').exists()


def test_listing_escapes_source_markup_without_altering_metadata(imported):
    row = imported['items'][0]
    row['title'] = '<script>alert(1)</script> [link](x)'
    original = copy.deepcopy(imported)
    text = listing(imported)
    assert '<script>' not in text and '&lt;script&gt;' in text and '\\[link\\]' in text
    assert imported == original
