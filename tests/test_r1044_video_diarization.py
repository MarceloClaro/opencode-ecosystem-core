"""R1044: diarização local sem modelos gated. Funções puras com vetores sintéticos."""
import importlib

import numpy as np
import pytest


def api():
    return importlib.import_module('integrations.video_diarization')


def unit(v):
    a = np.asarray(v, dtype='float32')
    return a / np.linalg.norm(a)


def test_merge_and_split_intervals():
    m = api()
    merged = m.merge_intervals([(0.0, 0.3), (0.4, 0.9), (2.0, 2.2)], max_gap=0.2,
                               min_duration=0.25)
    assert merged == [(0.0, 0.9)]
    chunks = m.chunk_timestamps([(0.0, 5.0)], max_window=2.0, min_window=0.4)
    assert chunks == [(0.0, 2.0), (2.0, 4.0), (4.0, 5.0)]
    with pytest.raises(ValueError):
        m.chunk_timestamps([(1.0, 0.5)], max_window=2.0, min_window=0.4)


def test_normalize_and_cluster_online():
    m = api()
    a = m.normalize_vectors([unit([1, 0, 0]), unit([0.98, 0.1, 0])])
    assert a.shape == (2, 3) and np.allclose(np.linalg.norm(a, axis=1), 1)
    with pytest.raises(ValueError):
        m.normalize_vectors([[0, 0, 0]])
    labels, centroids = m.online_cluster(a, threshold=0.9)
    assert labels.tolist() == [0, 0] and len(centroids) == 1
    labels, centroids = m.online_cluster(
        m.normalize_vectors([unit([1, 0, 0]), unit([0, 1, 0]), unit([0.99, 0.05, 0])]),
        threshold=0.9)
    assert labels.tolist() == [0, 1, 0]


def test_match_reference_margin_and_low_similarity():
    m = api()
    refs = {'a': unit([1, 0, 0]), 'b': unit([0, 1, 0])}
    best = m.match_reference(unit([0.99, 0.05, 0]), refs, min_similarity=0.8,
                             min_margin=0.1)
    assert best['character_id'] == 'a' and best['verified'] is False
    ambiguous = m.match_reference(unit([0.7, 0.7, 0]), refs, min_similarity=0.5,
                                  min_margin=0.1)
    assert ambiguous['character_id'] is None
    low = m.match_reference(unit([0, 0, 1]), refs, min_similarity=0.8, min_margin=0.1)
    assert low['character_id'] is None and low['reason'] == 'low_similarity'


def test_assign_speakers_blocks_unknown():
    m = api()
    chunks = [{'start': 0.0, 'end': 1.0, 'cluster': 0},
              {'start': 1.0, 'end': 2.0, 'cluster': 1}]
    mapping = {0: {'character_id': 'char_a', 'similarity': 0.9},
               1: {'character_id': None, 'similarity': 0.2}}
    result = m.assign_speakers(chunks, mapping)
    assert result[0]['character_id'] == 'char_a'
    assert result[1]['character_id'] is None
    assert result[1]['blocked'] is True
    assert all(r['verified'] is False for r in result)


def test_no_reference_never_invents_identity():
    m = api()
    assert m.match_reference(unit([1, 0]), {}, min_similarity=0.8,
                             min_margin=0.1)['reason'] == 'no_references'
