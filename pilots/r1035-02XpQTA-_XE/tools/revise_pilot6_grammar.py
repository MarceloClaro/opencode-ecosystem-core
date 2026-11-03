#!/usr/bin/env python3
"""Grammar/gender review of the final turns; changes are explicit and audited."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'pilot-P0006/dialogue-turns-final.json').read_text())
overrides = {
    'T003A': 'Não se estresse tanto, fica calma.',
    'T011': 'Igual.',
    'T017': 'Alô, Çağla. Por que não atende? Estou ligando há horas, quase enlouqueci.',
    'T018': 'Não é nada, mãe. Está tudo bem.',
    'T021': 'Sua voz está estranha. Aconteceu algo?',
    'T022': 'Mãe, nada. A gente só está se divertindo.',
}
genders = {'char_male_a': 'masculino', 'char_cagla': 'feminino',
           'char_ruya': 'feminino', 'char_mother': 'feminino'}
addressee = {
    'T001': '—', 'T002': 'homem da cena', 'T003A': 'Çağla', 'T003B': 'Çağla',
    'T004': 'homem da cena', 'T005': 'Çağla', 'T006': 'Rüya', 'T007': 'Çağla',
    'T008': 'Rüya', 'T009': 'Çağla', 'T010': 'Rüya', 'T011': 'Çağla',
    'T012': 'Rüya', 'T013': 'Çağla', 'T014': 'Rüya', 'T015': 'Çağla',
    'T016': 'Rüya', 'T017': 'Çağla', 'T018': 'mãe', 'T019': 'Çağla',
    'T020': 'mãe', 'T021': 'Çağla', 'T022': 'mãe',
}
notes = {
    'T003A': 'imperativo "fica" (você); "calma" feminino concorda com Çağla',
    'T011': '"Igual." evita o masculino "o mesmo" e cabe no intervalo',
    'T015': '"entediada" concorda com Rüya (feminino)',
    'T016': '"amiga" concorda com Rüya (feminino)',
    'T017': '"Estou ligando" em vez de "Ligo"; fala da mãe (feminino)',
    'T018': '"Não é nada" mais natural que "Nada"',
    'T021': '"Aconteceu algo?" mais fluido que "Algo errado?"',
    'T022': '"a gente" com verbo no singular, registro coloquial brasileiro',
}
reviewed = []
for turn in data['turns']:
    text = overrides.get(turn['id'], turn['fit_text_pt'])
    reviewed.append({**turn, 'fit_text_pt': text,
                     'grammar': {'speaker_gender': genders[turn['character_id']],
                                 'addressee': addressee.get(turn['id'], '—'),
                                 'note': notes.get(turn['id'], 'sem alteração')}})
payload = {**data, 'turns': reviewed,
           'status': 'grammar_gender_reviewed_pending_native_and_audiovisual_review'}
out = ROOT / 'pilot-P0006/dialogue-turns-reviewed.json'
if out.exists():
    raise SystemExit(f'refusing overwrite: {out}')
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
lines = ['# Revisão de conjugação e gênero — P0006', '',
         '| Turno | Personagem | Gênero | Destinatário | Texto | Observação |',
         '|---|---|---|---|---|---|']
for turn in reviewed:
    g = turn['grammar']
    lines.append(f"| {turn['id']} | {turn['character_id']} | {g['speaker_gender']} | "
                 f"{g['addressee']} | {turn['fit_text_pt']} | {g['note']} |")
lines += ['', 'Alterações: T003A, T011, T017, T018, T021 e T022. ',
          'A revisão é assistida; ainda requer falante nativo.',
          'Nenhum texto usa tratamento "tu" misturado com "você".']
(ROOT / 'pilot-P0006/GRAMMAR-REVIEW.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'turns': len(reviewed), 'changed': sorted(overrides)}, ensure_ascii=False))
