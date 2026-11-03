"""R1040 global voice registry and character consistency gate.

One character has one reference voice across every part. A local speaker maps
to exactly one character; two local clusters cannot silently become the same
character, and two characters cannot share the same reference. This enforces
identity consistency, not real-world identity or voice quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError('registry data must be finite JSON') from exc


def _hash(value):
    return hashlib.sha256(_canonical(value).encode('utf-8')).hexdigest()


def _regular_file(value, root, label):
    if not isinstance(value, str) or not value:
        raise ValueError(f'{label}: path required')
    path = Path(value)
    if not path.is_absolute():
        path = Path(root) / path
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'{label}: existing regular reference required')
    return path.resolve()


def validate_registry(registry, *, root=Path('.')):
    if not isinstance(registry, dict) or registry.get('schema_version') != 1:
        raise ValueError('unsupported registry schema')
    if registry.get('consent_declared') is not True:
        raise ValueError('consent must be explicitly declared')
    policy = registry.get('assignment_policy')
    required = ('one_voice_per_character', 'new_character_requires_review',
                'unmapped_speaker_blocks_tts', 'same_character_reuses_reference')
    if not isinstance(policy, dict) or any(policy.get(name) is not True for name in required):
        raise ValueError('assignment policy must enable one voice per character')
    characters = registry.get('characters')
    if not isinstance(characters, dict) or not characters:
        raise ValueError('characters object required')
    normalized = {}
    seen_voice = {}
    for character_id, record in characters.items():
        if not isinstance(character_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', character_id):
            raise ValueError('invalid character_id')
        if not isinstance(record, dict):
            raise ValueError(f'{character_id}: character object required')
        reference = _regular_file(record.get('reference'), root, 'reference')
        actual = sha256_file(reference)
        if not isinstance(record.get('sha256'), str) or actual != record['sha256']:
            raise ValueError(f'{character_id}: reference hash mismatch')
        if record.get('consent_declared') is not True:
            raise ValueError(f'{character_id}: consent not declared')
        if not isinstance(record.get('engine'), str) or not record['engine'].strip():
            raise ValueError(f'{character_id}: engine required')
        if record.get('identity_verified') not in (True, False):
            raise ValueError(f'{character_id}: identity_verified must be boolean')
        if not isinstance(record.get('display_hint'), str):
            raise ValueError(f'{character_id}: display_hint required')
        if actual in seen_voice:
            raise ValueError(f'duplicate reference/same voice across characters: '
                             f'{seen_voice[actual]} and {character_id}')
        seen_voice[actual] = character_id
        normalized[character_id] = {**record, 'reference': str(reference),
                                    'sha256': actual}
    result = {**registry, 'characters': normalized}
    result['registry_sha256'] = _hash({key: value for key, value in result.items()
                                      if key != 'registry_sha256'})
    return result


def validate_mapping(mapping, registry):
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError('speaker mapping required')
    characters = registry.get('characters')
    if not isinstance(characters, dict):
        raise ValueError('normalized registry required')
    seen = {}
    for speaker, character_id in mapping.items():
        if not isinstance(speaker, str) or not speaker.strip():
            raise ValueError('invalid local speaker')
        if not isinstance(character_id, str) or character_id not in characters:
            raise ValueError(f'unknown character for speaker {speaker}')
        if character_id in seen:
            raise ValueError(f'same character mapped to two local speakers: '
                             f'{seen[character_id]} and {speaker}; merge/review')
        seen[character_id] = speaker
    return dict(mapping)


GENDERS = {'feminino', 'masculino', 'nao_identificado'}
AGE_GROUPS = {'crianca', 'adulto', 'idoso', 'nao_identificado'}


def validate_profiles(profiles, registry):
    """Require explicit gender/age marking bound to the current registry."""
    if not isinstance(profiles, dict) or profiles.get('schema_version') != 1:
        raise ValueError('unsupported profiles schema')
    if profiles.get('source_registry_sha256') != registry.get('registry_sha256'):
        raise ValueError('profiles are not bound to the current registry hash')
    characters = profiles.get('characters')
    registry_characters = registry.get('characters')
    if not isinstance(characters, dict) or not isinstance(registry_characters, dict):
        raise ValueError('profile characters required')
    if set(characters) != set(registry_characters):
        raise ValueError('profile character set does not match registry')
    seen_ids = set()
    counts = {'gender': {}, 'age_group': {}}
    for character, profile in characters.items():
        if not isinstance(profile, dict):
            raise ValueError(f'{character}: profile object required')
        gender = profile.get('gender')
        age_group = profile.get('age_group')
        if gender not in GENDERS:
            raise ValueError(f'{character}: invalid gender marking')
        if age_group not in AGE_GROUPS:
            raise ValueError(f'{character}: invalid age_group marking')
        if not isinstance(profile.get('age_hint'), str):
            raise ValueError(f'{character}: age_hint must be a string')
        profile_id = profile.get('profile_id')
        if not isinstance(profile_id, str) or not profile_id.strip() or profile_id in seen_ids:
            raise ValueError(f'{character}: unique profile_id required')
        seen_ids.add(profile_id)
        if profile.get('reference_sha256') != registry_characters[character]['sha256']:
            raise ValueError(f'{character}: reference hash mismatch')
        if not isinstance(profile.get('clone_status'), str) or not profile['clone_status'].strip():
            raise ValueError(f'{character}: clone_status required')
        if not isinstance(profile.get('evidence'), str) or not profile['evidence'].strip():
            raise ValueError(f'{character}: evidence required')
        counts['gender'][gender] = counts['gender'].get(gender, 0) + 1
        counts['age_group'][age_group] = counts['age_group'].get(age_group, 0) + 1
    return {'schema_version': 1,
            'source_registry_sha256': registry['registry_sha256'],
            'characters': characters, 'counts': counts,
            'limitations': ['gender/age are declared markings, not biometric verification',
                            'children/elderly require a corresponding source voice']}


def validate_dialogue(dialogue, mapping, registry):
    if not isinstance(dialogue, dict):
        raise ValueError('dialogue object required')
    units = dialogue.get('units')
    if not isinstance(units, list) or not units:
        raise ValueError('dialogue units required')
    mapping = validate_mapping(mapping, registry)
    characters = {}
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError('dialogue unit object required')
        speaker = unit.get('speaker')
        if speaker not in mapping:
            raise ValueError(f'speaker not mapped: {speaker}')
        character_id = mapping[speaker]
        explicit = unit.get('character_id')
        if explicit is not None and explicit != character_id:
            raise ValueError(f'character mismatch for {unit.get("id")}: '
                             f'{explicit} != {character_id}')
        record = registry['characters'][character_id]
        entry = characters.setdefault(character_id, {
            'reference': record['reference'],
            'reference_sha256': record['sha256'],
            'unit_ids': [],
        })
        entry['unit_ids'].append(unit.get('id'))
    return {
        'schema_version': 1,
        'part_id': dialogue.get('part_id'),
        'registry_sha256': registry['registry_sha256'],
        'mapping_sha256': _hash(mapping),
        'dialogue_sha256': _hash(dialogue),
        'characters': characters,
        'one_voice_per_character': True,
        'status': 'voice_assignment_valid_pending_native_and_audiovisual_review',
        'limitations': [
            'consistency of reference voice, not real-world identity',
            'speaker labels and display hints require human review',
            'no synthesis, audiovisual approval or lip sync in this gate',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', required=True)
    parser.add_argument('--mapping', required=True)
    parser.add_argument('--dialogue', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--root', default='.')
    args = parser.parse_args(argv)
    try:
        registry = json.loads(Path(args.registry).read_text())
        mapping = json.loads(Path(args.mapping).read_text())
        dialogue = json.loads(Path(args.dialogue).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('registry/mapping/dialogue unreadable') from exc
    normalized = validate_registry(registry, root=args.root)
    receipt = validate_dialogue(dialogue, mapping, normalized)
    target = Path(args.out)
    if target.exists():
        raise FileExistsError(target)
    with target.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'characters': len(receipt['characters']),
                      'status': receipt['status'], 'out': str(target.resolve())}))


if __name__ == '__main__':
    main()
