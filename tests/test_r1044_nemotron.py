"""R1044: atribuição de unidades ASR a locutores diarizados, sem modelo real."""
import importlib

import pytest


def api():
    return importlib.import_module('integrations.video_diarization_nemotron')


def test_assign_clear_and_ambiguous():
    m = api()
    units = [{'id': 'U1', 'start_part': 0.0, 'end_part': 2.0},
             {'id': 'U2', 'start_part': 2.0, 'end_part': 4.0}]
    segments = [{'Start': 0.0, 'End': 1.8, 'Speaker': 0},
                {'Start': 2.0, 'End': 2.8, 'Speaker': 0},
                {'Start': 2.8, 'End': 4.0, 'Speaker': 1}]
    rows = m.assign_units(units, segments, min_overlap=0.3, min_margin=0.15)
    assert rows[0]['speaker'] == 0 and rows[0]['blocked'] is False
    assert rows[1]['speaker'] == 1 and rows[1]['blocked'] is False
    assert rows[0]['verified'] is False


def test_assign_blocks_no_overlap_and_tie():
    m = api()
    rows = m.assign_units(
        [{'id': 'U1', 'start_part': 5.0, 'end_part': 6.0}],
        [{'Start': 0.0, 'End': 1.0, 'Speaker': 0}])
    assert rows[0]['speaker'] is None and rows[0]['blocked'] is True
    rows = m.assign_units(
        [{'id': 'U1', 'start_part': 0.0, 'end_part': 2.0}],
        [{'Start': 0.0, 'End': 2.0, 'Speaker': 0},
         {'Start': 0.0, 'End': 2.0, 'Speaker': 1}])
    assert rows[0]['blocked'] is True and rows[0]['reason'] == 'ambiguous'


def test_cross_boundary_unit_is_clipped_not_rejected():
    m = api()
    rows = m.assign_units(
        [{'id': 'U1', 'start_part': -0.5, 'end_part': 1.0}],
        [{'Start': 0.0, 'End': 1.0, 'Speaker': 0}])
    assert rows[0]['speaker'] == 0 and rows[0]['blocked'] is False


def test_assign_rejects_invalid_segments():
    m = api()
    with pytest.raises(ValueError):
        m.assign_units([{'id': 'U1', 'start_part': 1.0, 'end_part': 0.0}], [])


def test_cache_key_changes_with_model_and_source():
    m = api()
    a = m.cache_key('sha', 'nvidia/Nemotron-3-Diarization', 'R1044-1')
    b = m.cache_key('sha', 'other', 'R1044-1')
    assert a != b and a == m.cache_key('sha', 'nvidia/Nemotron-3-Diarization', 'R1044-1')
