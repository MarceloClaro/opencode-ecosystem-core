"""R1040 fixtures are synthetic; they enforce voice identity policy, not identity."""
import importlib.util
import json
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'integrations/video_voice_registry.py'


def api():
    assert MODULE.is_file(), 'registro de vozes ainda ausente'
    spec = importlib.util.spec_from_file_location('video_voice_registry', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_ref(tmp_path, name, payload):
    path = tmp_path / name
    path.write_bytes(payload)
    return path


def registry(tmp_path, refs=None):
    refs = refs or [('char_a', 'a.wav', b'voice-a'), ('char_b', 'b.wav', b'voice-b')]
    characters = {}
    for character, filename, payload in refs:
        path = make_ref(tmp_path, filename, payload)
        characters[character] = {
            'display_hint': character, 'reference': str(path),
            'sha256': __import__('hashlib').sha256(payload).hexdigest(),
            'consent_declared': True, 'engine': 'XTTS v2',
            'identity_verified': False,
        }
    return {
        'schema_version': 1, 'source_id': 'fixture',
        'consent_declared': True, 'documents_verified': False,
        'assignment_policy': {
            'one_voice_per_character': True,
            'new_character_requires_review': True,
            'unmapped_speaker_blocks_tts': True,
            'same_character_reuses_reference': True,
        },
        'characters': characters,
    }, characters


def dialogue(units):
    return {'schema_version': 1, 'part_id': 'fixture-P0001', 'units': units}


def test_valid_registry_receipt_and_same_character_single_voice(tmp_path):
    m = api()
    reg, chars = registry(tmp_path)
    mapping = {'spk1': 'char_a', 'spk2': 'char_b'}
    data = dialogue([
        {'id': 'U0001', 'speaker': 'spk1', 'text': 'a'},
        {'id': 'U0002', 'speaker': 'spk2', 'text': 'b'},
        {'id': 'U0003', 'speaker': 'spk1', 'text': 'c'},
    ])
    normalized = m.validate_registry(reg)
    assert normalized['characters']['char_a']['sha256'] == chars['char_a']['sha256']
    assert m.validate_mapping(mapping, normalized) == mapping
    receipt = m.validate_dialogue(data, mapping, normalized)
    assert receipt['characters']['char_a']['unit_ids'] == ['U0001', 'U0003']
    assert len({v['reference_sha256'] for v in receipt['characters'].values()}) == 2
    assert receipt['status'] == 'voice_assignment_valid_pending_native_and_audiovisual_review'


def test_missing_reference_rejected(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    reg['characters']['char_a']['reference'] = str(tmp_path / 'absent.wav')
    with pytest.raises(ValueError, match='reference'):
        m.validate_registry(reg)


def test_hash_mismatch_rejected(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    reg['characters']['char_a']['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='hash'):
        m.validate_registry(reg)


def test_consent_required(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    reg['characters']['char_a']['consent_declared'] = False
    with pytest.raises(ValueError, match='consent'):
        m.validate_registry(reg)


def test_duplicate_voice_reference_rejected(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    reg['characters']['char_b']['sha256'] = reg['characters']['char_a']['sha256']
    reg['characters']['char_b']['reference'] = reg['characters']['char_a']['reference']
    with pytest.raises(ValueError, match='duplicate|same voice'):
        m.validate_registry(reg)


def test_unknown_character_and_duplicate_local_mapping_rejected(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    normalized = m.validate_registry(reg)
    with pytest.raises(ValueError, match='character'):
        m.validate_mapping({'spk1': 'char_x'}, normalized)
    with pytest.raises(ValueError, match='same character|duplicate'):
        m.validate_mapping({'spk1': 'char_a', 'spk2': 'char_a'}, normalized)


def test_dialogue_unknown_speaker_rejected(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    normalized = m.validate_registry(reg)
    with pytest.raises(ValueError, match='speaker'):
        m.validate_dialogue(dialogue([{'id': 'U0001', 'speaker': 'spk9', 'text': 'x'}]),
                            {'spk1': 'char_a'}, normalized)


def test_explicit_character_must_match_mapping(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    normalized = m.validate_registry(reg)
    with pytest.raises(ValueError, match='character'):
        m.validate_dialogue(dialogue([{
            'id': 'U0001', 'speaker': 'spk1', 'character_id': 'char_b', 'text': 'x'}]),
            {'spk1': 'char_a'}, normalized)


def test_receipt_changes_when_registry_changes(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    mapping = {'spk1': 'char_a'}
    data = dialogue([{'id': 'U0001', 'speaker': 'spk1', 'text': 'x'}])
    first = m.validate_dialogue(data, mapping, m.validate_registry(reg))
    ref = Path(reg['characters']['char_a']['reference'])
    ref.write_bytes(b'voice-a-changed')
    reg['characters']['char_a']['sha256'] = m.sha256_file(ref)
    second = m.validate_dialogue(data, mapping, m.validate_registry(reg))
    assert first['registry_sha256'] != second['registry_sha256']


def profiles(reg, overrides=None):
    characters = {}
    for character, record in reg['characters'].items():
        characters[character] = {
            'gender': 'feminino' if character != 'char_a' else 'masculino',
            'age_group': 'adulto', 'age_hint': 'adulto jovem',
            'profile_id': f'profile_{character}',
            'reference_sha256': record['sha256'],
            'clone_status': 'cloned_reference_tested',
            'evidence': 'visual/dialogue inference; not verified',
        }
    if overrides:
        for character, values in overrides.items():
            characters[character].update(values)
    return {'schema_version': 1,
            'source_registry_sha256': reg.get('registry_sha256', ''),
            'characters': characters}


def test_valid_profiles_and_counts(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    normalized = m.validate_registry(reg)
    data = profiles(normalized)
    result = m.validate_profiles(data, normalized)
    assert result['counts']['gender']['masculino'] == 1
    assert result['counts']['age_group']['adulto'] == 2
    assert result['characters']['char_a']['gender'] == 'masculino'


@pytest.mark.parametrize('field,value', [
    ('gender', 'outro'), ('age_group', 'jovem'),
    ('profile_id', ''), ('clone_status', ''), ('evidence', ''),
])
def test_invalid_profile_fields(tmp_path, field, value):
    m = api()
    reg, _ = registry(tmp_path)
    normalized = m.validate_registry(reg)
    data = profiles(normalized, {'char_a': {field: value}})
    with pytest.raises(ValueError):
        m.validate_profiles(data, normalized)


def test_profile_missing_character_or_hash_mismatch(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    normalized = m.validate_registry(reg)
    data = profiles(normalized)
    data['characters'].pop('char_b')
    with pytest.raises(ValueError, match='character'):
        m.validate_profiles(data, normalized)
    data = profiles(normalized)
    data['characters']['char_a']['reference_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='reference'):
        m.validate_profiles(data, normalized)


def test_profiles_bound_to_current_registry(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    normalized = m.validate_registry(reg)
    data = profiles(normalized)
    data['source_registry_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='registry'):
        m.validate_profiles(data, normalized)


def test_cli_no_overwrite(tmp_path):
    m = api()
    reg, _ = registry(tmp_path)
    mapping = {'spk1': 'char_a'}
    data = dialogue([{'id': 'U0001', 'speaker': 'spk1', 'text': 'x'}])
    registry_path = tmp_path / 'voices.json'
    mapping_path = tmp_path / 'map.json'
    dialogue_path = tmp_path / 'dialogue.json'
    out = tmp_path / 'receipt.json'
    registry_path.write_text(json.dumps(reg))
    mapping_path.write_text(json.dumps(mapping))
    dialogue_path.write_text(json.dumps(data))
    args = ['--registry', str(registry_path), '--mapping', str(mapping_path),
            '--dialogue', str(dialogue_path), '--out', str(out), '--root', str(tmp_path)]
    m.main(args)
    assert json.loads(out.read_text())['status'].startswith('voice_assignment')
    with pytest.raises(FileExistsError):
        m.main(args)
