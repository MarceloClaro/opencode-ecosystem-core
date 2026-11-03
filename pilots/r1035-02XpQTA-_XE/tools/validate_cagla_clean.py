#!/usr/bin/env python3
"""Batch ASR validation of the 11 clean Cagla takes."""
import difflib
import json
import re
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'pilot-P0006/tts-cagla-clean/cagla-clean-manifest.json').read_text())
MODEL = '/home/marceloclaro/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120'


def words(text):
    return re.findall(r'[a-zà-ÿ0-9]+', text.lower())


def similarity(a, b):
    return difflib.SequenceMatcher(None, words(a), words(b)).ratio()


model = WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=4,
                     num_workers=1, local_files_only=True)
rows = []
for take in MANIFEST['takes']:
    segments, info = model.transcribe(str(ROOT / take['artifact']), language='pt',
                                      word_timestamps=False, vad_filter=True, beam_size=3)
    transcript = ' '.join(segment.text.strip() for segment in segments)
    score = similarity(take['text'], transcript)
    row = {'id': take['id'], 'text': take['text'], 'asr': transcript,
           'similarity': round(score, 3), 'duration': take['final_seconds'],
           'available': take['available_seconds'],
           'passed': score >= 0.45 and take['final_seconds'] <= take['available_seconds'] + 0.35}
    rows.append(row)
    print(('OK  ' if row['passed'] else 'FAIL'), take['id'], f"sim={score:.2f}",
          f"{take['final_seconds']:.2f}/{take['available_seconds']:.2f}",
          '|', transcript, flush=True)
report = {'schema_version': 1, 'part_id': MANIFEST['part_id'],
          'gate': {'min_similarity': 0.45, 'max_overrun': 0.35},
          'passed': sum(r['passed'] for r in rows), 'total': len(rows), 'rows': rows,
          'limitations': ['ASR proxy; names can lower similarity', 'no listening approval']}
(ROOT / 'pilot-P0006/quality-gate-cagla-clean.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'total': report['total']}))
