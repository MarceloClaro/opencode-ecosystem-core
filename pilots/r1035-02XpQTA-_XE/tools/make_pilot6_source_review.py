#!/usr/bin/env python3
"""Source + translation review for P0006, before TTS/dubbing.

Basis: Turkish ASR + burned-in English subtitles (OCR/manual) + scene context.
This is a reviewed draft, not native-speaker certification.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE = json.loads((ROOT / 'pilot-P0006/dialogue-reviewed.json').read_text())
OCR = json.loads((ROOT / 'pilot-P0006/ocr-multiframe/english-ocr-multiframe.json').read_text())
ocr_by_id = {item['id']: item for item in OCR['results']}

# English screen text and contextual PT-BR. Short lines are translated by
# conversational function, not by literal dictionary wording.
REVIEW = {
    'U0001': ('It\'s impossible to believe you.', 'Você é inacreditável.',
              'Exasperação; a versão literal soaria artificial.', 'high'),
    'U0002': ('Do not do that.', 'Não faça isso.', '', 'high'),
    'U0003': ("Don't stress so much, calm down.", 'Não se estresse tanto, calma.',
              'ASR divergente; texto de tela usado.', 'medium'),
    'U0004': ("Learn to have fun, if you can't, at least show it.",
              'Aprenda a se divertir; se não conseguir, pelo menos demonstre.',
              'OCR completado por leitura manual do quadro.', 'medium'),
    'U0005': ("You're hurting me.", 'Você está me machucando.', '', 'high'),
    'U0006': ('Chagla, go and get treatment, you are impossible to bear.',
              'Çağla, vá se tratar. Você é insuportável.',
              'ASR divergente; texto de tela usado.', 'medium'),
    'U0007': ('Ryuya, how are you?', 'Rüya, como você está?', '', 'high'),
    'U0008': ('Good and you?', 'Bem, e você?',
              'Troca rápida; a legenda de tela combina duas falas.', 'medium'),
    'U0009': ("Fine. How's it going?", 'Bem. E aí?',
              'Encurtado para o intervalo rápido; sentido preservado.', 'medium'),
    'U0010': ('Okay, what about you?', 'Está indo bem.',
              'Legenda de tela parece adiantada/duplicada; ASR turco "Vallahi güzel gidiyor" usado para o sentido.', 'medium'),
    'U0011': ('Okay, what about you?', 'E você?',
              'Retorno conversacional curto.', 'high'),
    'U0012': ('Same.', 'O mesmo.',
              'Sentido de "o mesmo de sempre"; encurtado.', 'medium'),
    'U0013': ("Ryuya, let's leave.", 'Rüya, vamos embora.',
              'ASR "alayım benim" foi mal ouvido; texto de tela usado.', 'high'),
    'U0014': ('Reason?', 'Por quê?', '', 'high'),
    'U0015': ('Reason. Reason. Reason.', 'Por quê? Por quê? Por quê?', '', 'high'),
    'U0016': ("I'm bored. Let's...", 'Estou entediada. Vamos.', '', 'high'),
    'U0017': ("I'm tired of you, friend.", 'Também cansei de você, amiga.', '', 'high'),
    'U0018': ('Hello.', 'Alô, Çağla.',
              'Nome vem do turco/ASR; OCR só leu "Hello".', 'high'),
    'U0019': ("Chagla, why aren't you following the calls?", 'Por que não atende?',
              'Nome já usado em U0018; frase curta natural.', 'high'),
    'U0020': ("I've been calling you for so many hours, I almost went crazy.",
              'Ligo há horas, quase enlouqueci.', '', 'high'),
    'U0021': ("There's nothing, mom. Everything is fine.", 'Nada, mãe. Está tudo bem.',
              '', 'high'),
    'U0022': ('Alaz?', 'Alaz?', 'OCR leu "Alas?"; nome confirmado pelo contexto.', 'high'),
    'U0023': ('Alaz is fine. Good mood.', 'Alaz está bem. De bom humor.', '', 'high'),
    'U0024': ('Your voice is strange, is something wrong?', 'Sua voz está estranha.',
              'A pergunta seguinte foi separada em U0025.', 'high'),
    'U0025': ('...is something wrong?', 'Algo errado?',
              'Frase curta natural; pergunta completa no contexto.', 'high'),
    'U0026': ('Mom, nothing. Just having fun.', 'Mãe, nada. Só estamos nos divertindo.',
              '', 'high'),
}

reviewed = []
for unit in DIALOGUE['units']:
    english, text, note, confidence = REVIEW[unit['id']]
    ocr = ocr_by_id.get(unit['id'], {})
    reviewed.append({
        'id': unit['id'], 'speaker': unit['speaker'],
        'start_part': unit['start_part'], 'end_part': unit['end_part'],
        'slot_seconds': unit['slot_seconds'],
        'asr_tr': unit['source_text_tr'],
        'english_screen': english,
        'english_ocr_best': ocr.get('best_english', ''),
        'reviewed_pt': text,
        'review_note': note,
        'confidence': confidence,
    })

# Fit-aware dub text: short lines may be shortened but keep their function.
FIT = {
    'U0001': 'Inacreditável.',
    'U0003': 'Não se estresse tanto, calma.',
    'U0004': 'Aprenda a se divertir; se não der, ao menos demonstre.',
    'U0006': 'Çağla, vá se tratar. Você é insuportável.',
    'U0008': 'Bem, e você?',
    'U0009': 'Bem. E aí?',
    'U0010': 'Está indo bem.',
    'U0011': 'E você?',
    'U0012': 'O mesmo.',
    'U0013': 'Rüya, vamos embora.',
    'U0016': 'Estou entediada. Vamos.',
    'U0017': 'Também cansei de você, amiga.',
    'U0019': 'Por que não atende?',
    'U0020': 'Ligo há horas, quase enlouqueci.',
    'U0021': 'Nada, mãe. Está tudo bem.',
    'U0023': 'Alaz está bem. De bom humor.',
    'U0024': 'Sua voz está estranha.',
    'U0025': 'Algo errado?',
    'U0026': 'Mãe, nada. Só estamos nos divertindo.',
}
units = []
for index, item in enumerate(reviewed):
    next_start = reviewed[index + 1]['start_part'] if index + 1 < len(reviewed) else DIALOGUE['part_duration_seconds']
    available = round(max(0.0, next_start - item['start_part']), 3)
    text = FIT.get(item['id'], item['reviewed_pt'])
    units.append({**item, 'available_seconds': available, 'fit_text_pt': text,
                  'shortened_for_fit': text != item['reviewed_pt']})

source_review = {
    'schema_version': 1,
    'part_id': DIALOGUE['part_id'],
    'basis': ['Turkish ASR word timestamps', 'burned-in English subtitles OCR + manual reading',
              'scene context', 'manual PT-BR review'],
    'short_sentence_policy': 'translate conversational function and context, not literal wording',
    'status': 'source_and_translation_reviewed_pending_native_speaker',
    'identity_verified': False,
    'units': reviewed,
    'limitations': [
        'English screen text is itself a translation and may simplify the Turkish',
        'OCR lines were manually corrected where partial; two units remain lower confidence',
        'PT-BR is a reviewed draft, not native-speaker certification',
        'speaker labels are heuristic',
    ],
}
dub = {
    'schema_version': 1,
    'part_id': DIALOGUE['part_id'],
    'part_start_seconds': DIALOGUE['part_start_seconds'],
    'part_end_seconds': DIALOGUE['part_end_seconds'],
    'part_duration_seconds': DIALOGUE['part_duration_seconds'],
    'status': 'dub_text_ready_pending_tts_and_review',
    'speaker_assignment': 'heuristic_scene_review',
    'units': units,
    'limitations': source_review['limitations'],
}
for filename, payload in [('source-review.json', source_review), ('dialogue-dub.json', dub)]:
    target = ROOT / 'pilot-P0006' / filename
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'units': len(units), 'files': ['source-review.json', 'dialogue-dub.json']},
                 ensure_ascii=False))
