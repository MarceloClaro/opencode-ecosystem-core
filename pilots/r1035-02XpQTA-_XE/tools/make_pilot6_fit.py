#!/usr/bin/env python3
"""Create fit-aware pilot text using the gap until the next line; draft only."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / 'pilot-P0006/dialogue-reviewed.json').read_text())
overrides = {
    'U0001': 'Inacreditável.',
    'U0003': 'Minha filha, calma.',
    'U0008': 'Bem.',
    'U0009': 'Bem também.',
    'U0014': 'Por quê?',
    'U0019': 'Olha o celular.',
    'U0020': 'Ligo há horas, mãe.',
    'U0026': 'Mãe, o que seria? Só nos divertindo.',
}
units = source['units']
for index, unit in enumerate(units):
    unit['fit_text_pt'] = overrides.get(unit['id'], unit['reviewed_text_pt'])
    next_start = units[index + 1]['start_part'] if index + 1 < len(units) else source['part_duration_seconds']
    unit['available_seconds'] = round(max(0.0, next_start - unit['start_part']), 3)
    unit['fit_note'] = 'shortened for available gap' if unit['id'] in overrides else ''
payload = {
    'schema_version': 1,
    'part_id': source['part_id'],
    'part_start_seconds': source['part_start_seconds'],
    'part_end_seconds': source['part_end_seconds'],
    'part_duration_seconds': source['part_duration_seconds'],
    'status': 'fit_draft_pending_tts_and_review',
    'units': units,
    'limitations': [
        'available_seconds is the gap to the next line, not a lip-sync target',
        'text shortening is editorial and still needs native review',
        'no TTS audio or audiovisual approval yet',
    ],
}
out = ROOT / 'pilot-P0006/dialogue-fit.json'
if out.exists():
    raise SystemExit(f'refusing overwrite: {out}')
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'units': len(units), 'out': str(out)}, ensure_ascii=False))
