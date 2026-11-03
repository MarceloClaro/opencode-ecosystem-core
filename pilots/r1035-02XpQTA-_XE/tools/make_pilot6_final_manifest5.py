#!/usr/bin/env python3
"""Final5: T017B rephrased for intelligibility; per-line fades in render."""
import hashlib, json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_voice_registry import validate_dialogue, validate_registry  # noqa: E402

turns_payload = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
v4 = json.loads((ROOT / 'pilot-P0006/tts-manifest-final4.json').read_text())
registry = validate_registry(json.loads((ROOT / 'voices/voices.json').read_text()), root=ROOT)
mapping = json.loads((ROOT / 'pilot-P0006/speaker-map.json').read_text())
v4_by_id = {item['id']: item for item in v4['turns']}
gate = validate_dialogue({'part_id': turns_payload['part_id'],
                          'units': turns_payload['turns']}, mapping, registry)
path = ROOT / 'pilot-P0006/tts-final4/T017B-fit.wav'
sha = hashlib.sha256(path.read_bytes()).hexdigest()
merged = []
for turn in turns_payload['turns']:
    character = turn['character_id']
    record = registry['characters'][character]
    source = v4_by_id.get(turn['id'])
    if source is None:
        raise SystemExit(f'no source take for {turn["id"]}')
    if turn['id'] == 'T017B':
        artifact = str(path.relative_to(ROOT))
        seconds = 2.380
    else:
        artifact = source['artifact']
        seconds = source['final_seconds']
    if source['reference_sha256'] != record['sha256']:
        raise SystemExit(f'{turn["id"]}: reference mismatch')
    merged.append({
        'id': turn['id'], 'character_id': character, 'speaker': turn['speaker'],
        'unit_ids': turn['unit_ids'], 'text': turn['fit_text_pt'],
        'reference': record['reference'], 'reference_sha256': record['sha256'],
        'available_seconds': turn['available_seconds'], 'slot_seconds': turn['slot_seconds'],
        'start_part': turn['start_part'], 'end_part': turn['end_part'],
        'final_seconds': seconds, 'artifact': artifact,
        'sha256': sha if turn['id'] == 'T017B' else source['sha256'],
        'atempo': source.get('atempo', 1.0),
        'overrun': seconds > turn['available_seconds'] + 0.35,
        'registry_sha256': gate['registry_sha256'],
    })
payload = {
    'schema_version': 1, 'part_id': turns_payload['part_id'],
    'engine': 'XTTS v2 CPU; clean refs; T017B rephrased; per-line fades in render',
    'voice_gate': {'status': gate['status'], 'registry_sha256': gate['registry_sha256'],
                   'mapping_sha256': gate['mapping_sha256'],
                   'characters': sorted(gate['characters'])},
    'status': 'tts_generated_pending_audiovisual_review',
    'identity_verified': False,
    'turns': merged,
    'limitations': ['one clean reference per character',
                    'phone line rephrased for TTS intelligibility',
                    'no native-speaker, lip sync or audiovisual approval'],
}
for name, value in [('tts-manifest-final5.json', payload),
                    ('voice-receipt-final5.json', gate)]:
    target = ROOT / 'pilot-P0006' / name
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'turns': len(merged), 'overruns': sum(t['overrun'] for t in merged)},
                 ensure_ascii=False))
