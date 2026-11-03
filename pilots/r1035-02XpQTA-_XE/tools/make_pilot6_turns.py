#!/usr/bin/env python3
"""Group consecutive lines of the same character into natural TTS turns."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE = json.loads((ROOT / 'pilot-P0006/dialogue-dub-characters.json').read_text())
units = DIALOGUE['units']
turns = []
for unit in units:
    if turns and turns[-1]['character_id'] == unit['character_id']:
        turns[-1]['units'].append(unit)
    else:
        turns.append({'character_id': unit['character_id'],
                      'speaker': unit['speaker'], 'units': [unit]})
result = []
for index, turn in enumerate(turns, 1):
    first = turn['units'][0]
    last = turn['units'][-1]
    next_start = turns[index]['units'][0]['start_part'] if index < len(turns) else DIALOGUE['part_duration_seconds']
    text = ' '.join(unit['fit_text_pt'].strip() for unit in turn['units'])
    result.append({
        'id': f'T{index:03d}',
        'character_id': turn['character_id'],
        'speaker': turn['speaker'],
        'unit_ids': [unit['id'] for unit in turn['units']],
        'start_part': first['start_part'],
        'end_part': last['end_part'],
        'available_seconds': round(max(0.0, next_start - first['start_part']), 3),
        'slot_seconds': round(last['end_part'] - first['start_part'], 3),
        'fit_text_pt': text,
        'grouped': len(turn['units']) > 1,
        'review_note': 'consecutive same-character lines grouped for natural prosody',
    })
payload = {
    'schema_version': 1,
    'part_id': DIALOGUE['part_id'],
    'part_duration_seconds': DIALOGUE['part_duration_seconds'],
    'status': 'turn_draft_pending_native_and_audiovisual_review',
    'turns': result,
    'limitations': ['grouping changes line-level timing; subtitles must follow turns',
                    'same character still uses one global reference',
                    'no TTS or approval in this step'],
}
out = ROOT / 'pilot-P0006/dialogue-turns.json'
if out.exists():
    raise SystemExit(f'refusing overwrite: {out}')
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'turns': len(result), 'grouped': sum(t['grouped'] for t in result)},
                 ensure_ascii=False))
for turn in result:
    print(turn['id'], turn['character_id'], turn['unit_ids'],
          f"{turn['start_part']:.2f}/{turn['available_seconds']:.2f}", turn['fit_text_pt'][:100])
