"""R1041: regressões negativas do piloto e contrato de lote. Fixtures sintéticas."""
import importlib
import json

import pytest


def api():
    return importlib.import_module('integrations.dubbing_batch')


def plan():
    return {'video_id': 'v', 'fps': '25/1', 'total_frames': 100,
            'segments': [
                {'id': 'v-P0001', 'start_frame': 0, 'end_frame': 50},
                {'id': 'v-P0002', 'start_frame': 50, 'end_frame': 100}]}


def asr():
    return {'duration': 4, 'language': 'tr', 'segments': [
        {'start': 0.1, 'end': 0.9, 'text': 'bir'},
        {'start': 1.9, 'end': 2.3, 'text': 'iki'},
        {'start': 3, 'end': 3.5, 'text': 'üç'}]}


def test_ownership_exclusive_and_crossing_flag():
    parts = api().partition_source(plan(), asr())
    units = [u for p in parts for u in p['units']]
    assert len(units) == 3
    assert len({u['id'] for u in units}) == 3
    assert len(parts[0]['units']) == 1
    assert parts[1]['units'][0]['crosses_boundary'] is True
    assert all(u['character_id'] is None for u in units)
    assert all(u['source_review'] == 'pending' for u in units)


def test_no_asr_never_means_silent_approved():
    parts = api().partition_source(plan(), {'duration': 4, 'segments': []})
    assert all('no_asr_requires_review' in p['blockers'] for p in parts)


@pytest.mark.parametrize('change', ['gap', 'duplicate', 'traversal', 'nan'])
def test_reject_invalid_plan(change):
    p = plan()
    if change == 'gap': p['segments'][1]['start_frame'] = 51
    if change == 'duplicate': p['segments'][1]['id'] = 'v-P0001'
    if change == 'traversal': p['segments'][1]['id'] = '../outside'
    if change == 'nan': p['segments'][1]['end_frame'] = float('nan')
    with pytest.raises(ValueError): api().partition_source(p, asr())


@pytest.mark.parametrize('expected,heard', [
    ('Inacreditável.', 'Inacreditável, ponto.'),
    ('Não faça isso.', 'Não faça isso, puto.'),
    ('Não se estresse tanto, fique calma.', 'Não se estresse tanto.'),
    ('A gente se diverte.', 'A gente se divertiu.'),
    ('Alaz?', 'Alas!'), ('Bem.', ''),
])
def test_old_false_accepts_are_blocked(expected, heard):
    result = api().compare_transcript(expected, heard)
    assert result['screen_pass'] is False
    assert result['audiovisual_approved'] is False
    assert result['edit_distance'] > 0


def test_exact_asr_is_not_perceptual_approval():
    result = api().compare_transcript('Mãe, nada!', 'mãe nada.')
    assert result['screen_pass'] is True
    assert result['audiovisual_approved'] is False


def test_duration_has_no_editorial_tolerance():
    result = api().check_timing(start=71.13, samples=80640, sample_rate=24000,
                                part_end=74.44, next_start=None)
    assert result['screen_pass'] is False
    assert result['overrun_seconds'] == pytest.approx(0.05)
    assert api().check_timing(start=0, samples=24000, sample_rate=24000,
                             part_end=1, next_start=None)['screen_pass'] is True


def test_missing_review_blocks_tts_and_assembly():
    assert api().preflight('tts', {'units': [{'character_id': None}]})['allow'] is False
    assert api().preflight('assemble', {'parts': []})['allow'] is False
    assert api().preflight('arbitrary_shell', {})['allow'] is False


def test_cache_key_changes_with_text_reference_and_version():
    m = api()
    key = m.cache_key({'text': 'bem', 'ref': 'a'}, {'speed': 1}, 'v1')
    assert key == m.cache_key({'ref': 'a', 'text': 'bem'}, {'speed': 1}, 'v1')
    assert key != m.cache_key({'text': 'mal', 'ref': 'a'}, {'speed': 1}, 'v1')
    assert key != m.cache_key({'text': 'bem', 'ref': 'b'}, {'speed': 1}, 'v1')
    assert key != m.cache_key({'text': 'bem', 'ref': 'a'}, {'speed': 1}, 'v2')


def test_prepare_resume_and_tamper(tmp_path):
    (tmp_path/'parts-plan-final').mkdir()
    (tmp_path/'analysis').mkdir()
    (tmp_path/'parts-plan-final/segments.json').write_text(json.dumps(plan()))
    (tmp_path/'analysis/asr-tr.json').write_text(json.dumps(asr()))
    m = api()
    first = m.prepare(tmp_path)
    second = m.prepare(tmp_path)
    assert first['total_parts'] == second['total_parts'] == 2
    assert first['cache_hit'] is False and second['cache_hit'] is True
    assert second['dubbed_parts'] == 0
    part = tmp_path / second['run_dir'] / 'parts/v-P0001.json'
    part.write_text('{}')
    with pytest.raises(ValueError, match='hash|integrity'): m.prepare(tmp_path)


def test_path_escape_and_symlink_rejected(tmp_path):
    m = api()
    with pytest.raises(ValueError): m.confined_path(tmp_path, '../escape')
    (tmp_path/'link').symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError): m.confined_path(tmp_path, 'link/escape')


def test_hook_blocks_side_effect_and_exceptions(monkeypatch):
    m = api()
    calls = []
    with pytest.raises(ValueError, match='blocked'):
        m.guarded('tts', {'units': []}, lambda: calls.append('effect'))
    assert calls == []
    def broken(*args):
        raise RuntimeError('broken validation')
    monkeypatch.setattr(m, 'preflight', broken)
    with pytest.raises(ValueError, match='blocked'):
        m.guarded('prepare', {}, lambda: calls.append('effect'))
    assert calls == []


def test_hook_is_on_actual_prepare_path(tmp_path, monkeypatch):
    (tmp_path/'parts-plan-final').mkdir()
    (tmp_path/'analysis').mkdir()
    (tmp_path/'parts-plan-final/segments.json').write_text(json.dumps(plan()))
    (tmp_path/'analysis/asr-tr.json').write_text(json.dumps(asr()))
    m = api()
    monkeypatch.setattr(m, 'preflight', lambda *_: {'allow': False, 'blockers': ['test_deny']})
    with pytest.raises(ValueError, match='test_deny'): m.prepare(tmp_path)
    assert list(tmp_path.glob('.dubbing-batch/**/manifest.json')) == []


def test_lock_prevents_simultaneous_prepare(tmp_path):
    m = api()
    with m.locked(tmp_path):
        with pytest.raises(ValueError, match='lock'):
            with m.locked(tmp_path):
                raise AssertionError('must not acquire twice')


def test_immutable_source_review_binding():
    m = api()
    source = {'source_text': 'original', 'start_source': 1.0, 'end_source': 2.0}
    u = {**source, 'id': 'U1', 'crosses_boundary': False,
         'source_review': {'status': 'reviewed', 'reviewer': 'test',
                           'evidence': 'fixture', 'subject_sha256': m.digest(source)}}
    assert m.preflight('translate', {'units': [u]})['allow'] is True
    u['source_text'] = 'modified'
    assert m.preflight('translate', {'units': [u]})['allow'] is False


def test_profiles_exist_through_managed_lifecycle():
    from agents.lifecycle import AgentLifecycleService
    service = AgentLifecycleService()
    for name in ('dubbing-audio-qa', 'dubbing-dialogue-director',
                 'dubbing-voice-continuity', 'dubbing-batch-engineer'):
        assert service.validate(name)['definition_validated'] is True
