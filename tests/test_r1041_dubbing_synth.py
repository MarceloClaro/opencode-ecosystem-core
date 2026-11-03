"""Síntese com cache e gate estrito de duração. Motor falso; nenhum modelo é carregado."""
import importlib

import pytest


def api():
    return importlib.import_module('integrations.dubbing_synth')


class FakeEngine:
    def __init__(self, seconds=1.0):
        self.calls = []
        self.seconds = seconds

    def synthesize(self, text, reference, params):
        self.calls.append((text, reference, params))
        return [0.01] * int(self.seconds * 24000)


def line(**over):
    base = {'id': 'U1', 'character_id': 'char_a', 'translated_text': 'Bom dia.',
            'start_part': 0.5, 'end_part': 2.0, 'reference_sha256': 'a' * 64}
    base.update(over)
    return base


def voice():
    return {'reference': 'ref.wav', 'reference_sha256': 'a' * 64}


def test_cache_avoids_second_synthesis(tmp_path):
    m = api()
    engine = FakeEngine()
    first = m.synthesize_line(tmp_path, line(), voice(), engine, {'speed': 1.0}, 'v1')
    second = m.synthesize_line(tmp_path, line(), voice(), engine, {'speed': 1.0}, 'v1')
    assert first['cache_hit'] is False and second['cache_hit'] is True
    assert len(engine.calls) == 1
    assert first['sha256'] == second['sha256']
    assert first['duration_seconds'] <= 1.5
    assert first['audiovisual_approved'] is False


def test_overrun_is_rejected_without_truncation(tmp_path):
    m = api()
    engine = FakeEngine(seconds=2.0)
    with pytest.raises(ValueError, match='overrun'):
        m.synthesize_line(tmp_path, line(), voice(), engine, {}, 'v1')
    assert not list(tmp_path.rglob('*.wav'))


@pytest.mark.parametrize('change', ['unknown_character', 'ref_hash', 'missing_text'])
def test_unresolved_inputs_block(tmp_path, change):
    m = api()
    engine = FakeEngine()
    item = line()
    passed_voice = voice()
    if change == 'unknown_character':
        item['character_id'] = 'char_x'
        passed_voice = None
    if change == 'ref_hash':
        item['reference_sha256'] = 'b' * 64
    if change == 'missing_text':
        item['translated_text'] = ''
    with pytest.raises(ValueError):
        m.synthesize_line(tmp_path, item, passed_voice, engine, {}, 'v1')
    assert engine.calls == []


def test_text_normalization_is_recorded_and_never_changes_words():
    m = api()
    assert m.normalize_tts_text('Bom dia.') == ('Bom dia', True)
    assert m.normalize_tts_text('Bom dia') == ('Bom dia', False)
    assert m.normalize_tts_text('  A gente se diverte.  ') == ('A gente se diverte', True)
    with pytest.raises(ValueError):
        m.normalize_tts_text('   ')


def test_tampered_cached_artifact_is_rejected(tmp_path):
    m = api()
    engine = FakeEngine()
    result = m.synthesize_line(tmp_path, line(), voice(), engine, {}, 'v1')
    (tmp_path / result['artifact']).write_bytes(b'changed')
    with pytest.raises(ValueError, match='integrity'):
        m.synthesize_line(tmp_path, line(), voice(), engine, {}, 'v1')


def test_part_reports_failures_and_is_not_promotable(tmp_path):
    m = api()
    engine = FakeEngine(seconds=0.4)
    units = [line(id='U1'), line(id='U2', start_part=3.0, end_part=3.2)]
    result = m.synthesize_part(tmp_path, {'part_id': 'p', 'units': units},
                              {'char_a': voice()}, engine, {}, 'v1')
    assert result['part_status'] == 'blocked'
    assert [f['id'] for f in result['failures']] == ['U2']
    assert result['promotable'] is False
    assert result['audiovisual_approved'] is False
