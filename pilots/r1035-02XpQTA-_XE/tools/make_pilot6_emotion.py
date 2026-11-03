#!/usr/bin/env python3
"""Annotate emotion/intent per turn and derive a conservative prosody profile."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TURNS = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
# emotion, intensity 1-5, irony, evidence
ANNOTATION = {
    'T001': ('exasperação', 4, True, '“Inacreditável” + contexto de briga'),
    'T002': ('protesto/dor', 3, False, '“Não faça isso” + “Você está me machucando”'),
    'T003A': ('calma/ponderação', 3, False, 'homem tenta acalmar Çağla'),
    'T003B': ('ironia/crítica', 3, True, '“Aprenda a se divertir…”'),
    'T004': ('dor/queixa', 4, False, '“Você está me machucando”'),
    'T005': ('raiva/exasperação', 4, False, '“vá se tratar… insuportável”'),
    'T006': ('amizade/preocupação', 2, False, 'cumprimento a Rüya'),
    'T007': ('amizade/casual', 2, False, '“Bem, e você?”'),
    'T008': ('casual/leve', 2, False, 'resposta curta “Tudo bem.”'),
    'T009': ('casual', 2, False, '“Está indo bem.”'),
    'T010': ('brincadeira', 2, False, '“E você?”'),
    'T011': ('ironia/leve', 2, True, '“Igual.”'),
    'T012': ('urgência/aborrecimento', 3, False, '“Rüya, vamos embora.”'),
    'T013': ('curiosidade', 2, False, '“Por quê?”'),
    'T014': ('deboche/ironia', 4, True, 'repetição “Por quê? Por quê?”'),
    'T015': ('tédio', 3, False, '“Estou entediada. Vamos.”'),
    'T016': ('deboche/cansaço', 3, True, '“Também cansei de você, amiga.”'),
    'T017A': ('preocupação/urgência', 4, False, 'telefonema, “por que não atende?”'),
    'T017B': ('preocupação/urgência', 5, False, '“Chamei várias vezes, quase enlouqueci.”'),
    'T018': ('tranquilização/tensão', 3, False, '“Não é nada, mãe…”'),
    'T019': ('preocupação', 3, False, '“Alaz?”'),
    'T020': ('tranquilização/brincadeira', 3, False, '“Alaz está bem. De bom humor.”'),
    'T021A': ('preocupação', 4, False, '“Sua voz está estranha.”'),
    'T021B': ('apreensão', 4, False, '“Aconteceu algo?”'),
    'T022': ('tranquilização/leve', 3, False, '“Mãe, nada. A gente se diverte.”'),
}
PROFILES = {
    'exasperação': (1.06, 1.005, 1.0), 'protesto/dor': (0.98, 1.010, 1.0),
    'calma/ponderação': (0.97, 0.990, 0.0), 'ironia/crítica': (0.96, 0.980, 0.0),
    'dor/queixa': (0.98, 1.010, 1.0), 'raiva/exasperação': (1.06, 1.005, 1.0),
    'amizade/preocupação': (1.00, 1.000, 0.0), 'amizade/casual': (1.00, 1.000, 0.0),
    'casual/leve': (1.00, 1.005, 0.0), 'casual': (1.00, 1.000, 0.0),
    'brincadeira': (1.04, 1.010, 0.5), 'ironia/leve': (0.98, 0.990, 0.0),
    'urgência/aborrecimento': (1.05, 1.005, 0.5), 'curiosidade': (1.02, 1.010, 0.0),
    'deboche/ironia': (1.02, 1.015, 0.5), 'tédio': (0.95, 0.985, -0.5),
    'deboche/cansaço': (0.97, 0.990, 0.0), 'preocupação/urgência': (1.07, 1.015, 1.0),
    'tranquilização/tensão': (0.98, 0.995, 0.0), 'preocupação': (1.03, 1.010, 0.0),
    'tranquilização/brincadeira': (1.02, 1.005, 0.0), 'apreensão': (1.04, 1.015, 0.0),
    'tranquilização/leve': (1.00, 1.005, 0.0),
}
rows = []
for turn in TURNS['turns']:
    emotion, intensity, irony, evidence = ANNOTATION[turn['id']]
    base_tempo, base_pitch, base_gain = PROFILES[emotion]
    factor = 0.6 + 0.2 * intensity
    tempo = 1 + (base_tempo - 1) * factor
    pitch = 1 + (base_pitch - 1) * factor
    gain = base_gain * factor
    rows.append({**turn, 'intent': {
        'emotion': emotion, 'intensity': intensity, 'irony': irony,
        'evidence': evidence, 'prosody': {'tempo': round(tempo, 4),
                                          'pitch': round(pitch, 4),
                                          'gain_db': round(gain, 2)},
    }})
payload = {'schema_version': 1, 'part_id': TURNS['part_id'],
           'status': 'emotion_intent_annotated_pending_tts_validation',
           'turns': rows,
           'limitations': ['annotations are heuristic from text/screen/context',
                           'XTTS v2 has no certified emotion labels; prosody is approximate',
                           'native/audiovisual review required']}
out = ROOT / 'pilot-P0006/dialogue-turns-emotion.json'
if out.exists():
    raise SystemExit(f'refusing overwrite: {out}')
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
lines = ['# Emoção, ironia e intenção — P0006', '',
         '| Turno | Personagem | Emoção | Intensidade | Ironia | Evidência | Tempo | Pitch | Ganho |',
         '|---|---|---|---:|---|---|---:|---:|---:|']
for row in rows:
    i = row['intent']; p = i['prosody']
    lines.append(f"| {row['id']} | {row['character_id']} | {i['emotion']} | {i['intensity']} | "
                 f"{'sim' if i['irony'] else 'não'} | {i['evidence']} | {p['tempo']:.3f} | "
                 f"{p['pitch']:.3f} | {p['gain_db']:+.1f} dB |")
lines += ['', 'A prosódia é aplicada sobre a tomada validada; se o ASR/duração piorar,',
          'a tomada neutra é restaurada. Não é emoção certificada por modelo.']
(ROOT / 'pilot-P0006/EMOTION-REVIEW.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'turns': len(rows), 'irony': sum(r['intent']['irony'] for r in rows)},
                 ensure_ascii=False))
