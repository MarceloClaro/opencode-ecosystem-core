#!/usr/bin/env python3
"""Merge final turns, stable/clean references and TTS takes into one manifest."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_voice_registry import validate_dialogue, validate_registry  # noqa: E402

v3 = json.loads((ROOT / 'pilot-P0006/tts-manifest-v3.json').read_text())
v2 = json.loads((ROOT / 'pilot-P0006/tts-manifest-v2.json').read_text())
fixes = json.loads((ROOT / 'pilot-P0006/tts-final/fixes-manifest.json').read_text())
units = json.loads((ROOT / 'pilot-P0006/dialogue-dub-characters.json').read_text())
registry = validate_registry(json.loads((ROOT / 'voices/voices.json').read_text()), root=ROOT)
mapping = json.loads((ROOT / 'pilot-P0006/speaker-map.json').read_text())
v2_by_unit = {unit['id']: unit for unit in v2['units']}
v3_by_turn = {turn['id']: turn for turn in v3['turns']}
fix_by_id = {item['id']: item for item in fixes['fixes']}
unit_by_id = {unit['id']: unit for unit in units['units']}

# Split the grouped male turn back into two utterances for fit/flow.
final_turns = []
for turn in v3['turns']:
    if turn['id'] != 'T003':
        final_turns.append({**turn, 'fit_text_pt': turn.get('fit_text_pt', turn.get('text'))})
        continue
    for suffix, unit_id, available in [('A', 'U0003', 3.02), ('B', 'U0004', 5.58)]:
        unit = unit_by_id[unit_id]
        final_turns.append({
            'id': f'T003{suffix}', 'character_id': 'char_male_a', 'speaker': 'spk1',
            'unit_ids': [unit_id], 'start_part': unit['start_part'],
            'end_part': unit['end_part'], 'available_seconds': available,
            'slot_seconds': unit['slot_seconds'], 'fit_text_pt': unit['fit_text_pt'],
            'grouped': False, 'review_note': 'split grouped male turn for fit/flow',
        })

cagla_turn_to_unit = {
    'T002': 'U0002', 'T004': 'U0005', 'T006': 'U0007', 'T008': 'U0009',
    'T010': 'U0011', 'T012': 'U0013', 'T014': 'U0015', 'T016': 'U0017',
    'T018': 'U0021', 'T020': 'U0023', 'T022': 'U0026',
}
merged = []
for turn in final_turns:
    character = turn['character_id']
    record = registry['characters'][character]
    if turn['id'] in fix_by_id:
        source = fix_by_id[turn['id']]
    elif character == 'char_cagla':
        source = v2_by_unit[cagla_turn_to_unit[turn['id']]]
    else:
        source = v3_by_turn[turn['id']]
    if source['reference_sha256'] != record['sha256']:
        raise SystemExit(f'{turn["id"]}: source reference does not match registry')
    merged.append({
        'id': turn['id'], 'character_id': character, 'speaker': turn['speaker'],
        'unit_ids': turn['unit_ids'], 'text': turn['fit_text_pt'],
        'reference': record['reference'], 'reference_sha256': record['sha256'],
        'available_seconds': turn['available_seconds'], 'slot_seconds': turn['slot_seconds'],
        'start_part': turn['start_part'], 'end_part': turn['end_part'],
        'final_seconds': source['final_seconds'], 'artifact': source['artifact'],
        'sha256': source['sha256'], 'atempo': source.get('atempo', 1.0),
        'overrun': bool(source.get('overrun', False)),
    })
gate = validate_dialogue({'part_id': units['part_id'], 'units': final_turns}, mapping, registry)
for item in merged:
    item['registry_sha256'] = gate['registry_sha256']
turns_payload = {
    'schema_version': 1, 'part_id': units['part_id'],
    'part_duration_seconds': units['part_duration_seconds'],
    'status': 'final_turn_draft_pending_native_and_audiovisual_review',
    'turns': final_turns,
    'limitations': ['turn grouping applied where it improved flow',
                    'male T003 split for fit', 'no approval'],
}
tts_payload = {
    'schema_version': 1, 'part_id': units['part_id'],
    'engine': 'XTTS v2 CPU; Demucs-clean refs for male/ruya/mother; stable ref for cagla',
    'voice_gate': {'status': gate['status'], 'registry_sha256': gate['registry_sha256'],
                   'mapping_sha256': gate['mapping_sha256'],
                   'characters': sorted(gate['characters'])},
    'status': 'tts_generated_pending_audiovisual_review',
    'identity_verified': False,
    'turns': merged,
    'limitations': ['one reference per character',
                    'cagla uses the stable original reference; clean Demucs ref was unstable',
                    'no native-speaker, lip sync or audiovisual approval'],
}
for name, payload, exists_ok in [
    ('dialogue-turns-final.json', turns_payload, False),
    ('tts-manifest-final.json', tts_payload, False),
    ('voice-receipt-final.json', gate, False),
]:
    target = ROOT / 'pilot-P0006' / name
    if target.exists() and not exists_ok:
        raise SystemExit(f'refusing overwrite: {target}')
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'turns': len(merged), 'characters': sorted(gate['characters']),
                  'overruns': sum(t['overrun'] for t in merged),
                  'registry_sha256': gate['registry_sha256']}, ensure_ascii=False))
