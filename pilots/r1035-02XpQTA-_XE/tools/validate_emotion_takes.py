#!/usr/bin/env python3
"""ASR gate for emotion takes; fallback to final5 neutral take on failure."""
import difflib
import json
import re
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
EMO = json.loads((ROOT / 'pilot-P0006/tts-emotion/emotion-prosody-manifest.json').read_text())
TURNS = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
TTS = json.loads((ROOT / 'pilot-P0006/tts-manifest-final5.json').read_text())
by_turn = {t['id']: t for t in TURNS['turns']}
by_tts = {t['id']: t for t in TTS['turns']}
MODEL = '/home/marceloclaro/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120'


def words(text):
    return re.findall(r'[a-zà-ÿ0-9]+', text.lower())


def similarity(a, b):
    wa, wb = words(a), words(b)
    if len(wa) == 1 and len(wb) == 1:
        return difflib.SequenceMatcher(None, wa[0], wb[0]).ratio()
    return difflib.SequenceMatcher(None, wa, wb).ratio()


model = WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=4,
                     num_workers=1, local_files_only=True)
rows = []
for take in EMO['takes']:
    segments, info = model.transcribe(str(ROOT / take['artifact']), language='pt',
                                      word_timestamps=False, vad_filter=True, beam_size=3)
    transcript = ' '.join(segment.text.strip() for segment in segments)
    score = similarity(by_turn[take['id']]['fit_text_pt'], transcript)
    passed = score >= 0.45 and take['final_seconds'] <= take['available_seconds'] + 0.35
    selected = take['artifact']
    fallback = False
    if not passed:
        selected = by_tts[take['id']]['artifact']
        fallback = True
    rows.append({'id': take['id'], 'emotion': take['emotion'], 'text': by_turn[take['id']]['fit_text_pt'],
                 'asr': transcript, 'similarity': round(score, 3),
                 'duration': take['final_seconds'], 'available': take['available_seconds'],
                 'passed': passed, 'fallback_neutral': fallback,
                 'selected_artifact': selected, 'emotion_artifact': take['artifact']})
    print(('OK  ' if passed else 'FALL'), take['id'], f"sim={score:.2f}",
          f"{take['final_seconds']:.2f}/{take['available_seconds']:.2f}", '|', transcript, flush=True)
report = {'schema_version': 1, 'part_id': EMO['part_id'],
          'gate': {'min_similarity': 0.45, 'max_overrun': 0.35},
          'passed': sum(r['passed'] for r in rows), 'total': len(rows), 'rows': rows,
          'limitations': ['ASR proxy; prosody may reduce recognition', 'no listening approval']}
(ROOT / 'pilot-P0006/emotion-gate.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'total': report['total'],
                  'fallbacks': sum(r['fallback_neutral'] for r in rows)}))
