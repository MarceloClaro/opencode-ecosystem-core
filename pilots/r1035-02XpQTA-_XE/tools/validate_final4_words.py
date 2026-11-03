#!/usr/bin/env python3
"""Per-turn final4 gate using word timestamps, duration, peak and click proxy."""
import difflib
import json
import re
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
TURNS = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
TTS = json.loads((ROOT / 'pilot-P0006/tts-manifest-final4.json').read_text())
WORDS = json.loads((ROOT / 'pilot-P0006/render-final4/dialogue-words.json').read_text())['words']
by_id = {t['id']: t for t in TTS['turns']}


def words(text):
    return re.findall(r'[a-zà-ÿ0-9]+', text.lower())


def sim(expected, actual):
    a, b = words(expected), words(actual)
    if len(a) == 1 and len(b) == 1:
        return difflib.SequenceMatcher(None, a[0], b[0]).ratio()
    return difflib.SequenceMatcher(None, a, b).ratio()


def metrics(path):
    x, sr = sf.read(str(path), dtype='float32', always_2d=True)
    x = x.mean(axis=1)
    peak = float(np.max(np.abs(x))) if len(x) else 0.0
    diff = float(np.max(np.abs(np.diff(x)))) if len(x) > 1 else 0.0
    return len(x) / sr, peak, diff


rows = []
for turn in TURNS['turns']:
    item = by_id[turn['id']]
    start = float(turn['start_part'])
    end = start + max(float(item['final_seconds']), float(turn['slot_seconds'])) + 0.15
    spoken = ' '.join(w['text'] for w in WORDS
                      if start - 0.10 <= (w['start'] + w['end']) / 2 <= end)
    score = sim(turn['fit_text_pt'], spoken)
    duration, peak, diff = metrics(ROOT / item['artifact'])
    checks = {
        'similarity_ok': score >= 0.45,
        'duration_ok': duration <= float(item['available_seconds']) + 0.35,
        'peak_ok': peak < 0.99,
        'click_ok': diff <= 0.60,
    }
    rows.append({'id': turn['id'], 'character_id': turn['character_id'],
                 'expected': turn['fit_text_pt'], 'asr': spoken,
                 'similarity': round(score, 3), 'duration': round(duration, 3),
                 'available': float(item['available_seconds']),
                 'peak': round(peak, 4), 'max_diff': round(diff, 4),
                 'checks': checks, 'passed': all(checks.values())})
report = {'schema_version': 1, 'part_id': TURNS['part_id'],
          'gate': {'min_similarity': 0.45, 'max_overrun': 0.35,
                   'max_peak': 0.99, 'max_diff': 0.60},
          'passed': sum(r['passed'] for r in rows), 'total': len(rows), 'rows': rows,
          'limitations': ['word-timestamp ASR proxy; names may lower similarity',
                          'no listening approval']}
(ROOT / 'pilot-P0006/quality-gate-final4.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    print(('OK  ' if row['passed'] else 'FAIL'), row['id'],
          f"{row['character_id']:14} sim={row['similarity']:.2f} "
          f"dur={row['duration']:.2f}/{row['available']:.2f} "
          f"diff={row['max_diff']:.2f}", '|', row['asr'])
    if not row['passed']:
        print('   EXP:', row['expected'], 'BAD:', [k for k, v in row['checks'].items() if not v])
print(json.dumps({'passed': report['passed'], 'total': report['total']}))
