import importlib
import pytest


def api():
    return importlib.import_module('integrations.dubbing_evidence')


def test_samples_exclusive_and_bounded():
    p = {'part_id': 'v-P0001', 'start_frame': 100, 'end_frame': 200,
         'units': [{'id': 'U1', 'start_part': -0.1, 'end_part': 0.5},
                   {'id': 'U2', 'start_part': 3.8, 'end_part': 4.2}]}
    rows = api().requests(p)
    assert all(0 <= r['frame'] < 100 for r in rows)
    assert {u for r in rows for u in r['unit_ids']} == {'U1', 'U2'}


def test_no_asr_gets_sparse_evidence_not_approval():
    rows = api().requests({'start_frame': 0, 'end_frame': 1880, 'units': []})
    assert len(rows) >= 7
    assert all(r['unit_ids'] == [] for r in rows)


def test_evidence_resume_and_corrupt_cache(tmp_path):
    m = api()
    part = {'part_id': 'v-P0001', 'start_frame': 0, 'end_frame': 25,
            'units': [{'id': 'U1', 'start_part': 0, 'end_part': 1}]}
    source = tmp_path/'source.mp4'
    source.write_bytes(b'synthetic-video-fixture')
    calls = []
    def extract(path, frames):
        calls.append('extract')
        return [b'P5\n1 1\n255\n\xff' for _ in frames]
    def ocr(data):
        calls.append('ocr')
        return 'test text'
    a = m.process_part(tmp_path, part, source, extract, ocr, {'fixture': True})
    b = m.process_part(tmp_path, part, source, extract, ocr, {'fixture': True})
    assert a['cache_hit'] is False and b['cache_hit'] is True
    assert calls == ['extract', 'ocr']
    target = tmp_path / a['artifact']
    assert target.exists()
    image = next(target.parent.glob('*.pgm'))
    image.write_bytes(b'changed')
    with pytest.raises(ValueError, match='integrity'): m.process_part(
        tmp_path, part, source, extract, ocr, {'fixture': True})


def test_extract_count_mismatch_blocks(tmp_path):
    part = {'part_id': 'v-P0001', 'start_frame': 0, 'end_frame': 25, 'units': []}
    source = tmp_path/'source.mp4'
    source.write_bytes(b'fixture')
    with pytest.raises(ValueError, match='count'):
        api().process_part(tmp_path, part, source, lambda *_: [], lambda _: '', {})
