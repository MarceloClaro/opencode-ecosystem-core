#!/usr/bin/env python3
"""Create gender/age markings bound to the cloned reference hashes."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_voice_registry import validate_profiles, validate_registry  # noqa: E402

registry = validate_registry(json.loads((ROOT / 'voices/voices.json').read_text()), root=ROOT)
base = {
    'char_male_a': dict(gender='masculino', age_group='adulto', age_hint='adulto jovem',
                        profile_id='adult_male_01',
                        clone_status='cloned_reference_cleaned_tested',
                        evidence='aparência e diálogo; identidade não verificada'),
    'char_cagla': dict(gender='feminino', age_group='adulto', age_hint='adulto jovem',
                       profile_id='adult_female_01',
                       clone_status='cloned_from_demucs_vocals_compact',
                       evidence='aparência e diálogo; identidade não verificada'),
    'char_ruya': dict(gender='feminino', age_group='adulto', age_hint='adulto jovem',
                      profile_id='adult_female_02',
                      clone_status='cloned_from_demucs_vocals',
                      evidence='aparência e diálogo; identidade não verificada'),
    'char_mother': dict(gender='feminino', age_group='adulto', age_hint='meia-idade',
                        profile_id='adult_female_03',
                        clone_status='cloned_from_demucs_vocals',
                        evidence='aparência e diálogo; idade não verificada'),
}
characters = {}
for character, profile in base.items():
    record = registry['characters'][character]
    characters[character] = {**profile, 'reference_sha256': record['sha256'],
                             'reference': record['reference'],
                             'clone_engine': 'XTTS v2 CPU',
                             'listening_review': 'pending'}
payload = {
    'schema_version': 1,
    'source_registry_sha256': registry['registry_sha256'],
    'prosody_policy': {
        'crianca': {'tempo': 1.05, 'pitch': 1.03,
                    'note': 'somente se a referência original for de criança; nunca fabricar idade'},
        'adulto': {'tempo': 1.0, 'pitch': 1.0},
        'idoso': {'tempo': 0.97, 'pitch': 0.99,
                  'note': 'ajuste leve; não substitui timbre etário da referência'},
    },
    'gender_policy': 'marcação descritiva; o timbre vem da referência clonada, sem pitch artificial de gênero',
    'characters': characters,
    'limitations': ['gênero/idade são marcações declaradas, não biometria',
                    'nenhuma criança ou idoso foi identificado neste piloto',
                    'revisão humana de voz/idade pendente'],
}
result = validate_profiles(payload, registry)
out = ROOT / 'voices/voice-profiles.json'
if out.exists():
    raise SystemExit(f'refusing overwrite: {out}')
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
receipt = ROOT / 'pilot-P0006/voice-profiles-receipt.json'
if receipt.exists():
    raise SystemExit(f'refusing overwrite: {receipt}')
receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'registry_sha256': registry['registry_sha256'],
                  'counts': result['counts']}, ensure_ascii=False))
