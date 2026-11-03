#!/usr/bin/env python3
"""Final6: validated emotion takes for all 25 turns, same character refs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_voice_registry import validate_dialogue, validate_registry  # noqa: E402

TURNS = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
V5 = json.loads((ROOT / 'pilot-P0006/tts-manifest-final5.json').read_text())
EMO = json.loads((ROOT / 'pilot-P0006/tts-emotion/emotion-prosody-manifest.json').read_text())
GATE = json.loads((ROOT / 'pilot-P0006/emotion-gate.json').read_text())
REGISTRY = validate_registry(json.loads((ROOT / 'voices/voices.json').read_text()), root=ROOT)
MAPPING = json.loads((ROOT / 'pilot-P0006/speaker-map.json').read_text())
v5_by_id = {t['id']: t for t in V5['turns']}
emo_by_id = {t['id']: t for t in EMO['takes']}
gate_by_id = {t['id']: t for t in GATE['rows']}
gate = validate_dialogue({'part_id': TURNS['part_id'], 'units': TURNS['turns']},
                         MAPPING, REGISTRY)
merged = []
for turn in TURNS['turns']:
    base = v5_by_id[turn['id']]
    emo = emo_by_id[turn['id']]
    selected = gate_by_id[turn['id']]
    if selected['fallback_neutral']:
        raise SystemExit(f'unexpected fallback in final6: {turn["id"]}')
    record = REGISTRY['characters'][turn['character_id']]
    if base['reference_sha256'] != record['sha256']:
        raise SystemExit(f'{turn["id"]}: reference mismatch')
    merged.append({
        'id': turn['id'], 'character_id': turn['character_id'], 'speaker': turn['speaker'],
        'unit_ids': turn['unit_ids'], 'text': turn['fit_text_pt'],
        'reference': record['reference'], 'reference_sha256': record['sha256'],
        'available_seconds': turn['available_seconds'], 'slot_seconds': turn['slot_seconds'],
        'start_part': turn['start_part'], 'end_part': turn['end_part'],
        'final_seconds': emo['final_seconds'], 'artifact': emo['artifact'],
        'sha256': emo['sha256'], 'atempo': emo['tempo'],
        'overrun': emo['final_seconds'] > turn['available_seconds'] + 0.35,
        'emotion': emo['emotion'], 'intensity': emo['intensity'],
        'irony': emo['irony'], 'pitch': emo['pitch'], 'gain_db': emo['gain_db'],
        'registry_sha256': gate['registry_sha256'],
    })
payload = {
    'schema_version': 1, 'part_id': TURNS['part_id'],
    'engine': 'XTTS v2 CPU; clean refs; emotion prosody; ASR-gated 25/25',
    'voice_gate': {'status': gate['status'], 'registry_sha256': gate['registry_sha256'],
                   'mapping_sha256': gate['mapping_sha256'],
                   'characters': sorted(gate['characters'])},
    'emotion_gate': {'passed': GATE['passed'], 'total': GATE['total'],
                     'fallbacks': sum(r['fallback_neutral'] for r in GATE['rows'])},
    'status': 'tts_generated_pending_audiovisual_review',
    'identity_verified': False,
    'turns': merged,
    'limitations': ['prosody is approximate, not certified emotion acting',
                    'one clean reference per character',
                    'no native-speaker, lip sync or audiovisual approval'],
}
for name, value in [('tts-manifest-final6.json', payload),
                    ('voice-receipt-final6.json', gate)]:
    target = ROOT / 'pilot-P0006' / name
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'turns': len(merged), 'overruns': sum(t['overrun'] for t in merged),
                  'emotion_gate': payload['emotion_gate']}, ensure_ascii=False))
