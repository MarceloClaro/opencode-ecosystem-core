#!/usr/bin/env python3
"""Build a reviewed draft dialogue for pilot P0006; not native-speaker approval."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
translated = json.loads((ROOT / 'pilot-P0006/translated-absolute.json').read_text())
PART_START = 373.52
PART_END = 447.96
PART_DURATION = PART_END - PART_START

corrections = {
    'U0001': ('Você é inacreditável.', 'spk1', 'tom de exasperação, não elogio'),
    'U0002': ('Não faça isso.', 'spk2', ''),
    'U0003': ('Minha filha, chega, fica calma.', 'spk1', ''),
    'U0004': ('Quer dizer, ela não acredita; se não consegue, ao menos imite.', 'spk1', 'linha ambígua'),
    'U0005': ('Você está me machucando.', 'spk2', ''),
    'U0006': ('Çağla, vai chorar lá longe. Juro, você é insuportável.', 'spk1', ''),
    'U0007': ('Rüya, tudo bem?', 'spk2', 'encurtado para caber no slot'),
    'U0008': ('Bem, e você?', 'spk3', 'encurtado; fala rápida'),
    'U0009': ('Bem também. E você?', 'spk2', 'encurtado; fala rápida'),
    'U0010': ('Juro, tudo bem.', 'spk3', 'encurtado'),
    'U0011': ('E você?', 'spk2', 'encurtado'),
    'U0012': ('Tudo bem.', 'spk3', 'encurtado'),
    'U0013': ('Rüya, me dá aqui.', 'spk2', ''),
    'U0014': ('Por quê, filha?', 'spk3', ''),
    'U0015': ('Por quê, por quê?', 'spk2', ''),
    'U0016': ('Cansei, vamos.', 'spk3', ''),
    'U0017': ('Também cansei de você.', 'spk2', ''),
    'U0018': ('Alô, Çağla.', 'spk4', 'nome preservado'),
    'U0019': ('Por que não olha o celular?', 'spk4', ''),
    'U0020': ('Ligo há horas, vou enlouquecer.', 'spk4', 'encurtado'),
    'U0021': ('Não, mãe, está tudo bem.', 'spk2', ''),
    'U0022': ('Alaz.', 'spk4', 'nome preservado'),
    'U0023': ('Alaz está bem, de bom humor.', 'spk2', ''),
    'U0024': ('Sua voz está estranha.', 'spk4', ''),
    'U0025': ('Aconteceu algo?', 'spk4', 'encurtado'),
    'U0026': ('Mãe, o que seria? Só estamos nos divertindo.', 'spk2', 'encurtado'),
}

units = []
for unit in translated['units']:
    text, speaker, note = corrections[unit['id']]
    start = max(0.0, round(unit['start'] - PART_START, 3))
    end = min(PART_DURATION, round(unit['end'] - PART_START, 3))
    units.append({
        'id': unit['id'],
        'speaker': speaker,
        'start_part': start,
        'end_part': end,
        'slot_seconds': round(end - start, 3),
        'source_text_tr': unit['source_text'],
        'machine_text_pt': unit['translated_text'],
        'reviewed_text_pt': text,
        'review_note': note,
    })

payload = {
    'schema_version': 1,
    'part_id': '02XpQTA-_XE-P0006',
    'part_start_seconds': PART_START,
    'part_end_seconds': PART_END,
    'part_duration_seconds': PART_DURATION,
    'source_language': 'tr',
    'target_language': 'pt-BR',
    'translation': 'M2M100 418M plus manual draft review',
    'status': 'reviewed_draft_pending_native_and_audiovisual_review',
    'identity_verified': False,
    'speaker_assignment': 'heuristic_scene_review',
    'units': units,
    'limitations': [
        'speaker identities are inferred from scene and dialogue, not verified',
        'translation is a reviewed draft, not native-speaker approval',
        'timings are source ASR timings; dubbed audio will need fitting',
        'no lip sync was attempted',
    ],
}
out = ROOT / 'pilot-P0006/dialogue-reviewed.json'
if out.exists():
    raise SystemExit(f'refusing overwrite: {out}')
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'units': len(units), 'out': str(out)}, ensure_ascii=False))
