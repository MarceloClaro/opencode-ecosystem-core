"""R1045: agrupamento global de locutores e referências provisórias."""
import importlib

import numpy as np
import pytest


def api():
    return importlib.import_module('integrations.video_speaker_cluster')


def unit(v):
    a = np.asarray(v, dtype='float32')
    return a / np.linalg.norm(a)


def row(pid, idx, start, end, vec, speaker=0):
    return {'part_id': pid, 'index': idx, 'start': start, 'end': end,
            'speaker': speaker, 'vector': unit(vec)}


def test_choose_longest_per_cluster_and_block_short():
    m = api()
    rows = [row('p', 0, 0, 0.5, [1, 0]), row('p', 1, 1, 2.0, [1, 0]),
            row('p', 2, 3, 5.0, [0, 1])]
    labels = np.array([0, 0, 1])
    chosen = m.choose_references(rows, labels, min_duration=0.8)
    assert chosen[0]['index'] == 1
    assert chosen[1]['index'] == 2


def test_assign_units_to_clusters_blocks_ambiguity():
    m = api()
    segments = [{'Start': 0.0, 'End': 1.0, 'cluster': 0},
                {'Start': 1.0, 'End': 2.0, 'cluster': 1}]
    units = [{'id': 'U1', 'start_part': 0.0, 'end_part': 1.0},
             {'id': 'U2', 'start_part': 1.0, 'end_part': 2.0}]
    rows = m.assign_units(units, segments, min_overlap=0.5, min_margin=0.1)
    assert rows[0]['cluster'] == 0 and rows[0]['blocked'] is False
    assert rows[1]['cluster'] == 1 and rows[1]['blocked'] is False
    rows = m.assign_units(
        [{'id': 'U1', 'start_part': 0.0, 'end_part': 2.0}],
        [{'Start': 0.0, 'End': 2.0, 'cluster': 0},
         {'Start': 0.0, 'End': 2.0, 'cluster': 1}])
    assert rows[0]['blocked'] is True and rows[0]['reason'] == 'ambiguous'


def test_match_clusters_reports_known_candidates():
    m = api()
    centroids = np.stack([unit([1, 0]), unit([0, 1])])
    refs = {'known': unit([1, 0])}
    out = m.match_clusters(centroids, refs, min_similarity=0.8, min_margin=0.1)
    assert out[0]['nearest_known'] == 'known'
    assert out[1]['nearest_known'] is None


def test_auto_speakers_are_unique_and_unverified():
    m = api()
    refs = {0: {'path': 'a.wav', 'sha256': 'a' * 64, 'duration': 2.0, 'start': 0,
                'end': 2.0, 'part_id': 'p'},
            1: {'path': 'b.wav', 'sha256': 'b' * 64, 'duration': 3.0, 'start': 4,
                'end': 7.0, 'part_id': 'p'}}
    matches = {0: {'nearest_known': 'char_a', 'similarity': 0.7},
               1: {'nearest_known': None, 'similarity': None}}
    payload = m.build_auto_speakers(refs, matches, model='test', threshold=0.55)
    assert set(payload['characters']) == {'char_auto_01', 'char_auto_02'}
    assert all(c['verified'] is False for c in payload['characters'].values())
    assert len({c['sha256'] for c in payload['characters'].values()}) == 2


def test_invalid_vectors_rejected():
    m = api()
    with pytest.raises(ValueError):
        m.choose_references([{'index': 0, 'start': 0, 'end': 1, 'vector': [0, 0]}],
                            np.array([0]))
