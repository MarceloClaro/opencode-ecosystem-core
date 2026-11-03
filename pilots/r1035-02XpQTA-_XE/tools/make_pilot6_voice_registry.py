#!/usr/bin/env python3
"""Create the global character/voice registry for the pilot and mark units."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEAKERS = json.loads((ROOT / 'pilot-P0006/speakers.json').read_text())
DIALOGUE = json.loads((ROOT / 'pilot-P0006/dialogue-dub.json').read_text())
MAP = {'spk1': 'char_male_a', 'spk2': 'char_cagla',
       'spk3': 'char_ruya', 'spk4': 'char_mother'}
HINTS = {
    'char_male_a': 'homem da cena do clube; nome não verificado',
    'char_cagla': 'Çağla (inferido pelo diálogo; não verificado)',
    'char_ruya': 'Rüya (inferido pelo diálogo; não verificado)',
    'char_mother': 'mãe ao telefone (inferida; não verificada)',
}
STATUS = {
    'char_male_a': 'cloned_reference_cleaned_tested',
    'char_cagla': 'cloned_reference_tested',
    'char_ruya': 'cloned_reference_tested',
    'char_mother': 'cloned_reference_tested',
}
characters = {}
for local, character in MAP.items():
    record = SPEAKERS['speakers'][local]
    characters[character] = {
        'display_hint': HINTS[character],
        'reference': record['reference'],
        'sha256': record['sha256'],
        'consent_declared': True,
        'engine': 'XTTS v2 CPU',
        'identity_verified': False,
        'voice_status': STATUS[character],
        'source_units': record.get('source_units', []),
        'limitations': record.get('limitations', []),
    }
registry = {
    'schema_version': 1,
    'source_id': '02XpQTA-_XE',
    'consent_declared': True,
    'documents_verified': False,
    'assignment_policy': {
        'one_voice_per_character': True,
        'new_character_requires_review': True,
        'unmapped_speaker_blocks_tts': True,
        'same_character_reuses_reference': True,
    },
    'characters': characters,
    'notes': [
        'same character always resolves to the same reference/hash',
        'two different characters must not share a reference',
        'new or unmapped speakers block TTS until reviewed',
        'display hints are not verified identities',
    ],
}
voices = ROOT / 'voices'
voices.mkdir(exist_ok=True)
for path, payload in [
    (voices / 'voices.json', registry),
    (ROOT / 'pilot-P0006/speaker-map.json', MAP),
]:
    if path.exists():
        raise SystemExit(f'refusing overwrite: {path}')
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
marked = {**DIALOGUE, 'units': [
    {**unit, 'character_id': MAP[unit['speaker']]} for unit in DIALOGUE['units']]}
target = ROOT / 'pilot-P0006/dialogue-dub-characters.json'
if target.exists():
    raise SystemExit(f'refusing overwrite: {target}')
target.write_text(json.dumps(marked, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'characters': list(characters), 'mapping': MAP,
                  'units_marked': len(marked['units'])}, ensure_ascii=False))
