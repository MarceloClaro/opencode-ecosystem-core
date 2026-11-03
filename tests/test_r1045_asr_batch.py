"""R1045: cache e validação do lote ASR large-v3, sem carregar modelo."""
import importlib

import pytest


def api():
    return importlib.import_module('integrations.dubbing_asr_batch')


def test_cache_key_binds_source_model_and_params():
    m = api()
    a = m.cache_key('a' * 64, 'large-v3', {'language': 'tr', 'beam_size': 1})
    b = m.cache_key('a' * 64, 'large-v3', {'language': 'tr', 'beam_size': 2})
    assert a != b
    assert a == m.cache_key('a' * 64, 'large-v3', {'language': 'tr', 'beam_size': 1})


def test_segments_are_normalized_and_reject_empty():
    m = api()
    rows = m.normalize_segments([
        {'start': 0.0, 'end': 1.0, 'text': ' Merhaba '},
        {'start': 1.0, 'end': 2.0, 'text': 'Dünya'}])
    assert rows[0]['text'] == 'Merhaba'
    with pytest.raises(ValueError):
        m.normalize_segments([{'start': 0.0, 'end': 1.0, 'text': ' '}])
