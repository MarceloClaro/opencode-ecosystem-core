"""R1045: montagem das unidades de TTS a partir de cluster, tradução e voz."""
import importlib

import pytest


def api():
    return importlib.import_module('integrations.dubbing_xtts')


def test_build_units_maps_cluster_translation_and_voice():
    m = api()
    prepared = {'units': [
        {'id': 'U1', 'start_part': 0.0, 'end_part': 2.0, 'source_text': 'a'},
        {'id': 'U2', 'start_part': 2.0, 'end_part': 3.0, 'source_text': 'b'}]}
    assignment = {'units': [
        {'id': 'U1', 'cluster': 0, 'blocked': False},
        {'id': 'U2', 'cluster': 1, 'blocked': False}]}
    translation = {'units': [
        {'id': 'U1', 'translated_text': 'Bom dia.'},
        {'id': 'U2', 'translated_text': 'Até logo.'}]}
    registry = {'characters': {
        'char_auto_01': {'cluster': 0, 'reference': 'r1.wav', 'sha256': 'a' * 64},
        'char_auto_02': {'cluster': 1, 'reference': 'r2.wav', 'sha256': 'b' * 64}}}
    units, skipped = m.build_units(prepared, assignment, translation, registry)
    assert len(units) == 2 and skipped == []
    assert units[0]['character_id'] == 'char_auto_01'
    assert units[0]['translated_text'] == 'Bom dia.'
    assert units[0]['reference_sha256'] == 'a' * 64
    assert units[1]['reference'] == 'r2.wav'


def test_blocked_or_untranslated_is_skipped_not_guessed():
    m = api()
    prepared = {'units': [{'id': 'U1', 'start_part': 0.0, 'end_part': 1.0}]}
    assignment = {'units': [{'id': 'U1', 'cluster': 0, 'blocked': True}]}
    units, skipped = m.build_units(prepared, assignment, {'units': []},
                                   {'characters': {}})
    assert units == [] and skipped[0]['reason'] == 'blocked'
    assignment['units'][0]['blocked'] = False
    registry = {'characters': {'char_auto_01': {
        'cluster': 0, 'reference': 'r.wav', 'sha256': 'a' * 64}}}
    with pytest.raises(ValueError, match='translation'):
        m.build_units(prepared, assignment, {'units': []}, registry)


def test_cluster_without_character_is_skipped():
    m = api()
    prepared = {'units': [{'id': 'U1', 'start_part': 0.0, 'end_part': 1.0}]}
    assignment = {'units': [{'id': 'U1', 'cluster': 9, 'blocked': False}]}
    translation = {'units': [{'id': 'U1', 'translated_text': 'Oi.'}]}
    units, skipped = m.build_units(prepared, assignment, translation,
                                   {'characters': {}})
    assert units == [] and skipped[0]['reason'] == 'unmapped_cluster'
