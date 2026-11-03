#!/usr/bin/env python3
"""Merge grammar-reviewed turns, split mother lines and stable/clean takes."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_voice_registry import validate_dialogue, validate_registry  # noqa: E402

turns_payload = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
v1 = json.loads((ROOT / 'pilot-P0006/tts-manifest-final.json').read_text())
fixes = json.loads((ROOT / 'pilot-P0006/tts-reviewed/fixes-manifest.json').read_text())
mother = json.loads((ROOT / 'pilot-P0006/tts-reviewed/mother-split-manifest.json').read_text())
registry = validate_registry(json.loads((ROOT / 'voices/voices.json').read_text()), root=ROOT)
mapping = json.loads((ROOT / 'pilot-P0006/speaker-map.json').read_text())
v1_by_id = {item['id']: item for item in v1['turns']}
fix_by_id = {item['id']: item for item in fixes['fixes']}
mother_by_id = {item['id']: item for item in mother['fixes']}
gate = validate_dialogue({'part_id': turns_payload['part_id'],
                          'units': turns_payload['turns']}, mapping, registry)
merged = []
for turn in turns_payload['turns']:
    character = turn['character_id']
    record = registry['characters'][character]
    if turn['id'] in mother_by_id:
        source = mother_by_id[turn['id']]
    elif turn['id'] in fix_by_id and turn['id'] not in ('T017', 'T022'):
        source = fix_by_id[turn['id']]
    elif turn['id'] in v1_by_id:
        source = v1_by_id[turn['id']]
    else:
        raise SystemExit(f'no source take for {turn["id"]}')
    if source['reference_sha256'] != record['sha256']:
        raise SystemExit(f'{turn["id"]}: reference mismatch')
    merged.append({
        'id': turn['id'], 'character_id': character, 'speaker': turn['speaker'],
        'unit_ids': turn['unit_ids'], 'text': turn['fit_text_pt'],
        'reference': record['reference'], 'reference_sha256': record['sha256'],
        'available_seconds': turn['available_seconds'], 'slot_seconds': turn['slot_seconds'],
        'start_part': turn['start_part'], 'end_part': turn['end_part'],
        'final_seconds': source['final_seconds'], 'artifact': source['artifact'],
        'sha256': source['sha256'], 'atempo': source.get('atempo', 1.0),
        'overrun': bool(source.get('overrun', False)),
        'registry_sha256': gate['registry_sha256'],
    })
payload = {
    'schema_version': 1, 'part_id': turns_payload['part_id'],
    'engine': 'XTTS v2 CPU; clean refs for male/ruya/mother; stable ref for cagla',
    'voice_gate': {'status': gate['status'], 'registry_sha256': gate['registry_sha256'],
                   'mapping_sha256': gate['mapping_sha256'],
                   'characters': sorted(gate['characters'])},
    'status': 'tts_generated_pending_audiovisual_review',
    'identity_verified': False,
    'turns': merged,
    'limitations': ['one reference per character',
                    'cagla uses the stable original reference',
                    'grammar/gender reviewed draft; native review pending',
                    'no lip sync or audiovisual approval'],
}
for name, value in [('tts-manifest-final2.json', payload),
                    ('voice-receipt-final2.json', gate)]:
    target = ROOT / 'pilot-P0006' / name
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'turns': len(merged), 'overruns': sum(t['overrun'] for t in merged),
                  'refs': {k: len({t['reference_sha256'] for t in merged
                                   if t['character_id'] == k}) for k in gate['characters']}},
                 ensure_ascii=False))
